# CHARLS Research Harness — shared utilities
# Date: 2026-06-02
# Author: Claude Code

import sys
import logging
import datetime
from pathlib import Path
from typing import List, Optional, Tuple

import pandas as pd
import pyreadstat

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_ROOT = PROJECT_ROOT / "input" / "data" / "CHARLS_raw"
INTER_DIR = PROJECT_ROOT / "data" / "intermediate"
PROC_DIR = PROJECT_ROOT / "data" / "processed"
LOG_DIR = PROJECT_ROOT / "logs"
REPORTS_DIR = PROJECT_ROOT / "reports"

# Key columns exempt from module prefixing
CHARLS_KEY_COLS = {"ID", "HOUSEHOLDID", "COMMUNITYID", "WAVE"}

# Wave year → folder mapping
WAVE_DIRS = {
    2011: RAW_ROOT / "2011charls",
    2013: RAW_ROOT / "2013charls",
    2015: RAW_ROOT / "2015charls",
    2018: RAW_ROOT / "2018charls",
    2020: RAW_ROOT / "2020charls",
}


def get_logger(name: str, log_file: str) -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return logger
    fh = logging.FileHandler(LOG_DIR / log_file, encoding="utf-8", mode="w")
    sh = logging.StreamHandler(sys.stdout)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    fh.setFormatter(fmt)
    sh.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger


def read_dta(
    path: Path,
    prefix: Optional[str] = None,
    log=None,
) -> Tuple[pd.DataFrame, object]:
    """Read .dta file, uppercase column names, optionally prefix non-key cols."""
    df, meta = pyreadstat.read_dta(str(path))
    df.columns = [c.upper() for c in df.columns]
    if log:
        log.info("READ %s: %d rows × %d cols", path.name, len(df), len(df.columns))
    if prefix:
        rename = {c: f"{prefix}{c}" for c in df.columns if c not in CHARLS_KEY_COLS}
        df = df.rename(columns=rename)
    return df, meta


def log_filter(log, description: str, before: int, after: int) -> None:
    dropped = before - after
    log.info("FILTER [%s]: %d → %d (dropped %d)", description, before, after, dropped)


def append_merge_report(
    step: str,
    merge_type: str,
    keys: List[str],
    left_n: int,
    right_n: int,
    result_n: int,
    matched: int,
    unmatched_left: int,
    unmatched_right: int,
    dup_note: str = "",
    conflict_note: str = "",
) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORTS_DIR / "charls_merge_report.md"
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    block = (
        f"\n## {step}\n"
        f"- **Timestamp**: {ts}\n"
        f"- **Merge type**: {merge_type}\n"
        f"- **Keys**: {', '.join(keys)}\n"
        f"- **Left rows**: {left_n:,}\n"
        f"- **Right rows**: {right_n:,}\n"
        f"- **Post-merge rows**: {result_n:,}\n"
        f"- **Matched**: {matched:,}\n"
        f"- **Unmatched left**: {unmatched_left:,}\n"
        f"- **Unmatched right**: {unmatched_right:,}\n"
        f"- **Duplicate key note**: {dup_note or 'none'}\n"
        f"- **Variable conflict note**: {conflict_note or 'none'}\n"
    )
    with open(path, "a", encoding="utf-8") as f:
        f.write(block)


def do_merge(
    left: pd.DataFrame,
    right: pd.DataFrame,
    keys: List[str],
    how: str,
    step: str,
    merge_type: str,
    log,
    suffix_right: str = "_right",
    conflict_note: str = "",
) -> pd.DataFrame:
    """Left-join with automatic merge report logging."""
    left_n = len(left)
    right_n = len(right)

    dup_count = int(right.duplicated(subset=keys).sum())
    if dup_count > 0 and merge_type == "1:1":
        log.warning("MERGE %s: %d duplicate keys in right table", step, dup_count)
    dup_note = f"{dup_count} duplicate key rows in right table" if dup_count else ""

    merged = left.merge(right, on=keys, how=how, suffixes=("", suffix_right))
    result_n = len(merged)

    # Use only key columns for indicator joins to avoid copying the full wide panel
    ind = left[keys].merge(right[keys].drop_duplicates(), on=keys, how="left", indicator=True)
    matched = int((ind["_merge"] == "both").sum())
    unmatched_left = int((ind["_merge"] == "left_only").sum())

    ind_r = right[keys].drop_duplicates().merge(
        left[keys].drop_duplicates(), on=keys, how="left", indicator=True
    )
    unmatched_right = int((ind_r["_merge"] == "left_only").sum())

    log.info(
        "MERGE %s: left=%d right=%d result=%d matched=%d unmatched_left=%d unmatched_right=%d",
        step, left_n, right_n, result_n, matched, unmatched_left, unmatched_right,
    )
    append_merge_report(
        step=step,
        merge_type=merge_type,
        keys=keys,
        left_n=left_n,
        right_n=right_n,
        result_n=result_n,
        matched=matched,
        unmatched_left=unmatched_left,
        unmatched_right=unmatched_right,
        dup_note=dup_note,
        conflict_note=conflict_note,
    )
    return merged


