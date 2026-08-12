# Phase 11: Convention & Tech Debt - Research

**Researched:** 2026-03-17
**Domain:** Skill conventions authoring, tech debt resolution, markdown documentation patterns
**Confidence:** HIGH

## Summary

Phase 11 is a documentation-only phase that updates `references/skill-conventions.md` and verifies two previously-applied code fixes. No new Skills are authored; no runtime code changes. The four requirements (DEBT-01, DEBT-02, DEBT-03, UXFIX-02) decompose into two categories: (1) verify-only items where commit `8492320` already applied the fix (DEBT-02, DEBT-03), and (2) conventions expansion items that add new subsections to `skill-conventions.md` (DEBT-01 enhancement, UXFIX-02 AskUserQuestion enforcement rule, bilingual eligibility classification).

The primary risk is breaking the existing conventions document's coherence or exceeding a manageable length while adding three new pieces of content. The conventions file is currently 199 lines with clear section boundaries using `---` dividers. The additions (escape hatch enhancement, AskUserQuestion enforcement, bilingual eligibility) should add approximately 40-60 lines total, keeping the document well under 300 lines.

**Primary recommendation:** Treat this as a single plan with three editing tasks on `skill-conventions.md` plus two verification checks on existing Skills. The skeleton file (`references/skill-skeleton.md`) may need minor sync updates if conventions add new fields or section expectations.

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions

**AskUserQuestion Enforcement Rule (UXFIX-02):**
- Per-Skill audit approach: Each Skill's `## Ask Strategy` section declares which questions use AskUserQuestion vs plain text. No blanket mandate -- authors decide per-Skill based on interaction needs
- Placement: Expand existing `## Ask Strategy Conventions` section in `skill-conventions.md` to include AskUserQuestion enforcement subsection
- Direct-mode exemption: In direct mode, Skills skip all AskUserQuestion calls entirely. User chose direct = they want speed. Proceed with defaults and inferred context
- Examples format: Include 1 good/bad comparison showing correct AskUserQuestion invocation vs the anti-pattern (plain dialogue for multi-option questions)

**Bilingual Output Scope Categories:**
- Classification rule: Based on `output_contract` type -- Skills that produce academic text support bilingual; pure analysis/recommendation/citation Skills are exempt
- Placement: Expand `Output Contract` description in Body Structure table area with a bilingual eligibility subsection
- Default behavior: Bilingual output ON by default for eligible Skills. Users can opt out, but the default serves Chinese-primary users
- Exempt Skills: caption-skill (English-only captions), cover-letter-skill (journal-specific format), visualization-skill (recommendation-only), literature-skill (BibTeX output)
- Eligible Skills: translation-skill, polish-skill, de-ai-skill, reviewer-skill, abstract-skill, experiment-skill, logic-skill (7 total)

**Already-Fixed Debt Items (DEBT-02, DEBT-03):**
- Approach: Verify fixes from commit `8492320` are still correct during execution, then mark as complete. No rework needed
- DEBT-02: `literature-skill` tools field already uses `External MCP` -- verify only
- DEBT-03: `cover-letter-skill` required field already lists `references/journals/ceus.md` -- verify only

**Escape Hatch Documentation (DEBT-01):**
- Approach: Enhance existing line 73 text in skill-conventions.md to include specific Skill name references (logic-skill, visualization-skill, literature-skill) instead of only generic category descriptions
- Keep as inline rule, not a full subsection -- current format is clear enough

### Claude's Discretion

- Exact wording and formatting of the AskUserQuestion good/bad comparison example
- How to phrase bilingual eligibility rule (table vs prose)
- Whether to add batch-mode note alongside direct-mode exemption

### Deferred Ideas (OUT OF SCOPE)

None -- discussion stayed within phase scope.

