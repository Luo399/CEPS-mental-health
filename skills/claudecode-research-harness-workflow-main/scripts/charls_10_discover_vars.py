# CHARLS Research Harness — Variable Metadata Discovery for LTCI Replication
# Task: charls_10 — identify exact variable names across waves 2011/2013/2018
# Date: 2026-06-03
# Author: Claude Code

import sys
import csv
from pathlib import Path

import pyreadstat

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _charls_utils import get_logger, find_file, WAVE_DIRS, INTER_DIR, PROC_DIR, LOG_DIR

WAVES = [2011, 2013, 2018]

# Modules to scan — (candidate filenames in order of preference)
MODULES = {
    "Family_Transfer":              ["Family_Transfer.dta", "family_transfer.dta"],
    "Work_Retirement":              ["Work_Retirement_and_Pension.dta", "Work_Retirement.dta",
                                     "work_retirement_and_pension.dta"],
    "Demographic_Background":       ["Demographic_Background.dta", "demographic_background.dta"],
    "Family_Information":           ["Family_Information.dta", "family_information.dta"],
    "Health_Status_and_Functioning":["Health_Status_and_Functioning.dta",
                                     "health_status_and_functioning.dta"],
    "Health_Care_and_Insurance":    ["Health_Care_and_Insurance.dta",
                                     "health_care_and_insurance.dta"],
    "Household_Income":             ["Household_Income.dta", "household_income.dta"],
    "PSU":                          ["PSU.dta", "psu.dta"],
    "Sample_Infor":                 ["Sample_Infor.dta", "sample_infor.dta"],
}

# Keywords to highlight in output (labels containing these are flagged)
KEYWORDS = [
    "care", "parent", "help", "everyday", "activ", "caregiv",
    "work", "paid", "employ", "farm", "agri", "labor",
    "city", "community", "county", "province", "urban", "rural", "hukou", "registr",
    "chronic", "disease", "pain", "depress", "sleep", "social",
    "income", "household", "marr", "educat", "gender", "sex", "age",
]


def main() -> None:
    log = get_logger("charls_10", "charls_10_vars.log")
    log.info("=== charls_10_discover_vars.py START ===")

    PROC_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = PROC_DIR / "charls_10_var_list.csv"
    rows = []

    for wave in WAVES:
        wave_dir = WAVE_DIRS[wave]
        log.info("--- Wave %d : %s ---", wave, wave_dir)

        for module_key, candidates in MODULES.items():
            path = find_file(wave_dir, *candidates)
            if path is None:
                log.info("  [%s] NOT FOUND in wave %d (tried: %s)", module_key, wave, candidates)
                continue

            try:
                _, meta = pyreadstat.read_dta(str(path), metadataonly=True)
            except Exception as e:
                log.warning("  [%s] wave %d READ ERROR: %s", module_key, wave, e)
                continue

            var_names = meta.column_names
            var_labels = meta.column_labels  # list aligned with column_names
            n_vars = len(var_names)
            log.info("  [%s] wave %d → %s  (%d vars)", module_key, wave, path.name, n_vars)

            for i, (vname, vlabel) in enumerate(zip(var_names, var_labels)):
                label_str = vlabel if vlabel else ""
                label_lower = label_str.lower()
                vname_lower = vname.lower()
                flagged = any(
                    kw in label_lower or kw in vname_lower for kw in KEYWORDS
                )
                rows.append({
                    "wave": wave,
                    "module": module_key,
                    "file": path.name,
                    "var_name": vname,
                    "label": label_str,
                    "flagged": "Y" if flagged else "",
                })

                # Log all flagged variables inline for easy scanning
                if flagged:
                    log.info("    FLAG  %-25s  %s", vname, label_str[:90])

    # Write full variable list
    if rows:
        with open(out_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["wave", "module", "file", "var_name", "label", "flagged"])
            writer.writeheader()
            writer.writerows(rows)
        log.info("Saved var list: %s  (%d rows)", out_csv, len(rows))
    else:
        log.error("No variables found — check WAVE_DIRS paths")
        sys.exit(1)

    log.info("=== charls_10_discover_vars.py SUCCESS ===")


if __name__ == "__main__":
    main()
