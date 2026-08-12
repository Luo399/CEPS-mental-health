# Phase 14: Repo-to-Paper Core Structure - Research

**Researched:** 2026-03-18
**Domain:** Claude Code Skill creation (multi-checkpoint workflow), Python ML repo analysis, academic paper outlining
**Confidence:** HIGH

## Summary

Phase 14 creates two artifacts: (1) a new `repo-to-paper-skill/SKILL.md` with a multi-checkpoint workflow (scan repo, generate H1, generate H2, generate H3 with user approval between each layer), and (2) a `references/repo-patterns.md` reference file containing scan heuristics and section mapping rules. Both are pure markdown files following established project conventions. No external libraries, build steps, or tooling are involved.

The technical challenge is not in any external technology but in **Skill design under a tight line budget** (~300 lines, with acknowledged flexibility to ~320). The experiment-skill (230 lines, two-phase checkpoint) is the closest existing pattern reference. The repo-to-paper Skill has four checkpoints (scan summary + three heading levels), which is significantly more complex. Keeping the workflow concise while remaining unambiguous is the primary authoring challenge.

**Primary recommendation:** Model the repo-to-paper Skill directly on the experiment-skill two-phase pattern, but extend it to four phases (Scan, H1, H2, H3). Extract ALL scan heuristics and file-to-section mapping rules into `references/repo-patterns.md` to keep the Skill body lean. Use `references/bilingual-output.md` (~95 lines) as the structural model for `repo-patterns.md` (~100 lines target).

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **Scan method**: Directory structure inference based on common Python ML project patterns defined in `references/repo-patterns.md`
- **Scan depth**: Only top 2 levels of directories (root + first-level subdirectories). User can manually specify deeper paths if needed
- **Result presentation**: Categorized summary table -- files grouped by category (documentation, config, results, code, figures, dependencies), each listing key files and brief content description
- **Missing files**: Warn + continue. Mark missing items in scan summary but proceed with outline generation using available information. Missing sections get placeholder markers
- **Interaction method**: Plain text display + confirmation. Output the outline as formatted text; user replies "ok" to proceed or describes modifications needed. AskUserQuestion is NOT used for outline review (too complex for option boxes)
- **Modification loop**: On user feedback, directly modify the outline and re-display for confirmation. Loop until user is satisfied -- no iteration limit
- **Generation cascade**: Layer-by-layer full generation. All H1 first -> user confirms -> all H2 for all sections -> user confirms -> all H3 -> user confirms. User sees the full picture at each layer before judging
- **Detail level**: Title + one-sentence description at each level. Concise but sufficient for judging structure
- **H1 source**: Journal template (if specified) provides standard section structure, adjusted based on repo content. Default to generic IMRaD (Introduction, Methods, Results and Discussion, Conclusion) when no journal specified
- **H2/H3 source**: Read actual file contents (README, config files, result files) to generate more accurate sub-headings. H1 only needs directory structure
- **Mapping rules**: Defined in `references/repo-patterns.md` -- file categories map to paper sections
- **Source annotation**: H2/H3 entries annotated with inference source -- e.g., `<- from: config.yaml, results/table1.csv`
- **repo-patterns.md content**: Two parts -- (1) file type identification patterns (glob -> category -> priority table), (2) category to paper section mapping rules table
- **repo-patterns.md format**: Markdown tables for both parts, with Notes columns for rationale
- **repo-patterns.md scope**: Python ML projects only (v2.0). Non-Python support deferred per ADVR-01
- **repo-patterns.md size**: ~100 lines, single flat file