</user_constraints>

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DEBT-01 | skill-conventions.md documents escape hatch for Skills with `required: []` | Current line 73 already has the rule. Enhancement adds specific Skill names (logic-skill, visualization-skill, literature-skill) as concrete examples. Research confirms all three Skills use `required: []` correctly. |
| DEBT-02 | literature-skill uses capability category "External MCP" instead of vendor-specific "Semantic Scholar MCP" | **Already fixed in commit 8492320.** Verified: line 16 of literature-skill SKILL.md reads `- External MCP`. Verify-only task. |
| DEBT-03 | cover-letter-skill moves CEUS from leaf_hints to required | **Already fixed in commit 8492320.** Verified: line 22 of cover-letter-skill SKILL.md reads `- references/journals/ceus.md` under `required:`. Verify-only task. |
| UXFIX-02 | skill-conventions.md updated with AskUserQuestion enforcement rule and invocation examples | New subsection under existing `## Ask Strategy Conventions` (lines 159-177). Must include: per-Skill audit approach, direct-mode exemption, good/bad comparison example. |

</phase_requirements>

## Standard Stack

This phase does not involve any libraries, frameworks, or packages. It is purely a markdown documentation editing phase.

### Core

| Tool | Purpose | Why Standard |
|------|---------|--------------|
| Markdown | All conventions and skill files use markdown format | Project standard since Phase 2 |
| YAML frontmatter | Skill metadata format | Defined by skill-conventions.md |
| Git | Version control and commit verification | Standard VCS |

### Files Modified

| File | Change Type | Current Lines |
|------|------------|---------------|
| `references/skill-conventions.md` | Edit (3 additions) | 199 |
| `references/skill-skeleton.md` | Possible sync edit | 155 |
| `.claude/skills/literature-skill/SKILL.md` | Verify only (no edit) | 226 |
| `.claude/skills/cover-letter-skill/SKILL.md` | Verify only (no edit) | 220 |

## Architecture Patterns

### Current Document Structure

```
references/skill-conventions.md (199 lines)
├── ## Frontmatter Contract          (lines 9-31)
├── ## Body Structure                (lines 34-55)
├── ## Reference Loading Rules       (lines 58-80)
├── ## Interaction Modes             (lines 82-101)
├── ## Fallback Rules                (lines 104-131)
├── ## Line Budget                   (lines 134-156)
├── ## Ask Strategy Conventions      (lines 159-177)  ← UXFIX-02 goes here
├── ## Naming and Discovery          (lines 182-186)
└── ## Maintenance Rules             (lines 190-195)
```

### Pattern 1: Section Expansion (not new section)

**What:** Add content within existing sections rather than creating new top-level `##` sections.
**When to use:** When the new content is a sub-topic of an existing convention area.
**Rationale:** The CONTEXT.md explicitly states that DEBT-01 stays as inline rule and UXFIX-02 expands the existing Ask Strategy section. Bilingual eligibility goes under Body Structure near Output Contract.

### Pattern 2: Inline Enhancement vs. Subsection

**What:** For DEBT-01 (escape hatch), the user decided to enhance the existing bullet point at line 73 rather than creating a new subsection. The enhancement adds concrete Skill name references.
**How:** Modify the existing bullet to include `(e.g., `logic-skill`, `visualization-skill`, `literature-skill`)` alongside the generic category descriptions already present.

### Pattern 3: Good/Bad Comparison Example

**What:** For UXFIX-02, include one good/bad comparison showing correct AskUserQuestion invocation vs. the anti-pattern.
**Format convention:** The project uses `> Example:` blockquotes in the skeleton and inline code fences in conventions. A good/bad comparison should use clearly labeled code blocks.

### Anti-Patterns to Avoid

