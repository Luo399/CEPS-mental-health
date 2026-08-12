# CHARLS Research Harness — Task 04: merge household-level modules into panel
# Date: 2026-06-02
# Author: Claude Code

import sys
from pathlib import Path
from typing import Optional

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from _charls_utils import (
    get_logger, INTER_DIR, WAVE_DIRS,
    read_dta, do_merge, find_file, write_parquet,
)

log = get_logger("charls_household", "charls_04_household.log")

HOUSEHOLD_MODULES = [
    ("hhinc", {
        2011: ["household_income.dta"],
        2013: ["Household_Income.dta"],
        2015: ["Household_Income.dta"],
        2018: ["Household_Income.dta"],
        2020: ["Household_Income.dta"],
    }),
    ("housing", {
        2011: ["housing_characteristics.dta"],
        2013: ["Housing_Characteristics.dta"],
        2015: ["Housing_Characteristics.dta"],
        2018: ["Housing.dta"],
        # 2020: not present
    }),
    ("faminfo", {
        2011: ["family_information.dta"],
        2013: ["Family_Information.dta"],
        2015: ["Family_Information.dta"],
        2018: ["Family_Information.dta"],
        2020: ["Family_Information.dta"],
    }),
    ("famtfr", {
        2011: ["family_transfer.dta"],
        2013: ["Family_Transfer.dta"],
        2015: ["Family_Transfer.dta"],
        2018: ["Family_Transfer.dta"],
        # 2020: not present
    }),
]


def load_hh_module(wave: int, candidates: list) -> Optional[pd.DataFrame]:
    wave_dir = WAVE_DIRS[wave]
    path = find_file(wave_dir, *candidates)
    if path is None:
        log.info("  Wave %d: %s not found — skip", wave, candidates[0])
        return None
    df, _ = read_dta(path, log=log)
    df["WAVE"] = wave

    n_before = len(df)
    df = df[df["HOUSEHOLDID"].notna() & (df["HOUSEHOLDID"].astype(str).str.strip() != "")]
    if len(df) < n_before:
        log.warning("  Wave %d %s: dropped %d null-HOUSEHOLDID rows", wave, path.name, n_before - len(df))

    # Warn on duplicate HOUSEHOLDID within wave
    dup = df.duplicated(subset=["HOUSEHOLDID"]).sum()
    if dup > 0:
        log.warning("  Wave %d %s: %d duplicate HOUSEHOLDID rows — keeping first", wave, path.name, dup)
        df = df.drop_duplicates(subset=["HOUSEHOLDID"], keep="first")

    return df


def merge_hh_module_into_panel(
    panel: pd.DataFrame,
    module_key: str,
    wave_files: dict,
) -> pd.DataFrame:
    frames = []
    for wave in sorted(WAVE_DIRS.keys()):
        candidates = wave_files.get(wave)
        if candidates is None:
            continue
        df = load_hh_module(wave, candidates)
        if df is not None:
            frames.append(df)

    if not frames:
        log.info("HH module '%s': no data in any wave — skip", module_key)
        return panel

    module_df = pd.concat(frames, ignore_index=True, sort=False)
    log.info("HH module '%s': %d total rows across waves", module_key, len(module_df))

    keys = ["HOUSEHOLDID", "WAVE"]
    # Drop all non-key columns already in panel (prevents _right duplicate chains)
    existing = set(panel.columns) - set(keys)
    drop = [c for c in module_df.columns if c in existing and c not in keys]
    if drop:
        log.info("  Dropping from '%s' (already in panel): %s", module_key, drop[:10])
        module_df = module_df.drop(columns=drop)

    panel = do_merge(
        left=panel,
        right=module_df,
        keys=keys,
        how="left",
        step=f"hh: panel ← {module_key}",
        merge_type="1:1",
        log=log,
    )
    return panel


def main():
    log.info("START merge household modules")
    INTER_DIR.mkdir(parents=True, exist_ok=True)

    in_path = INTER_DIR / "charls_indiv.parquet"
    if not in_path.exists():
        log.error("charls_indiv.parquet not found — run charls_03_individual.py first")
        sys.exit(1)

    panel = pd.read_parquet(in_path)
    log.info("Loaded indiv panel: %d rows × %d cols", len(panel), len(panel.columns))
    n_spine = len(panel)

    if "HOUSEHOLDID" not in panel.columns:
        log.error("Panel missing HOUSEHOLDID — cannot merge household modules")
        sys.exit(1)

    for module_key, wave_files in HOUSEHOLD_MODULES:
        log.info("--- HH Module: %s ---", module_key)
        panel = merge_hh_module_into_panel(panel, module_key, wave_files)
        if len(panel) != n_spine:
            log.error(
                "Row count changed after %s: %d → %d",
                module_key, n_spine, len(panel),
            )
            sys.exit(1)

    out_path = INTER_DIR / "charls_hh.parquet"
    write_parquet(panel, out_path, log=log)
    log.info("SUCCESS")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        log.exception("FATAL: %s", exc)
        sys.exit(1)
