# Phase 13: Bilingual Pattern Standardization - Research

**Researched:** 2026-03-18
**Domain:** Reference file authoring (Markdown specification document)
**Confidence:** HIGH

## Summary

Phase 13 is a documentation-only phase: create `references/bilingual-output.md`, a single authoritative specification file that defines how bilingual (English + Chinese) output is formatted across all eligible Skills. The deliverable is a Markdown reference file, not code. The specification codifies two format variants (LaTeX comment-based and Markdown blockquote-based) that are already in use by existing Skills, plus adds standardized paragraph markers, file naming conventions, opt-out keyword detection rules, and a per-Skill migration checklist for Phase 17.

The research confirms that the existing patterns in translation-skill (LaTeX variant) and reviewer-simulation-skill / logic-skill (Markdown variant) are already consistent with each other and with the CONTEXT.md decisions. The new spec file needs to formally document these patterns, add the opt-out mechanism, and provide the migration checklist. No libraries, dependencies, or code changes are required.

**Primary recommendation:** Write the spec as a concise, single flat file following the established reference file conventions. Include two complete code examples (one LaTeX, one Markdown), opt-out keyword detection rules, Chinese translation quality guidelines, and a per-Skill migration checklist table.

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions

**Output Format Rules:**
- Format-specific encoding: LaTeX output uses `%` comment lines for Chinese; Markdown output uses `>` blockquote for Chinese. Each format follows its own native conventions
- Display order: English first, Chinese after -- English is the primary submission text, Chinese is auxiliary reference
- Paragraph markers: Use `% --- Paragraph N ---` format (consistent with translation-skill's existing pattern) for both LaTeX and Markdown (Markdown variant: `<!-- Paragraph N -->`)
- File naming: Bilingual files use `_bilingual` suffix -- e.g., `intro_bilingual.tex`, `abstract_bilingual.md`. All Skills follow this convention

**Granularity & Trigger:**
- Comparison granularity: Paragraph-level -- each English paragraph immediately followed by its Chinese counterpart
- Default state: Bilingual ON by default for all eligible Skills (Phase 11 decision carried forward)
- Opt-out mechanism: Trigger keyword detection in user prompt. Opt-out keywords: "English only", "no bilingual", "only English". If detected, skip Chinese output
- No AskUserQuestion for toggle: The default-ON + keyword-opt-out approach avoids adding interaction steps

**Chinese Translation Quality:**
- Purpose: Auxiliary comprehension aid -- helps user understand English expressions, not intended as standalone Chinese paper
- Terminology handling: Preserve English terms + Chinese in parentheses -- e.g., "urban heat island"
- Register: Academic written Chinese -- e.g., "..." not "..."
- Glossary integration: If user provides a glossary file, use it for term mappings. Otherwise Claude translates based on domain knowledge

**Compatibility with Existing Skills:**
- No migration needed for reviewer/logic: Their existing blockquote format is already the correct Markdown bilingual implementation
- Core examples: Include 2 code examples -- 1 LaTeX format + 1 Markdown format
- Migration checklist: Include a concise per-Skill checklist for Phase 17 implementers

### Claude's Discretion
- Exact wording of opt-out keyword detection rules
- How to handle edge cases (e.g., mixed Chinese-English input paragraphs)
- Migration checklist detail level per Skill
- Whether to include a "quick reference card" section at the top of the file

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope.

</user_constraints>

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| BILN-02 | Bilingual output format standardized: LaTeX comment for .tex output, markdown blockquote for .md output | Existing patterns in translation-skill (LaTeX) and reviewer/logic-skill (Markdown) confirmed as consistent; spec codifies both variants with examples |
| BILN-03 | Shared bilingual reference file `references/bilingual-output.md` created as pattern documentation | File location, format conventions, and integration points (skill-conventions.md line 65 already references it) all confirmed |

</phase_requirements>

## Standard Stack

### Core

This phase produces a Markdown reference document only. No libraries, packages, or runtime dependencies are involved.

| Tool | Purpose | Why Standard |
|------|---------|--------------|
| Write tool | Create `references/bilingual-output.md` | Project convention for file creation |
| Read tool | Verify existing Skill patterns for consistency | Needed to cross-check spec against implementations |

### Supporting

None. This is a documentation-only phase.

### Alternatives Considered

None applicable -- the deliverable is a Markdown specification file.

## Architecture Patterns

### Target File Location

```
references/
  bilingual-output.md          # NEW -- single flat file (no leaf hierarchy)
  expression-patterns.md       # Existing entrypoint + leaf pattern
  expression-patterns/         # Existing leaf modules
  anti-ai-patterns.md          # Existing entrypoint + leaf pattern
  anti-ai-patterns/            # Existing leaf modules
  skill-conventions.md         # Already references bilingual-output.md on line 65
  skill-skeleton.md            # Already references bilingual eligibility on line 135
```

### Pattern 1: Single Flat Reference File

**What:** `bilingual-output.md` is a single file, not an entrypoint + leaf hierarchy.
**When to use:** When the specification is compact enough to fit in one file without exceeding context budget concerns.
**Why:** The CONTEXT.md explicitly states "bilingual-output.md should be a single flat file (no leaf hierarchy needed for a spec)". The content scope (two format variants, opt-out rules, quality guidelines, migration checklist) fits comfortably in one file.

### Pattern 2: Reference File Loading Convention

**What:** Skills load reference files at runtime via the Read tool. Files should be concise for context efficiency.
**When to use:** All reference files in this project follow this pattern.
**Source:** `references/skill-conventions.md` lines 70-91.

### Pattern 3: Existing Bilingual Patterns to Codify

Three existing implementations establish the patterns the spec will formalize:

**LaTeX variant (translation-skill, SKILL.md lines 145-148):**
```latex
% --- Paragraph 1 ---
% [Chinese text line 1]
% [Chinese text line 2]
English paragraph text here.

% --- Paragraph 2 ---
% [Chinese text line 2]
English paragraph text here.
```

**Markdown blockquote variant (reviewer-simulation-skill, SKILL.md lines 162-163):**
```markdown
**Problem:** [English description]

**Why this matters:** [English impact statement]

**Suggestion:** [English suggestion]

> **[Chinese]** [Chinese translation of all three parts]
```

**Markdown blockquote variant (logic-skill, SKILL.md line 167):**
```markdown
**Problem:** [English description]
**Why this matters:** [impact]
**Suggestion:** [suggestion]
> **[中文]** 问题：... 为什么重要：... 建议：...
```

**Observation:** The reviewer-skill uses `**[Chinese]**` while logic-skill uses `**[中文]**`. The spec should standardize on one label. Recommendation: use `**[Chinese]**` for consistency with English-language formatting, since the reviewer-skill pattern is more established in the codebase.

### Pattern 4: Spec File Structure (Recommended)

Based on the project's reference file conventions and the CONTEXT.md decisions, the spec should follow this structure:

```markdown
# Bilingual Output Specification

[Quick reference card -- optional, Claude's discretion]

## Format Variants
### LaTeX Comment Format (.tex output)
### Markdown Blockquote Format (.md output)

## When to Use Each Variant

## Paragraph Markers

## File Naming Convention

## Opt-Out Mechanism

## Chinese Translation Quality Guidelines

## Edge Cases

## Migration Checklist (Phase 17)
```

### Anti-Patterns to Avoid

- **Duplicating Skill workflow details:** The spec defines the FORMAT, not the WORKFLOW. Workflow details belong in each Skill's SKILL.md.
- **Over-specifying beyond the two variants:** The CONTEXT.md locks the format to exactly two variants (LaTeX comment, Markdown blockquote). Do not invent additional variants.
- **Making the file too long:** Reference files are loaded at runtime into context. The spec should be concise -- target 80-120 lines.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Bilingual format definition | Custom per-Skill format docs | Single `references/bilingual-output.md` | Eliminates format drift across 7 eligible Skills |
| Opt-out keyword logic | Per-Skill keyword lists | Centralized list in the spec | Consistent opt-out behavior across all Skills |

**Key insight:** The entire purpose of this phase is to prevent hand-rolling: instead of each Skill defining its own bilingual format, one spec file governs all.

## Common Pitfalls

### Pitfall 1: Label Inconsistency Between Reviewer and Logic Skills
**What goes wrong:** The reviewer-skill uses `> **[Chinese]**` while logic-skill uses `> **[中文]**`. If the spec doesn't pick one, Phase 17 will have ambiguity.
**Why it happens:** Skills were authored independently before a shared spec existed.
**How to avoid:** The spec must standardize on exactly one label. Recommend `**[Chinese]**` (matches reviewer-skill, more readable in English-dominant output).
**Warning signs:** If the spec says "use either", Phase 17 will propagate the inconsistency.

### Pitfall 2: Paragraph Marker Format Mismatch
**What goes wrong:** CONTEXT.md specifies `% --- Paragraph N ---` for LaTeX and `<!-- Paragraph N -->` for Markdown. If the spec deviates from these exact formats, existing translation-skill output becomes non-compliant.
**Why it happens:** The translation-skill already uses `% --- Paragraph N ---` (confirmed in SKILL.md line 147). The spec must match exactly.
**How to avoid:** Copy the marker format verbatim from the CONTEXT.md decisions. Verify against translation-skill's existing pattern.
**Warning signs:** Any deviation from the literal string format in the spec.

### Pitfall 3: Scope Creep Into Phase 17 Territory
**What goes wrong:** The spec file tries to modify existing Skills or add bilingual support details to SKILL.md files.
**Why it happens:** Natural temptation to "complete the job" while writing the spec.
**How to avoid:** This phase creates the reference file ONLY. The CONTEXT.md explicitly states: "applying it to existing Skills is Phase 17."
**Warning signs:** Any plan step that involves editing files under `.claude/skills/`.

### Pitfall 4: Overly Long Spec File
**What goes wrong:** The spec becomes a 300+ line document that consumes excessive context when loaded by Skills at runtime.
**Why it happens:** Including too many examples, edge cases, or migration details.
**How to avoid:** Target 80-120 lines. The migration checklist can be a compact table. Two code examples (one per variant) are sufficient.
**Warning signs:** File exceeding 150 lines.

### Pitfall 5: Forgetting the `_bilingual` Suffix Convention for Markdown Output
**What goes wrong:** The CONTEXT.md specifies `_bilingual` suffix for ALL bilingual files, but most existing Markdown Skills (reviewer, logic) write to `_review.md` / `_logic.md` with inline bilingual content rather than separate bilingual files.
**Why it happens:** LaTeX Skills produce separate `_bilingual.tex` files (English-only + bilingual pair), while Markdown Skills embed bilingual content inline.
**How to avoid:** The spec should clarify that the `_bilingual` suffix applies to Skills that produce SEPARATE bilingual output files (translation-skill pattern). Skills that embed bilingual inline (reviewer, logic) keep their existing naming.
**Warning signs:** If the spec mandates `_bilingual` suffix universally, it will conflict with reviewer-skill and logic-skill output patterns.

## Code Examples

### LaTeX Comment Format (from translation-skill, verified)

```latex
% --- Paragraph 1 ---
% 城市热岛效应（urban heat island effect）已成为城市规划和公共健康研究中日益重要的议题。
% 理解街道层面的语义特征如何塑造居民的安全感知，对于循证城市设计至关重要。
The urban heat island effect has become increasingly important in urban planning and public-health research.
Understanding how street-level semantics shape perceived safety is essential for evidence-based urban design.

% --- Paragraph 2 ---
% 然而，现有研究在解释街道层面语义特征与感知安全之间的关系方面仍存在局限。
However, existing studies remain limited in their ability to explain how street-level semantics relate to perceived safety.
```

**Source:** translation-skill SKILL.md lines 145-148, extended with CONTEXT.md terminology handling rules.

### Markdown Blockquote Format (from reviewer-simulation-skill, verified)

```markdown
<!-- Paragraph 1 -->
**Problem:** The Introduction proposes a "multi-scale prediction framework," but Methods describes a single-scale gradient boosting model.

**Why this matters:** Reviewers will note the mismatch between the stated contribution and the actual implementation.

**Suggestion:** Update the Introduction to describe a single-scale model, or add a multi-scale component to Methods.

> **[Chinese]** 问题：引言提出"多尺度预测框架"（multi-scale prediction framework），但方法章节仅描述单尺度梯度提升模型（gradient boosting model）。为什么重要：审稿人会注意到声明贡献与实际实现之间的不一致。建议：修改引言或在方法中补充多尺度组件。
```

**Source:** reviewer-simulation-skill SKILL.md lines 153-163, logic-skill SKILL.md line 167, adapted with CONTEXT.md paragraph markers and terminology handling.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Per-Skill bilingual format | Shared spec in `references/bilingual-output.md` | Phase 13 (this phase) | Eliminates format drift, enables Phase 17 bulk migration |
| No opt-out mechanism | Keyword detection opt-out (default ON) | Phase 11 decision, codified Phase 13 | Users who don't want Chinese can opt out naturally |

**Pre-existing state:**
- `skill-conventions.md` line 65 already references `references/bilingual-output.md` as the format spec (created in Phase 13)
- `skill-skeleton.md` line 135 already cross-references bilingual eligibility
- 7 eligible Skills, 4 exempt (classification done in Phase 11)

## Existing Skill Bilingual Status (Migration Checklist Input)

This table summarizes each eligible Skill's current bilingual support and what Phase 17 will need to add/modify. The spec should include a simplified version of this as the migration checklist.

| Skill | Current Bilingual Support | Output Type | Phase 17 Work Needed |
|-------|--------------------------|-------------|---------------------|
| translation-skill | Full LaTeX bilingual (`_bilingual.tex` with `%` comments, `% --- Paragraph N ---` markers) | LaTeX file | Minimal -- add `references/bilingual-output.md` to `references.required`, verify opt-out keywords |
| reviewer-simulation-skill | Full Markdown bilingual (`> **[Chinese]** ...` inline blockquotes) | Markdown file/conversation | Add `references/bilingual-output.md` to references, standardize label to `**[Chinese]**`, add paragraph markers, add opt-out keywords |
| logic-skill | Full Markdown bilingual (`> **[中文]** ...` inline blockquotes) | Markdown file/conversation | Add `references/bilingual-output.md` to references, change label from `**[中文]**` to `**[Chinese]**`, add paragraph markers, add opt-out keywords |
| polish-skill | No bilingual support currently | In-place edits (LaTeX) / conversation | Add bilingual output variant, add opt-out keywords, add `references/bilingual-output.md` to references |
| de-ai-skill | No bilingual support currently | In-place edits (LaTeX) / conversation | Add bilingual output variant, add opt-out keywords, add `references/bilingual-output.md` to references |
| abstract-skill | No bilingual support currently | Conversation output | Add bilingual output variant (Markdown blockquote), add opt-out keywords, add `references/bilingual-output.md` to references |
| experiment-skill | No bilingual support currently | Conversation / file output | Add bilingual output variant (Markdown blockquote), add opt-out keywords, add `references/bilingual-output.md` to references |

## Opt-Out Keyword Detection (Claude's Discretion Recommendation)

The CONTEXT.md lists: "English only", "no bilingual", "only English". The spec should also include the Chinese variant already listed: "no bilingual".

**Recommended detection rules:**
- Case-insensitive substring match against the user's trigger prompt
- Keywords: `english only`, `no bilingual`, `only english`
- When detected: skip all Chinese output, produce English-only output
- When NOT detected: bilingual ON (default)
- No partial matching -- "English only" must appear as a phrase, not "English-only" as a hyphenated adjective in a different context

## Edge Case Handling (Claude's Discretion Recommendation)

**Mixed Chinese-English input paragraphs:**
- When the input paragraph contains both Chinese and English (common in drafts), treat the entire paragraph as one unit for bilingual comparison
- The English output is the polished/translated version; the Chinese output is the auxiliary reference
- Do not split mixed paragraphs into separate language segments

**Quick reference card:**
Recommend YES -- include a 5-line quick reference card at the top of the spec file. Skills loading this reference at runtime benefit from an immediate summary before diving into details. This follows the pattern of `expression-patterns.md` which has a "Quick Picks" table.

## Open Questions

1. **Paragraph marker necessity for inline-bilingual Skills**
   - What we know: Translation-skill uses `% --- Paragraph N ---` because it produces a separate bilingual file where markers aid navigation. Reviewer-skill and logic-skill embed bilingual inline (after each concern, not as separate paragraphs).
   - What's unclear: Should the spec require `<!-- Paragraph N -->` markers for Skills that already structure output by concern/issue (reviewer, logic)?
   - Recommendation: Make paragraph markers REQUIRED for paragraph-level bilingual files (translation pattern) and OPTIONAL for structured-output Skills (reviewer, logic) where the document structure already provides navigation. The spec should state both cases.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Manual verification (no automated test framework in project) |
| Config file | None -- documentation-only project |
| Quick run command | `cat references/bilingual-output.md` (verify file exists and content is well-formed) |
| Full suite command | Manual: verify spec content against CONTEXT.md decisions, cross-check with existing Skill patterns |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| BILN-02 | Spec defines LaTeX comment + Markdown blockquote variants | manual | Read `references/bilingual-output.md`, verify both variants documented with examples | Wave 0 |
| BILN-03 | Shared reference file exists at correct path | smoke | `test -f references/bilingual-output.md && echo PASS` | Wave 0 |

### Sampling Rate
- **Per task commit:** Verify file exists and is non-empty
- **Per wave merge:** Manual review of spec content against CONTEXT.md decisions
- **Phase gate:** Full manual verification before `/gsd:verify-work`

### Wave 0 Gaps
None -- no test infrastructure needed for a documentation-only phase. Verification is manual file content review.

## Sources

### Primary (HIGH confidence)
- `13-CONTEXT.md` -- All implementation decisions, format rules, and constraints
- `.claude/skills/translation-skill/SKILL.md` lines 145-148 -- Existing LaTeX bilingual pattern
- `.claude/skills/reviewer-simulation-skill/SKILL.md` lines 153-188 -- Existing Markdown blockquote pattern
- `.claude/skills/logic-skill/SKILL.md` lines 140-188 -- Existing Markdown blockquote pattern (variant label)
- `references/skill-conventions.md` lines 56-65 -- Bilingual eligibility classification and reference to `bilingual-output.md`
- `references/skill-skeleton.md` line 135 -- Bilingual eligibility cross-reference

### Secondary (MEDIUM confidence)
- `.claude/skills/polish-skill/SKILL.md` -- No current bilingual support (Phase 17 target)
- `.claude/skills/de-ai-skill/SKILL.md` -- No current bilingual support (Phase 17 target)
- `.claude/skills/abstract-skill/SKILL.md` -- No current bilingual support (Phase 17 target)
- `.claude/skills/experiment-skill/SKILL.md` -- No current bilingual support (Phase 17 target)

### Tertiary (LOW confidence)
None -- all findings verified against primary project sources.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- documentation-only phase, no dependency questions
- Architecture: HIGH -- file location and format confirmed by existing references and CONTEXT.md
- Pitfalls: HIGH -- all pitfalls derived from direct inspection of existing Skill files

**Research date:** 2026-03-18
**Valid until:** 2026-04-17 (stable -- documentation spec, not fast-moving library)
