# CHARLS Research Harness — Task 02: build ID×wave spine from Demographic_Background
# Date: 2026-06-02
# Author: Claude Code

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from _charls_utils import (
    get_logger, INTER_DIR, WAVE_DIRS, RAW_ROOT,
    read_dta, do_merge, log_filter, find_file, clean_dtypes, write_parquet,
)

log = get_logger("charls_spine", "charls_02_spine.log")

# Demographic_Background file name per wave (2011 is lowercase)
DEMO_FILES = {
    2011: "demographic_background.dta",
    2013: "Demographic_Background.dta",
    2015: "Demographic_Background.dta",
    2018: "Demographic_Background.dta",
    2020: "Demographic_Background.dta",
}

SAMPLE_INFO_FILE = "Sample_Infor.dta"


def load_demo(wave: int) -> pd.DataFrame:
    wave_dir = WAVE_DIRS[wave]
    fname = DEMO_FILES[wave]
    path = wave_dir / fname
    if not path.exists():
        # Try case-insensitive fallback
        found = find_file(wave_dir, fname)
        if found is None:
            raise FileNotFoundError(f"Demographic_Background not found for wave {wave} in {wave_dir}")
        path = found

    df, _ = read_dta(path, log=log)
    n_before = len(df)

    # Remove rows with null ID
    df = df[df["ID"].notna() & (df["ID"].astype(str).str.strip() != "")]
    log_filter(log, f"wave {wave}: drop null ID", n_before, len(df))

    df["WAVE"] = wave
    log.info("Wave %d demo: %d rows × %d cols", wave, len(df), len(df.columns))
    return df


def load_sample_info(wave: int) -> pd.DataFrame:
    wave_dir = WAVE_DIRS[wave]
    path = wave_dir / SAMPLE_INFO_FILE
    if not path.exists():
        log.info("Wave %d: Sample_Infor.dta not found — skipping", wave)
        return pd.DataFrame()

    df, _ = read_dta(path, log=log)
    df["WAVE"] = wave
    # Keep only admin columns that don't overlap with demo; prefix remainder
    keep_cols = {"ID", "HOUSEHOLDID", "COMMUNITYID", "WAVE"}
    admin_cols = {"CROSSSECTION", "DIED", "IYEAR", "IMONTH", "VERSIONID"}
    extra = {c for c in df.columns if c in admin_cols}
    df = df[sorted(keep_cols & set(df.columns)) + sorted(extra & set(df.columns))]
    log.info("Wave %d Sample_Infor: %d rows × %d cols", wave, len(df), len(df.columns))
    return df


def main():
    log.info("START build CHARLS spine")
    INTER_DIR.mkdir(parents=True, exist_ok=True)

    # --- Load and stack Demographic_Background across waves ---
    frames = []
    expected_total = 0
    for wave in sorted(WAVE_DIRS.keys()):
        df = load_demo(wave)
        expected_total += len(df)
        frames.append(df)

    spine = pd.concat(frames, ignore_index=True, sort=False)
    log.info("Stacked demo: %d rows × %d cols (expected %d)", len(spine), len(spine.columns), expected_total)

    if len(spine) != expected_total:
        log.warning("Row count mismatch after concat: got %d expected %d", len(spine), expected_total)

    # --- Check ID × WAVE uniqueness ---
    dup_mask = spine.duplicated(subset=["ID", "WAVE"])
    n_dup = int(dup_mask.sum())
    if n_dup > 0:
        log.warning("ID × WAVE duplicates in spine: %d rows — keeping first occurrence", n_dup)
        spine = spine[~dup_mask].copy()
        log_filter(log, "drop ID×WAVE duplicates", expected_total, len(spine))
    else:
        log.info("ID × WAVE uniqueness OK (0 duplicates)")

    # --- Merge Sample_Infor (admin variables) ---
    for wave in sorted(WAVE_DIRS.keys()):
        si = load_sample_info(wave)
        if si.empty:
            continue
        # Only merge columns not already in spine
        new_cols = [c for c in si.columns if c not in spine.columns or c in ("ID", "WAVE")]
        si = si[new_cols]
        if len(new_cols) <= 2:
            log.info("Wave %d Sample_Infor: no new columns to add", wave)
            continue
        spine = do_merge(
            left=spine,
            right=si,
            keys=["ID", "WAVE"],
            how="left",
            step=f"spine ← Sample_Infor wave {wave}",
            merge_type="1:1",
            log=log,
        )

    out_path = INTER_DIR / "charls_spine.parquet"
    write_parquet(spine, out_path, log=log)

    # Summary by wave
    for wave, grp in spine.groupby("WAVE"):
        log.info(
            "  Wave %d: %d individuals, %d households",
            wave, grp["ID"].nunique(),
            grp["HOUSEHOLDID"].nunique() if "HOUSEHOLDID" in grp.columns else -1,
        )

    log.info("SUCCESS")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        log.exception("FATAL: %s", exc)
        sys.exit(1)
