# CHARLS Research Harness — Task 07: 2014 Life History survey → separate panel
# Date: 2026-06-02
# Author: Claude Code

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from _charls_utils import (
    get_logger, RAW_ROOT, PROC_DIR,
    read_dta, do_merge, find_file, build_codebook,
)

log = get_logger("charls_life_history", "charls_07_life_history.log")

LH_DIR = RAW_ROOT / "2014charls"

# Modules in 2014 Life History; spine is Demographic_Backgrounds (note plural)
LH_MODULES = [
    ("edu", ["Education_History.dta"]),
    ("work", ["Work_History.dta"]),
    ("wealth", ["Wealth_History.dta"]),
    ("health", ["Health_History.dta"]),
    ("faminfo", ["Family_Information.dta"]),
    ("residence", ["Residence.dta"]),
    ("sample", ["Sample_Infor.dta"]),
]


def main():
    log.info("START Life History pipeline")
    PROC_DIR.mkdir(parents=True, exist_ok=True)

    if not LH_DIR.exists():
        log.error("2014charls/ directory not found at %s", LH_DIR)
        sys.exit(1)

    # --- Spine: Demographic_Backgrounds ---
    spine_path = find_file(LH_DIR, "Demographic_Backgrounds.dta", "Demographic_Background.dta")
    if spine_path is None:
        log.error("Demographic_Backgrounds.dta not found in %s", LH_DIR)
        sys.exit(1)

    spine, _ = read_dta(spine_path, log=log)
    n_spine = len(spine)
    log.info("LH spine: %d rows × %d cols", n_spine, len(spine.columns))

    # Drop null ID rows
    spine = spine[spine["ID"].notna() & (spine["ID"].astype(str).str.strip() != "")]
    if len(spine) < n_spine:
        log.warning("Dropped %d null-ID rows from LH spine", n_spine - len(spine))
        n_spine = len(spine)

    # Check ID uniqueness
    dup = spine.duplicated(subset=["ID"]).sum()
    if dup > 0:
        log.warning("LH spine: %d duplicate IDs — keeping first", dup)
        spine = spine.drop_duplicates(subset=["ID"], keep="first")
        n_spine = len(spine)

    panel = spine.copy()

    # --- Merge each module ---
    for module_key, candidates in LH_MODULES:
        path = find_file(LH_DIR, *candidates)
        if path is None:
            log.info("  LH module '%s' (%s) not found — skip", module_key, candidates[0])
            continue

        df, _ = read_dta(path, log=log)
        df = df[df["ID"].notna()].copy()

        # Drop columns already in panel
        existing = set(panel.columns) - {"ID"}
        drop = [c for c in df.columns if c in existing and c != "ID"]
        if drop:
            log.info("  Dropping from '%s' (already in panel): %s", module_key, drop[:10])
            df = df.drop(columns=drop)

        # Deduplicate on ID before merge
        dup_mod = df.duplicated(subset=["ID"]).sum()
        if dup_mod > 0:
            log.warning("  LH '%s': %d duplicate IDs in module — keeping first", module_key, dup_mod)
            df = df.drop_duplicates(subset=["ID"], keep="first")

        panel = do_merge(
            left=panel,
            right=df,
            keys=["ID"],
            how="left",
            step=f"LH: panel ← {module_key}",
            merge_type="1:1",
            log=log,
        )
        if len(panel) != n_spine:
            log.error("Row count changed after LH '%s': %d → %d", module_key, n_spine, len(panel))
            sys.exit(1)

    # Export
    out_csv = PROC_DIR / "charls_life_history_panel.csv"
    panel.to_csv(out_csv, index=False, encoding="utf-8-sig")
    log.info("Wrote %s: %d rows × %d cols", out_csv.name, len(panel), len(panel.columns))

    cb = build_codebook(panel)
    out_cb = PROC_DIR / "charls_life_history_codebook.csv"
    cb.to_csv(out_cb, index=False, encoding="utf-8-sig")
    log.info("Wrote %s: %d variables", out_cb.name, len(cb))

    log.info("--- LH summary ---")
    log.info("  Rows:    %d", len(panel))
    log.info("  Columns: %d", len(panel.columns))
    if "ID" in panel.columns:
        log.info("  Unique individuals: %d", panel["ID"].nunique())
    missing = 100.0 * panel.isna().sum().sum() / (len(panel) * len(panel.columns))
    log.info("  Overall missing%%: %.2f%%", missing)
    log.info("SUCCESS")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        log.exception("FATAL: %s", exc)
        sys.exit(1)
