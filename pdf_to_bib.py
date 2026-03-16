#!/usr/bin/env python3
"""
bibliography_builder.py
Object-oriented tool to build bibliographies from PDFs with Crossref + OpenAlex.

Pattern support:
    {year}_{journal_abbreviation}_{author}_{short_description}.pdf
Example:
    2021_GRL_Peacock_crustal_anisotropy.pdf

Usage:
    python bibliography_builder.py /path/to/pdfs --outbase my_bib --email you@example.org
"""

from __future__ import annotations
import argparse
import os
import re
import sys
import time
import unicodedata
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from loguru import logger

import fitz  # PyMuPDF
import pandas as pd
import requests
from tqdm import tqdm

# --------------------------
# Configuration constants
# --------------------------

DOI_PATTERN = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", flags=re.IGNORECASE)
DEFAULT_PAGES_TO_SCAN = 5
DEFAULT_RATE_LIMIT_SECS = 0.25  # be nice to public APIs

# Optional: common geophysics journal abbreviation mapping (extend as needed)
JOURNAL_MAP = {
    "GRL": "Geophysical Research Letters",
    "JGR": "Journal of Geophysical Research",
    "JGR-SolidEarth": "Journal of Geophysical Research: Solid Earth",
    "EPSL": "Earth and Planetary Science Letters",
    "GJI": "Geophysical Journal International",
    "Tectonophysics": "Tectonophysics",
    "SRL": "Seismological Research Letters",
    "BSSA": "Bulletin of the Seismological Society of America",
    "SEG": "Society of Exploration Geophysicists (conference/journal)",
    "AGU": "American Geophysical Union (general)",
}

# --------------------------
# Data class for a record
# --------------------------

@dataclass
class BibRecord:
    key: str
    title: Optional[str] = None
    authors: Optional[str] = None                # "A. Author; B. Author"
    container: Optional[str] = None              # Journal/venue
    publisher: Optional[str] = None
    year: Optional[int] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    page: Optional[str] = None                   # "123-134"
    doi: Optional[str] = None
    url: Optional[str] = None
    type: Optional[str] = None                   # article|book|etc
    pdf_file: Optional[str] = None
    # Seeded from filename (helpful when no API metadata)
    journal_abbrev: Optional[str] = None
    first_author_last: Optional[str] = None
    short_description: Optional[str] = None

    def to_bibtex(self) -> str:
        """
        Minimal BibTeX; prefer 'article' when a container (journal) is present.
        """
        entry_type = "article" if self.container else "misc"
        def esc(val: Optional[str]) -> Optional[str]:
            if val is None:
                return None
            # Escape literal braces (BibTeX-safe)
            return str(val).replace("{", "\\{").replace("}", "\\}")

        fields = []
        def add(name: str, value: Optional[str]):
            if value:
                fields.append(f"  {name} = {{{esc(value)}}}")

        add("title", self.title)
        add("author", self.authors)
        add("journal", self.container)
        add("publisher", self.publisher)
        add("year", str(self.year) if self.year else None)
        add("volume", self.volume)
        add("number", self.issue)
        add("pages", self.page)
        add("doi", self.doi)
        add("url", self.url)
        # Helpful note to link back to local PDF
        if self.pdf_file:
            add("note", f"PDF: {self.pdf_file}")

        return f"@{entry_type}{{{self.key},\n" + ",\n".join(fields) + "\n}\n"

    def to_dict(self) -> Dict:
        """Flat dict for DataFrame/CSV."""
        return asdict(self)

# --------------------------
# Main builder class
# --------------------------