### Claude's Discretion
- Exact file patterns in repo-patterns.md (which globs to include)
- How to handle ambiguous file categories (e.g., a Jupyter notebook that contains both code and results)
- Skill frontmatter field values (triggers, tools, references)
- Whether to include a "Scan Summary" confirmation step before proceeding to H1 generation
- Workflow step naming and sub-step distribution within ~300-line Skill budget

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| REPO-01 | User can point Skill to an experiment repo and get automatic full scan identifying valuable files (README, configs, results, code) | Scan workflow design pattern, file categorization heuristics in repo-patterns.md, categorized summary table format |
| REPO-02 | User can generate H1 (section) headings from repo analysis and review/approve before proceeding | IMRaD default structure, journal template loading for H1, checkpoint interaction pattern from experiment-skill |
| REPO-03 | User can generate H2 (subsection) headings with detailed outlines and review/approve before proceeding | Content-reading strategy for H2, source annotation pattern, modification loop design |
| REPO-05 | User can generate H3 headings and review/approve before proceeding | Same checkpoint pattern as H2, deeper content analysis strategy |
| REPO-08 | Repo scan heuristics extracted to reference file `references/repo-patterns.md` for maintainability | bilingual-output.md as structural model, two-table design (patterns + mappings), ~100 line budget |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Pure Markdown SKILL.md | N/A | Skill definition file | Project convention -- no build steps, no npm packages |
| Pure Markdown reference file | N/A | `repo-patterns.md` scan heuristics | Matches `bilingual-output.md` pattern exactly |
| YAML frontmatter | N/A | Skill metadata | Required by `skill-conventions.md` |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `references/journals/ceus.md` | N/A | Journal template for H1 structure | When user specifies CEUS as target journal |
| `references/bilingual-output.md` | N/A | Bilingual output format | Repo-to-paper is bilingual-eligible (produces academic text) |
| `references/skill-conventions.md` | N/A | Authoring rules | Must-follow during Skill creation |
| `references/skill-skeleton.md` | N/A | Copyable skeleton template | Starting point for SKILL.md creation |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Markdown tables in repo-patterns.md | YAML/JSON config | Markdown is project convention; YAML would break pattern. Markdown is readable but less machine-parseable -- acceptable since Claude reads it as prose |
| IMRaD default | Custom default structure | IMRaD is the universal academic standard; custom would confuse users. User locked this decision |

**Installation:** None required. Pure markdown project.

## Architecture Patterns

### Recommended Project Structure
```
.claude/skills/repo-to-paper-skill/
  SKILL.md                          # ~300-320 lines, multi-checkpoint workflow

references/
  repo-patterns.md                  # ~100 lines, scan heuristics + section mapping
  bilingual-output.md               # (existing) bilingual format spec
  journals/ceus.md                  # (existing) journal template
  skill-conventions.md              # (existing) authoring rules
  skill-skeleton.md                 # (existing) skeleton template
```

### Pattern 1: Multi-Checkpoint Workflow (extended from experiment-skill)
**What:** A Skill with 4 sequential phases, each requiring user confirmation before proceeding to the next. This extends the experiment-skill's 2-phase pattern (Phase 1: analyze -> confirm -> Phase 2: generate).
**When to use:** When output quality depends on user validation of intermediate structure before investing in deeper generation.

The experiment-skill pattern:
```
Phase 1: Analyze Results -> Present Finding List -> User Confirms
Phase 2: Generate Discussion -> Present Paragraphs -> Done
```

Extended to repo-to-paper (4 phases):
```
Step 1: Scan Repo -> Present Categorized Summary -> [Optional: User Reviews Scan]
Step 2: Generate H1 -> Present H1 Outline -> User Confirms
Step 3: Generate H2 -> Present H2 Outline -> User Confirms
Step 4: Generate H3 -> Present H3 Outline -> User Confirms
```

**Key design constraint:** Each phase must be described concisely. The experiment-skill uses ~60 lines for its two-phase workflow section. With four phases, the repo-to-paper workflow section could easily balloon to ~120+ lines. Keeping each phase to ~25 lines average is essential.

### Pattern 2: Reference File as Configuration (from bilingual-output.md)
**What:** A standalone markdown file that acts as a runtime-loaded "config" for a Skill. The Skill reads it via the Read tool at execution time.
**When to use:** When scan heuristics, mapping rules, or format specifications should be maintainable independently from the Skill logic.

