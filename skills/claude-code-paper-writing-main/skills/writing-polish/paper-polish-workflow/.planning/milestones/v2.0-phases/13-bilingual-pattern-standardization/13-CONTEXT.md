# Phase 13: Bilingual Pattern Standardization - Context

**Gathered:** 2026-03-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Create `references/bilingual-output.md` — a single authoritative bilingual output specification that all eligible Skills reference for consistent paragraph-by-paragraph English + Chinese comparison. This phase produces the reference file only; applying it to existing Skills is Phase 17.

</domain>

<decisions>
## Implementation Decisions

### Output Format Rules
- **Format-specific encoding**: LaTeX output uses `%` comment lines for Chinese; Markdown output uses `>` blockquote for Chinese. Each format follows its own native conventions
- **Display order**: English first, Chinese after — English is the primary submission text, Chinese is auxiliary reference
- **Paragraph markers**: Use `% --- Paragraph N ---` format (consistent with translation-skill's existing pattern) for both LaTeX and Markdown (Markdown variant: `<!-- Paragraph N -->`)
- **File naming**: Bilingual files use `_bilingual` suffix — e.g., `intro_bilingual.tex`, `abstract_bilingual.md`. All Skills follow this convention

### Granularity & Trigger
- **Comparison granularity**: Paragraph-level — each English paragraph immediately followed by its Chinese counterpart. Matches BILN-01 requirement
- **Default state**: Bilingual ON by default for all eligible Skills (Phase 11 decision carried forward)
- **Opt-out mechanism**: Trigger keyword detection in user prompt. Opt-out keywords: "English only", "不要中文", "no bilingual", "only English". If detected, skip Chinese output
- **No AskUserQuestion for toggle**: The default-ON + keyword-opt-out approach avoids adding interaction steps

### Chinese Translation Quality
- **Purpose**: Auxiliary comprehension aid — helps user understand English expressions, not intended as standalone Chinese paper
- **Terminology handling**: Preserve English terms + Chinese in parentheses — e.g., "urban heat island（城市热岛）". Matches geography/urban science conventions
- **Register**: Academic written Chinese (学术书面语) — e.g., "本研究提出了..." not "我们做了..."
- **Glossary integration**: If user provides a glossary file, use it for term mappings. Otherwise Claude translates based on domain knowledge

### Compatibility with Existing Skills
- **No migration needed for reviewer/logic**: Their existing blockquote format is already the correct Markdown bilingual implementation. The spec will codify this as the standard
- **Core examples**: Include 2 code examples — 1 LaTeX format + 1 Markdown format — covering the two main output scenarios
- **Migration checklist**: Include a concise per-Skill checklist for Phase 17 implementers, listing key additions/modifications each eligible Skill needs

### Claude's Discretion
- Exact wording of opt-out keyword detection rules
- How to handle edge cases (e.g., mixed Chinese-English input paragraphs)
- Migration checklist detail level per Skill
- Whether to include a "quick reference card" section at the top of the file

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Convention files
- `references/skill-conventions.md` — Bilingual Output Eligibility section (lines 56-65): defines 7 eligible / 4 exempt Skills, references `references/bilingual-output.md` as the format spec
- `references/skill-skeleton.md` — Bilingual eligibility note (line 135): cross-references conventions for output_contract classification

### Existing bilingual implementations (patterns to codify)
- `.claude/skills/translation-skill/SKILL.md` — LaTeX bilingual pattern: `%` comment lines, `% --- Paragraph N ---` markers, `_bilingual.tex` suffix
- `.claude/skills/reviewer-simulation-skill/SKILL.md` — Markdown bilingual pattern: `> **[Chinese]** ...` blockquote after each concern
- `.claude/skills/logic-skill/SKILL.md` — Markdown bilingual pattern: `> **[中文]** ...` blockquote after issue entries

### Requirements
- `.planning/REQUIREMENTS.md` — BILN-02 (format standardization), BILN-03 (shared reference file creation)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `translation-skill/SKILL.md` lines 142-148: Complete LaTeX bilingual output specification — paragraph markers, comment format, file naming. Direct source for LaTeX section of the spec
- `reviewer-simulation-skill/SKILL.md` lines 185-188: Blockquote bilingual pattern — `> **[Chinese]**` format with domain terminology preservation. Direct source for Markdown section
- `references/expression-patterns/` (5 leaf files): All contain bilingual examples (`English | 中文`). Demonstrates the project's bilingual convention in reference files

### Established Patterns
- Reference files in `references/` follow the entrypoint + leaf pattern (e.g., `expression-patterns.md` → `expression-patterns/*.md`). `bilingual-output.md` should be a single flat file (no leaf hierarchy needed for a spec)
- Reference files are loaded via `Read` tool at runtime. Keep file concise for context efficiency

### Integration Points
- `skill-conventions.md` line 65 already references `references/bilingual-output.md` — the file this phase creates
- Phase 17 will add `references/bilingual-output.md` to the `references.required` or `references.leaf_hints` of each eligible Skill's frontmatter
- Phase 16 (body generation) will use this spec for repo-to-paper bilingual output

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

*Phase: 13-bilingual-pattern-standardization*
*Context gathered: 2026-03-18*
