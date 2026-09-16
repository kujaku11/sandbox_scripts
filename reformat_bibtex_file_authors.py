from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterator, Tuple, Optional, List

# Optional parser; we fall back to text-mode if not available or not requested
try:
    import bibtexparser  # type: ignore
    HAS_BIBTEXPARSER = True
except Exception:
    HAS_BIBTEXPARSER = False


# ----------------------------
# Configuration / dictionaries
# ----------------------------

SUFFIXES = {"Jr.", "Sr.", "III", "II", "IV", "Jr", "Sr"}
LASTNAME_PARTICLES = {
    # Single-token particles
    "de", "del", "van", "von", "der", "den", "da", "di", "la", "le", "du",
    # Common multi-token particle matched while scanning backward
    "de la"
}


# ----------------------------
# Name utilities
# ----------------------------

def _is_top_level_braced(s: str) -> bool:
    """Return True if s is exactly one top-level { ... } block."""
    if not (s.startswith("{") and s.endswith("}")):
        return False
    depth = 0
    for i, ch in enumerate(s):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and i != len(s) - 1:
                # closed braces before end-of-string
                return False
        if depth < 0:
            return False
    return depth == 0


def is_organization_name(name: str) -> bool:
    """Detect organization authors enclosed in a single top-level brace pair."""
    name = name.strip()
    return name.startswith("{") and name.endswith("}") and _is_top_level_braced(name)


def is_name_normalized(name: str) -> bool:
    """
    Detect if a single author name already appears in 'Last, First Middle [Suffix]' form.
    Heuristics:
      - Organization names in braces: already normalized.
      - Contains a comma separating last/given names.
      - Left and right parts are non-empty; given part does not contain ' and '.
    """
    name = name.strip()
    if not name:
        return True
    if is_organization_name(name):
        return True
    if "," not in name:
        return False

    last, given = [p.strip() for p in name.split(",", 1)]
    if not last or not given:
        return False
    if " and " in given:
        return False
    return True


def normalize_author_name(name: str) -> str:
    """Normalize one BibTeX author to 'Last, First Middle [Suffix]' while preserving LaTeX and braces."""
    original = name
    name = name.strip()
    if not name:
        return original

    # Preserve org names and already normalized names
    if is_organization_name(name) or is_name_normalized(name):
        return name

    parts = name.split()
    if not parts:
        return original

    # Detect suffix at end
    suffix: Optional[str] = None
    if parts[-1] in SUFFIXES:
        suffix = parts[-1]
        parts = parts[:-1]
        if not parts:
            return original

    # Build last name with possible lowercase particles preceding it (backward scan)
    last_parts: List[str] = [parts[-1]]
    i = len(parts) - 2
    while i >= 0:
        token = parts[i]
        if token.islower():
            # Try multi-token particle like 'de la' (look back one more token)
            if i - 1 >= 0 and parts[i - 1].islower():
                candidate = f"{parts[i - 1]} {token}"
                if candidate in LASTNAME_PARTICLES:
                    last_parts.insert(0, parts[i - 1])
                    last_parts.insert(1, token)
                    i -= 2
                    continue
            # Single-token particle
            if token in LASTNAME_PARTICLES:
                last_parts.insert(0, token)
                i -= 1
                continue
        break

    given_end = len(parts) - len(last_parts)
    given = " ".join(parts[:given_end]).strip()
    last = " ".join(last_parts).strip()

    formatted = f"{last}, {given}" if given else last
    if suffix:
        formatted += f" {suffix}"
    return formatted


def split_authors(author_field: str) -> List:
    """
    Split author field at ' and ' separators **only at top level** (outside braces).
    This preserves 'and' inside organization names or LaTeX brace groups.
    """
    authors: List[str] = []
    buf: List[str] = []
    depth = 0
    i = 0
    s = author_field

    while i < len(s):
        ch = s[i]
        if ch == "{":
            depth += 1
            buf.append(ch)
            i += 1
            continue
        elif ch == "}":
            depth = max(0, depth - 1)
            buf.append(ch)
            i += 1
            continue

        # ' and ' at top level only
        if depth == 0 and s.startswith(" and ", i):
            authors.append("".join(buf).strip())
            buf = []
            i += 5
            continue

        buf.append(ch)
        i += 1

    if buf:
        authors.append("".join(buf).strip())

    return authors or [author_field.strip()]


def normalize_author_field(value: str) -> str:
    authors = split_authors(value)
    normalized = [normalize_author_name(a) for a in authors if a.strip()]
    return " and ".join(normalized)


# ----------------------------
# Text-mode BibTeX handling
# ----------------------------

AUTHOR_OPEN_RE = re.compile(r'author\s*=\s*\{', re.IGNORECASE | re.MULTILINE)

def find_author_blocks(text: str) -> Iterator[Tuple[int, int, str]]:
    """
    Yield (start_index, end_index, inner_text) for each 'author = { ... }' block.
    Handles multi-line and nested braces. end_index points to the char **after** closing '}'.
    """
    pos = 0
    while True:
        m = AUTHOR_OPEN_RE.search(text, pos)
        if not m:
            break
        start_brace = m.end()  # position **after** '{'
        depth = 1
        i = start_brace
        while i < len(text) and depth > 0:
            ch = text[i]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            i += 1
        if depth != 0:
            # Unbalanced; skip occurrence
            pos = m.end()
            continue
        end_index = i  # position after closing '}'
        inner = text[start_brace:end_index - 1]
        yield (m.start(), end_index, inner)
        pos = end_index


