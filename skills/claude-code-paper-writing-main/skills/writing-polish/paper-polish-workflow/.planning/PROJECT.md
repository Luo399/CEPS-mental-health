# Paper Polish Workflow

## What This Is

A complete Claude Code Skill suite (13 Skills) for academic paper writing, covering the full lifecycle: repo-to-paper draft generation, Chinese-to-English translation, English polishing, de-AI detection and rewriting, peer reviewer simulation, abstract generation, experiment analysis and discussion generation, figure/table caption optimization, logic chain verification, literature search and BibTeX generation, cover letter generation, visualization recommendation, and remote skill sync. All Skills use the `ppw:` namespace prefix and share a modular reference library (expression patterns, anti-AI patterns, journal templates, bilingual output spec, body generation rules). Primarily for geography/urban science research papers; open-sourced for the community.

## Core Value

Every Skill must produce output that is directly usable in a real paper submission — no toy demos, no generic advice. Quality of prompt engineering and execution flow determines whether this tool suite is actually useful or just another prompt collection.

## Requirements

### Validated

- ✓ Shared expression patterns library (sentence starters, transitions, hedging, results, conclusions) with bilingual examples — v1.0
- ✓ Journal template system with CEUS as first template, strict contract with invariant headings — v1.0
- ✓ Anti-AI patterns library with risk-tiered vocabulary blacklist and human-sounding alternatives — v1.0
- ✓ Skill template conventions: YAML frontmatter format, ~300-line budget, progressive disclosure, 4 interaction modes — v1.0
- ✓ 11 core writing Skills (translation, polish, de-ai, reviewer, abstract, experiment, caption, logic, literature, cover-letter, visualization) — v1.0
- ✓ Bilingual README with installation guide and quick-start workflows — v1.0
- ✓ v1.0 tech debt resolved (escape hatch docs, capability categories, required references) — v2.0
- ✓ AskUserQuestion enforcement across all Skills — v2.0
- ✓ Bilingual paragraph-by-paragraph comparison output for 7 eligible Skills — v2.0
- ✓ Repo-to-Paper draft generator: repo scan → H1/H2/H3 outline → body text with [SOURCE] annotations — v2.0
- ✓ Integrated literature search at H2 stage via Semantic Scholar — v2.0
- ✓ Workflow Memory system: Skills record invocations and detect frequent patterns — v2.0

## Current Milestone: v2.1 Team Agents Orchestration

**Goal:** Add a universal team agents orchestration layer that parallelizes any Skill (or Skill chain) across paper sections, with observable progress and automatic consistency review.

**Target features:**
- Universal orchestrator Skill (`ppw:team`) for parallel section-level processing
- Single-Skill parallel mode: split paper by H1/H2 sections, run same Skill on each section concurrently
- Multi-Skill pipeline mode: chain Skills (e.g., translate→polish→de-ai), flowing sections through stages
- Observable collaboration: real-time agent progress display with intervention points between stages
- Automatic consistency review: post-merge check for terminology/style/tone inconsistencies across sections

### Active

- [ ] Universal orchestrator Skill for parallel section-level processing
- [ ] Section splitter that parses paper into H1/H2 sections for parallel dispatch
- [ ] Single-Skill parallel mode with agent-per-section execution
- [ ] Multi-Skill pipeline mode with stage-based flow
- [ ] Observable progress display with intervention points
- [ ] Automatic consistency review after parallel merge

### Out of Scope

- Web UI or standalone application — this is a Claude Code Skill project, not a SaaS
- Real-time collaboration — single-user workflow
- Non-academic writing (blog posts, marketing copy) — focused on research papers
- Automated paper generation from scratch — assists human writers, not replaces them
- Image/figure generation — requires image generation models; out of scope for text Skills
- Plagiarism detection — requires specialized databases (Turnitin, iThenticate)

## Context

