# CHARLS Research Harness — LTCI Replication Subsample Extraction
# Task: charls_11 — extract subsample for Zhang et al. (2026) LTCI replication
# Paper: "The effect of long-term care insurance on labor force participation
#         among informal caregivers: evidence from China"
# Date: 2026-06-03
# Author: Claude Code

import sys
import math
import numpy as np
import pandas as pd
import pyreadstat

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _charls_utils import (
    get_logger, find_file, log_filter,
    WAVE_DIRS, INTER_DIR, PROC_DIR, LOG_DIR, write_parquet,
)

WAVES = [2011, 2013, 2018]

# --- LTCI Pilot City Names (Chinese) ---
# 12 pilot cities as listed in the paper; matched against PSU CITY field (string).
# The PSU/Sample_Infor CITY column uses Chinese city names, e.g. "青岛市", "上海市".
# We match using partial city-name matching (city name without 市/区 suffix).
LTCI_CITY_NAMES = [
    "青岛",   # Qingdao  (special: post=1 from 2013)
    "上海",   # Shanghai
    "广州",   # Guangzhou
    "重庆",   # Chongqing
    "成都",   # Chengdu
    "宁波",   # Ningbo
    "齐齐哈尔", # Qiqihar
    "安庆",   # Anqing
    "荆门",   # Jingmen
    "苏州",   # Suzhou (Jiangsu)
    "上饶",   # Shangrao
    "承德",   # Chengde
]
QINGDAO_NAME = "青岛"  # special case: post=1 from 2013 (already had LTCI since 2012)


# ─────────────────────────────────────────────────────────────
#   1. COMMUNITY → CITY MAPPING  (from PSU file)
# ─────────────────────────────────────────────────────────────

def build_city_map(log) -> pd.DataFrame:
    """
    Build communityID→city_name→is_ltci_city mapping.
    PSU file available in 2011 and 2013 waves. 2018 uses Sample_Infor (no city name).
    We merge 2011 and 2013 PSU records and union them, then apply to all waves.
    """
    frames = []
    for wave in [2011, 2013]:
        path = find_file(WAVE_DIRS[wave], "PSU.dta", "psu.dta")
        if path is None:
            log.warning("PSU file not found for wave %d", wave)
            continue
        df, _ = pyreadstat.read_dta(str(path))
        df.columns = [c.upper() for c in df.columns]
        if "COMMUNITYID" not in df.columns or "CITY" not in df.columns:
            log.warning("PSU W%d missing COMMUNITYID or CITY columns", wave)
            continue
        sub = df[["COMMUNITYID", "CITY"]].copy()
        sub["WAVE"] = wave
        frames.append(sub)
        log.info("PSU W%d: %d communities", wave, len(sub))

    if not frames:
        log.error("No PSU data loaded — cannot identify LTCI cities")
        sys.exit(1)

    psu = pd.concat(frames, ignore_index=True)
    # Deduplicate: prefer 2013 over 2011 for the same communityID
    psu = psu.sort_values("WAVE", ascending=False).drop_duplicates("COMMUNITYID")
    psu = psu[["COMMUNITYID", "CITY"]].copy()

    # Tag LTCI cities: partial match on city name string
    def is_ltci(city_val):
        if pd.isna(city_val):
            return 0
        s = str(city_val)
        return int(any(name in s for name in LTCI_CITY_NAMES))

    def is_qingdao(city_val):
        if pd.isna(city_val):
            return 0
        return int(QINGDAO_NAME in str(city_val))

    psu["IS_LTCI_CITY"] = psu["CITY"].apply(is_ltci)
    psu["IS_QINGDAO"] = psu["CITY"].apply(is_qingdao)

    n_ltci = int(psu["IS_LTCI_CITY"].sum())
    n_qdao = int(psu["IS_QINGDAO"].sum())
    log.info("City map: %d total communities, %d in LTCI cities (%d Qingdao)",
             len(psu), n_ltci, n_qdao)
    log.info("LTCI community city names found: %s",
             sorted(psu.loc[psu.IS_LTCI_CITY == 1, "CITY"].unique().tolist()))
    return psu


# ─────────────────────────────────────────────────────────────
#   2. LOAD ONE WAVE
# ─────────────────────────────────────────────────────────────

