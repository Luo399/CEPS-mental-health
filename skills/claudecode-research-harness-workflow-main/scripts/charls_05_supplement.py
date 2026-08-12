# CHARLS Research Harness — Task 05: wave-specific supplemental modules
# Date: 2026-06-02
# Author: Claude Code
# NOTE: Loads only key columns from the hh panel to avoid OOM on the 19k-col DataFrame.
#       Outputs charls_supplement.parquet containing keys + new supplement columns only.
#       charls_06_export.py handles the final column-join of all parquet files.

import sys
from pathlib import Path
from typing import Optional

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from _charls_utils import (
    get_logger, INTER_DIR, WAVE_DIRS, RAW_ROOT,
    read_dta, find_file, write_parquet,
)

log = get_logger("charls_supplement", "charls_05_supplement.log")

KEY_COLS = ["ID", "WAVE", "HOUSEHOLDID", "COMMUNITYID"]


def load_opt(wave: int, *candidates: str) -> Optional[pd.DataFrame]:
    wave_dir = WAVE_DIRS[wave]
    path = find_file(wave_dir, *candidates)
    if path is None:
        log.info("  Wave %d: %s not found — skip", wave, candidates[0])
        return None
    df, _ = read_dta(path, log=log)
    df["WAVE"] = wave
    return df


def drop_existing(supplement: pd.DataFrame, df: pd.DataFrame, keys: list) -> pd.DataFrame:
    existing = set(supplement.columns) - set(keys)
    drop = [c for c in df.columns if c in existing and c not in keys]
    if drop:
        log.info("  Dropping already-present cols: %s", drop[:10])
        df = df.drop(columns=drop)
    return df


def merge_into_supplement(
    supplement: pd.DataFrame,
    df: pd.DataFrame,
    keys: list,
    step: str,
) -> pd.DataFrame:
    """Left-join new columns into the supplement frame (slim key frame)."""
    n = len(supplement)
    df = df[df[keys[0]].notna()].copy()
    df = drop_existing(supplement, df, keys)

    new_cols = [c for c in df.columns if c not in keys]
    if not new_cols:
        log.info("SKIP %s — no new columns", step)
        return supplement

    # Deduplicate right on keys
    dup = df.duplicated(subset=keys).sum()
    if dup > 0:
        log.warning("  %s: %d duplicate key rows — keeping first", step, dup)
        df = df.drop_duplicates(subset=keys, keep="first")

    right_slim = df[keys + new_cols]
    result = supplement.merge(right_slim, on=keys, how="left")

    if len(result) != n:
        log.error("Row count changed after %s: %d → %d", step, n, len(result))
        sys.exit(1)

    log.info("MERGE %s: added %d cols, matched %d/%d",
             step, len(new_cols),
             int(supplement[keys[0]].isin(df[keys[0]]).sum()), n)
    return result


def aggregate_child_table(wave: int) -> Optional[pd.DataFrame]:
    df = load_opt(wave, "Child.dta")
    if df is None:
        return None
    df = df[df["ID"].notna()].copy()
    agg = df.groupby(["ID"]).size().reset_index(name=f"N_CHILDREN_W{wave}")
    agg["WAVE"] = wave
    log.info("  Wave %d Child: %d respondents", wave, len(agg))
    return agg


def aggregate_parent_table(wave: int) -> Optional[pd.DataFrame]:
    df = load_opt(wave, "Parent.dta")
    if df is None:
        return None
    df = df[df["ID"].notna()].copy()
    agg = df.groupby(["ID"]).size().reset_index(name=f"N_PARENTS_W{wave}")
    agg["WAVE"] = wave
    log.info("  Wave %d Parent: %d respondents", wave, len(agg))
    return agg


def aggregate_sibling_table(wave: int) -> Optional[pd.DataFrame]:
    df = load_opt(wave, "Sibling.dta")
    if df is None:
        return None
    df = df[df["ID"].notna()].copy()
    agg = df.groupby(["ID"]).size().reset_index(name=f"N_SIBLINGS_W{wave}")
    agg["WAVE"] = wave
    log.info("  Wave %d Sibling: %d respondents", wave, len(agg))
    return agg


def aggregate_exit(wave: int, *candidates: str) -> Optional[pd.DataFrame]:
    df = load_opt(wave, *candidates)
    if df is None:
        return None
    df = df[df["ID"].notna()].copy()
    agg = df.drop_duplicates(subset=["ID"])[["ID"]].copy()
    agg[f"EXIT_INTERVIEWED_W{wave}"] = 1
    agg["WAVE"] = wave
    log.info("  Wave %d exit: %d unique IDs", wave, len(agg))
    return agg