bilingual-output.md structure (model for repo-patterns.md):
```markdown
# Title
Quick Reference (summary table)
Format Variants (detailed specs)
When to Use Each
Edge Cases
```

repo-patterns.md should follow a similar structure:
```markdown
# Repo Scan Patterns
Quick Reference (file category summary)
Part 1: File Identification Patterns (glob -> category -> priority table)
Part 2: Section Mapping Rules (category -> paper section table)
Edge Cases / Ambiguity Rules
```

### Pattern 3: Plain Text Confirmation (no AskUserQuestion)
**What:** For complex structured output like outlines, present as formatted text and await user reply of "ok" or modification instructions.
**When to use:** When the output is too complex for option boxes (>4 options, hierarchical structure, multi-line content).

This is a locked decision. The Skill must NOT use AskUserQuestion for outline review. It should use AskUserQuestion only for pre-workflow questions (journal selection, etc.) per the skill-conventions.md rules.

### Pattern 4: Source Annotation on H2/H3
**What:** Each H2/H3 heading includes an annotation showing which repo files informed its generation.
**When to use:** Always for H2 and H3 entries.
**Example:**
```
### 3.1 Gradient Boosting Model Configuration  <- from: config.yaml, src/model.py
    Configuration details for the XGBoost model including hyperparameters and feature selection strategy.
```

### Anti-Patterns to Avoid
- **Hardcoding scan heuristics in SKILL.md:** All file patterns and mapping rules belong in `repo-patterns.md`. The Skill body should only describe the workflow steps, not list file globs.
- **Deep nesting in workflow description:** Each phase should be flat (Step 1, Step 2, Step 3), not deeply nested sub-sub-steps. The experiment-skill achieves this well.
- **Blocking on missing files:** The user decided "warn + continue." Never stop the workflow because README.md is missing. Mark gaps and proceed.
- **Using AskUserQuestion for outline review:** Explicitly locked out. Plain text display + confirmation only.
- **Generating H2/H3 from directory structure alone:** H1 uses directory structure. H2/H3 must read actual file contents (README, config, results) per user decision.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Skill structure/format | Custom layout | `references/skill-skeleton.md` template | Convention compliance, proven pattern |
| Journal section structure | Custom H1 defaults | `references/journals/ceus.md` + IMRaD fallback | Journal templates are maintained separately |
| Bilingual output format | Custom bilingual format | `references/bilingual-output.md` spec | Standardized in Phase 13 |
| File categorization logic | Inline pattern lists | `references/repo-patterns.md` reference file | Maintainability, separation of concerns |

**Key insight:** This phase is about Skill authoring, not coding. The "don't hand-roll" principle means: don't inline reference content, don't reinvent patterns that exist in conventions, and don't duplicate journal template structure.

## Common Pitfalls

### Pitfall 1: Line Budget Overflow
**What goes wrong:** The four-phase workflow description exceeds 300 lines, making the Skill too long to be context-efficient.
**Why it happens:** Each phase has scan/generate/present/confirm sub-steps. Four phases times ~30 lines each = 120 lines for workflow alone, plus frontmatter (~35 lines), plus all other required sections (~100+ lines).
**How to avoid:** (1) Extract ALL heuristics to repo-patterns.md. (2) Keep each workflow phase to 15-25 lines. (3) Use shared patterns across phases (e.g., "same confirmation loop as Step 2") rather than repeating. (4) Accept ~320 lines as justified per STATE.md risk note.
**Warning signs:** Workflow section exceeding 100 lines; any single phase exceeding 30 lines.

### Pitfall 2: Scan Heuristics Too Rigid or Too Loose
**What goes wrong:** File categorization patterns either miss common ML files (too rigid) or miscategorize ambiguous files (too loose).
**Why it happens:** Python ML repos vary widely in structure. Some use `src/`, some use flat structure, some use `experiments/`, some use `runs/`.
**How to avoid:** (1) Categorize by file extension AND directory name patterns. (2) Include priority ordering so a file matching multiple categories gets assigned to the most specific one. (3) Document ambiguity rules (e.g., Jupyter notebooks: categorize as "code" unless in a `results/` or `figures/` directory).
**Warning signs:** Test against 2-3 mental models of typical repos during authoring.

