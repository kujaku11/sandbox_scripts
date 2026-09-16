import os
from src.alphamelts_io import AlphaMELTSLoader

LIQUID_TBL = """T (C),P (kbars),SiO2,Al2O3,FeO,MgO,CaO,Na2O,K2O,H2O,CO2
1200,10,50.1,15.0,8.8,8.0,10.5,3.0,1.0,2.0,0.2
"""

MELTS_OUT = """**********----------**********
Title: Test
T  = 1200.00 (C)   P  = 10.000 (kbars)
Liquid mass  = 60.00 (gm)   density  = 2.60 (gm/cc)
olivine mass  = 20.00 (gm)   density  = 3.27 (gm/cc)
pyroxene mass  = 15.00 (gm)   density  = 3.20 (gm/cc)
feldspar mass  = 5.00 (gm)   density  = 2.65 (gm/cc)
System mass  = 100.00 (gm)
"""

def test_loader_parses(tmp_run_dir):
    with open(os.path.join(tmp_run_dir, "melts-liquid.tbl"), "w") as f:
        f.write(LIQUID_TBL)
    with open(os.path.join(tmp_run_dir, "melts.out"), "w") as f:
        f.write(MELTS_OUT)

    loader = AlphaMELTSLoader(tmp_run_dir)
    steps = loader.load()
    assert len(steps) == 1
    ms = loader.to_melts_state(0)
    assert abs(ms.melt_fraction - 0.6) < 1e-6
    assert ms.melt_composition["H2O"] == 2.0
    assert ms.temperature_K == 1473.15
    assert ms.pressure_GPa == 1.0