- **Over-expanding sections:** Adding too many sub-subsections that bloat the document. The user explicitly said "Keep as inline rule" for DEBT-01.
- **Blanket mandates:** The AskUserQuestion enforcement must NOT be a blanket "all Skills must use AskUserQuestion." It must be per-Skill audit approach where each Skill's `## Ask Strategy` section declares its own approach.
- **Vendor-specific tool names:** Never reference `mcp_question` in new convention text. Use `AskUserQuestion` (Claude Code's actual built-in tool name).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| AskUserQuestion schema documentation | Custom schema spec | Reference Claude Code's built-in tool | The schema (`question`, `options` array with `label`/`description`, `multiSelect` boolean) is defined by Claude Code itself. Conventions should describe *when* to use it, not redefine the schema. |
| Bilingual eligibility table | Complex decision tree | Simple output_contract classification rule | The rule is straightforward: if `output_contract` produces academic text, bilingual eligible. The user already enumerated the 4 exempt and 7 eligible Skills. |

## Common Pitfalls

### Pitfall 1: Breaking Existing Convention Coherence

**What goes wrong:** New subsections disrupt the reading flow or introduce conflicting guidance with existing sections.
**Why it happens:** Adding content without re-reading the full document for consistency.
**How to avoid:** Read the entire `skill-conventions.md` before and after editing. Ensure new content references existing sections where appropriate (e.g., AskUserQuestion enforcement should cross-reference the existing Fallback Rules section at lines 108-114 which already mentions AskUserQuestion fallback).
**Warning signs:** Two sections giving different guidance about the same topic.

### Pitfall 2: AskUserQuestion vs. Structured Interaction Confusion

**What goes wrong:** Conflating the capability category name (`Structured Interaction`) used in frontmatter `tools:` lists with the actual Claude Code tool name (`AskUserQuestion`) used in workflow instructions.
**Why it happens:** The project uses two naming layers: capability categories in frontmatter (generic, tool-agnostic) and actual tool names in body/workflow sections (specific to Claude Code).
**How to avoid:** Conventions should clarify the distinction:
- Frontmatter `tools:` field lists `Structured Interaction` (capability category per existing convention rule at line 29)
- Body `## Ask Strategy` and `## Workflow` sections reference `AskUserQuestion` (actual Claude Code tool name)
- Fallback sections describe behavior when `AskUserQuestion` is unavailable
**Warning signs:** Conventions using `AskUserQuestion` in frontmatter rules or `Structured Interaction` in workflow instructions.

### Pitfall 3: Skeleton Desync

**What goes wrong:** Updating conventions without checking if `skill-skeleton.md` needs corresponding updates.
**Why it happens:** Forgetting that the skeleton is a companion document that must stay in sync (stated in conventions line 194).
**How to avoid:** After editing conventions, review `skill-skeleton.md` for any sections that should reflect new rules. For this phase: the skeleton's `## Ask Strategy` example (lines 90-101) may need a note about AskUserQuestion enforcement, and the `## Output Contract` area may need a bilingual eligibility note.
**Warning signs:** New Skill authors using the skeleton and missing newly added conventions.

### Pitfall 4: Verify-Only Items Getting Accidentally Modified

**What goes wrong:** While verifying DEBT-02 and DEBT-03, accidentally making edits to those files.
**Why it happens:** Opening a file for verification and making "improvements" while there.
**How to avoid:** Verification tasks should be read-only. Use `Read` tool, confirm the correct content, report verification result. Do not edit.
**Warning signs:** Git diff showing changes to `literature-skill/SKILL.md` or `cover-letter-skill/SKILL.md` after this phase.

## Code Examples

### Example 1: Current Escape Hatch Text (Line 73, to be enhanced for DEBT-01)

```markdown
- **`required: []` is acceptable** only for self-contained Skills that produce no written academic text and load no local reference files by design. Qualifying cases: pure analysis Skills (e.g., logic checking), pure recommendation Skills (e.g., chart type suggestions), and external-MCP-only Skills (e.g., literature search). The `## References` body section must document why no reference loading is needed.
```

**Enhancement target:** Add specific Skill names in parentheses alongside the generic category descriptions. Change to include `logic-skill`, `visualization-skill`, `literature-skill` as concrete references.

### Example 2: AskUserQuestion Good/Bad Comparison (for UXFIX-02)

This is the good/bad example format that should be added to the Ask Strategy Conventions section. The wording is at Claude's discretion, but the structure should follow this pattern:

```markdown
### AskUserQuestion Enforcement

#### Good: Structured question for multi-option selection
Use AskUserQuestion when the user must choose between 2-4 discrete options:

AskUserQuestion({
  question: "Which section should I polish first?",
  options: [
    { label: "Abstract", description: "Full abstract rewrite with word count check" },
    { label: "Introduction", description: "Logic flow and contribution statement" },
    { label: "Methods", description: "Technical accuracy and reproducibility" }
  ]
})

#### Bad: Plain dialogue for multi-option questions
Do NOT present options as numbered plain text when AskUserQuestion is available:

"Which section should I polish first?
1. Abstract
2. Introduction
3. Methods
Please type the number."
```

### Example 3: Bilingual Eligibility Classification (for conventions)

This subsection should appear near the Output Contract description in Body Structure:

```markdown
### Bilingual Output Eligibility

Skills are classified as bilingual-eligible based on their `output_contract` type:

| Eligibility | Skills | Reason |
|------------|--------|--------|
| Eligible (default ON) | translation, polish, de-ai, reviewer-simulation, abstract, experiment, logic | Produces academic text where Chinese comparison aids the user |
| Exempt | caption, cover-letter, visualization, literature | English-only captions, journal-specific format, recommendation-only, BibTeX output |

Eligible Skills support bilingual paragraph-by-paragraph comparison output. Bilingual mode is ON by default; users may opt out.
```

### Example 4: Verification Evidence for DEBT-02

```
literature-skill/SKILL.md line 16:
tools:
  - External MCP        ← CORRECT (was "Semantic Scholar MCP" before commit 8492320)
  - Structured Interaction
```

### Example 5: Verification Evidence for DEBT-03

```
cover-letter-skill/SKILL.md lines 20-23:
references:
  required:
    - references/journals/ceus.md    ← CORRECT (was in leaf_hints before commit 8492320)
  leaf_hints: []
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `mcp_question` tool name | `AskUserQuestion` (Claude Code built-in) | Claude Code v2.0.21 (late 2025) | Legacy paper-polish-workflow SKILL.md is broken; Phase 12 fixes the actual code, Phase 11 documents the convention |
| Vendor-specific tool names in frontmatter | Capability categories (`Structured Interaction`, `External MCP`, `PDF Analysis`) | v1.0 Phase 2 (2026-03-11) | All 11 Skills now use capability categories; this is established project convention |
| No `required: []` escape hatch | Documented escape hatch at line 73 | v1.0 commit 8492320 (2026-03-13) | Phase 11 enhances with Skill name references |

## AskUserQuestion Technical Reference

### Tool Name
`AskUserQuestion` -- Claude Code's built-in structured interaction tool.

### Schema (from project FEATURES.md research, verified)
```
AskUserQuestion({
  question: string,           // The question text
  options: [                   // 2-4 options
    {
      label: string,           // Short option label
      description: string      // Longer description
    }
  ],
  multiSelect: boolean         // Optional: allow multiple selections (default: false)
})
```

### Key Behaviors
- Users always get an "Other" option automatically (do not add manually)
- The tool presents a timed multiple-choice interface in Claude Code UI
- Cannot be used from sub-agents (only main Claude can ask questions)
- When unavailable, Skills must fall back to 1-3 plain-text questions (existing convention at lines 108-114)

### Naming Layers in This Project
| Layer | Name | Where Used |
|-------|------|------------|
| Capability category | `Structured Interaction` | Frontmatter `tools:` field |
| Actual tool name | `AskUserQuestion` | Body sections (`## Ask Strategy`, `## Workflow`, `## Fallbacks`) |
| Legacy wrong name | `mcp_question` | Only in `paper-polish-workflow/SKILL.md` (Phase 12 will fix) |

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Manual verification (no automated test framework in project) |
| Config file | none |
| Quick run command | `git diff --name-only` (verify only expected files changed) |
| Full suite command | Manual review of conventions document + skill file verification |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DEBT-01 | Escape hatch documents Skill names | manual | `grep -n "logic-skill\|visualization-skill\|literature-skill" references/skill-conventions.md` | N/A (doc edit) |
| DEBT-02 | literature-skill uses External MCP | manual | `grep "External MCP" .claude/skills/literature-skill/SKILL.md` | Already verified |
| DEBT-03 | cover-letter-skill lists CEUS in required | manual | `grep -A2 "required:" .claude/skills/cover-letter-skill/SKILL.md` | Already verified |
| UXFIX-02 | AskUserQuestion enforcement rule exists | manual | `grep -c "AskUserQuestion" references/skill-conventions.md` (should be >= 3) | N/A (doc edit) |

### Sampling Rate
- **Per task commit:** `git diff` to verify only expected files changed
- **Per wave merge:** Full read of `references/skill-conventions.md` for coherence
- **Phase gate:** Manual checklist against 4 success criteria from ROADMAP

### Wave 0 Gaps
None -- this phase is documentation-only with no test infrastructure to set up. Verification is via grep commands and manual review.

## Open Questions

1. **Should `skill-skeleton.md` be updated in this phase?**
   - What we know: Conventions line 194 says "Keep the example skeleton in sync with this document." The skeleton currently has no mention of AskUserQuestion enforcement or bilingual eligibility.
   - What's unclear: Whether the skeleton needs these additions or if they are "conventions-only" rules that don't need skeleton representation.
   - Recommendation: Add minimal notes to skeleton's Ask Strategy and Output Contract sections. The skeleton is 155 lines and has room. But keep additions brief (1-2 lines each) since the skeleton is meant to be a copyable starting point, not a full rule set.

2. **Should batch-mode note accompany the direct-mode exemption?**
   - What we know: The CONTEXT.md lists this as Claude's discretion. Batch mode (line 94 of conventions) is "same operation across multiple inputs, minimal per-item interaction."
   - What's unclear: Whether batch mode should also skip AskUserQuestion calls.
   - Recommendation: Yes, add a brief note. Batch mode is semantically similar to direct mode in terms of interaction minimization. A one-line addition: "In `batch` mode, AskUserQuestion calls are also skipped; settings from the first item apply to all subsequent items."

## Sources

### Primary (HIGH confidence)
- `references/skill-conventions.md` -- Full read, 199 lines, all section boundaries mapped
- `references/skill-skeleton.md` -- Full read, 155 lines
- `.claude/skills/literature-skill/SKILL.md` -- Full read, DEBT-02 fix verified at line 16
- `.claude/skills/cover-letter-skill/SKILL.md` -- Full read, DEBT-03 fix verified at line 22
- `.claude/skills/logic-skill/SKILL.md` -- Full read, `required: []` escape hatch example confirmed
- `.claude/skills/visualization-skill/SKILL.md` -- Full read, `required: []` escape hatch example confirmed
- Git commit `8492320` -- Diff reviewed, confirms DEBT-02/DEBT-03/DEBT-01 fixes applied
- `.planning/research/FEATURES.md` -- AskUserQuestion schema at TS-5 section (line 64)
- `.planning/research/ARCHITECTURE.md` -- AskUserQuestion fix strategy at lines 354-387
- `.planning/ROADMAP.md` -- Phase 11 success criteria and dependency chain

### Secondary (MEDIUM confidence)
- [Claude Code AskUserQuestion blog](https://torqsoftware.com/blog/2026/2026-01-14-claude-ask-user-question/) -- General behavior description, no schema details
- [ClaudeLog AskUserQuestion FAQ](https://claudelog.com/faqs/what-is-ask-user-question-tool-in-claude-code/) -- Confirms tool name and basic interaction model
- [Claude API docs on user input](https://platform.claude.com/docs/en/agent-sdk/user-input) -- SDK integration perspective

### Tertiary (LOW confidence)
None -- all findings verified against project source files.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- no libraries involved, purely documentation editing
- Architecture: HIGH -- all edit locations precisely identified with line numbers in existing files
- Pitfalls: HIGH -- based on direct analysis of existing document structure and project patterns
- AskUserQuestion schema: MEDIUM -- verified against project's own FEATURES.md research but not against live Claude Code source

**Research date:** 2026-03-17
**Valid until:** 2026-04-17 (stable -- conventions are project-internal, not dependent on external library versions)