### Pitfall 3: H1 Rigidity vs Flexibility Mismatch
**What goes wrong:** When CEUS is specified, the Skill rigidly applies CEUS sections even when repo content doesn't map cleanly. Or vice versa: without a journal, generic IMRaD doesn't capture the repo's actual structure.
**Why it happens:** Tension between journal template requirements and repo content reality.
**How to avoid:** (1) H1 starts from journal template or IMRaD as base. (2) Adjustments allowed based on repo scan (e.g., adding "Study Area" section if spatial data detected). (3) User confirms H1 before proceeding, so mismatches are caught early.
**Warning signs:** H1 output that has sections with no corresponding repo content, or repo content with no matching section.

### Pitfall 4: Source Annotation Noise
**What goes wrong:** Every H2/H3 entry has 5+ source files listed, making annotations useless as navigation aids.
**Why it happens:** Many files contribute loosely to each section. Without filtering, everything is annotated.
**How to avoid:** Limit source annotations to the 1-3 most directly relevant files. Use the highest-priority files per the repo-patterns.md priority ordering.
**Warning signs:** Annotations longer than the heading text itself.

### Pitfall 5: Forgetting Bilingual Eligibility
**What goes wrong:** The Skill produces outlines and heading descriptions but doesn't support bilingual output, even though it generates academic text.
**Why it happens:** Outlines feel like "structure" not "academic text," so bilingual seems inapplicable.
**How to avoid:** The one-sentence descriptions at each heading level ARE academic text. The Skill should be bilingual-eligible. Add `references/bilingual-output.md` to required references, support opt-out keywords, and apply bilingual format to the one-sentence descriptions.
**Warning signs:** `output_contract` containing academic text types without bilingual eligibility declared.

## Code Examples

Verified patterns from existing project files:

### Frontmatter Template (adapted from experiment-skill)
```yaml
---
name: repo-to-paper-skill
description: >-
  Scan an experiment repo and generate a complete paper outline (H1/H2/H3)
  with user approval checkpoints at each level. Python ML repos.
  扫描实验仓库，逐级生成论文大纲（H1/H2/H3），每级用户确认后推进。
triggers:
  primary_intent: generate paper outline from experiment repo
  examples:
    - "Generate a paper outline from my repo"
    - "帮我从实验仓库生成论文大纲"
    - "Scan my project and create paper structure"
    - "把我的代码仓库转成论文框架"
tools:
  - Read
  - Write
  - Structured Interaction
references:
  required:
    - references/repo-patterns.md
    - references/bilingual-output.md
  leaf_hints:
    - references/journals/ceus.md
input_modes:
  - repo_path
output_contract:
  - paper_outline
  - scan_summary
---
```

