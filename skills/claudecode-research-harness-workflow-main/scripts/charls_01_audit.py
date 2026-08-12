# CHARLS Research Harness — Task 01: audit all raw .dta files per wave
# Date: 2026-06-02
# Author: Claude Code

import sys
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _charls_utils import get_logger, RAW_ROOT, REPORTS_DIR, WAVE_DIRS, read_dta

log = get_logger("charls_audit", "charls_01_audit.log")

LIFE_HISTORY_DIR = RAW_ROOT / "2014charls"

EXPECTED_MODULES = {
    "individual": [
        "demographic_background", "health_status_and_functioning",
        "health_care_and_insurance", "individual_income",
        "work_retirement_and_pension", "work_retirement",
    ],
    "household": [
        "household_income", "housing_characteristics", "housing",
        "family_information", "family_transfer",
    ],
    "supplement": [
        "biomarkers", "biomarker", "blood", "blood_20140429",
        "weights", "weight", "sample_infor",
        "cognition", "pension", "insider",
        "covid_module", "exit_module",
        "child", "parent", "sibling", "spousal_sibling",
        "verbal_autopsy", "exit_interview", "other_hhmember",
        "interviewer_observation", "psu", "community",
    ],
}


def audit_wave(wave: int, wave_dir: Path, report_lines: list) -> None:
    report_lines.append(f"\n## Wave {wave} — `{wave_dir.name}/`\n")
    if not wave_dir.exists():
        log.warning("Wave dir missing: %s", wave_dir)
        report_lines.append("**ERROR: directory not found**\n")
        return

    dta_files = sorted(wave_dir.glob("*.dta"))
    log.info("Wave %d: found %d .dta files", wave, len(dta_files))

    report_lines.append(f"| File | Rows | Cols | ID cols present |\n")
    report_lines.append(f"|------|------|------|-----------------|\n")

    for f in dta_files:
        try:
            df, _ = read_dta(f, log=None)
            cols_upper = set(df.columns)
            id_cols = sorted(cols_upper & {"ID", "HOUSEHOLDID", "COMMUNITYID"})
            report_lines.append(
                f"| {f.name} | {len(df):,} | {len(df.columns)} | {', '.join(id_cols) or '—'} |\n"
            )
            log.info(
                "  %s: %d rows × %d cols  IDs=%s",
                f.name, len(df), len(df.columns), id_cols,
            )
        except Exception as exc:
            log.error("  FAILED %s: %s", f.name, exc)
            report_lines.append(f"| {f.name} | ERROR | — | {exc} |\n")


def main():
    log.info("START CHARLS audit")
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    report_lines = [
        "# CHARLS Audit Report\n",
        f"> Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        "> Source: `input/data/CHARLS_raw/`\n",
    ]

    for wave, wave_dir in sorted(WAVE_DIRS.items()):
        audit_wave(wave, wave_dir, report_lines)

    # Life History (2014)
    report_lines.append(f"\n## Life History (2014) — `2014charls/`\n")
    if LIFE_HISTORY_DIR.exists():
        dta_files = sorted(LIFE_HISTORY_DIR.glob("*.dta"))
        report_lines.append("| File | Rows | Cols | ID cols present |\n")
        report_lines.append("|------|------|------|-----------------|\n")
        for f in dta_files:
            try:
                df, _ = read_dta(f, log=None)
                cols_upper = set(df.columns)
                id_cols = sorted(cols_upper & {"ID", "HOUSEHOLDID", "COMMUNITYID"})
                report_lines.append(
                    f"| {f.name} | {len(df):,} | {len(df.columns)} | {', '.join(id_cols) or '—'} |\n"
                )
                log.info(
                    "  LH %s: %d rows × %d cols  IDs=%s",
                    f.name, len(df), len(df.columns), id_cols,
                )
            except Exception as exc:
                log.error("  FAILED LH %s: %s", f.name, exc)
                report_lines.append(f"| {f.name} | ERROR | — | {exc} |\n")
    else:
        report_lines.append("**Directory not found**\n")

    # Harmonized (not used in pipeline, just noted)
    report_lines.append("\n## Harmonized CHARLS (reference only, not used in pipeline)\n")
    for hdir_name in ["Harmonized_CHARLS_C", "Harmonized_CHARLS_D"]:
        hdir = RAW_ROOT / hdir_name
        if hdir.exists():
            dta_files = list(hdir.glob("*.dta"))
            report_lines.append(f"- `{hdir_name}/`: {len(dta_files)} .dta files\n")

    audit_path = REPORTS_DIR / "charls_audit_report.md"
    audit_path.write_text("".join(report_lines), encoding="utf-8")
    log.info("Wrote %s", audit_path.name)
    log.info("SUCCESS")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        log.exception("FATAL: %s", exc)
        sys.exit(1)
