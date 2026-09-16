from dataclasses import dataclass
from typing import Dict, List, Optional
import os
import re
import csv
import numpy as np

# Reuse MELTSState when called from the package
try:
    from .melt_physics_workflow import MELTSState
except ImportError:
    @dataclass
    class MELTSState:
        temperature_K: float
        pressure_GPa: float
        melt_fraction: float
        melt_composition: Dict[str, float]
        mineral_modes: Dict[str, float]
        melt_density_kg_m3: Optional[float] = None
        solid_density_kg_m3: Optional[float] = None


class AlphaMELTSStep:
    """Internal container per equilibrium step."""
    def __init__(self,
                 T_C: float,
                 P_kbar: float,
                 liquid_mass_g: Optional[float],
                 system_mass_g: Optional[float],
                 melt_oxides_wt: Dict[str, float],
                 solids_masses_g: Dict[str, float]):
        self.T_C = T_C
        self.P_kbar = P_kbar
        self.liquid_mass_g = liquid_mass_g
        self.system_mass_g = system_mass_g
        self.melt_oxides_wt = melt_oxides_wt
        self.solids_masses_g = solids_masses_g

    @property
    def phi(self) -> float | None:
        if self.liquid_mass_g is None or self.system_mass_g is None or self.system_mass_g == 0:
            return None
        return float(self.liquid_mass_g / self.system_mass_g)

    @property
    def T_K(self) -> float:
        return float(self.T_C + 273.15)

    @property
    def P_GPa(self) -> float:
        return float(self.P_kbar * 0.1)  # 1 kbar = 0.1 GPa