### repo-patterns.md Structure (modeled on bilingual-output.md)
```markdown
# Repo Scan Patterns

Scan heuristics for Python ML experiment repositories.

## File Identification Patterns

| Glob | Category | Priority | Notes |
|------|----------|----------|-------|
| `README.md`, `README.rst` | documentation | 1 | Primary project description |
| `*.yaml`, `*.yml`, `*.json`, `*.toml`, `*.ini`, `*.cfg` | config | 2 | Hyperparameters, experiment settings |
| `*.csv`, `*.xlsx`, `*.tsv`, `results/**` | results | 3 | Experiment output data |
| `*.py`, `*.ipynb` | code | 4 | Source code and notebooks |
| `*.png`, `*.jpg`, `*.svg`, `*.pdf`, `figures/**` | figures | 5 | Visualizations |
| `requirements.txt`, `setup.py`, `pyproject.toml`, `Pipfile` | dependencies | 6 | Environment specification |

## Category to Paper Section Mapping

| Category | Primary Section | Secondary Section | Notes |
|----------|----------------|-------------------|-------|
| documentation | Introduction | Methods | README often describes both motivation and approach |
| config | Methods | - | Hyperparameters, model architecture choices |
| results | Results and Discussion | - | Tables, metrics, evaluation outputs |
| code | Methods | - | Algorithm implementation details |
| figures | Results and Discussion | - | Visualizations of findings |
| dependencies | Methods | - | Technology stack and reproducibility |

## Ambiguity Rules
...
```

### Workflow Phase Pattern (following experiment-skill)
```markdown
### Step 2: Generate H1 Outline

**Prepare:**
- If journal specified, load `references/journals/[journal].md` for section structure
- If no journal, use IMRaD default: Introduction, Methods, Results and Discussion, Conclusion
- Adjust sections based on scan summary (e.g., add "Study Area" if spatial data detected)

**Present:**
- Display H1 headings with one-sentence descriptions
- Format: `# 1. Introduction\n    Establish research context and contribution.`
- Wait for user confirmation ("ok") or modification instructions

**On modification:** Revise and re-display. Loop until confirmed.
```

### Confirmation Loop Pattern (from experiment-skill)
```markdown
Summary line: "Generated N H1 sections. Please confirm, modify, or add before proceeding to H2."
- Wait for user approval before proceeding
```

Source: `.claude/skills/experiment-skill/SKILL.md` lines 134-141

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Single-pass paper outline generation | Multi-checkpoint layered generation (H1->H2->H3) | This phase | User validates structure at each level, preventing cascading errors |
| Inline heuristics in Skill | External reference file (`repo-patterns.md`) | This phase | Maintainable, testable, swappable |
| AskUserQuestion for all confirmations | Plain text + "ok" for complex outputs | Phase 12 / this phase | Better UX for hierarchical content review |

**Deprecated/outdated:**
- None for this phase. This is new Skill creation, not updating existing artifacts.

## Open Questions

1. **Include a Scan Summary confirmation step?**
   - What we know: CONTEXT.md lists this as Claude's discretion. The user sees the categorized file summary before H1 generation.
   - What's unclear: Whether the scan summary should be a formal checkpoint (user must say "ok") or just informational display before auto-proceeding to H1.
   - Recommendation: Include it as an optional confirmation. Display the scan summary and then immediately say "Proceeding to H1 generation..." unless the user interrupts. This avoids an unnecessary "ok" step for simple repos while allowing intervention for complex ones.

2. **Jupyter notebook dual categorization**
   - What we know: Notebooks can contain both code and results. CONTEXT.md lists this as Claude's discretion.
   - What's unclear: Whether to categorize by directory location or by content inspection.
   - Recommendation: Categorize by directory first (notebook in `results/` = results, in `notebooks/exploration/` = code). If directory is ambiguous (root level), default to "code" category with a note "(may contain results)".

3. **Bilingual output scope for outlines**
   - What we know: The Skill produces "paper_outline" which includes one-sentence descriptions at each heading level. These descriptions are academic text.
   - What's unclear: Should bilingual apply to just the descriptions, or also to the heading titles themselves?
   - Recommendation: Bilingual applies to one-sentence descriptions only. Heading titles stay English-only (they are structural, not prose). This keeps bilingual overhead manageable.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Manual verification (pure markdown project, no automated test framework) |
| Config file | none |
| Quick run command | Visual inspection + line count verification |
| Full suite command | Structural checklist (see below) |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REPO-01 | Skill scans repo and produces categorized summary | manual | Visual inspection of SKILL.md workflow Step 1 | N/A (manual) |
| REPO-02 | Skill generates H1 with user checkpoint | manual | Visual inspection of SKILL.md workflow Step 2 | N/A (manual) |
| REPO-03 | Skill generates H2 with user checkpoint | manual | Visual inspection of SKILL.md workflow Step 3 | N/A (manual) |
| REPO-05 | Skill generates H3 with user checkpoint | manual | Visual inspection of SKILL.md workflow Step 4 | N/A (manual) |
| REPO-08 | `references/repo-patterns.md` exists with heuristics | manual | `test -f references/repo-patterns.md && wc -l references/repo-patterns.md` | Wave 0 |

### Sampling Rate
- **Per task commit:** `wc -l .claude/skills/repo-to-paper-skill/SKILL.md` (verify line budget) + `wc -l references/repo-patterns.md` (verify ~100 lines)
- **Per wave merge:** Structural checklist verification
- **Phase gate:** All requirements addressed in SKILL.md, repo-patterns.md exists, line budgets met

### Structural Verification Checklist
Since this is a pure markdown project, automated testing is replaced by structural verification:
- [ ] `SKILL.md` has valid YAML frontmatter with all required fields per `skill-conventions.md`
- [ ] `SKILL.md` has all required body sections (Purpose, Trigger, Modes, References, Ask Strategy, Workflow, Output Contract, Edge Cases, Fallbacks)
- [ ] `SKILL.md` workflow has four distinct phases with user confirmation between each
- [ ] `SKILL.md` line count is within budget (~300-320 lines)
- [ ] `repo-patterns.md` has file identification patterns table
- [ ] `repo-patterns.md` has category-to-section mapping table
- [ ] `repo-patterns.md` line count is ~100 lines
- [ ] `repo-patterns.md` is listed in SKILL.md `references.required`
- [ ] `references/bilingual-output.md` is listed in SKILL.md `references.required`
- [ ] Journal template is in `references.leaf_hints` (loaded conditionally)

### Wave 0 Gaps
- [ ] `.claude/skills/repo-to-paper-skill/` directory -- needs creation
- [ ] `references/repo-patterns.md` -- needs creation

## Sources

### Primary (HIGH confidence)
- `references/skill-conventions.md` -- Authoring rules, line budget, frontmatter contract, mode taxonomy, AskUserQuestion enforcement
- `references/skill-skeleton.md` -- Copyable starting template for new Skills
- `.claude/skills/experiment-skill/SKILL.md` -- Two-phase checkpoint workflow pattern reference (230 lines)
- `.claude/skills/de-ai-skill/SKILL.md` -- Two-phase detect-then-rewrite pattern reference (213 lines)
- `references/bilingual-output.md` -- Structural model for single-flat-file reference files (~95 lines)
- `references/journals/ceus.md` -- CEUS journal template with section guidance for H1 structure
- `.planning/REQUIREMENTS.md` -- REPO-01, REPO-02, REPO-03, REPO-05, REPO-08 specifications
- `14-CONTEXT.md` -- All locked decisions and discretion areas

### Secondary (MEDIUM confidence)
- [MLOps Guide - Project Structure](https://mlops-guide.github.io/Structure/project_structure/) -- Typical Python ML repo directory layout
- [Generic Folder Structure for ML Projects](https://dev.to/luxdevhq/generic-folder-structure-for-your-machine-learning-projects-4coe) -- File categorization patterns
- [IMRaD Format](https://libguides.umn.edu/StructureResearchPaper) -- Standard academic paper structure
- [IMRAD Wikipedia](https://en.wikipedia.org/wiki/IMRAD) -- Historical context and section definitions

### Tertiary (LOW confidence)
- None. All findings verified against primary project sources.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- this is a pure markdown project with well-documented conventions; no external dependencies to verify
- Architecture: HIGH -- experiment-skill provides a proven checkpoint pattern; extending to 4 phases follows the same logic
- Pitfalls: HIGH -- based on direct analysis of line budgets across all 11 existing Skills and the known ~320 line risk from STATE.md
- repo-patterns.md design: MEDIUM -- file categorization patterns derived from web research on typical Python ML repos; specific glob patterns may need tuning against real repos

**Research date:** 2026-03-18
**Valid until:** 2026-04-18 (stable -- pure markdown project with no external dependency versioning concerns)

---

*Research: Phase 14 - Repo-to-Paper Core Structure*
*Phase directory: .planning/phases/14-repo-to-paper-core-structure/*
