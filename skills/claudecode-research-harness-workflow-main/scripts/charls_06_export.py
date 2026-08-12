# CHARLS Research Harness — Task 06: export final CSV and codebook
# Date: 2026-06-02
# Author: Claude Code
# Uses PyArrow iter_batches to stream-join charls_hh + charls_supplement
# without loading the full 20k-column panel into RAM at once.

import sys
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).parent))
from _charls_utils import get_logger, INTER_DIR, PROC_DIR, build_codebook

log = get_logger("charls_export", "charls_06_export.log")

# charls_hh.parquet already contains spine + individual + household modules.
# charls_supplement.parquet adds biomarker, blood, cognition, COVID, etc.
BATCH_ROWS = 3000   # rows per chunk (controls peak RAM)


def get_schema_names(parquet_path: Path) -> list:
    return pq.read_schema(str(parquet_path)).names


def main():
    log.info("START export CSV and codebook")
    PROC_DIR.mkdir(parents=True, exist_ok=True)

    hh_path  = INTER_DIR / "charls_hh.parquet"
    sup_path = INTER_DIR / "charls_supplement.parquet"

    for p in [hh_path, sup_path]:
        if not p.exists():
            log.error("Missing: %s", p)
            sys.exit(1)

    # Determine which supplement columns are new (not already in hh)
    hh_cols  = set(get_schema_names(hh_path))
    sup_cols = get_schema_names(sup_path)
    new_sup_cols = [c for c in sup_cols if c not in hh_cols]
    log.info("hh cols: %d | supplement new cols: %d | total: %d",
             len(hh_cols), len(new_sup_cols), len(hh_cols) + len(new_sup_cols))

    out_csv = PROC_DIR / "charls_merged_panel.csv"
    log.info("Streaming export → %s ...", out_csv.name)

    hh_file  = pq.ParquetFile(str(hh_path))
    sup_file = pq.ParquetFile(str(sup_path))

    first_chunk = True
    total_rows = 0

    for hh_batch, sup_batch in zip(
        hh_file.iter_batches(batch_size=BATCH_ROWS),
        sup_file.iter_batches(batch_size=BATCH_ROWS, columns=["ID", "WAVE"] + new_sup_cols),
    ):
        hh_df  = hh_batch.to_pandas()
        sup_df = sup_batch.to_pandas()

        # Align supplement to hh by row position (same spine order)
        # Drop key columns from sup that are already in hh_df
        sup_new_only = sup_df[new_sup_cols] if new_sup_cols else pd.DataFrame(index=sup_df.index)

        chunk = pd.concat([hh_df, sup_new_only], axis=1)

        chunk.to_csv(
            out_csv,
            index=False,
            encoding="utf-8-sig",
            mode="w" if first_chunk else "a",
            header=first_chunk,
        )
        total_rows += len(chunk)
        first_chunk = False

        if total_rows % 30000 == 0 or total_rows <= BATCH_ROWS:
            log.info("  Written %d rows so far ...", total_rows)

    log.info("Wrote %s: %d rows", out_csv.name, total_rows)

    # --- Build codebook ---
    # Read hh schema + supplement schema for column list
    all_col_names = get_schema_names(hh_path) + new_sup_cols
    total_cols = len(all_col_names)
    log.info("Total columns in panel: %d", total_cols)

    # Build codebook by scanning the CSV in chunks (avoids full RAM load)
    log.info("Building codebook from CSV chunks ...")
    agg = {}  # col → {dtype, n_obs, n_missing, min, max, sum, sum_sq, n_unique_sample, example}

    chunk_iter = pd.read_csv(out_csv, chunksize=10000, encoding="utf-8-sig", low_memory=False)
    n_total = 0
    for chunk in chunk_iter:
        n_total += len(chunk)
        for col in chunk.columns:
            s = chunk[col]
            if col not in agg:
                agg[col] = {
                    "dtype": str(s.dtype),
                    "n_obs": 0,
                    "n_missing": 0,
                    "numeric": pd.api.types.is_numeric_dtype(s),
                    "min": None, "max": None, "sum": 0.0,
                    "examples": set(),
                }
            entry = agg[col]
            entry["n_missing"] += int(s.isna().sum())
            entry["n_obs"] += int(s.notna().sum())
            if entry["numeric"]:
                nn = s.dropna()
                if len(nn):
                    cur_min = float(nn.min())
                    cur_max = float(nn.max())
                    entry["min"] = cur_min if entry["min"] is None else min(entry["min"], cur_min)
                    entry["max"] = cur_max if entry["max"] is None else max(entry["max"], cur_max)
                    entry["sum"] += float(nn.sum())
            else:
                entry["examples"].update(str(v)[:30] for v in s.dropna().unique()[:5])

    records = []
    for col, e in agg.items():
        n_obs = e["n_obs"]
        n_miss = e["n_missing"]
        pct_miss = round(100.0 * n_miss / n_total, 2) if n_total > 0 else 0.0
        col_mean = ""
        if e["numeric"] and n_obs > 0:
            col_mean = str(round(e["sum"] / n_obs, 6))
        records.append({
            "variable_name": col,
            "dtype": e["dtype"],
            "n_obs": n_obs,
            "n_missing": n_miss,
            "pct_missing": pct_miss,
            "min": "" if e["min"] is None else str(round(e["min"], 6)),
            "max": "" if e["max"] is None else str(round(e["max"], 6)),
            "mean": col_mean,
            "example_values": "; ".join(list(e["examples"])[:5]),
        })

    cb = pd.DataFrame(records)
    out_cb = PROC_DIR / "charls_codebook.csv"
    cb.to_csv(out_cb, index=False, encoding="utf-8-sig")
    log.info("Wrote %s: %d variables", out_cb.name, len(cb))

    # --- Summary ---
    log.info("--- Final dataset summary ---")
    log.info("  Total rows:    %d", total_rows)
    log.info("  Total columns: %d", total_cols)

    # Quick wave summary from first part of CSV
    wave_df = pd.read_csv(out_csv, usecols=["WAVE", "ID", "HOUSEHOLDID"],
                          encoding="utf-8-sig", low_memory=False)
    for wave, cnt in wave_df["WAVE"].value_counts().sort_index().items():
        log.info("  Wave %s: %d rows", wave, cnt)
    log.info("  Unique individuals: %d", wave_df["ID"].nunique())
    log.info("  Unique households:  %d", wave_df["HOUSEHOLDID"].nunique())

    # Overall missing % from codebook
    total_cells = n_total * total_cols
    total_missing = sum(e["n_missing"] for e in agg.values())
    log.info("  Overall missing%%: %.2f%%", 100.0 * total_missing / total_cells if total_cells else 0)
    log.info("SUCCESS")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        log.exception("FATAL: %s", exc)
        sys.exit(1)