def load_wave(wave: int, log) -> pd.DataFrame:
    """Load and merge relevant modules for one wave. Returns individual-level frame."""
    wd = WAVE_DIRS[wave]
    log.info("--- Loading wave %d ---", wave)

    # ── Demographic_Background (spine) ──────────────────────────────────
    dem_path = find_file(wd, "Demographic_Background.dta", "demographic_background.dta")
    dem, _ = pyreadstat.read_dta(str(dem_path))
    dem.columns = [c.upper() for c in dem.columns]
    dem["WAVE"] = wave
    n0 = len(dem)
    log.info("W%d Demographic: %d rows", wave, n0)

    # Standardise key columns
    for col in ["COMMUNITYID", "HOUSEHOLDID", "ID"]:
        low = col.lower()
        if col not in dem.columns and low in dem.columns:
            dem = dem.rename(columns={low: col})
    keys = ["ID", "HOUSEHOLDID", "COMMUNITYID", "WAVE"]

    # ── Family_Transfer (caregiving + grandchild care) ──────────────────
    ft_path = find_file(wd, "Family_Transfer.dta", "family_transfer.dta")
    ft, _ = pyreadstat.read_dta(str(ft_path))
    ft.columns = [c.upper() for c in ft.columns]
    ft_keys = [c for c in ["ID", "HOUSEHOLDID", "COMMUNITYID"] if c in ft.columns]
    if not ft_keys:
        ft_keys = [c for c in ["id", "householdID", "communityID"] if c.upper() in ft.columns]
    ft = ft.rename(columns={c: c.upper() for c in ft.columns})

    # Select caregiving columns based on wave
    ft_cols = set(ft.columns)
    care_cols = []
    if wave in [2011, 2013]:
        for c in ["CF004", "CF001",
                  "CF005_2", "CF005_4", "CF005_6", "CF005_8",
                  "CF005_1", "CF005_3", "CF005_5", "CF005_7"]:
            if c in ft_cols:
                care_cols.append(c)
    else:  # 2018
        for c in ft_cols:
            cu = c.upper()
            if cu.startswith("CF004_W4") or cu.startswith("CF005_W4") or cu == "CF001":
                care_cols.append(c)

    merge_keys = [c for c in ["ID", "HOUSEHOLDID", "COMMUNITYID"] if c in ft_cols]
    ft_sub = ft[merge_keys + care_cols].drop_duplicates(subset=["ID"] if "ID" in ft_cols else merge_keys[:1])
    dem = dem.merge(ft_sub, on=[k for k in merge_keys if k in dem.columns], how="left")
    log.info("W%d after FamilyTransfer merge: %d rows", wave, len(dem))

    # ── Work_Retirement ────────────────────────────────────────────────
    wr_path = find_file(wd,
                        "Work_Retirement_and_Pension.dta",
                        "Work_Retirement.dta",
                        "work_retirement_and_pension.dta")
    wr, _ = pyreadstat.read_dta(str(wr_path))
    wr.columns = [c.upper() for c in wr.columns]
    wr_cols_need = []
    if wave in [2011, 2013]:
        for c in ["FA001", "FA002", "FA003", "FC001", "FC014", "FC015"]:
            if c in wr.columns:
                wr_cols_need.append(c)
    else:
        for c in ["FA001", "FA002_W4", "FA003", "FC001", "FA006_W3_3"]:
            if c in wr.columns:
                wr_cols_need.append(c)
    wr_keys = [c for c in ["ID", "HOUSEHOLDID", "COMMUNITYID"] if c in wr.columns]
    wr_sub = wr[wr_keys + wr_cols_need].drop_duplicates("ID")
    dem = dem.merge(wr_sub, on=[k for k in wr_keys if k in dem.columns], how="left")
    log.info("W%d after WorkRetirement merge: %d rows", wave, len(dem))

    # ── Health_Status_and_Functioning ──────────────────────────────────
    hs_path = find_file(wd, "Health_Status_and_Functioning.dta",
                        "health_status_and_functioning.dta")
    hs, _ = pyreadstat.read_dta(str(hs_path))
    hs.columns = [c.upper() for c in hs.columns]
    hs_want = []
    # Self-rated health (wave-specific)
    # 2011: DA001 (5-point); 2013: DA001 still 5-point but also DA079;
    # 2018: DA002 is the main self-rated health
    for c in ["DA001", "DA002", "DA079"]:
        if c in hs.columns:
            hs_want.append(c)
    # Chronic disease indicators (up to 14 diseases)
    for i in range(1, 15):
        c = f"DA007_{i}_"
        if c in hs.columns:
            hs_want.append(c)
    # Pain sentinel
    for c in ["DA041", "DA041_W4"]:
        if c in hs.columns:
            hs_want.append(c)
    # Pain: number of pain sites — try both naming conventions
    for i in range(1, 16):
        for fmt in [f"DA042S{i}", f"DA042_S{i}"]:
            if fmt in hs.columns:
                hs_want.append(fmt)
                break
    # Sleep
    for c in ["DA049", "DA049_W4", "DA050"]:
        if c in hs.columns:
            hs_want.append(c)
            break
    # Social activities (last month) — try both naming conventions
    for i in range(1, 12):
        for fmt in [f"DA056S{i}", f"DA056_S{i}"]:
            if fmt in hs.columns:
                hs_want.append(fmt)
                break
    # CES-D 10 items (DC009-DC018 — only available in 2011 and 2013)
    for i in range(9, 19):
        c = f"DC0{i:02d}"
        if c in hs.columns:
            hs_want.append(c)
    hs_keys = [c for c in ["ID", "HOUSEHOLDID", "COMMUNITYID"] if c in hs.columns]
    hs_sub = hs[hs_keys + hs_want].drop_duplicates("ID")
    dem = dem.merge(hs_sub, on=[k for k in hs_keys if k in dem.columns], how="left")
    log.info("W%d after HealthStatus merge: %d rows", wave, len(dem))

    # ── Health_Care_and_Insurance ──────────────────────────────────────
    hci_path = find_file(wd, "Health_Care_and_Insurance.dta",
                         "health_care_and_insurance.dta")
    hci, _ = pyreadstat.read_dta(str(hci_path))
    hci.columns = [c.upper() for c in hci.columns]
    hci_want = []
    if wave in [2011, 2013]:
        for i in range(1, 11):
            c = f"EA001S{i}"
            if c in hci.columns:
                hci_want.append(c)
    else:  # 2018
        for i in range(1, 13):
            c = f"EA001_W4_S{i}"
            if c in hci.columns:
                hci_want.append(c)
    hci_keys = [c for c in ["ID", "HOUSEHOLDID", "COMMUNITYID"] if c in hci.columns]
    hci_sub = hci[hci_keys + hci_want].drop_duplicates("ID")
    dem = dem.merge(hci_sub, on=[k for k in hci_keys if k in dem.columns], how="left")
    log.info("W%d after HealthInsurance merge: %d rows", wave, len(dem))

    # ── Family_Information (grandchild care alternative + marital/edu check) ──
    fi_path = find_file(wd, "Family_Information.dta", "family_information.dta")
    fi, _ = pyreadstat.read_dta(str(fi_path))
    fi.columns = [c.upper() for c in fi.columns]
    fi_want = [c for c in fi.columns if c in {"CF001"}]
    # Also try to pick up grandchild care if not already from Family_Transfer
    fi_keys = [c for c in ["ID", "HOUSEHOLDID", "COMMUNITYID"] if c in fi.columns]
    if fi_want:
        fi_sub = fi[fi_keys + fi_want].drop_duplicates("ID")
        dem = dem.merge(fi_sub, on=[k for k in fi_keys if k in dem.columns],
                        how="left", suffixes=("", "_FI"))

    # ── Household_Income ──────────────────────────────────────────────
    hi_path = find_file(wd, "Household_Income.dta", "household_income.dta")
    hi, _ = pyreadstat.read_dta(str(hi_path))
    hi.columns = [c.upper() for c in hi.columns]
    # Look for total household income: try gi010, gh001, or sum of member wages
    # CHARLS stores individual wages in ga006_1_N_ (amount by year) per member.
    # We collect HOUSEHOLDID-level total income.
    total_income_var = None
    for candidate in ["GH_INCOME", "HHNETINCOME", "GH001", "GH002",
                       "TOTAL_INCOME", "TOTALINCOME"]:
        if candidate in hi.columns:
            total_income_var = candidate
            break
    if total_income_var:
        hi_sub = hi[["HOUSEHOLDID", total_income_var]].drop_duplicates("HOUSEHOLDID")
        hi_sub = hi_sub.rename(columns={total_income_var: "HH_INCOME_RAW"})
    else:
        # Sum annual wage amounts per household member.
        # 2011/2013: ga006_1_N_ (annual amount by year per member)
        # 2018: ga006_w4_N_ (amount per member, wave 4 naming)
        wage_cols = (
            [c for c in hi.columns if c.startswith("GA006_1_")] or
            [c for c in hi.columns if c.startswith("GA006_W4_") and not c.endswith("_MIN") and not c.endswith("_MAX")]
        )
        if wage_cols:
            hi_nums = hi[["HOUSEHOLDID"] + wage_cols].copy()
            for wc in wage_cols:
                hi_nums[wc] = pd.to_numeric(hi_nums[wc], errors="coerce")
            hi_hh = hi_nums.groupby("HOUSEHOLDID")[wage_cols].sum(min_count=1)
            hi_hh["HH_INCOME_RAW"] = hi_hh[wage_cols].sum(axis=1, min_count=1)
            hi_sub = hi_hh[["HH_INCOME_RAW"]].reset_index()
            log.info("W%d HH income: summed %d wage cols", wave, len(wage_cols))
        else:
            log.warning("W%d: No household income variable found; HH_INCOME_RAW will be NaN", wave)
            hi_sub = None

    if hi_sub is not None:
        dem = dem.merge(hi_sub, on="HOUSEHOLDID", how="left")
    log.info("W%d after HouseholdIncome merge: %d rows", wave, len(dem))

    return dem


