# CHARLS Research Harness — Task 08: enrich codebook with Stata variable labels
# Date: 2026-06-02
# Author: Claude Code

import sys
from pathlib import Path

import pandas as pd
import pyreadstat

sys.path.insert(0, str(Path(__file__).parent))
from _charls_utils import get_logger, RAW_ROOT, PROC_DIR

log = get_logger("charls_enrich_codebook", "charls_08_enrich_codebook.log")

# All source directories to scan for variable labels
SCAN_DIRS = [
    RAW_ROOT / "2011charls",
    RAW_ROOT / "2013charls",
    RAW_ROOT / "2014charls",
    RAW_ROOT / "2015charls",
    RAW_ROOT / "2018charls",
    RAW_ROOT / "2020charls",
]


def collect_labels_from_dir(wave_dir: Path) -> dict:
    """Read all .dta files in a directory and collect variable labels.
    Returns dict: UPPER_VAR_NAME → label string (first non-empty label wins)."""
    labels = {}
    dta_files = sorted(wave_dir.glob("*.dta"))
    for f in dta_files:
        try:
            _, meta = pyreadstat.read_dta(str(f), metadataonly=True)
            col_labels = getattr(meta, "column_labels", []) or []
            col_names  = getattr(meta, "column_names", []) or []
            for name, label in zip(col_names, col_labels):
                upper = name.upper()
                lbl = (label or "").strip()
                if lbl and upper not in labels:
                    labels[upper] = lbl
            log.info("  %s: %d labeled variables", f.name, sum(1 for l in col_labels if l and l.strip()))
        except Exception as exc:
            log.warning("  SKIP %s: %s", f.name, exc)
    return labels


def main():
    log.info("START codebook enrichment — collecting Stata variable labels")

    # Collect labels from all wave directories
    all_labels: dict = {}
    for d in SCAN_DIRS:
        if not d.exists():
            log.warning("Dir not found: %s", d)
            continue
        log.info("Scanning %s ...", d.name)
        wave_labels = collect_labels_from_dir(d)
        # Merge: first non-empty label per variable wins
        for var, lbl in wave_labels.items():
            if var not in all_labels and lbl:
                all_labels[var] = lbl

    log.info("Total unique labeled variables: %d", len(all_labels))

    # Enrich main codebook
    for cb_name in ["charls_codebook.csv", "charls_life_history_codebook.csv"]:
        cb_path = PROC_DIR / cb_name
        if not cb_path.exists():
            log.warning("Not found: %s — skip", cb_name)
            continue

        cb = pd.read_csv(cb_path, encoding="utf-8-sig")
        log.info("Loaded %s: %d variables", cb_name, len(cb))

        # Add or overwrite description column
        cb["description"] = cb["variable_name"].map(all_labels).fillna("")

        n_filled = (cb["description"] != "").sum()
        log.info("  Filled description for %d / %d variables (%.1f%%)",
                 n_filled, len(cb), 100.0 * n_filled / len(cb) if len(cb) else 0)

        # Reorder: variable_name, description, then the rest
        cols = ["variable_name", "description"] + [c for c in cb.columns
                                                    if c not in ("variable_name", "description")]
        cb = cb[cols]

        cb.to_csv(cb_path, index=False, encoding="utf-8-sig")
        log.info("  Saved enriched codebook: %s", cb_name)

    log.info("SUCCESS")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        log.exception("FATAL: %s", exc)
        sys.exit(1)