class AlphaMELTSLoader:
    """
    Loader for alphaMELTS / MELTS outputs:
      - melts-liquid.tbl (CSV-like, one record per step)
      - melts.out (full text log)

    Format references: MELTS manual output docs (>= v1.1.3).  # See README citations
    """

    def __init__(self, run_dir: str):
        self.run_dir = run_dir
        self.liquid_tbl_path = os.path.join(run_dir, "melts-liquid.tbl")
        self.melts_out_path = os.path.join(run_dir, "melts.out")
        self.steps: List[AlphaMELTSStep] = []

    def load(self) -> Listliquid_records = self._read_liquid_tbl()
        out_records = self._parse_melts_out()

        n = max(len(liquid_records), len(out_records))
        for i in range(n):
            lr = liquid_records[i] if i < len(liquid_records) else {}
            orc = out_records[i] if i < len(out_records) else {}

            T_C = lr.get("T_C", orc.get("T_C"))
            P_kbar = lr.get("P_kbar", orc.get("P_kbar"))
            if T_C is None or P_kbar is None:
                continue

            step = AlphaMELTSStep(
                T_C=T_C,
                P_kbar=P_kbar,
                liquid_mass_g=orc.get("Liquid_mass_g"),
                system_mass_g=orc.get("System_mass_g"),
                melt_oxides_wt=lr.get("melt_oxides_wt", {}),
                solids_masses_g=orc.get("solids_masses_g", {})
            )
            self.steps.append(step)
        return self.steps

    def to_melts_state(self, idx: int,
                       mineral_mode_from_solids: bool = True) -> MELTSState:
        step = self.steps[idx]
        phi = step.phi if step.phi is not None else 0.0

        mineral_modes = {}
        if mineral_mode_from_solids and step.solids_masses_g:
            total_solids = sum(step.solids_masses_g.values())
            if total_solids > 0:
                mineral_modes = {k: v / total_solids for k, v in step.solids_masses_g.items()}

        return MELTSState(
            temperature_K=step.T_K,
            pressure_GPa=step.P_GPa,
            melt_fraction=phi,
            melt_composition=step.melt_oxides_wt,
            mineral_modes=mineral_modes,
            melt_density_kg_m3=None,
            solid_density_kg_m3=None
        )

    # -----------------------------
    # Internal readers
    # -----------------------------
    def _read_liquid_tbl(self) -> Listrecords = []
        if not os.path.exists(self.liquid_tbl_path):
            return records

        with open(self.liquid_tbl_path, "r", newline="") as f:
            sample = f.read(4096)
            f.seek(0)
            sniffer = csv.Sniffer()
            try:
                dialect = sniffer.sniff(sample)
            except Exception:
                dialect = csv.excel
            reader = csv.DictReader(f, dialect=dialect)

            for row in reader:
                T_C = self._coerce_float(row.get("T (C)") or row.get("T_C") or row.get("Temperature (C)"))
                P_kbar = self._coerce_float(row.get("P (kbars)") or row.get("P_kbar") or row.get("Pressure (kbars)"))
                melt_oxides_wt = {}
                for key, val in row.items():
                    if key is None:
                        continue
                    k = key.strip()
                    if k in ("SiO2","TiO2","Al2O3","Fe2O3","Cr2O3","FeO","MnO","MgO","NiO",
                             "CoO","CaO","Na2O","K2O","P2O5","H2O","CO2"):
                        melt_oxides_wt[k] = self._coerce_float(val) or 0.0

                records.append({
                    "T_C": T_C if T_C is not None else np.nan,
                    "P_kbar": P_kbar if P_kbar is not None else np.nan,
                    "melt_oxides_wt": melt_oxides_wt
                })
        return records

    def _parse_melts_out(self) -> Listrecords = []
        if not os.path.exists(self.melts_out_path):
            return records

        re_tp = re.compile(r"T\s*=\s*([\-0-9.]+)\s*\(C\)\s*P\s*=\s*([\-0-9.]+)\s*\(kbars\)")
        re_liq_mass = re.compile(r"Liquid mass\s*=\s*([0-9.]+)\s*\(gm\)")
        re_sys_mass = re.compile(r"System mass\s*=\s*([0-9.]+)\s*\(gm\)")
        re_phase_mass = re.compile(r"([A-Za-z][A-Za-z0-9\-\s]+)\s+mass\s*=\s*([0-9.]+)\s*\(gm\)")

        with open(self.melts_out_path, "r") as f:
            text = f.read()

        # Split by obvious separators; block parsing is heuristic
        blocks = re.split(r"\*{6,}[-]+\*{6,}|Title:", text)
        for block in blocks:
            T_C = P_kbar = None
            liquid_mass = system_mass = None
            solids_masses: Dict[str, float] = {}

            m = re_tp.search(block)
            if m:
                T_C = float(m.group(1))
                P_kbar = float(m.group(2))

            lm = re_liq_mass.search(block)
            sm = re_sys_mass.search(block)
            if lm:
                liquid_mass = float(lm.group(1))
            if sm:
                system_mass = float(sm.group(1))

            for pm in re_phase_mass.findall(block):
                phase_name = pm[0].strip()
                mass_val = float(pm[1])
                if phase_name.lower() in ("liquid", "fluid", "water"):
                    continue
                solids_masses[phase_name] = mass_val

            if T_C is not None and P_kbar is not None:
                records.append({
                    "T_C": T_C,
                    "P_kbar": P_kbar,
                    "Liquid_mass_g": liquid_mass,
                    "System_mass_g": system_mass,
                    "solids_masses_g": solids_masses
                })
        return records

    @staticmethod
    def _coerce_float(x):
        try:
            return float(x)
        except Exception:
            return None

    def nearest_step(self, T_target_C: Optional[float] = None,
                     P_target_kbar: Optional[float] = None) -> int:
        if not self.steps:
            return 0
        scores = []
        for i, s in enumerate(self.steps):
            dT = 0.0 if T_target_C is None else abs(s.T_C - T_target_C)
            dP = 0.0 if P_target_kbar is None else abs(s.P_kbar - P_target_kbar)
            scores.append((dT + dP, i))
        scores.sort(key=lambda x: x[0])
        return scores[0][1]