def rewrite_text_authors(text: str, dry_run: bool = False) -> str:
    """
    Rewrite all 'author = { ... }' blocks in raw BibTeX text by splicing
    the normalized content directly into the string. This avoids using
    regex replacements on LaTeX escape sequences (e.g., \'\i), which can
    trigger PatternError in re.sub.

    Parameters
    ----------
    text : str
        The entire BibTeX file contents as a single string.
    dry_run : bool
        If True, print OLD/NEW diffs and return the text unchanged.

    Returns
    -------
    str
        The rewritten BibTeX text with normalized author fields.
    """
    # We rebuild the document by iteratively splicing replacements.
    out = []
    cursor = 0
    changes = 0

    # Collect blocks first to avoid index drift while editing.
    blocks = list(find_author_blocks(text))

    for start, end, inner in blocks:
        # Append text before the current author block.
        out.append(text[cursor:start])

        # Normalize the inner content (the part inside author = { ... }).
        normalized = normalize_author_field(inner)

        # Detect if a trailing comma immediately follows the '}' in the original.
        trailing_comma = ""
        if end < len(text) and text[end] == ",":
            trailing_comma = ","
            # We will skip this comma when advancing the cursor.

        # Original segment as it appears (without trailing comma).
        original_segment = text[start:end]
        # New segment we will insert (including any trailing comma).
        new_segment = f"author = {{{normalized}}}{trailing_comma}"

        # Print diffs in dry-run mode.
        if dry_run and (original_segment + trailing_comma) != new_segment:
            changes += 1
            print("---- Change detected ----")
            # .strip() in prints keeps output neat across multi-line fields
            print("OLD:", (original_segment + trailing_comma).strip())
            print("NEW:", new_segment.strip())

        # Append the replacement segment.
        out.append(new_segment)

        # Advance cursor beyond the block and any trailing comma we consumed.
        cursor = end + len(trailing_comma)

    #[start:end segment we will insert (e last block.
    out.append(text[cursor:])

    result = "".join(out)
    if dry_run:
        print(f"Total changes: {changes}")
        # In dry-run we return the original text unchanged.
        return text
    return result


# ----------------------------
# bibtexparser-mode handling
# ----------------------------

def rewrite_with_bibtexparser(text: str, dry_run: bool = False) -> str:
    """
    Use bibtexparser to normalize author fields and re-serialize.
    Falls back to text mode if bibtexparser is not available.
    """
    if not HAS_BIBTEXPARSER:
        return rewrite_text_authors(text, dry_run=dry_run)

    db = bibtexparser.loads(text)
    changes = 0
    for entry in db.entries:
        if "author" in entry:
            old = entry["author"]
            new = normalize_author_field(old)
            if old != new:
                changes += 1
                if dry_run:
                    print("---- Change detected ----")
                    print("OLD:", old)
                    print("NEW:", new)
            entry["author"] = new

    if dry_run:
        print(f"Total changes: {changes}")

    writer = bibtexparser.bwriter.BibTexWriter()
    # Formatting preferences (tweak as needed)
    writer.indent = "  "
    writer.comma_first = False
    writer.order_entries_by = None
    writer.add_trailing_comma = False
    return bibtexparser.dumps(db, writer)


# ----------------------------
# File and CLI helpers
# ----------------------------

def make_output_path(in_path: Path) -> Path:
    """Return <stem>_edit<suffix> in the same directory."""
    return in_path.with_name(f"{in_path.stem}_edit{in_path.suffix}")

def process_file(in_path: Path, use_parser: bool, dry_run: bool) -> Optional:
    text = in_path.read_text(encoding="utf-8")
    if use_parser and HAS_BIBTEXPARSER:
        out_text = rewrite_with_bibtexparser(text, dry_run=dry_run)
    else:
        out_text = rewrite_text_authors(text, dry_run=dry_run)

    out_path = make_output_path(in_path)
    if dry_run:
        print(f"[DRY-RUN] Would write: {out_path}")
        return None
    out_path.write_text(out_text, encoding="utf-8")
    print(f"Saved edited file as: {out_path}")
    return out_path

def process_path(path: Path, use_parser: bool, dry_run: bool) -> None:
    if path.is_dir():
        bibs = sorted(p for p in path.iterdir() if p.suffix.lower() == ".bib")
        if not bibs:
            print(f"No .bib files found in: {path}")
            return
        for bib in bibs:
            process_file(bib, use_parser=use_parser, dry_run=dry_run)
    else:
        process_file(path, use_parser=use_parser, dry_run=dry_run)

def main():
    parser = argparse.ArgumentParser(
        description="Normalize BibTeX author fields to 'Last, First Middle [Suffix]' and write <name>_edit.bib"
    )
    parser.add_argument("input", type=str, help="Input .bib file or directory")
    parser.add_argument(
        "--use-parser", action="store_true",
        help="Use bibtexparser (requires 'pip install bibtexparser')"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show changes without writing output files"
    )
    args = parser.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        raise SystemExit(f"Path not found: {in_path}")

    if args.use_parser and not HAS_BIBTEXPARSER:
        print("[WARN] bibtexparser not available; falling back to text-mode.")

    process_path(in_path, use_parser=args.use_parser, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
    

# Single file (auto-falls back to text mode if bibtexparser isn’t installed)
# python normalize_bib_authors.py "C:\path\to\your.bib"

# Force bibtexparser mode (requires: pip install bibtexparser)
# python normalize_bib_authors.py "C:\path\to\your.bib" --use-parser

# Directory: process all .bib files inside it (non-recursive)
# python normalize_bib_authors.py "C:\path\to\your-dir"

# Dry-run: show changes without writing files
# python normalize_bib_authors.py "C:\path\to\your.bib" --dry-run