def main():
    log.info("START supplemental module merges (keys-only mode)")
    INTER_DIR.mkdir(parents=True, exist_ok=True)

    hh_path = INTER_DIR / "charls_hh.parquet"
    if not hh_path.exists():
        log.error("charls_hh.parquet not found — run charls_04_household.py first")
        sys.exit(1)

    # Load ONLY key columns — avoids OOM from the 19k-col panel
    log.info("Loading key columns from charls_hh.parquet ...")
    supplement = pd.read_parquet(hh_path, columns=KEY_COLS)
    log.info("Key frame: %d rows × %d cols", len(supplement), len(supplement.columns))
    n_spine = len(supplement)

    # --- 1. Biomarker ---
    log.info("--- Biomarker ---")
    bio_frames = []
    for wave, candidates in [(2011, ["biomarkers.dta"]), (2013, ["Biomarker.dta"]), (2015, ["Biomarker.dta"])]:
        df = load_opt(wave, *candidates)
        if df is not None:
            bio_frames.append(df)
    if bio_frames:
        bio = pd.concat(bio_frames, ignore_index=True, sort=False)
        bio = bio[bio["ID"].notna()].copy()
        supplement = merge_into_supplement(supplement, bio, ["ID", "WAVE"], "Biomarker")

    # --- 2. Blood ---
    log.info("--- Blood ---")
    blood_frames = []
    for wave, candidates in [(2011, ["Blood_20140429.dta"]), (2015, ["Blood.dta"])]:
        df = load_opt(wave, *candidates)
        if df is not None:
            blood_frames.append(df)
    if blood_frames:
        blood = pd.concat(blood_frames, ignore_index=True, sort=False)
        blood = blood[blood["ID"].notna()].copy()
        supplement = merge_into_supplement(supplement, blood, ["ID", "WAVE"], "Blood")

    # --- 3. Cognition (2018) ---
    log.info("--- Cognition (2018) ---")
    cog = load_opt(2018, "Cognition.dta")
    if cog is not None:
        cog = cog[cog["ID"].notna()].copy()
        supplement = merge_into_supplement(supplement, cog, ["ID", "WAVE"], "Cognition_2018")

    # --- 4. COVID_Module (2020) ---
    log.info("--- COVID_Module (2020) ---")
    covid = load_opt(2020, "COVID_Module.dta")
    if covid is not None:
        covid = covid[covid["ID"].notna()].copy()
        supplement = merge_into_supplement(supplement, covid, ["ID", "WAVE"], "COVID_2020")

    # --- 5. Pension + Insider (2018) ---
    log.info("--- Pension (2018) ---")
    pension = load_opt(2018, "Pension.dta")
    if pension is not None:
        pension = pension[pension["ID"].notna()].copy()
        supplement = merge_into_supplement(supplement, pension, ["ID", "WAVE"], "Pension_2018")

    log.info("--- Insider (2018) ---")
    insider = load_opt(2018, "Insider.dta")
    if insider is not None:
        insider = insider[insider["ID"].notna()].copy()
        supplement = merge_into_supplement(supplement, insider, ["ID", "WAVE"], "Insider_2018")

    # --- 6. Exit data ---
    log.info("--- Exit/Verbal Autopsy ---")
    for wave, candidates in [
        (2013, ("Verbal_Autopsy.dta",)),
        (2013, ("Exit_Interview.dta",)),
        (2020, ("Exit_Module.dta",)),
    ]:
        agg = aggregate_exit(wave, *candidates)
        if agg is not None:
            supplement = merge_into_supplement(supplement, agg, ["ID", "WAVE"], f"Exit_w{wave}")

    # --- 7. Child / Parent / Sibling counts ---
    log.info("--- Child / Parent / Sibling counts ---")
    for wave in [2013, 2015]:
        for fn, label in [(aggregate_child_table, "Child"), (aggregate_parent_table, "Parent")]:
            agg = fn(wave)
            if agg is not None:
                supplement = merge_into_supplement(supplement, agg, ["ID", "WAVE"], f"{label}_w{wave}")

    agg_sib = aggregate_sibling_table(2015)
    if agg_sib is not None:
        supplement = merge_into_supplement(supplement, agg_sib, ["ID", "WAVE"], "Sibling_2015")

    # --- 8. PSU + Community (2011, community-level) ---
    log.info("--- PSU/Community (2011) ---")
    psu = load_opt(2011, "psu.dta")
    if psu is not None:
        psu["WAVE"] = 2011
        psu = psu[psu["COMMUNITYID"].notna()].drop_duplicates(subset=["COMMUNITYID"])
        supplement = merge_into_supplement(supplement, psu, ["COMMUNITYID", "WAVE"], "PSU_2011")

    community = load_opt(2011, "community.dta")
    if community is not None:
        community["WAVE"] = 2011
        community = community[community["COMMUNITYID"].notna()].drop_duplicates(subset=["COMMUNITYID"])
        supplement = merge_into_supplement(supplement, community, ["COMMUNITYID", "WAVE"], "Community_2011")

    if len(supplement) != n_spine:
        log.error("Final row count %d ≠ spine %d", len(supplement), n_spine)
        sys.exit(1)

    out_path = INTER_DIR / "charls_supplement.parquet"
    write_parquet(supplement, out_path, log=log)
    log.info("SUCCESS")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        log.exception("FATAL: %s", exc)
        sys.exit(1)
