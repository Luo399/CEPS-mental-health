# CHARLS Research Harness — LTCI Subsample Codebook Generator
# Task: charls_12 — generate codebook for charls_ltci_subsample.parquet
# Date: 2026-06-03
# Author: Claude Code

import sys
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _charls_utils import get_logger, INTER_DIR, PROC_DIR

# ─────────────────────────────────────────────────────────────
#  Variable metadata (paper-level definitions from Table 1)
# ─────────────────────────────────────────────────────────────
VAR_META = {
    # IDs / keys
    "ID":             {"role": "id",    "paper_def": "Individual ID (12-char CHARLS respondent code)", "source": "Demographic_Background"},
    "HOUSEHOLDID":    {"role": "id",    "paper_def": "Household ID", "source": "Demographic_Background"},
    "COMMUNITYID":    {"role": "id",    "paper_def": "Community ID (links to PSU city mapping)", "source": "Demographic_Background"},
    "WAVE":           {"role": "id",    "paper_def": "Survey wave year (2011 / 2013 / 2018)", "source": "constructed"},

    # Outcomes
    "NON_AGRI_EMPLOY": {
        "role": "outcome",
        "paper_def": "Non-agricultural employment. =1 if working ≥1hr last week in non-agri paid/business work OR on leave/training from non-agri job. Yes=1, No=0.",
        "source": "Work_Retirement: FC014==1 OR FA003==1 (2011/2013); FA002_W4==1 OR FA003==1 (2018)",
        "paper_mean": 0.462, "note": "Our mean ~0.283 may differ due to questionnaire routing (FC014 vs FA002). Verify with full CHARLS questionnaire manual."
    },
    "AGRI_EMPLOY": {
        "role": "outcome",
        "paper_def": "Agricultural employment. =1 if working for OTHER farmers/employers and paid ≥10 days in past year. Yes=1, No=0.",
        "source": "Work_Retirement: FC001==1 (all waves)",
        "paper_mean": 0.075, "note": "Uses FC001 (hired farm labor), NOT FA001 (any agricultural work). Paper's 7.5% vs our 2.7% — gap may reflect coverage differences across waves."
    },

    # Treatment variables
    "TREAT":          {"role": "treatment", "paper_def": "=1 if individual lives in LTCI pilot city (12 cities; excl. Nantong/Changchun/Shihezi). =0 otherwise.", "source": "constructed from PSU city names"},
    "POST":           {"role": "treatment", "paper_def": "=1 if year is post-LTCI implementation. Qingdao: post=1 for WAVE≥2013. Other cities: post=1 for WAVE=2018.", "source": "constructed"},
    "TREAT_X_POST":   {"role": "treatment", "paper_def": "DID interaction term: TREAT × POST. Key regressor in all baseline regressions.", "source": "constructed"},
    "IS_LTCI_CITY":   {"role": "treatment", "paper_def": "=1 if community is in an LTCI pilot city (before treatment timing). Raw city flag.", "source": "PSU city name matching"},
    "IS_QINGDAO":     {"role": "treatment", "paper_def": "=1 if community is in Qingdao (early adopter). Used to set POST=1 from 2013.", "source": "PSU city name matching"},

    # Demographics
    "GENDER": {
        "role": "control",
        "paper_def": "Gender. Male=1, Female=0.",
        "source": "Demographic_Background: RGENDER (2011), XRGENDER (2018). NOTE: 2013 wave has no gender in demographic file — missing for respondents not tracked from 2011 (23% missing).",
        "paper_mean": 0.450
    },
    "AGE": {
        "role": "control",
        "paper_def": "Age of respondents at time of survey.",
        "source": "Computed from birth year: wave - BA002_1 (2011/2018) or ZBA002_1 (2013); 2018 uses BA004_W3_1.",
        "paper_mean": 53.671
    },
    "HUKOU": {
        "role": "control",
        "paper_def": "Hukou (household registration). Urban=1, Rural=0. Non-agricultural hukou=1.",
        "source": "Demographic_Background: BC001 (2011), ZBC001 (2013). Missing for 2018 wave (~49%) due to ID format change between waves.",
        "paper_mean": 0.290
    },
    "MARITAL": {
        "role": "control",
        "paper_def": "Marital status. Married=0, Others (separated/divorced/widowed/never)=1.",
        "source": "Demographic_Background: BE001. Married=(BE001==1). NOTE: our 0.174 vs paper's 0.074 — coding difference possible (paper may define married as BE001 in {1,2}).",
        "paper_mean": 0.074
    },
    "EDUCATION": {
        "role": "control",
        "paper_def": "Education. Middle school (junior high) and above=1, Primary or less=0. Threshold: BD001≥4.",
        "source": "Demographic_Background: BD001 (2011), ZBD001 (2013), BD001_W2_4 (2018).",
        "paper_mean": 0.534
    },

    # Health controls
    "HEALTH_SELF": {
        "role": "control",
        "paper_def": "Self-reported health. Very poor=1, Poor=2, Fair=3, Good=4, Very good=5.",
        "source": "Health_Status: DA001 recoded as (6-DA001) for 2011/2013 [original 1=VG→5=VP]; DA002 for 2018.",
        "note": "26.7% missing — 2018 wave uses DA002, earlier waves use DA001. Validate recoding direction against Table 2."
    },
    "N_CHRONIC": {
        "role": "control",
        "paper_def": "Number of chronic diseases (count of diagnosed conditions).",
        "source": "Health_Status: sum of DA007_1_ through DA007_14_ ==1.",
        "paper_mean": 0.838
    },
    "HEALTH_INSURED": {
        "role": "control",
        "paper_def": "Health insurance coverage. Covered=1, Not covered=0.",
        "source": "Health_Care_and_Insurance: any of EA001S1-EA001S9 non-null (multi-select question, value=type number). NOTE: paper mean=0.965; our 0.485 likely reflects merge gaps or routing for non-respondents. Researcher should verify.",
        "paper_mean": 0.965
    },

    # Caregiving controls
    "CARE_GRANDCHILD": {
        "role": "control",
        "paper_def": "Taking care of grandchildren in the past year. Yes=1, No=0.",
        "source": "Family_Transfer: CF001==1.",
        "paper_mean": 0.490
    },
    "CARE_INTENSITY": {
        "role": "control",
        "paper_def": "Intensity of caregiving for parents per week. <10h/wk=1, 10-20h/wk=2, ≥20h/wk=3.",
        "source": "Family_Transfer: categorized from CARE_HRS_WEEK. Missing 48% (2018 structure changed to per-parent indexing).",
        "note": "48% missing"
    },
    "LN_HH_INCOME": {
        "role": "control",
        "paper_def": "Log of household income in the past year (natural log).",
        "source": "Household_Income: log(sum of GA006_1_N_ wage amounts). NOTE: 84.6% missing — wage sum is incomplete proxy for total household income. Paper uses total household net income which includes agricultural income.",
        "note": "84.6% missing — wage sum only; researcher should add agricultural and transfer income components."
    },

    # Mechanism variables
    "LN_CARE_HRS": {
        "role": "mechanism",
        "paper_def": "Log of hours of caregiving for parents in the past year (mechanism variable, Table 6).",
        "source": "Family_Transfer: log(sum of CF005_2/4/6/8 × CF005_1/3/5/7) for 2011/2013; CF005_W4 for 2018.",
        "note": "48% missing"
    },
    "CARE_HRS_WEEK": {
        "role": "mechanism",
        "paper_def": "Total hours of parent care per week (used to construct CARE_INTENSITY and LN_CARE_HRS).",
        "source": "Family_Transfer: sum of hours/week across all parents."
    },
    "SLEEP_HOURS": {
        "role": "mechanism",
        "paper_def": "Average nightly sleep hours in the past month (mechanism variable, Table 6).",
        "source": "Health_Status: DA049.",
        "note": "1.5% missing"
    },
    "SOCIAL_ACTIVITY": {
        "role": "mechanism",
        "paper_def": "Social activity participation in the past month. =1 if any activity participated (mechanism variable, Table 6).",
        "source": "Health_Status: any of DA056S1-DA056S11 (2011/2013) or DA056_S1-DA056_S11 (2018) non-null."
    },
    "N_PAIN_PARTS": {
        "role": "mechanism",
        "paper_def": "Number of body parts with pain (0-15 scale, mechanism variable, Table 7).",
        "source": "Health_Status: count of DA042S1-DA042S15 or DA042_S1-DA042_S15 ==1."
    },
    "DEPRESSION_CESD": {
        "role": "mechanism",
        "paper_def": "CES-D 10 depression score (0-30, mechanism variable, Table 7). Higher=more depressed.",
        "source": "Health_Status: sum of DC009-DC018 (10 items, coding 0-3). DC013/DC016 reversed. Missing for 2018 wave (CES-D not in 2018 Health_Status).",
        "note": "51.5% missing (2018 wave lacks CES-D)"
    },

    # Flag
    "IS_CAREGIVER_RAW": {
        "role": "flag",
        "paper_def": "Raw caregiving screening variable. =1 if helped parents/parents-in-law with everyday activities in past year.",
        "source": "Family_Transfer: CF004==1 (2011/2013); any CF004_W4_N_==1 (2018). All obs in subsample have IS_CAREGIVER_RAW=1."
    },
}

