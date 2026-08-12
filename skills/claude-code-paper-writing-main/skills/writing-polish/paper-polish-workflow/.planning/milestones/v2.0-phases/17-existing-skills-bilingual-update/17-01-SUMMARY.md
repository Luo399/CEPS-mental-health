---
phase: 17-existing-skills-bilingual-update
plan: 01
subsystem: skills
tags: [bilingual, chinese, opt-out, SKILL.md, output-contract]

# Dependency graph
requires:
  - phase: 13-bilingual-output-reference
    provides: references/bilingual-output.md defining bilingual format and opt-out keywords
provides:
  - All 7 existing eligible Skills updated with bilingual output support
  - Opt-out keyword detection across all 7 Skills
  - bilingual-output.md reference linked in all 7 SKILL.md files
affects: [18-final-integration-testing]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - bilingual_mode flag pattern for opt-out gating
    - Consistent opt-out keyword check placement at workflow entry point

key-files:
  created: []
  modified:
    - .claude/skills/translation-skill/SKILL.md
    - .claude/skills/reviewer-simulation-skill/SKILL.md
    - .claude/skills/logic-skill/SKILL.md
    - .claude/skills/polish-skill/SKILL.md
    - .claude/skills/de-ai-skill/SKILL.md
    - .claude/skills/abstract-skill/SKILL.md
    - .claude/skills/experiment-skill/SKILL.md

key-decisions:
  - "No new decisions -- followed plan exactly as specified"

patterns-established:
  - "Opt-out check placement: always at context collection step (Step 1 or equivalent)"
  - "bilingual_mode flag: stored early, consumed by output step"
  - "Bilingual conversation output: displayed in session only, never written to files"

requirements-completed: [BILN-04]

# Metrics
duration: 9min
completed: 2026-03-18
---

# Phase 17 Plan 01: Existing Skills Bilingual Update Summary

**All 7 eligible Skills updated with bilingual-output.md reference, opt-out keyword detection, and skill-appropriate bilingual output format**

## Performance

- **Duration:** 9 min
- **Started:** 2026-03-18T13:10:59Z
- **Completed:** 2026-03-18T13:20:58Z
- **Tasks:** 7
- **Files modified:** 7

## Accomplishments
- All 7 existing Skills now reference `references/bilingual-output.md` in their `references.required` frontmatter
- All 7 Skills detect opt-out keywords (`english only`, `no bilingual`, `only english`, `不要中文`) and skip Chinese output when detected
- logic-skill: fixed all `**[中文]**` labels to `**[Chinese]**` for consistency
- polish-skill and de-ai-skill: added `bilingual_conversation` output contract with `> **[Chinese]** ...` blockquote display per modified paragraph
- abstract-skill: added `bilingual_abstract` output contract with per-sentence Farquhar formula Chinese blockquotes
- experiment-skill: added `bilingual_discussion` output contract with per-finding-paragraph Chinese blockquotes

## Task Commits

Each task was committed atomically:

1. **Task 1: translation-skill -- add opt-out + reference** - `64fb4bf` (feat)
2. **Task 2: reviewer-simulation-skill -- add opt-out + reference** - `e32336f` (feat)
3. **Task 3: logic-skill -- fix label + add opt-out + reference** - `99f5054` (feat)
4. **Task 4: polish-skill -- add bilingual conversation output + opt-out + reference** - `f5b0366` (feat)
5. **Task 5: de-ai-skill -- add bilingual conversation output + opt-out + reference** - `6601922` (feat)
6. **Task 6: abstract-skill -- add bilingual blockquote output + opt-out + reference** - `adbf2e6` (feat)
7. **Task 7: experiment-skill -- add bilingual blockquote output + opt-out + reference** - `64a3a22` (feat)

## Files Created/Modified
- `.claude/skills/translation-skill/SKILL.md` - Added bilingual-output.md ref, opt-out check, updated output contract condition
- `.claude/skills/reviewer-simulation-skill/SKILL.md` - Added bilingual-output.md ref, opt-out check in Step 3
- `.claude/skills/logic-skill/SKILL.md` - Added bilingual-output.md ref, fixed [中文] to [Chinese], opt-out check, updated References section
- `.claude/skills/polish-skill/SKILL.md` - Added bilingual-output.md ref, bilingual_conversation contract, opt-out check, Step 5/6 bilingual display
- `.claude/skills/de-ai-skill/SKILL.md` - Added bilingual-output.md ref, bilingual_conversation contract, opt-out check, Phase 2 Step 4 bilingual display
- `.claude/skills/abstract-skill/SKILL.md` - Added bilingual-output.md ref, bilingual_abstract contract, opt-out check, per-sentence bilingual display in Step 3
- `.claude/skills/experiment-skill/SKILL.md` - Added bilingual-output.md ref, bilingual_discussion contract, opt-out check, per-paragraph bilingual display in Phase 2 Step 3

## Decisions Made
None - followed plan as specified.

## Deviations from Plan
None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All 7 Skills are bilingual-ready with opt-out support
- Phase 18 (final integration testing) can proceed to validate end-to-end bilingual output across all Skills

## Self-Check: PASSED

All 8 files verified as present. All 7 task commits verified in git log.

---
*Phase: 17-existing-skills-bilingual-update*
*Completed: 2026-03-18*