class BibliographyBuilder:
    def __init__(self,
                 pages_to_scan: int = DEFAULT_PAGES_TO_SCAN,
                 rate_limit_secs: float = DEFAULT_RATE_LIMIT_SECS,
                 email: Optional[str] = None):
        """
        :param pages_to_scan: Number of initial pages to search for a DOI.
        :param rate_limit_secs: Delay between API calls.
        :param email: Used in API User-Agent (good etiquette for Crossref/OpenAlex).
        """
        self.pages_to_scan = pages_to_scan
        self.rate_limit_secs = rate_limit_secs
        self.email = email or "you@example.org"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": f"USGS-bib-builder/2.0 (mailto:{self.email})"
        })

    # --------- Class factory ---------
    @classmethod
    def from_defaults(cls, email: Optional[str] = None) -> "BibliographyBuilder":
        return cls(pages_to_scan=DEFAULT_PAGES_TO_SCAN,
                   rate_limit_secs=DEFAULT_RATE_LIMIT_SECS,
                   email=email)

    # --------- Public API ---------
    def build_from_folder(self, pdf_folder: Path, outbase: str) -> Tuple[Path, Path]:
        """
        Walk the folder, process PDFs, and write CSV + BibTeX.
        """
        pdfs = sorted([p for p in pdf_folder.glob("*.pdf") if p.is_file()])
        if not pdfs:
            raise FileNotFoundError(f"No PDFs found in {pdf_folder}")

        records: List[BibRecord] = []
        for pdf in tqdm(pdfs, desc="Processing PDFs"):
            try:
                rec = self.process_pdf(pdf)
                records.append(rec)
            except Exception as e:
                logger.warning(f"Failed to process {pdf}: {e}")

        csv_path, bib_path = self.write_outputs(records, outbase, pdf_folder)
        return csv_path, bib_path
    
    def process_pdf(self, pdf_path: Path) -> BibRecord:
        """
        Extract DOI (if present), enrich via Crossref; fallback to OpenAlex; normalize to BibRecord.
        Also seed fields from filename convention.
        """
        # Seed from filename
        seed = self.parse_filename(pdf_path.stem)
        pdf_text = self.extract_pdf_text(pdf_path, self.pages_to_scan)
        doi = self.find_doi(pdf_text)

        # Try Crossref first
        cr_json, cr_bib = (None, None)
        if doi:
            cr_json, cr_bib = self.crossref_fetch(doi)
            time.sleep(self.rate_limit_secs)

        oa_json = None
        if (not cr_json) and doi:
            oa_json = self.openalex_fetch(doi)
            time.sleep(self.rate_limit_secs)

        # >>> NEW: If DOI absent or APIs didn’t return enough, mine the text <<<
        heur = self.extract_structured_from_text(pdf_text)

        if not cr_json and not oa_json and heur.get("title"):
            # Last-ditch: try Crossref title search with heuristic title from PDF text
            cr_json = self.crossref_search_by_title(heur["title"])
            time.sleep(self.rate_limit_secs)

        # Build record (priority: Crossref → OpenAlex → filename seeds → PDF metadata)
        rec = self.normalize_record(pdf_path, doi, cr_json, oa_json, seed)

        # Fill missing fields from heuristics (non-destructive backfill)
        if not rec.title and heur.get("title"):
            rec.title = heur["title"]
        if not rec.authors and heur.get("authors"):
            rec.authors = heur["authors"]
        if not rec.container and heur.get("journal"):
            rec.container = heur["journal"]
        if not rec.year and heur.get("year"):
            try:
                rec.year = int(heur["year"]) if heur["year"] else None
            except Exception:
                pass
        if not rec.page and heur.get("pages"):
            rec.page = heur["pages"]
        if not rec.authors:
             logger.warning(f"{pdf_path.name}Record {rec.key} missing authors after all attempts")
        if not rec.title:
             logger.warning(f"{pdf_path.name}Record {rec.key} missing title after all attempts")
        if rec.key == "unnamed":
             logger.warning(f"{pdf_path.name}Record has generic key 'unnamed'; consider renaming file for better seeding")

        rec_bibtex = self.crossref_bibtex(cr_bib, desired_key=rec.key) if cr_bib else None
        rec._bibtex_external = rec_bibtex  # type: ignore[attr-defined]
        return rec

    # --------- Parsing helpers ---------
    def parse_filename(self, stem: str) -> Dict[str, Optional[str]]:
        """
        Parse {year}_{journal_abbreviation}_{author}_{short_description}
        Returns dict with year:int, journal_abbrev:str, first_author_last:str, short_description:str, bib_key:str.
        """
        # Split on underscores; minimum 4 components
        parts = stem.split("_")
        if len(parts) < 4:
            return {"year": None, "journal_abbrev": None, "first_author_last": None,
                    "short_description": None, "bib_key": self.make_key_from_stem(stem)}

        year_str, journal_abbrev, author_last = parts[0], parts[1], parts[2]
        short_desc = "_".join(parts[3:])  # keep underscores; we will normalize for key

        # Normalize and validate year
        year = None
        if year_str.isdigit() and len(year_str) in (4,):
            try:
                year = int(year_str)
            except Exception:
                year = None

        key = self.make_key(author_last, year, short_desc)

        return {
            "year": year,
            "journal_abbrev": journal_abbrev,
            "first_author_last": author_last,
            "short_description": short_desc,
            "bib_key": key,
        }

    @staticmethod
    def _slug(text: Optional[str]) -> str:
        """
        ASCII slug: lower, alnum only, compact.
        """
        if not text:
            return ""
        # Remove accents
        norm = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
        # Replace non-alnum with spaces, then compact
        norm = re.sub(r"[^A-Za-z0-9]+", " ", norm)
        norm = norm.strip().lower()
        return re.sub(r"\s+", "", norm)

    def make_key(self, author_last: Optional[str], year: Optional[int], short_desc: Optional[str]) -> str:
        """
        Key format: {author}{year}{shortdesc} → peacock2021crustalanisotropy
        """
        a = self._slug(author_last)
        y = str(year) if year else ""
        base = f"{a}{y}" if (a or y) else "unnamed"
        return base or "unnamed"

    def make_key_from_stem(self, stem: str) -> str:
        return self._slug(stem) or "unnamed"

    # --------- PDF extraction ---------
    def extract_pdf_text(self, pdf_path: Path, max_pages: int) -> str:
        try:
            doc = fitz.open(pdf_path)
            text_chunks = []
            pages = min(max_pages, len(doc))
            for i in range(pages):
                text_chunks.append(doc[i].get_text("text"))
            doc.close()
            return "\n".join(text_chunks)
        except Exception as e:
            logger.warning(f"Failed text extraction: {pdf_path}: {e}")
            return ""

    def find_doi(self, text: str) -> Optional[str]:
        matches = DOI_PATTERN.findall(text or "")
        if not matches:
            return None
        doi = matches[0].strip().rstrip(").,;").lower()
        return doi
    
    # ---------- Heuristic text parsing ----------
    def crossref_search_by_title(self, title: str) -> Optional[Dict]:
        try:
            r = self.session.get("https://api.crossref.org/works",
                                 params={"query.title": title, "rows": 3}, timeout=20)
            if r.status_code == 200:
                items = r.json().get("message", {}).get("items", [])
                return items[0] if items else None
        except Exception as e:
            logger.warning(f"Crossref title search failed: {e}")
        return None

    def openalex_search_by_title(self, title: str) -> Optional[Dict]:
        try:
            r = self.session.get("https://api.openalex.org/works",
                                 params={"search": title, "per_page": 3}, timeout=20)
            if r.status_code == 200:
                results = r.json().get("results", [])
                return results[0] if results else None
        except Exception as e:
            logger.warning(f"OpenAlex title search failed: {e}")

    def extract_structured_from_text(self, text: str) -> Dict[str, Optional[str]]:
        """
        Heuristically infer title, authors, journal, year, and pages from PDF text.
        Works best on publisher PDFs or well-formatted manuscripts.
        """
        if not text:
            return {"title": None, "authors": None, "journal": None, "year": None, "pages": None}

        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        # Normalize unicode
        lines = [unicodedata.normalize("NFKC", ln) for ln in lines]

        # --- Title candidate: first non-empty, non-boilerplate line before 'Abstract'
        title = None
        for i, ln in enumerate(lines[:50]):  # first ~50 lines usually includes title block
            if self._looks_like_title(ln):
                title = ln
                # Stop before reaching abstract/keywords
                break

        # --- Authors candidate: search near the title line, prefer comma/semicolon-separated person names
        authors = None
        if title:
            start_idx = lines.index(title)
            window = lines[start_idx + 1 : start_idx + 8]
            authors = self._extract_authors_line(window)

        # --- Journal + year + pages: use regexes
        journal = self._extract_journal(lines)
        year = self._extract_year(lines)
        pages = self._extract_pages(lines)

        return {
            "title": title,
            "authors": authors,
            "journal": journal,
            "year": str(year) if year else None,
            "pages": pages,
        }

    @staticmethod
    def _looks_like_title(ln: str) -> bool:
        """
        Title heuristics: not all-caps boilerplate, not section header, reasonably long.
        """
        bad_starters = ("abstract", "introduction", "received", "accepted", "copyright",
                        "contents", "supplementary", "research letter", "article")
        if len(ln) < 10 or len(ln) > 200:
            return False
        lnc = ln.strip().lower()
        if any(lnc.startswith(b) for b in bad_starters):
            return False
        # Exclude lines ending with colon (likely a section header)
        if lnc.endswith(":"):
            return False
        # Titles often have mixed case; avoid all‑caps (common in headers)
        if ln.isupper():
            return False
        return True

    def _extract_authors_line(self, window_lines: List[str]) -> Optional[str]:
        """
        Pick the line with multiple capitalized name tokens, join as 'A. Author; B. Author'.
        """
        person_pat = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+|(?:\s+[A-Z]\.)+))(?:\s*[†*^0-9,;])?")
        best = None
        best_hits = 0
        for ln in window_lines:
            hits = person_pat.findall(ln)
            if hits and len(hits) > best_hits:
                best = hits
                best_hits = len(hits)
        if best:
            # Dedup, strip footnote markers
            cleaned = []
            for n in best:
                n = re.sub(r"[†*^0-9]+", "", n).strip()
                cleaned.append(n)
            # Unique while preserving order
            seen = set()
            uniq = []
            for n in cleaned:
                if n not in seen:
                    seen.add(n)
                    uniq.append(n)
            return "; ".join(uniq)
        return None

    def _extract_journal(self, lines: List[str]) -> Optional[str]:
        """
        Look for known geophysics journals; otherwise return best label near volume/issue markers.
        """
        joined = " \n ".join(lines)
        # Known journals
        for abbr, full in JOURNAL_MAP.items():
            if re.search(rf"\b{re.escape(full)}\b", joined, flags=re.IGNORECASE):
                return full
        # Generic journal cues: e.g., 'Geophysical Research Letters', 'Journal of ...', 'Proceedings of ...'
        m = re.search(r"\b(Journal of [A-Za-z &\-:]+|Geophysical [A-Za-z &\-:]+|Proceedings of [A-Za-z &\-:]+)\b",
                      joined, flags=re.IGNORECASE)
        return m.group(0) if m else None

    @staticmethod
    def _extract_year(lines: List[str]) -> Optional[int]:
        """
        Prefer four-digit years between 1900 and 2100 near volume/issue/page cues.
        """
        candidates = []
        for ln in lines[:200]:  # first ~200 lines
            for y in re.findall(r"\b(19\d{2}|20\d{2}|2100)\b", ln):
                y = int(y)
                candidates.append((y, ln))
        if not candidates:
            return None
        # Bias toward lines that also mention volume/issue/pages
        def score(item):
            y, ln = item
            bonus = 0
            if re.search(r"\b(vol|volume|issue|no\.|pages|pp\.)\b", ln, flags=re.IGNORECASE):
                bonus += 1
            if "©" in ln or "Copyright" in ln:
                bonus -= 1  # likely boilerplate
            return (bonus, y)
        candidates.sort(key=score, reverse=True)
        return candidates[0][0]

    @staticmethod
    def _extract_pages(lines: List[str]) -> Optional[str]:
        """
        Match common page patterns: 'pp. 123-134' or '123–134' etc.
        """
        joined = " \n ".join(lines)
        m = re.search(r"\bpp?\.\s*([0-9]+)\s*[-–—]\s*([0-9]+)\b", joined, flags=re.IGNORECASE)
        if m:
            return f"{m.group(1)}-{m.group(2)}"
        m2 = re.search(r"\b([0-9]{1,4})\s*[-–—]\s*([0-9]{1,4})\b", joined)
        if m2:
            return f"{m2.group(1)}-{m2.group(2)}"
        return None

    def find_doi_deep(self, text: str) -> Optional[str]:
        """
        Wider DOI search across more text (use when first-pass failed).
        """
        matches = DOI_PATTERN.findall(text or "")
        if not matches:
            return None
        doi = matches[0].strip().rstrip(").,;").lower()
        return doi

    # --------- External sources ---------
    def crossref_fetch(self, doi: str) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Returns (JSON message dict, BibTeX string or None).
        """
        base = "https://api.crossref.org/works/"
        try:
            rj = self.session.get(f"{base}{doi}", timeout=20)
            cr = rj.json().get("message") if rj.status_code == 200 else None
            rb = self.session.get(f"{base}{doi}/transform/application/x-bibtex", timeout=20)
            bib = rb.text if rb.status_code == 200 else None
            return cr, bib
        except Exception as e:
            logger.warning(f"Crossref lookup failed for {doi}: {e}")
            return None, None

    def crossref_bibtex(self, bib_text: str, desired_key: str) -> Optional[str]:
        """
        Rewrite Crossref BibTeX key to our desired key if possible.
        """
        if not bib_text:
            return None
        m = re.match(r"^@(\w+)\{([^,]+),", bib_text)
        if m:
            entry_type, old_key = m.groups()
            return bib_text.replace(f"@{entry_type}{{{old_key},", f"@{entry_type}{{{desired_key},")
        return bib_text

    def openalex_fetch(self, doi: str) -> Optional[Dict]:
        """
        OpenAlex fallback: https://api.openalex.org/works/doi:{doi}
        """
        url = f"https://api.openalex.org/works/doi:{doi}"
        try:
            r = self.session.get(url, timeout=20)
            return r.json() if r.status_code == 200 else None
        except Exception as e:
            logger.warning(f"OpenAlex lookup failed for {doi}: {e}")
            return None
        
    @staticmethod
    def _year_from_crossref(cr: Dict) -> Optional[int]:
        """
        Extract publication year from Crossref 'message' dict.
        Preference order: published-print → issued → published-online.
        """
        def year_from_dateparts(obj: Optional[Dict]) -> Optional[int]:
            if not obj:
                return None
            parts = obj.get("date-parts") or []
            if parts and parts[0] and isinstance(parts[0], (list, tuple)) and parts[0][0]:
                try:
                    return int(parts[0][0])
                except Exception:
                    return None
            return None

        # Try fields in order of typical citation preference
        for field in ("published-print", "issued", "published-online"):
            y = year_from_dateparts(cr.get(field))
            if y:
                return y

        # Fallbacks that sometimes appear in Crossref
        # 'created' and 'deposited' are not publication dates, but useful if nothing else exists.
        for field in ("created", "deposited"):
            y = year_from_dateparts(cr.get(field))
            if y:
                return y

        # Last resort: 'published' (rare) or None
        y = year_from_dateparts(cr.get("published"))
        return y

    # --------- Normalization ---------
    def normalize_record(self,
                         pdf_path: Path,
                         doi: Optional[str],
                         cr: Optional[Dict],
                         oa: Optional[Dict],
                         seed: Dict[str, Optional[str]]) -> BibRecord:
        """
        Build a BibRecord by merging (Crossref → OpenAlex → filename seeds → PDF metadata stub).
        """
        # PDF metadata stub (title/author if present)
        pdf_meta = self.extract_pdf_metadata(pdf_path)

        # Title
        title = None
        authors = None
        container = None
        publisher = None
        year = seed.get("year")
        volume = None
        issue = None
        page = None
        url = None
        rec_type = None
        doi_final = doi

        # Prefer Crossref
        if cr:
            title = self._first(cr.get("title"))
            authors = self._authors_from_crossref(cr)
            container = self._first(cr.get("container-title"))
            publisher = cr.get("publisher")
            year = year or self._year_from_crossref(cr)
            volume = cr.get("volume")
            issue = cr.get("issue")
            page = cr.get("page")
            url = cr.get("URL")
            rec_type = cr.get("type")
            doi_final = cr.get("DOI") or doi_final

        # Fallback: OpenAlex
        elif oa:
            title = oa.get("title")
            authors = self._authors_from_openalex(oa)
            hv = oa.get("host_venue", {}) or {}
            container = hv.get("display_name")
            publisher = hv.get("publisher")
            year = year or oa.get("publication_year")
            biblio = oa.get("biblio", {}) or {}
            volume = biblio.get("volume")
            issue = biblio.get("issue")
            fp = biblio.get("first_page")
            lp = biblio.get("last_page")
            page = f"{fp}-{lp}" if fp and lp else (fp or lp)
            url = oa.get("id") or oa.get("doi")
            rec_type = oa.get("type")
            # OpenAlex sometimes returns doi with lowercase; keep existing if present
            doi_final = doi_final or oa.get("doi")

        # Final fallback: PDF metadata
        if not title:
            title = pdf_meta.get("title")
        if not authors and pdf_meta.get("author"):
            # PDF author metadata is often a single name; keep as-is
            authors = pdf_meta.get("author")

        # If we still lack a container, map abbreviation from filename seed
        if not container and seed.get("journal_abbrev"):
            container = JOURNAL_MAP.get(seed["journal_abbrev"], seed["journal_abbrev"])

        # Build key
        bib_key = seed.get("bib_key") or self.make_key_from_stem(pdf_path.stem)

        rec = BibRecord(
            key=bib_key,
            title=title,
            authors=authors,
            container=container,
            publisher=publisher,
            year=year,
            volume=volume,
            issue=issue,
            page=page,
            doi=doi_final,
            url=url,
            type=rec_type,
            pdf_file=str(pdf_path),
            journal_abbrev=seed.get("journal_abbrev"),
            first_author_last=seed.get("first_author_last"),
            short_description=seed.get("short_description"),
        )
        return rec

    def extract_pdf_metadata(self, pdf_path: Path) -> Dict[str, Optional[str]]:
        meta = {"title": None, "author": None}
        try:
            doc = fitz.open(pdf_path)
            info = doc.metadata or {}
            meta["title"] = info.get("title")
            meta["author"] = info.get("author")
            doc.close()
        except Exception as e:
            print(f"[WARN] Failed metadata read: {pdf_path}: {e}", file=sys.stderr)
        return meta

    # --------- Utilities ---------
    @staticmethod
    def _first(value):
        if isinstance(value, list):
            return value[0] if value else None
        return value

    @staticmethod
    def _authors_from_crossref(cr: Dict) -> Optional[str]:
        out = []
        for a in cr.get("author", []) or []:
            given = a.get("given", "")
            family = a.get("family", "")
            full = " ".join(x for x in [given, family] if x).strip()
            if full:
                out.append(full)
        return "; ".join(out) if out else None

    @staticmethod
    def _authors_from_openalex(oa: Dict) -> Optional[str]:
        out = []
        for auth in oa.get("authorships", []) or []:
            disp = (auth.get("author") or {}).get("display_name")
            if disp:
                out.append(disp)
        return "; ".join(out) if out else None

    # --------- Output ---------
    def write_outputs(self, records: List[BibRecord], outbase: str, pdf_folder: Path) -> Tuple[Path, Path]:
        df = pd.DataFrame([r.to_dict() for r in records])
        pdf_folder = Path(pdf_folder)
        csv_path = pdf_folder / f"{outbase}.csv"
        bib_path = pdf_folder / f"{outbase}.bib"

        # CSV
        df.to_csv(csv_path, index=False)

        # BibTeX
        with open(bib_path, "w", encoding="utf-8") as f:
            for r in records:
                ext = getattr(r, "_bibtex_external", None)  # type: ignore[attr-defined]
                if ext:
                    f.write(ext.strip() + "\n\n")
                else:
                    f.write(r.to_bibtex() + "\n")

        return csv_path, bib_path

# --------------------------
# CLI
# --------------------------

def main():
    parser = argparse.ArgumentParser(description="Build bibliography (Crossref + OpenAlex fallback).")
    parser.add_argument("pdf_folder", type=str, help="Folder containing PDF files")
    parser.add_argument("--outbase", type=str, default="bibliography",
                        help="Base name for output files (without extension)")
    parser.add_argument("--email", type=str, default=None,
                        help="Your email for API User-Agent (etiquette with Crossref/OpenAlex)")
    parser.add_argument("--pages", type=int, default=DEFAULT_PAGES_TO_SCAN,
                        help="Pages to scan for DOI in each PDF (default 5)")
    parser.add_argument("--rate", type=float, default=DEFAULT_RATE_LIMIT_SECS,
                        help="Delay between API calls in seconds (default 0.25)")

    args = parser.parse_args()

    pdf_dir = Path(args.pdf_folder)
    if not pdf_dir.exists() or not pdf_dir.is_dir():
        print(f"[ERROR] Not a directory: {pdf_dir}", file=sys.stderr)
        sys.exit(1)

    builder = BibliographyBuilder(pages_to_scan=args.pages,
                                  rate_limit_secs=args.rate,
                                  email=args.email)

    try:
        csv_path, bib_path = builder.build_from_folder(pdf_dir, args.outbase)
        logger.info(f"[OK] CSV → {csv_path}")
        logger.info(f"[OK] Bib → {bib_path}")
    except Exception as e:
        logger.error(f"{e}")
        sys.exit(2)

if __name__ == "__main__":
    main()