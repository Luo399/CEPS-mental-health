# Phase 17: Existing Skills Bilingual Update - Context

**Gathered:** 2026-03-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Add bilingual (English + Chinese paragraph-by-paragraph comparison) output support to 7 existing Skills: translation-skill, polish-skill, de-ai-skill, reviewer-simulation-skill, abstract-skill, experiment-skill, logic-skill. Each Skill gets opt-out keywords and a reference to `references/bilingual-output.md`. Skills that already have bilingual output get opt-out keywords and any label fixes. Skills without bilingual get the full bilingual output variant added.

</domain>

<decisions>
## Implementation Decisions

### Default State
- **Default ON** for all 7 Skills — bilingual output is produced by default
- Overrides ROADMAP's "opt-in" wording; follows Phase 13 spec (`references/bilingual-output.md`) which is the authoritative source
- **Opt-out keywords** (case-insensitive, exact phrase match): `english only`, `no bilingual`, `only english`, `不要中文`
- When opt-out detected: produce English-only output, no Chinese

### Format Per Skill

| Skill | Current State | Output Type | Changes |
|---|---|---|---|
| translation | Always bilingual | LaTeX file `_bilingual.tex` | Add opt-out keywords + bilingual-output.md ref |
| reviewer-simulation | Always bilingual `**[Chinese]**` | Markdown in-file | Add opt-out keywords + bilingual-output.md ref |
| logic | Always bilingual `**[中文]**` | Markdown in-file | Fix label → `**[Chinese]**` + opt-out + ref |
| polish | No bilingual | LaTeX in-place edit | Add bilingual: **Chinese only in conversation response** (markdown blockquote), English edit remains in-file |
| de-ai | No bilingual | LaTeX in-place edit | Add bilingual: **Chinese only in conversation response** (markdown blockquote), English edit remains in-file |
| abstract | No bilingual | Conversation output | Add bilingual: Markdown blockquote `> **[Chinese]**` after each paragraph in response |
| experiment | No bilingual | Conversation/file | Add bilingual: Markdown blockquote `> **[Chinese]**` after each paragraph in response |

### In-Place Edit Skills (polish + de-ai)
- File edit = English only (clean LaTeX, no Chinese inserted)
- After editing, display each modified paragraph with Chinese translation in conversation as `> **[Chinese]** ...` blockquote
- This keeps the output file submission-ready while providing bilingual comprehension aid in the UI
- No `_bilingual.tex` file is generated for these two Skills

### logic-skill Label Fix
- Change `**[中文]**` → `**[Chinese]**` in all output examples and format rules within the SKILL.md
- This is a Phase 13 spec compliance fix, included in Phase 17 migration

### Bilingual Output Reference
- Add `references/bilingual-output.md` to the `references.required` (or `references.leaf_hints`) list in each of the 7 Skills' frontmatter
- Downstream agents MUST check current frontmatter structure before adding to avoid duplication

### Claude's Discretion
- Exact placement of opt-out keyword detection logic in each Skill's workflow (before or after first user interaction)
- Whether to add `bilingual_output_contract` to frontmatter `output_contract` field for the 4 new bilingual Skills
- Exact wording of the Chinese translation note in conversation for polish/de-ai (e.g., "双语对照如下：" header or inline)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Bilingual format specification
- `references/bilingual-output.md` — Authoritative spec: format variants (LaTeX `%` comment vs Markdown `>` blockquote), opt-out keywords, paragraph markers, file naming, migration checklist per Skill. **Read this first.**

### Skill conventions
- `references/skill-conventions.md` — Skill structure rules, bilingual eligibility classification (lines 56-65), output_contract convention, ~300-line budget

### Target Skill files (all 7 must be read before modifying)
- `.claude/skills/translation-skill/SKILL.md` — Already has full LaTeX bilingual; needs opt-out keywords + ref
- `.claude/skills/polish-skill/SKILL.md` — In-place edit Skill; needs bilingual conversation output added
- `.claude/skills/de-ai-skill/SKILL.md` — In-place edit Skill; needs bilingual conversation output added
- `.claude/skills/reviewer-simulation-skill/SKILL.md` — Already has Markdown bilingual; needs opt-out + ref
- `.claude/skills/abstract-skill/SKILL.md` — Conversation output; needs bilingual blockquote added
- `.claude/skills/experiment-skill/SKILL.md` — Conversation/file output; needs bilingual blockquote added
- `.claude/skills/logic-skill/SKILL.md` — Already has bilingual with wrong label; fix `**[中文]**` → `**[Chinese]**` + opt-out + ref

### Requirements
- `.planning/REQUIREMENTS.md` — BILN-04: "7 existing Skills updated to support bilingual output"

### Prior phase context
- `.planning/phases/13-bilingual-pattern-standardization/13-CONTEXT.md` — Phase 13 decisions: format rules, opt-out keywords list, migration checklist source

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `references/bilingual-output.md` Migration Checklist table: exact per-Skill change list already defined — use as task spec for each Skill
- `translation-skill/SKILL.md` lines 145-148: Reference implementation for LaTeX bilingual output; pattern for how `_bilingual.tex` is described in output contract
- `reviewer-simulation-skill/SKILL.md` lines 184-188: Reference implementation for Markdown bilingual with `**[Chinese]**` label and inline blockquote rules

### Established Patterns
- Opt-out keyword detection: check user's trigger prompt before generating output; if any opt-out keyword detected, skip all Chinese — no AskUserQuestion needed
- `references.required` frontmatter list: new reference files are added here when they must be loaded before execution
- output_contract field: lists output artifact types (e.g., `bilingual_tex`, `logic_report`); may need update for Skills gaining new bilingual output

### Integration Points
- Each Skill is independent — changes are isolated to individual SKILL.md files
- `references/skill-conventions.md` already cross-references `references/bilingual-output.md` as the format spec; no update needed there
- Phase 17 does NOT modify `repo-to-paper-skill` (Phase 16 explicitly noted it as independent)

</code_context>

<specifics>
## Specific Ideas

No specific requirements — the migration checklist in `references/bilingual-output.md` provides the per-Skill task breakdown.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 17-existing-skills-bilingual-update*
*Context gathered: 2026-03-18*