# ─────────────────────────────────────────────────────────────
#   3. CONSTRUCT ANALYSIS VARIABLES
# ─────────────────────────────────────────────────────────────

def _to_num(series):
    return pd.to_numeric(series, errors="coerce")


def construct_vars(df: pd.DataFrame, wave: int, log) -> pd.DataFrame:
    """Construct all analysis variables from raw module columns."""

    # ── Caregiving screening ───────────────────────────────────────────
    if wave in [2011, 2013]:
        if "CF004" in df.columns:
            df["IS_CAREGIVER_RAW"] = (_to_num(df["CF004"]) == 1).astype(float)
        else:
            df["IS_CAREGIVER_RAW"] = float("nan")
            log.warning("W%d: CF004 not found — IS_CAREGIVER_RAW = NaN", wave)
    else:  # 2018
        cf4_cols = [c for c in df.columns if c.startswith("CF004_W4")]
        if cf4_cols:
            df["IS_CAREGIVER_RAW"] = (
                df[cf4_cols].apply(pd.to_numeric, errors="coerce").eq(1).any(axis=1)
            ).astype(float)
        else:
            df["IS_CAREGIVER_RAW"] = float("nan")
            log.warning("W%d: No CF004_W4 cols found", wave)

    # ── Hours of parent care per week (for intensity & log hours) ─────
    if wave in [2011, 2013]:
        # cf005_2=father hrs/wk, cf005_4=mother, cf005_6=father-in-law, cf005_8=mother-in-law
        # cf005_1/3/5/7 = corresponding weeks (to compute annual hours: hrs_per_wk * weeks)
        hrs_cols = ["CF005_2", "CF005_4", "CF005_6", "CF005_8"]
        wks_cols = ["CF005_1", "CF005_3", "CF005_5", "CF005_7"]
        total_hrs_wk = pd.Series(0.0, index=df.index)
        total_annual_hrs = pd.Series(0.0, index=df.index)
        has_care = pd.Series(False, index=df.index)
        for h, w in zip(hrs_cols, wks_cols):
            hvals = pd.to_numeric(df.get(h, pd.Series(float("nan"), index=df.index)), errors="coerce")
            wvals = pd.to_numeric(df.get(w, pd.Series(float("nan"), index=df.index)), errors="coerce")
            valid = hvals.notna() & hvals.gt(0)
            has_care |= valid
            total_hrs_wk = total_hrs_wk.add(hvals.fillna(0))
            # Annual hours = hours/week * weeks
            total_annual_hrs = total_annual_hrs.add(
                (hvals * wvals.fillna(1)).fillna(0)
            )
        df["CARE_HRS_WEEK"] = total_hrs_wk.where(has_care, float("nan"))
        df["CARE_HRS_ANNUAL"] = total_annual_hrs.where(has_care, float("nan"))
    else:  # 2018
        hrs_cols = sorted([c for c in df.columns if c.startswith("CF005_W4_2")])
        wks_cols = sorted([c for c in df.columns if c.startswith("CF005_W4_1")])
        total_hrs_wk = pd.Series(0.0, index=df.index)
        total_annual_hrs = pd.Series(0.0, index=df.index)
        has_care = pd.Series(False, index=df.index)
        for h in hrs_cols:
            idx = h.replace("CF005_W4_2", "CF005_W4_1")
            hvals = pd.to_numeric(df.get(h, pd.Series(float("nan"), index=df.index)), errors="coerce")
            wvals = pd.to_numeric(df.get(idx, pd.Series(float("nan"), index=df.index)), errors="coerce")
            valid = hvals.notna() & hvals.gt(0)
            has_care |= valid
            total_hrs_wk = total_hrs_wk.add(hvals.fillna(0))
            total_annual_hrs = total_annual_hrs.add((hvals * wvals.fillna(1)).fillna(0))
        df["CARE_HRS_WEEK"] = total_hrs_wk.where(has_care, float("nan"))
        df["CARE_HRS_ANNUAL"] = total_annual_hrs.where(has_care, float("nan"))

    # Intensity of caregiving: <10h/wk=1, 10-20h/wk=2, >=20h/wk=3
    def intensity(h):
        if pd.isna(h):
            return float("nan")
        if h < 10:
            return 1.0
        elif h < 20:
            return 2.0
        else:
            return 3.0
    df["CARE_INTENSITY"] = df["CARE_HRS_WEEK"].apply(intensity)

    # Log of annual care hours (mechanism variable)
    df["LN_CARE_HRS"] = df["CARE_HRS_ANNUAL"].apply(
        lambda x: math.log(x) if (pd.notna(x) and x > 0) else float("nan")
    )

    # ── Grandchild care ────────────────────────────────────────────────
    gc_col = "CF001" if "CF001" not in [None] else "CF001_FI"
    if "CF001" in df.columns:
        df["CARE_GRANDCHILD"] = (pd.to_numeric(df["CF001"], errors="coerce") == 1).astype(float)
    else:
        df["CARE_GRANDCHILD"] = float("nan")

    # ── Employment outcomes ─────────────────────────────────────────────
    # Paper definitions (Table 1):
    # NON_AGRI_EMPLOY: ≥1hr non-agri paid/business work last week OR on leave from non-agri job
    # AGRI_EMPLOY: worked for OTHER farmers/employers AND paid ≥10 days past year
    #
    # Key CHARLS variable mapping — NON_AGRI_EMPLOY:
    #
    # 2011/2013 questionnaire routing:
    #   FA001=2 respondents (no agri work) → asked FA002 (non-agri ≥1hr last week/month)
    #   FA001=1 respondents (agri workers)  → routed through agri section, then asked
    #     FC014 ("Did you also work in wage/self-employed/family business last week?")
    #   FA003 = "Have a job but temporarily on leave/sick/training" (non-agri)
    #   FC015 = "Temporarily laid-off from non-agri job" (2011 equivalent of FA003)
    #
    #   → Union: FA002==1 OR FC014==1 OR FA003==1 OR FC015==1
    #     captures BOTH pure non-agri workers AND agri-primary workers who also have non-agri jobs
    #
    # 2018: FA002_W4 is asked of everyone (explicitly "nonfarm"), so FA002_W4 OR FA003 suffices.

    def _get(col):
        return _to_num(df.get(col, pd.Series(float("nan"), index=df.index)))

    if wave in [2011, 2013]:
        fa002  = _get("FA002")
        fa003  = _get("FA003")
        fc001  = _get("FC001")
        fc014  = _get("FC014")
        fc015  = _get("FC015")
        df["NON_AGRI_EMPLOY"] = (
            (fa002 == 1) | (fc014 == 1) | (fa003 == 1) | (fc015 == 1)
        ).astype(float)
        df["AGRI_EMPLOY"] = (fc001 == 1).astype(float)

    else:  # 2018
        fa002w4 = _get("FA002_W4")
        fa003   = _get("FA003")
        fc001   = _get("FC001")
        df["NON_AGRI_EMPLOY"] = ((fa002w4 == 1) | (fa003 == 1)).astype(float)
        df["AGRI_EMPLOY"] = (fc001 == 1).astype(float)

    # ── Demographics ───────────────────────────────────────────────────
    # Gender: 1=Male, 0=Female
    # 2011: RGENDER (1=male, 2=female)
    # 2013: no gender in demographic file — will fill from 2011 baseline
    # 2018: XRGENDER (1=male, 2=female)
    gender_assigned = False
    for gcol in ["RGENDER", "XRGENDER"]:
        if gcol in df.columns:
            val = _to_num(df[gcol])
            if val.nunique() > 1:  # skip all-same preload vars
                df["GENDER"] = (val == 1).astype(float)
                gender_assigned = True
                break
    if not gender_assigned:
        df["GENDER"] = float("nan")
        log.warning("W%d: Gender not found in demographic file (will fill from baseline)", wave)

    # Age: coalesce from multiple sources (most complete wins)
    # 2011: BA002_1 (direct, complete); 2013: ZBA002_1 (preloaded, ~15k) > BA002_1 (~4k update)
    # 2018: BA002_1 (direct, complete)
    # Coalesce birth year from multiple sources per wave
    # 2011: BA002_1 (complete); 2013: ZBA002_1 (preloaded) + BA002_1 (update)
    # 2018: BA004_W3_1 (birth year for all, ~19494 non-null) + BA002_1 (new respondents)
    if wave == 2018:
        by_pref = ["BA004_W3_1", "BA002_1", "ZBA002_1"]
    elif wave == 2013:
        by_pref = ["ZBA002_1", "BA002_1"]
    else:
        by_pref = ["BA002_1", "ZBA002_1"]
    birth_yr = pd.Series(float("nan"), index=df.index)
    for bcol in by_pref:
        if bcol in df.columns:
            birth_yr = birth_yr.fillna(_to_num(df[bcol]))
    if birth_yr.notna().sum() > 0:
        df["AGE"] = wave - birth_yr
    elif "BA004" in df.columns:
        df["AGE"] = _to_num(df["BA004"])
    else:
        df["AGE"] = float("nan")
        log.warning("W%d: Age/birth-year variable not found", wave)
    log.info("W%d AGE: %d non-null / %d total", wave, df["AGE"].notna().sum(), len(df))

    # Hukou: Urban (non-agricultural)=1, Rural (agricultural)=0
    # BC001 coding: 1=Agricultural, 2=Non-agricultural, 3=Unified resident
    # Coalesce: ZBC001 (preloaded, more complete in 2013) and BC001 (direct in 2011/2018)
    bc_coalesce = pd.Series(float("nan"), index=df.index)
    for hcol in ["ZBC001", "BC001"]:
        if hcol in df.columns:
            bc_coalesce = bc_coalesce.fillna(_to_num(df[hcol]))
    if bc_coalesce.notna().any():
        df["HUKOU"] = (bc_coalesce == 2).astype(float)
        df.loc[bc_coalesce.isna(), "HUKOU"] = float("nan")
        log.info("W%d HUKOU: %d non-null", wave, df["HUKOU"].notna().sum())
    else:
        df["HUKOU"] = float("nan")
        log.warning("W%d: Hukou not found — will fill from baseline", wave)

    # Marital status: Married=0, Others=1 (paper's inverted coding)
    # BE001 available in 2011, 2013, and 2018 directly
    # Married=0 if BE001 in {1, 2}: 1=married living together, 2=married living apart
    # Others (divorced/widowed/never-married)=1; paper mean 0.074 confirms ~93% married
    be001_src = "BE001" if "BE001" in df.columns else ("ZBE001" if "ZBE001" in df.columns else None)
    if be001_src:
        be001 = _to_num(df[be001_src])
        df["MARITAL"] = (be001 > 2).astype(float)   # {1,2}=married → 0; {3,4,5,...}=other → 1
        df.loc[be001.isna(), "MARITAL"] = float("nan")
    else:
        df["MARITAL"] = float("nan")
        log.warning("W%d: Marital status not found", wave)

    # Education: Middle school and above = 1, Primary or less = 0.
    # CHARLS BD001 coding: 1=illiterate, 2=literate no school, 3=partial primary,
    #   4=PRIMARY COMPLETE (小学毕业), 5=MIDDLE SCHOOL (初中) ← paper's threshold,
    #   6=vocational HS, 7=senior HS, 8=2yr college, 9=4yr college, 10=grad.
    # Threshold: BD001 >= 5 (NOT >=4; value 4 is primary school, not middle school).
    #
    # Variable priority per wave:
    #   2011: BD001 (direct, full coverage)
    #   2013: ZBD001 (preloaded from 2011, more complete); BD001 = update-only, mostly NaN
    #   2018: BD001_W2_4 (most recently confirmed education level, full coverage)
    if wave == 2013:
        edu_pref = ["ZBD001", "BD001", "BD001_W2_4"]   # ZBD001 first for 2013
    elif wave == 2018:
        edu_pref = ["BD001_W2_4", "BD001", "ZBD001"]
    else:
        edu_pref = ["BD001", "ZBD001", "BD001_W2_4"]
    edu_assigned = False
    for ecol in edu_pref:
        if ecol in df.columns:
            bd = _to_num(df[ecol])
            if bd.notna().sum() > len(df) * 0.5:   # skip sparse update-only vars
                df["EDUCATION"] = (bd >= 5).astype(float)
                df.loc[bd.isna(), "EDUCATION"] = float("nan")
                edu_assigned = True
                log.info("W%d EDUCATION: using %s, pct_educ=%.1f%%",
                         wave, ecol, 100.0 * (bd >= 5).sum() / bd.notna().sum())
                break
    if not edu_assigned:
        df["EDUCATION"] = float("nan")
        log.warning("W%d: Education not found (all candidates sparse)", wave)

    # ── Self-reported health ────────────────────────────────────────────
    # CHARLS self-rated health (DA001) distribution: modal at 4-5 in 2011/2013.
    # Based on CHARLS questionnaire, coding is 1=Very Good → 5=Very Poor.
    # Paper recodes as Very poor=1 → Very good=5, so: health_self = 6 - DA001.
    # In 2018: DA002 = "Self-Reported Health Status" (direct 5-point scale).
    if wave == 2018:
        # 2018 uses DA002 as the self-rated health variable
        health_col = "DA002" if "DA002" in df.columns else None
        if health_col:
            df["HEALTH_SELF"] = _to_num(df[health_col])
        else:
            df["HEALTH_SELF"] = float("nan")
    else:
        # 2011/2013: DA001 coded 1=VeryGood(Excellent) to 5=VeryPoor
        # recode: 6 - DA001 → 1=VeryPoor, 5=VeryGood (matches paper)
        if "DA001" in df.columns:
            df["HEALTH_SELF"] = 6 - _to_num(df["DA001"])
        else:
            df["HEALTH_SELF"] = float("nan")
            log.warning("W%d: Self-rated health DA001 not found", wave)

    # ── Chronic diseases ───────────────────────────────────────────────
    chronic_cols = [f"DA007_{i}_" for i in range(1, 15) if f"DA007_{i}_" in df.columns]
    if chronic_cols:
        df["N_CHRONIC"] = (
            df[chronic_cols]
            .apply(pd.to_numeric, errors="coerce")
            .eq(1).sum(axis=1)
        ).astype(float)
    else:
        df["N_CHRONIC"] = float("nan")
        log.warning("W%d: Chronic disease vars not found", wave)

    # ── Health insurance ──────────────────────────────────────────────
    # Encoding differs across waves:
    #   2011/2013: EA001S1-S9 are NULL for non-selected; NON-NULL (value=type#) when selected.
    #              EA001S10 NON-NULL → explicitly "no insurance".
    #              Detection: .notna().any()
    #   2018: EA001_W4_S1-S11 always have a value: 0=not selected, non-zero=selected.
    #              EA001_W4_S12 non-zero → explicitly "no insurance".
    #              Detection: != 0 (not .notna(), since everyone has a row)
    if wave in [2011, 2013]:
        ins_cols = [f"EA001S{i}" for i in range(1, 10) if f"EA001S{i}" in df.columns]
        no_ins = "EA001S10"
        if ins_cols:
            has_any = df[ins_cols].notna().any(axis=1)
            df["HEALTH_INSURED"] = has_any.astype(float)
            if no_ins in df.columns:
                df.loc[df[no_ins].notna(), "HEALTH_INSURED"] = 0.0
        else:
            df["HEALTH_INSURED"] = float("nan")
            log.warning("W%d: Insurance cols not found", wave)
    else:  # 2018
        ins_cols = [f"EA001_W4_S{i}" for i in range(1, 12) if f"EA001_W4_S{i}" in df.columns]
        no_ins = "EA001_W4_S12"
        if ins_cols:
            # Non-zero means the type was selected (0 = not selected)
            has_any = (df[ins_cols].apply(pd.to_numeric, errors="coerce") != 0).any(axis=1)
            df["HEALTH_INSURED"] = has_any.astype(float)
            if no_ins in df.columns:
                explicitly_uninsured = _to_num(df[no_ins]) != 0
                df.loc[explicitly_uninsured, "HEALTH_INSURED"] = 0.0
            n_ins = int(df["HEALTH_INSURED"].sum())
            log.info("W%d HEALTH_INSURED: %d insured / %d total (%.1f%%)",
                     wave, n_ins, len(df), 100.0 * n_ins / len(df))
        else:
            df["HEALTH_INSURED"] = float("nan")
            log.warning("W%d: Insurance cols (EA001_W4_S*) not found", wave)

    # ── Household income (log) ─────────────────────────────────────────
    if "HH_INCOME_RAW" in df.columns:
        hh = pd.to_numeric(df["HH_INCOME_RAW"], errors="coerce")
        df["LN_HH_INCOME"] = hh.apply(
            lambda x: math.log(x) if (pd.notna(x) and x > 0) else float("nan")
        )
    else:
        df["LN_HH_INCOME"] = float("nan")

    # ── Mechanism: sleep hours ─────────────────────────────────────────
    for c in ["DA049", "DA050", "DA049_W4"]:
        if c in df.columns:
            df["SLEEP_HOURS"] = pd.to_numeric(df[c], errors="coerce")
            break
    else:
        df["SLEEP_HOURS"] = float("nan")

    # ── Mechanism: social activity participation ───────────────────────
    # Try both DA056S{i} (2011/2013) and DA056_S{i} (2018) naming
    soc_cols = []
    for i in range(1, 12):
        for fmt in [f"DA056S{i}", f"DA056_S{i}"]:
            if fmt in df.columns:
                soc_cols.append(fmt)
                break
    if soc_cols:
        df["SOCIAL_ACTIVITY"] = (
            df[soc_cols].apply(pd.to_numeric, errors="coerce").eq(1).any(axis=1)
        ).astype(float)
    else:
        df["SOCIAL_ACTIVITY"] = float("nan")

    # ── Mechanism: number of pain body parts (0-15) ────────────────────
    # Try both DA042S{i} (2011/2013) and DA042_S{i} (2018) naming
    pain_cols = []
    for i in range(1, 16):
        for fmt in [f"DA042S{i}", f"DA042_S{i}"]:
            if fmt in df.columns:
                pain_cols.append(fmt)
                break
    if pain_cols:
        df["N_PAIN_PARTS"] = (
            df[pain_cols].apply(pd.to_numeric, errors="coerce").eq(1).sum(axis=1)
        ).astype(float)
        # Set to 0 if "any pain" sentinel == 0
        for pain_sent in ["DA041", "DA041_W4"]:
            if pain_sent in df.columns:
                no_pain = _to_num(df[pain_sent]).eq(0)
                df.loc[no_pain, "N_PAIN_PARTS"] = 0.0
                break
    else:
        df["N_PAIN_PARTS"] = float("nan")

    # ── Mechanism: CES-D 10 depression score (0-30) ────────────────────
    # Items dc009-dc018 (10 items), typical coding 0=rarely/none to 3=most of time
    cesd_cols = [f"DC0{i:02d}" for i in range(9, 19) if f"DC0{i:02d}" in df.columns]
    if len(cesd_cols) >= 8:
        cesd_df = df[cesd_cols].apply(pd.to_numeric, errors="coerce")
        # Reverse positive items: DC013 (Hopeful about future) and DC016 (Happy)
        # In CHARLS CES-D coding: typically 1=rarely, 2=sometimes, 3=frequently, 4=most
        # Recode to 0-3: subtract 1 from raw (if coded 1-4)
        # Check if max > 3 → coding is 1-4
        max_val = cesd_df.max().max()
        if max_val > 3:
            cesd_df = cesd_df - 1
        # Reverse items (higher = better → recode: 3 - value)
        for rev_col in ["DC013", "DC016"]:
            if rev_col in cesd_df.columns:
                cesd_df[rev_col] = 3 - cesd_df[rev_col]
        df["DEPRESSION_CESD"] = cesd_df.sum(axis=1, skipna=False)
    else:
        df["DEPRESSION_CESD"] = float("nan")
        log.warning("W%d: CES-D items not found (%d found, need ≥8)", wave, len(cesd_cols))

    return df