**v1.0 shipped:** 2026-03-13 — 11 Skills, 15 plans across 10 phases, 16/16 requirements satisfied.
**v2.0 shipped:** 2026-03-18 — 13 Skills (ppw:* namespace), 9 plans across 8 phases, 18/18 requirements satisfied.

**Current codebase:**
- 13 SKILL.md files in `.claude/skills/ppw-*/` (~4,500 lines total)
- 10 reference files in `references/` (expression patterns, anti-AI patterns, CEUS journal template, bilingual output spec, body generation rules, repo patterns, skill conventions, skill skeleton)
- Bilingual README.md at repository root
- Platform: Claude Code only (`.claude/skills/` format)

**Tech stack:**
- Pure markdown Skills (no build steps, no npm packages)
- Shared reference library loaded on-demand via Read tool
- Semantic Scholar MCP for literature search
- AskUserQuestion for interactive mode Skills
- Workflow Memory system (`.planning/workflow-memory.json`)

**Known tech debt from v2.0 audit:**
- `skill-conventions.md` uses stale `*-skill` names after ppw:* rename (4 items)
- REPO-04 checkbox stale in REQUIREMENTS.md (clerical)

**Target journals:** Geography and urban science — CEUS (template complete), IJGIS, Cities (future candidates)

## Constraints

- **Platform**: Claude Code only — Skills must follow `.claude/skills/[name]/SKILL.md` format
- **No external dependencies**: Skills are pure markdown prompts, no npm packages or build steps
- **Journal specificity**: First-class support for geography/urban journals; other fields secondary
- **Language**: Skills work in both Chinese and English (bilingual triggers and instructions)
- **Tool access**: Skills may use `AskUserQuestion`, `Read`/`Write`/`Edit`, `Grep`/`Glob`, `Bash`, and `mcp__semantic-scholar__*`
- **Namespace**: All Skills use `ppw:` prefix (e.g., `ppw:polish`, `ppw:translation`)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Multi-Skill architecture (not single Skill with routing) | Each capability is independent and self-contained; users invoke what they need directly | ✓ Good — 13 Skills are independently invokable with no shared state issues |
| Adapt prompts from awesome-ai-research-writing as base | High-quality prompts from top researchers; adapt for Claude Code Skill format with interactivity | ✓ Good — all core Skills functional and convention-compliant |
| CEUS as first journal template | User's primary target journal; establishes template pattern for others | ✓ Good — CEUS contract used by translation, polish, cover letter, reviewer, repo-to-paper Skills |
| Modular reference library (expression patterns, anti-AI, bilingual spec) | On-demand loading keeps Skill context narrow; each Skill loads only what it needs | ✓ Good — avoids context bloat; each Skill loads 1-3 leaf files max |
| Strict ~300-line Skill budget | Keeps Skills readable and context-efficient; forces progressive disclosure | ✓ Good — all Skills within budget (repo-to-paper exceeds with justification) |
| Anti-hallucination citation rule (MCP data only) | Prior incident pattern: AI-generated citations have ~40% error rate | ✓ Good — literature-skill refuses to infer BibTeX fields from prior knowledge |
| Two-phase workflow for analysis Skills | User must confirm findings before generation begins; reduces wasted generation | ✓ Good — adopted as pattern for de-ai, experiment, reviewer Skills |
| Bilingual output as default ON with opt-out | Chinese-primary users benefit from paragraph-by-paragraph comparison | ✓ Good — 7 Skills support bilingual, 4 exempt (caption, cover-letter, visualization, literature) |
| ppw:* namespace prefix | Avoids name collisions with other skill packages in user's project | ✓ Good — unified `/ppw:skill` invocation format |
| Workflow Memory system | Detects frequent skill chains (e.g., polish→de-ai) and offers direct mode | ✓ Good — reduces repetitive setup for power users |
| Top-down repo-to-paper structure (H1→H2→H3→body) | Matches how humans outline papers; user confirms at each level before detail generation | ✓ Good — prevents wasted generation on wrong structure |

---
*Last updated: 2026-03-19 after v2.1 milestone started*
