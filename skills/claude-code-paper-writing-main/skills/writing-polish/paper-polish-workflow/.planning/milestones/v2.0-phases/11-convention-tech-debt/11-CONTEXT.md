# Phase 11: Convention & Tech Debt - Context

**Gathered:** 2026-03-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Resolve all v1.0 tech debt items and update `skill-conventions.md` so that v2.0 authoring starts from a clean, consistent foundation. This includes AskUserQuestion enforcement, bilingual output scope categories, and verifying previously-applied fixes. No new Skills are authored in this phase.

</domain>

<decisions>
## Implementation Decisions

### AskUserQuestion Enforcement Rule (UXFIX-02)
- **Per-Skill audit approach**: Each Skill's `## Ask Strategy` section declares which questions use AskUserQuestion vs plain text. No blanket mandate — authors decide per-Skill based on interaction needs
- **Placement**: Expand existing `## Ask Strategy Conventions` section in `skill-conventions.md` to include AskUserQuestion enforcement subsection
- **Direct-mode exemption**: In direct mode, Skills skip all AskUserQuestion calls entirely. User chose direct = they want speed. Proceed with defaults and inferred context
- **Examples format**: Include 1 good/bad comparison showing correct AskUserQuestion invocation vs the anti-pattern (plain dialogue for multi-option questions)

### Bilingual Output Scope Categories
- **Classification rule**: Based on `output_contract` type — Skills that produce academic text support bilingual; pure analysis/recommendation/citation Skills are exempt
- **Placement**: Expand `Output Contract` description in Body Structure table area with a bilingual eligibility subsection
- **Default behavior**: Bilingual output ON by default for eligible Skills. Users can opt out, but the default serves Chinese-primary users
- **Exempt Skills**: caption-skill (English-only captions), cover-letter-skill (journal-specific format), visualization-skill (recommendation-only), literature-skill (BibTeX output)
- **Eligible Skills**: translation-skill, polish-skill, de-ai-skill, reviewer-skill, abstract-skill, experiment-skill, logic-skill (7 total)

### Already-Fixed Debt Items (DEBT-02, DEBT-03)
- **Approach**: Verify fixes from commit `8492320` are still correct during execution, then mark as complete. No rework needed
- DEBT-02: `literature-skill` tools field already uses `External MCP` — verify only
- DEBT-03: `cover-letter-skill` required field already lists `references/journals/ceus.md` — verify only

### Escape Hatch Documentation (DEBT-01)
- **Approach**: Enhance existing line 73 text in skill-conventions.md to include specific Skill name references (logic-skill, visualization-skill, literature-skill) instead of only generic category descriptions
- Keep as inline rule, not a full subsection — current format is clear enough

### Claude's Discretion
- Exact wording and formatting of the AskUserQuestion good/bad comparison example
- How to phrase bilingual eligibility rule (table vs prose)
- Whether to add batch-mode note alongside direct-mode exemption

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Convention files
- `references/skill-conventions.md` — Main file being updated. Current AskUserQuestion mention at line 110 (fallback only), escape hatch at line 73, Body Structure at line 36
- `references/skill-skeleton.md` — Companion skeleton that must stay in sync with conventions

### Skills needing verification
- `.claude/skills/literature-skill/SKILL.md` — Verify tools field uses "External MCP" (DEBT-02)
- `.claude/skills/cover-letter-skill/SKILL.md` — Verify CEUS in required field (DEBT-03)
- `.claude/skills/logic-skill/SKILL.md` — Reference for `required: []` escape hatch example
- `.claude/skills/visualization-skill/SKILL.md` — Reference for `required: []` escape hatch example

### Requirements
- `.planning/REQUIREMENTS.md` — DEBT-01, DEBT-02, DEBT-03, UXFIX-02 definitions and traceability

### Prior fix commit
- Git commit `8492320` — "fix(v1.0-tech-debt): resolve 4 pre-milestone convention and doc issues" — contains DEBT-02 and DEBT-03 fixes to verify

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `skill-conventions.md` line 73: Existing `required: []` escape hatch text — enhance with Skill name references
- `skill-conventions.md` lines 159-177: Existing `## Ask Strategy Conventions` section — expand with AskUserQuestion enforcement subsection
- `skill-conventions.md` lines 36-49: Body Structure table — `Output Contract` row is the hook for bilingual eligibility

### Established Patterns
- Conventions use `---` section dividers with `##` headings
- Rules use `###` subheadings within sections
- Bullet lists for specific rules, tables for taxonomies
- Cross-references use backtick-quoted file paths

### Integration Points
- `skill-skeleton.md` must stay in sync — may need updates to reflect new AskUserQuestion and bilingual fields
- All 11 existing `SKILL.md` files are downstream consumers of conventions — Phase 12 and Phase 17 will apply these new rules

</code_context>

<specifics>
## Specific Ideas

No specific requirements — decisions above are clear enough for standard implementation.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 11-convention-tech-debt*
*Context gathered: 2026-03-17*