def find_file(wave_dir: Path, *candidates: str) -> Optional[Path]:
    """Return the first existing file from a list of candidate names (case-insensitive)."""
    names_lower = {c.lower(): c for c in candidates}
    for f in wave_dir.iterdir():
        if f.suffix.lower() == ".dta" and f.name.lower() in names_lower:
            return f
    return None


def clean_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize object columns for parquet: bytes→str; mixed str+numeric→float or str."""
    import math

    for col in df.columns:
        if df[col].dtype != object:
            continue

        non_null = df[col].dropna()
        if len(non_null) == 0:
            continue

        # Decode bytes (check first 100 rows as hint, then apply to all)
        if any(isinstance(x, bytes) for x in non_null.iloc[:100]):
            df[col] = df[col].apply(
                lambda x: x.decode("utf-8", errors="replace") if isinstance(x, bytes) else x
            )
            non_null = df[col].dropna()

        # Sample head+tail to detect mixed types without full O(n) scan
        sample = pd.concat([non_null.head(200), non_null.tail(200)]).drop_duplicates()
        type_set = set(sample.apply(type))
        has_str = str in type_set
        has_num = bool(type_set & {int, float})

        if has_str and has_num:
            # Use .str accessor (vectorized): returns NaN for non-string values
            str_stripped = df[col].str.strip()
            actual_strings = str_stripped.dropna()
            all_empty = len(actual_strings) == 0 or bool((actual_strings == "").all())
            if all_empty:
                # '' represents missing → coerce column to numeric
                df[col] = pd.to_numeric(df[col].where(df[col].str.len().isna(), other=None),
                                        errors="coerce")
            else:
                # Meaningful string values exist → convert everything to str
                df[col] = df[col].apply(
                    lambda x: None if (x is None or (isinstance(x, float) and math.isnan(x)))
                    else str(x)
                )

    return df


def write_parquet(df: pd.DataFrame, path: Path, log=None) -> None:
    """Write DataFrame to parquet after deduplicating columns and normalizing types."""
    # Drop duplicate column names (keep first occurrence)
    dup_mask = df.columns.duplicated()
    if dup_mask.any():
        dup_names = df.columns[dup_mask].tolist()
        if log:
            log.warning("Dropping %d duplicate columns: %s", len(dup_names), dup_names[:10])
        df = df.loc[:, ~df.columns.duplicated()]

    df = clean_dtypes(df)
    df.to_parquet(str(path), index=False)
    if log:
        log.info("Saved parquet: %s (%d rows × %d cols)", path.name, len(df), len(df.columns))


def build_codebook(df: pd.DataFrame) -> pd.DataFrame:
    """Build a codebook DataFrame from a panel."""
    records = []
    n_total = len(df)
    for col in df.columns:
        series = df[col]
        dtype = str(series.dtype)
        n_missing = int(series.isna().sum())
        n_obs = n_total - n_missing
        pct_missing = round(100.0 * n_missing / n_total, 2) if n_total > 0 else 0.0
        n_unique = int(series.nunique(dropna=True))
        col_min = col_max = col_mean = example_values = ""
        if pd.api.types.is_numeric_dtype(series):
            non_null = series.dropna()
            if len(non_null) > 0:
                col_min = str(round(float(non_null.min()), 6))
                col_max = str(round(float(non_null.max()), 6))
                col_mean = str(round(float(non_null.mean()), 6))
        else:
            top = series.dropna().value_counts().head(5).index.tolist()
            example_values = "; ".join(str(v)[:40] for v in top)
        records.append({
            "variable_name": col,
            "dtype": dtype,
            "n_obs": n_obs,
            "n_missing": n_missing,
            "pct_missing": pct_missing,
            "min": col_min,
            "max": col_max,
            "mean": col_mean,
            "n_unique": n_unique,
            "example_values": example_values,
        })
    return pd.DataFrame(records)