# ─────────────────────────────────────────────────────────────
#   4. MAIN PIPELINE
# ─────────────────────────────────────────────────────────────

def main():
    log = get_logger("charls_11", "charls_11_subsample.log")
    log.info("=== charls_11_ltci_subsample.py START ===")

    # Step 1: Build community → city mapping
    city_map = build_city_map(log)

    all_waves = []
    for wave in WAVES:
        # Step 2: Load raw modules
        df = load_wave(wave, log)

        # Step 3: Construct analysis variables
        df = construct_vars(df, wave, log)

        # Step 4: Merge city info
        comm_col = "COMMUNITYID"
        if comm_col in df.columns:
            df = df.merge(city_map[["COMMUNITYID", "IS_LTCI_CITY", "IS_QINGDAO"]],
                          on=comm_col, how="left")
        else:
            log.warning("W%d: COMMUNITYID not found — cannot assign city treatment", wave)
            df["IS_LTCI_CITY"] = float("nan")
            df["IS_QINGDAO"] = float("nan")

        all_waves.append(df)
        log.info("W%d loaded: %d rows", wave, len(df))

    # Step 5: Stack waves
    panel = pd.concat(all_waves, ignore_index=True)
    n_stacked = len(panel)
    log.info("Stacked panel: %d rows", n_stacked)

    # Step 5b: Fill time-invariant demographics from baseline (2011) for later waves
    # GENDER: available in 2011 (RGENDER), 2018 (XRGENDER), but NOT 2013 demographic file
    # HUKOU: available in 2011 (BC001), 2013 (ZBC001), but NOT 2018 demographic file
    baseline_gender = (
        panel[panel["WAVE"] == 2011][["ID", "GENDER"]]
        .dropna(subset=["GENDER"])
        .drop_duplicates("ID")
    )
    baseline_hukou = (
        panel[panel["WAVE"] == 2011][["ID", "HUKOU"]]
        .dropna(subset=["HUKOU"])
        .drop_duplicates("ID")
    )

    # Fill missing GENDER from 2011 baseline (for 2013 where gender is not in demo file)
    n_miss_g_before = int(panel["GENDER"].isna().sum())
    if n_miss_g_before > 0:
        panel = panel.merge(
            baseline_gender.rename(columns={"GENDER": "_G_FILL"}),
            on="ID", how="left"
        )
        # After merge: fill NaN gender from baseline
        to_fill = panel["GENDER"].isna() & panel["_G_FILL"].notna()
        panel.loc[to_fill, "GENDER"] = panel.loc[to_fill, "_G_FILL"]
        panel.drop(columns=["_G_FILL"], inplace=True)
        n_filled = n_miss_g_before - int(panel["GENDER"].isna().sum())
        log.info("Filled GENDER from 2011 baseline for %d rows (still missing: %d)",
                 n_filled, int(panel["GENDER"].isna().sum()))

    # Fill missing HUKOU from 2011 baseline (for 2018 where hukou update info only)
    n_miss_h_before = int(panel["HUKOU"].isna().sum())
    if n_miss_h_before > 0:
        panel = panel.merge(
            baseline_hukou.rename(columns={"HUKOU": "_H_FILL"}),
            on="ID", how="left"
        )
        to_fill_h = panel["HUKOU"].isna() & panel["_H_FILL"].notna()
        panel.loc[to_fill_h, "HUKOU"] = panel.loc[to_fill_h, "_H_FILL"]
        panel.drop(columns=["_H_FILL"], inplace=True)
        n_filled_h = n_miss_h_before - int(panel["HUKOU"].isna().sum())
        log.info("Filled HUKOU from 2011 baseline for %d rows (still missing: %d)",
                 n_filled_h, int(panel["HUKOU"].isna().sum()))

    # Step 6: Filter to caregivers
    before = len(panel)
    panel = panel[panel["IS_CAREGIVER_RAW"] == 1].copy()
    log_filter(log, "keep informal caregivers (IS_CAREGIVER_RAW==1)", before, len(panel))

    # Step 7: Construct TREAT and POST variables
    panel["TREAT"] = panel["IS_LTCI_CITY"].fillna(0).astype(int)
    # POST definition:
    #   Qingdao: post=1 for WAVE in {2013, 2018} (had LTCI since 2012)
    #   Other LTCI cities: post=1 for WAVE == 2018
    #   Control group: post=0 always
    def assign_post(row):
        if row["TREAT"] == 0:
            return 0
        if row["IS_QINGDAO"] == 1:
            return 1 if row["WAVE"] >= 2013 else 0
        else:
            return 1 if row["WAVE"] == 2018 else 0
    panel["POST"] = panel.apply(assign_post, axis=1)
    panel["TREAT_X_POST"] = panel["TREAT"] * panel["POST"]

    log.info("Treatment assignment:")
    log.info("  Treat=1 (LTCI cities): %d obs", int((panel["TREAT"] == 1).sum()))
    log.info("  Control=0: %d obs", int((panel["TREAT"] == 0).sum()))
    log.info("  Post=1 (after LTCI): %d obs", int((panel["POST"] == 1).sum()))
    log.info("  Treat x Post=1: %d obs", int((panel["TREAT_X_POST"] == 1).sum()))

    # Step 8: Select final columns
    final_cols = [
        "ID", "HOUSEHOLDID", "COMMUNITYID", "WAVE",
        # Outcomes
        "NON_AGRI_EMPLOY", "AGRI_EMPLOY",
        # Treatment
        "TREAT", "POST", "TREAT_X_POST", "IS_LTCI_CITY", "IS_QINGDAO",
        # Demographics
        "GENDER", "AGE", "HUKOU", "MARITAL", "EDUCATION",
        # Health controls
        "HEALTH_SELF", "N_CHRONIC", "HEALTH_INSURED",
        # Caregiving controls
        "CARE_GRANDCHILD", "CARE_INTENSITY", "LN_HH_INCOME",
        # Mechanism variables
        "LN_CARE_HRS", "CARE_HRS_WEEK", "SLEEP_HOURS",
        "SOCIAL_ACTIVITY", "N_PAIN_PARTS", "DEPRESSION_CESD",
        # Raw caregiving flag
        "IS_CAREGIVER_RAW",
    ]
    existing = [c for c in final_cols if c in panel.columns]
    missing = [c for c in final_cols if c not in panel.columns]
    if missing:
        log.warning("Missing final columns: %s", missing)
    panel = panel[existing].copy()

    # Step 9: Log missing rates per variable; keep all caregivers for the subsample.
    # The replication analysis scripts will use complete cases per regression
    # (paper Table 3 N=2418 vs N=2725 suggests different samples per outcome).
    log.info("=== Missing rates (all caregivers) ===")
    for col in sorted(panel.columns):
        n_miss = int(panel[col].isna().sum())
        if n_miss > 0:
            log.info("  %-30s  missing: %d / %d  (%.1f%%)",
                     col, n_miss, len(panel), 100.0 * n_miss / len(panel))

    # Only drop if BOTH outcome variables are missing (completely uninformative rows)
    both_missing = panel["NON_AGRI_EMPLOY"].isna() & panel["AGRI_EMPLOY"].isna()
    before = len(panel)
    panel_clean = panel[~both_missing].copy()
    log_filter(log, "drop rows where BOTH outcomes missing", before, len(panel_clean))

    # Step 10: Report descriptive statistics
    log.info("=== Descriptive Statistics ===")
    for col in ["NON_AGRI_EMPLOY", "AGRI_EMPLOY", "GENDER", "AGE",
                "HUKOU", "MARITAL", "EDUCATION", "HEALTH_SELF",
                "N_CHRONIC", "HEALTH_INSURED", "CARE_GRANDCHILD",
                "CARE_INTENSITY", "LN_HH_INCOME"]:
        if col in panel_clean.columns:
            s = panel_clean[col]
            log.info("  %-25s  N=%d  mean=%.3f  sd=%.3f  min=%.1f  max=%.1f",
                     col, s.notna().sum(), s.mean(), s.std(), s.min(), s.max())

    # Compare with paper Table 2 (N=4626, mean non_agri=0.462, mean agri=0.075)
    log.info("=== WAVE breakdown ===")
    log.info(panel_clean.groupby("WAVE")[["ID"]].count().to_string())
    log.info("=== TREAT group ===")
    log.info(panel_clean.groupby("TREAT")[["NON_AGRI_EMPLOY","AGRI_EMPLOY","GENDER","AGE"]].mean().round(3).to_string())

    # Step 11: Save all output to data/processed/
    PROC_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROC_DIR / "charls_ltci_subsample.parquet"
    write_parquet(panel_clean, out_path, log=log)
    csv_path = PROC_DIR / "charls_ltci_subsample.csv"
    panel_clean.to_csv(str(csv_path), index=False)
    log.info("Also saved CSV: %s (%d rows x %d cols)", csv_path.name, len(panel_clean), len(panel_clean.columns))

    log.info("=== charls_11_ltci_subsample.py SUCCESS ===")
    log.info("Final subsample: %d observations  (paper target: ~4,626)", len(panel_clean))


if __name__ == "__main__":
    main()
