# CHARLS Research Harness — Task 03: merge individual-level modules into spine
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

log = get_logger("charls_individual", "charls_03_individual.log")

# (wave, candidate_filenames) → module key
INDIVIDUAL_MODULES = [
    ("hsf", {
        2011: ["health_status_and_functioning.dta"],
        2013: ["Health_Status_and_Functioning.dta"],
        2015: ["Health_Status_and_Functioning.dta"],
        2018: ["Health_Status_and_Functioning.dta"],
        2020: ["Health_Status_and_Functioning.dta"],
    }),
    ("hci", {
        2011: ["health_care_and_insurance.dta"],
        2013: ["Health_Care_and_Insurance.dta"],
        2015: ["Health_Care_and_Insurance.dta"],
        2018: ["Health_Care_and_Insurance.dta"],
        # 2020: not present
    }),
    ("inc", {
        2011: ["individual_income.dta"],
        2013: ["Individual_Income.dta"],
        2015: ["Individual_Income.dta"],
        2018: ["Individual_Income.dta"],
        2020: ["Individual_Income.dta"],
    }),
    ("wrp", {
        2011: ["work_retirement_and_pension.dta"],
        2013: ["Work_Retirement_and_Pension.dta"],
        2015: ["Work_Retirement_and_Pension.dta"],
        2018: ["Work_Retirement.dta"],
        2020: ["Work_Retirement.dta"],
    }),
    ("obs", {
        2011: ["interviewer_observation.dta"],
        2013: ["Interviewer_Observation.dta"],
        # 2015, 2018, 2020: not present
    }),
    ("wgt", {
        2011: ["weight.dta"],
        2013: ["Weights.dta"],
        2015: ["Weights.dta"],
        2018: ["Weights.dta"],
        2020: ["Weights.dta"],
    }),
]


def load_module(wave: int, candidates: list) -> Optional[pd.DataFrame]:
    wave_dir = WAVE_DIRS[wave]
    path = find_file(wave_dir, *candidates)
    if path is None:
        log.info("  Wave %d: %s not found — skip", wave, candidates[0])
        return None
    df, _ = read_dta(path, log=log)
    df["WAVE"] = wave

    # Drop rows with null ID
    n_before = len(df)
    df = df[df["ID"].notna() & (df["ID"].astype(str).str.strip() != "")]
    if len(df) < n_before:
        log.warning("  Wave %d %s: dropped %d null-ID rows", wave, path.name, n_before - len(df))

    return df


def merge_module_into_panel(
    panel: pd.DataFrame,
    module_key: str,
    wave_files: dict,
) -> pd.DataFrame:
    """Collect a module across all waves and left-merge into panel."""
    frames = []
    for wave in sorted(WAVE_DIRS.keys()):
        candidates = wave_files.get(wave)
        if candidates is None:
            continue
        df = load_module(wave, candidates)
        if df is not None:
            frames.append(df)

    if not frames:
        log.info("Module '%s': no data in any wave — skip", module_key)
        return panel

    module_df = pd.concat(frames, ignore_index=True, sort=False)
    log.info("Module '%s': %d total rows across waves", module_key, len(module_df))

    # Drop all non-key columns already in panel (prevents _right duplicate chains)
    keys = ["ID", "WAVE"]
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
        step=f"indiv: panel ← {module_key}",
        merge_type="1:1",
        log=log,
    )
    return panel


def main():
    log.info("START merge individual modules")
    INTER_DIR.mkdir(parents=True, exist_ok=True)

    spine_path = INTER_DIR / "charls_spine.parquet"
    if not spine_path.exists():
        log.error("charls_spine.parquet not found — run charls_02_spine.py first")
        sys.exit(1)

    panel = pd.read_parquet(spine_path)
    log.info("Loaded spine: %d rows × %d cols", len(panel), len(panel.columns))
    n_spine = len(panel)

    for module_key, wave_files in INDIVIDUAL_MODULES:
        log.info("--- Module: %s ---", module_key)
        panel = merge_module_into_panel(panel, module_key, wave_files)
        if len(panel) != n_spine:
            log.error(
                "Row count changed after %s: %d → %d",
                module_key, n_spine, len(panel),
            )
            sys.exit(1)

    out_path = INTER_DIR / "charls_indiv.parquet"
    write_parquet(panel, out_path, log=log)
    log.info("SUCCESS")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        log.exception("FATAL: %s", exc)
        sys.exit(1)