# ─────────────────────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────────────────────

def main():
    log = get_logger("charls_12", "charls_12_codebook.log")
    log.info("=== charls_12_subsample_codebook.py START ===")

    in_path = PROC_DIR / "charls_ltci_subsample.parquet"
    if not in_path.exists():
        log.error("Subsample not found: %s — run charls_11 first", in_path)
        sys.exit(1)

    df = pd.read_parquet(str(in_path))
    log.info("Loaded subsample: %d rows × %d cols", len(df), len(df.columns))

    records = []
    n_total = len(df)

    for col in df.columns:
        meta = VAR_META.get(col, {})
        series = df[col]
        dtype = str(series.dtype)
        n_missing = int(series.isna().sum())
        n_obs = n_total - n_missing
        pct_missing = round(100.0 * n_missing / n_total, 2) if n_total > 0 else 0.0
        n_unique = int(series.nunique(dropna=True))

        col_min = col_max = col_mean = col_sd = ""
        example_values = ""
        if pd.api.types.is_numeric_dtype(series):
            non_null = series.dropna()
            if len(non_null) > 0:
                col_min = str(round(float(non_null.min()), 4))
                col_max = str(round(float(non_null.max()), 4))
                col_mean = str(round(float(non_null.mean()), 4))
                col_sd = str(round(float(non_null.std()), 4))
        else:
            top = series.dropna().value_counts().head(5).index.tolist()
            example_values = "; ".join(str(v)[:40] for v in top)

        paper_mean = meta.get("paper_mean", "")
        mean_match = ""
        if paper_mean and col_mean:
            diff = abs(float(col_mean) - float(paper_mean))
            if diff < 0.02:
                mean_match = "CLOSE"
            elif diff < 0.10:
                mean_match = "MODERATE"
            else:
                mean_match = "DIFFERS"

        rec = {
            "variable_name":   col,
            "role":            meta.get("role", "unknown"),
            "paper_definition": meta.get("paper_def", ""),
            "source":          meta.get("source", ""),
            "notes":           meta.get("note", ""),
            "dtype":           dtype,
            "n_obs":           n_obs,
            "n_missing":       n_missing,
            "pct_missing":     pct_missing,
            "n_unique":        n_unique,
            "min":             col_min,
            "max":             col_max,
            "mean":            col_mean,
            "sd":              col_sd,
            "example_values":  example_values,
            "paper_mean":      str(paper_mean) if paper_mean else "",
            "mean_match":      mean_match,
        }
        records.append(rec)
        log.info("  %-25s  role=%-10s  N=%d  pct_miss=%.1f%%  mean=%s (paper: %s) %s",
                 col, rec["role"], n_obs, pct_missing, col_mean or "N/A",
                 str(paper_mean) if paper_mean else "N/A", mean_match)

    cb = pd.DataFrame(records)
    PROC_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROC_DIR / "charls_ltci_codebook.csv"
    cb.to_csv(str(out_path), index=False, encoding="utf-8-sig")
    log.info("Saved codebook: %s  (%d variables)", out_path, len(cb))

    # Summary report
    log.info("=== Summary: variable match against paper Table 2 ===")
    for _, row in cb[cb["mean_match"] != ""].iterrows():
        log.info("  %-25s  mean=%-7s  paper=%-7s  match=%s",
                 row["variable_name"], row["mean"], row["paper_mean"], row["mean_match"])

    log.info("=== charls_12_subsample_codebook.py SUCCESS ===")


if __name__ == "__main__":
    main()
