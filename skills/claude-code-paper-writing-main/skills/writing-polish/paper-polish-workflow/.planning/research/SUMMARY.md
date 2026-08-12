# Project Research Summary

**Project:** Paper Polish Workflow — v2.1 Team Agents Orchestration Layer
**Domain:** Claude Code Skill orchestration for academic paper writing
**Researched:** 2026-03-19
**Confidence:** HIGH

## Executive Summary

The v2.1 project adds a parallel section-processing orchestration layer (`ppw:team`) to an existing, validated 13-Skill suite for academic paper writing. The research conclusion is unambiguous: build on Claude Code's stable subagent mechanism (Agent tool), not the experimental Agent Teams feature. The orchestrator must be a Skill running in the main conversation — not a subagent itself — because only the main conversation can spawn subagents and use AskUserQuestion. The canonical architecture is: section splitter (physically decomposes the paper into per-section files) → parallel Agent tool dispatch (one subagent per section) → file-based result collection → section merger → post-merge consistency review. No new external dependencies are required; the entire system remains pure markdown Skills and Claude Code built-in tools.

The primary target Skills for orchestration are exactly three: `ppw:translation`, `ppw:polish`, and `ppw:de-ai`. These are the only ones that operate independently on individual paper sections. The remaining 10 Skills require full-paper context or operate on non-section artifacts and must NOT be wrapped in parallel dispatch. The canonical pipeline is `translate → polish → de-ai`, giving users a complete paper localization and quality pipeline in a single orchestrator invocation. All 13 existing Skills require zero modifications; the orchestrator forces `direct` mode on workers to suppress interactive questions that background subagents cannot answer.

The dominant risk is silent data loss from parallel agents writing to the same paper file simultaneously — a blocking pitfall that must be addressed before any other orchestration logic is built. The second major risk is consistency drift: independent agents make different terminology and style choices, producing papers that appear multi-authored. Both risks have clear mitigations (file decomposition before dispatch, terminology anchor injected into every agent prompt, mandatory post-merge consistency review), but they must be designed into the architecture from day one, not retrofitted.

---

## Key Findings

### Recommended Stack

The v1.0/v2.0 stack (13 SKILL.md files, shared reference library, Semantic Scholar MCP, AskUserQuestion, Workflow Memory) is unchanged and requires no additions for v2.1. The only new infrastructure is Claude Code's built-in Agent tool plus one new file: a generic worker agent definition at `.claude/agents/ppw-section-worker.md`.

The agent definition uses a single generic worker (not 13 per-skill workers). The orchestrator reads the target Skill's SKILL.md at runtime and injects relevant instructions into each subagent's spawn prompt dynamically. This avoids combinatorial agent file proliferation while remaining fully compatible with the existing Skill suite. The `skills:` frontmatter field (which would preload full Skill content into every worker) is explicitly NOT recommended — prompt injection is more targeted and avoids loading 300-line Skill bodies into each of 6+ parallel agents.

**Core technologies:**
- **Agent tool (Claude Code built-in):** Spawns isolated subagents for parallel section processing — the only stable, production-ready parallelism mechanism. Stable since v2.1.63 (Task alias still works).
- **`.claude/agents/ppw-section-worker.md`:** Single generic worker agent definition (tools: Read, Write, Edit, Grep, Glob; model: sonnet; maxTurns: 50) — replaces what would otherwise be 13 per-skill alternatives.
- **File-based data exchange (`.paper-team/` directory):** Sections written as individual `.tex` files before dispatch, output collected after completion — the only viable cross-agent data transport that avoids main-conversation context pollution.
- **Sonnet model for section workers:** Best cost/quality tradeoff for focused academic text processing tasks; Opus reserved for the orchestrator (main conversation) and optional consistency review.
- **Prompt injection (read SKILL.md at orchestrator level, pass inline):** Injects only the relevant portion of a Skill's instructions into each worker rather than loading all 13 Skills.

**What NOT to add:**
- Agent Teams (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) — experimental, Windows Terminal unsupported, inter-agent messaging not needed for embarrassingly parallel section processing.
- Per-skill agent definitions — single generic worker with orchestrator-constructed prompts is sufficient and avoids maintenance burden.
- `skills:` frontmatter field on workers — injects full 300-line Skill bodies into every worker context; too expensive at 6+ parallel agents.
- Git worktree isolation — sections don't conflict when each agent owns a separate section file; worktree overhead is unnecessary for text processing.

### Expected Features

**Must have (table stakes — v2.1.0 MVP):**
- **T1: Section Splitter** — parse paper into H1 sections with LaTeX/Markdown awareness; exclude preamble and bibliography; write section files with metadata headers; present confirmed list to user before any dispatch.
- **T2: Single-Skill Parallel Dispatch** — spawn one background subagent per section via Agent tool, each applying the same Skill in direct mode with injected instructions.
- **T3: Result Merger** — reassemble processed sections in original order into a unified output file; preserve LaTeX preamble and `\end{document}` footer.
- **T4: Progress Display** — bilingual status updates (Chinese + English) showing which sections are queued/in-progress/done.
- **T5: Error Handling per Section** — graceful per-section failure with original content preserved and `% [Team] Error:` annotation; other sections complete normally.
- **T6: Shared Settings Propagation** — journal template, `direct` mode enforcement, glossary path, and section-type-specific reference leaf selection sent to all agents at dispatch time.

**Should have (differentiators — v2.1.x after validation):**
- **D1: Automatic Consistency Review** — post-merge pass checking terminology variants, hedging uniformity, tense, abbreviation usage, and cross-reference integrity across all sections. This is THE key quality differentiator of parallel academic processing — essential given that parallel agents independently make different stylistic choices.
- **D4: Workflow Memory Integration** — record `ppw:team` invocations; detect repeated pipeline patterns (e.g., user consistently runs translate→polish→de-ai) to offer streamlined re-runs.
- **D5: Smart Section Grouping** — group short sections (<200 words) together for a single agent; split very long sections at H2 level. Reduces agent count and cost.

**Defer (v2.2+):**
- **D2: Multi-Skill Pipeline Mode** — chain Skills sequentially per section (translate→polish→de-ai pipeline). High complexity; requires stage-gated execution, inter-stage validation, annotation conflict management, and partial retry. Defer until single-skill mode is stable.
- **D3: User Intervention Points Between Pipeline Stages** — only meaningful when D2 exists; defer together.

**Anti-features (explicitly excluded):**
- Real-time inter-agent communication — subagents cannot communicate with each other; post-merge review is the correct substitute.
- Automatic per-section Skill selection — mixing Skills across sections creates unmergeable results.
- Paragraph-level parallelism — destroys intra-section coherence and explodes agent count (20-30 agents for a typical paper).
- Persistent agent definitions per Skill (13 files) — combinatorial maintenance burden with no benefit over prompt injection.

**Skill eligibility matrix (critical constraint):**
Only 3 of 13 Skills are parallel-ready: `ppw:translation`, `ppw:polish`, `ppw:de-ai`. The orchestrator must validate at invocation time and refuse with a clear error for the other 10 Skills.

### Architecture Approach

The orchestrator (`ppw:team`) is a Skill in the main conversation that spawns subagents via the Agent tool. All data flows through the file system (`.paper-team/` directory), never through in-memory return values, to keep the main conversation context lean and provide natural checkpointing. Subagent prompts are constructed dynamically: the orchestrator reads the target Skill's SKILL.md plus only the section-relevant reference leaf (not all reference files), then injects this content alongside the section file path, shared settings, and a terminology anchor document extracted from the original paper before dispatch.

**Major components:**
1. **ppw:team Skill** (`.claude/skills/ppw-team/SKILL.md`) — user-facing orchestrator in the main conversation: parse intent, confirm section split, backup original, dispatch agents, collect results, merge, run consistency review, report. MUST remain in the main conversation (cannot be forked or run as a subagent).
2. **Section Splitter (inline in ppw:team)** — parse `\section{}`/`##` markers; exclude preamble and bibliography; write each section to `.paper-team/sections/sec_N_title.tex` with metadata header comment; present confirmed list to user via AskUserQuestion before any agent is spawned.
3. **Terminology Anchor Extractor (inline in ppw:team)** — extract key terms, abbreviations, and preferred phrasings from the original paper before dispatch; write to `.paper-team/glossary.md`; inject into every agent prompt.
4. **Worker Subagents (spawned via Agent tool)** — one per section; receive: section file path, Skill instructions (injected inline), shared settings, terminology anchor, section-type-specific reference leaf content. Write output to `.paper-team/output/`. Return only a brief summary to avoid context pollution.
5. **Result Merger (inline in ppw:team)** — read output files in original order; concatenate; preserve LaTeX preamble and footer; write final `paper_[skill]_[timestamp].tex`.
6. **Consistency Reviewer (dedicated subagent or inline)** — runs on merged output; checks terminology variants, hedging uniformity, tense, abbreviation first-use, cross-reference integrity; presents findings to user.
7. **manifest.json** (`.paper-team/manifest.json`) — session state: sections, stages, status per section, config. Enables partial retry in pipeline mode.
8. **Existing 13 ppw:* Skills** — ZERO modifications required. Orchestrator forces `direct` mode, suppresses bilingual conversation output, and skips workflow-memory writes in all worker prompts.

**Key architectural patterns:**
- File-based data exchange (not in-memory): avoids context pollution; provides checkpointing; compatible with existing Skills.
- Prompt-injected Skill instructions (not `skills:` frontmatter): dynamic composition; works for any Skill combination; no static agent files per Skill.
- Single generic worker agent (not per-skill agent files): orchestrator controls specialization via prompt; single `.claude/agents/ppw-section-worker.md` file.
- Orchestrator handles all user interaction before dispatch: background workers auto-deny AskUserQuestion; all decisions made upfront.

### Critical Pitfalls

1. **Parallel agents writing to the same paper file — BLOCKING.** Multiple agents using Edit on the same `.tex` file causes silent data loss (last write wins, no error). Mitigation: physically decompose the paper into per-section files BEFORE any agent is spawned; enforce file ownership contracts in every agent prompt ("you own only this file"); backup original before dispatch. This is a hard architectural prerequisite — nothing else is safe to build without it.

2. **Consistency drift across parallel sections — BLOCKING.** Independent agents choose different terminology, hedging levels, and style. Formally documented in arXiv 2601.04170 as "semantic drift." Mitigation: extract terminology anchor before dispatch and inject into every agent prompt; propagate style profile from the Introduction section to all others; mandatory post-merge consistency review catches remaining inconsistencies.

3. **Skill invocation failure inside subagents — BLOCKING.** Skills are not automatically inherited by subagents; AskUserQuestion is auto-denied in background subagents; reference files must be loadable via Read tool. Mitigation: use prompt injection (orchestrator reads SKILL.md and injects inline); force `direct` mode on all workers; validate with a single-subagent proof-of-concept before building the full orchestrator — this is a go/no-go gate.

4. **Context window exhaustion in section-processing agents — BLOCKING.** Each agent must bootstrap from scratch: Skill instructions + reference content + section text + output generation. Mitigation: pre-extract only the section-relevant reference leaf (not all leaves); pre-inject reference content from the orchestrator rather than having agents Read files at runtime; set `maxTurns: 50` cap; use Sonnet (not Haiku) for section workers.

5. **workflow-memory.json race condition — Moderate.** All 13 existing Skills append to the same JSON file. Six parallel agents doing this simultaneously cause JSON corruption (parallel read-modify-write, no file locking). Mitigation: agents skip workflow memory entirely; orchestrator records a single `ppw:team` entry covering the whole operation.

---

## Implications for Roadmap

Based on combined research, the architecture research's suggested five-phase build order is well-justified. Each phase has clear dependencies, and two of the four blocking pitfalls must be addressed before writing a single line of orchestration logic.

### Phase 1: Foundation — Proof-of-Concept and Section Infrastructure

**Rationale:** Before parallel dispatch exists, two things must be validated as go/no-go gates: (a) a subagent can successfully run ppw:polish-equivalent injected instructions and produce quality output comparable to main-session execution, and (b) the section splitter correctly decomposes real papers. Both blocking pitfalls P1 (file writes) and P3 (Skill invocation) are addressed here. Building orchestration on an unvalidated foundation causes architectural rewrites.

**Delivers:**
- Single-subagent proof-of-concept: one section processed with injected Skill instructions, quality verified against main-session output on a real paper.
- Section splitter: LaTeX/Markdown-aware H1 parser; excludes preamble and bibliography; writes per-section files with metadata headers; presents section list for user confirmation via AskUserQuestion before dispatch.
- File-based data exchange infrastructure: `.paper-team/` directory structure, manifest.json schema, original-paper backup mechanism.
- Terminology anchor extractor: identifies key terms, abbreviations, and preferred phrasings from the original paper; writes to `.paper-team/glossary.md`.
- Skill registry reference file (`references/skill-registry.md`): compact summaries of the 3 parallel-eligible Skills (input/output contracts, reference dependencies, key constraints). Prevents orchestrator context bloat (Pitfall P9) by giving the orchestrator a lightweight meta-view instead of loading 13 full SKILL.md files.

**Addresses:** T1, P1 (file ownership architecture), P3 (Skill invocation validation), P9 (orchestrator context budget), P11 (splitter error prevention).
**Avoids:** Proceeding to parallel dispatch without validating the core subagent execution model.
**Research flag:** Standard patterns — all Agent tool APIs, subagent frontmatter, and Skill injection mechanisms are verified against official docs. No research-phase needed.

---

### Phase 2: Core Orchestration — Single-Skill Parallel Mode

**Rationale:** With the foundation proven, implement the full parallel dispatch-collect-merge cycle. This phase delivers the end-to-end MVP. Pitfall P2 (consistency drift) and P5 (workflow-memory race) are design choices in the dispatch mechanism — they must be addressed here, not retrofitted. The preview-first UX pattern (process one section, get approval, then dispatch remaining) avoids Pitfall P8 (no user intervention) from the start.

**Delivers:**
- Full ppw:team Skill with single-Skill parallel dispatch for polish, translation, and de-ai.
- Orchestrator validates Skill eligibility and refuses non-parallel-ready Skills with clear message.
- Terminology anchor injected into every agent prompt.
- Per-section direct-mode enforcement in all agent spawn prompts.
- Bilingual conversation output suppressed in agent prompts (agents write to files only).
- Workflow memory: agents skip it; orchestrator records a single entry.
- Result merger with section-order reassembly and LaTeX structure preservation.
- Progress display: bilingual status updates per section.
- Per-section error handling: original content preserved; annotated with error reason.
- Shared settings propagation: journal, direct mode, glossary, section-type-specific reference leaf.
- Preview-first pattern: process first section, present result, require approval before remaining dispatch.
- Cost estimation displayed before full dispatch.

**Implements:** Main ppw:team Skill, Agent tool dispatch loop, `.paper-team/` data flow, result merger.
**Addresses:** T2, T3, T4, T5, T6, P2, P5, P8 (partial), P12, P13.
**Research flag:** Standard patterns. The one item requiring empirical validation: actual agent output quality vs. main-session quality on a real paper section. Build the proof-of-concept from Phase 1 into the acceptance criteria.

---

### Phase 3: Quality Layer — Post-Merge Consistency Review

**Rationale:** Consistency drift (Pitfall P2) is the central quality risk of parallel processing. The terminology anchor reduces it but cannot eliminate it — different agents make different valid stylistic choices from the same reference material. The post-merge consistency review is the mandatory quality gate. It is also the primary differentiator (D1) that elevates the orchestrator from "fast parallel processing" to "quality-assured parallel processing."

**Delivers:**
- Consistency review as a dedicated subagent (or inline logic) operating on the merged output.
- Checks: terminology variants across sections, hedging uniformity, tense consistency, abbreviation first-use, cross-reference integrity (figure/table numbering, `\cite{}` and `\ref{}` usage).
- Report presented to user with specific fix suggestions per inconsistency.
- Optional auto-apply for unambiguous terminology unification.
- Annotation preservation audit: verify all LaTeX `% [Skill]` annotations survived the merge.

**Addresses:** D1, remainder of P2 (consistency catch-all).
**Research flag:** Standard text analysis patterns. The specific consistency checks are well-defined in PITFALLS.md. No research-phase needed. One empirical question: what consistency issues actually occur in real parallel runs? Plan to iterate on the check categories after first real use.

---

### Phase 4: UX Hardening — Intervention Points, Cost Controls, and Workflow Memory

**Rationale:** Once the core quality loop works, address the remaining UX and operational pitfalls. Users need the ability to see one section before committing all token cost (preview-first, already partially in Phase 2), a cost estimate before dispatch, and workflow pattern recognition for repeated team invocations. These transform a functional tool into a production-quality experience.

**Delivers:**
- Batch size control: dispatch in configurable batches (default 2-3) so user sees results before full commitment. Complementing the preview-first pattern from Phase 2.
- Detailed cost estimation: calculate expected tokens (agents × per-agent budget) and display before dispatch.
- Cancel mechanism: if orchestrator detects abort intent in main session, no new agents are spawned.
- Workflow memory integration: record `ppw:team` invocations with Skill chain metadata; detect repeated pipeline patterns; offer streamlined re-runs.
- Smart section grouping (D5): group short sections (<200 words); split very long sections at H2 with user confirmation.
- Cleanup mechanism: `.paper-team/` workspace cleanup after successful merge, with option to keep for debugging.

**Addresses:** D4, D5, P8 (full resolution).
**Research flag:** Standard patterns. Workflow memory extension follows existing skill-conventions.md protocol precisely.

---

### Phase 5: Multi-Skill Pipeline Mode (Deferred — v2.2+)

**Rationale:** Pipeline mode (translate→polish→de-ai) requires stage-gated execution, inter-stage output validation, LaTeX annotation conflict management across multiple Skill passes, and per-section partial retry. This is substantially more complex than single-Skill mode and introduces two new moderate pitfalls (P6 and P7) that are pipeline-specific. Build only after the single-Skill orchestrator is battle-tested on real user papers.

**Delivers:**
- Multi-stage pipeline with configurable Skill chain (translate→polish→de-ai as canonical).
- Stage-gate validation between stages: verify output file exists, is non-empty, contains stage-appropriate annotations.
- Per-section status tracking in manifest.json: current stage, completion status, error messages per stage.
- Partial retry: re-run only failed sections from last successful stage.
- Annotation preservation contract: agents instructed to preserve `% [StageName] Original:` annotations from all previous stages.
- Optional user intervention points between stages: present stage N summary, offer approve/review/abort.
- "Strip annotations" post-pipeline option: removes all `% [*] Original:` lines for clean final output.

**Addresses:** D2, D3, P6, P7.
**Research flag:** Needs empirical validation before design is finalized. Run a manual translate→polish→de-ai on one section and audit annotation layering to verify regex scoping is correctly limited to each Skill's own annotation type.

---

### Phase Ordering Rationale

- **Phase 1 before Phase 2:** The single-subagent proof-of-concept and file decomposition architecture are go/no-go gates. Building parallel dispatch on an unvalidated subagent execution model causes full architectural rewrites.
- **Phase 2 before Phase 3:** Consistency review requires a working merge. The quality layer cannot exist without the core loop.
- **Phase 3 before Phase 4:** Users should see the full quality loop before UX polish is added. Consistency review is core, not polish.
- **Phase 4 before Phase 5:** Preview-first pattern and cost estimation are safety nets that are especially important for pipeline runs, which cost 3-7x more. These should be in place before the costlier feature is built.
- **Phase 5 deferred:** Pipeline mode is complex enough to deserve its own iteration cycle. Single-Skill mode proves the architecture; pipeline mode extends it.

### Research Flags

Phases needing empirical validation during implementation (not additional pre-work research):
- **Phase 2:** Validate actual subagent output quality vs. main-session quality on a real paper section. This is built into Phase 1's proof-of-concept acceptance criteria.
- **Phase 5:** Audit annotation regex scoping across a real translate→polish→de-ai run before finalizing inter-stage contract design.

Phases with standard, fully-documented patterns (no research-phase needed):
- **Phase 1:** All Agent tool APIs and subagent behavior are verified against official Claude Code docs.
- **Phase 2:** Parallel dispatch patterns and file-based exchange are documented (including Anthropic's own 16-agent C compiler case study).
- **Phase 3:** Consistency analysis is standard text processing with no novel platform dependencies.
- **Phase 4:** Workflow memory extension follows existing skill-conventions.md conventions exactly.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All Agent tool parameters, subagent frontmatter fields, model selection options, tool inheritance rules, and the subagents-cannot-spawn-subagents constraint are verified against official Claude Code docs. The 10-concurrent-agent limit is community-reported (MEDIUM) but safely above the 4-7 sections typical of academic papers. |
| Features | MEDIUM-HIGH | Table stakes (T1-T6) are clearly scoped from codebase analysis of all 13 existing Skills. Differentiators (D1-D5) have concrete designs. The Skill eligibility matrix (3 of 13 parallel-ready) is based on direct Skill file analysis. One gap: eligibility has not been empirically tested with actual subagent execution — the proof-of-concept in Phase 1 closes this. |
| Architecture | HIGH | Core architectural constraint (only main conversation can spawn subagents) is explicitly documented. File-based data exchange pattern is validated by Anthropic Engineering's own case study (16 parallel agents on C compiler). Component boundaries are derived from direct analysis of all 13 existing Skills and skill-conventions.md. Zero modifications to existing Skills is a verified claim, not an assumption. |
| Pitfalls | MEDIUM-HIGH | Blocking pitfalls (P1-P4) are grounded in official docs, complete codebase analysis, and cited academic research (arXiv 2601.04170 on semantic drift). Moderate pitfalls draw on verified GitHub issue numbers with specific version references. Community-sourced pitfalls (P8 UX, P12 bilingual doubling) are well-reasoned inferences. The race condition risk (P5) is supported by the `.claude.json` corruption precedent (GitHub #28847, fixed v2.1.61). |

**Overall confidence:** HIGH

### Gaps to Address

- **Actual subagent output quality vs. main-session quality:** The architecture is sound; empirical validation requires running a real section through a subagent with injected ppw:polish instructions and comparing to main-session output. This is Phase 1's proof-of-concept and is a deployment gate, not a research task.
- **Exact concurrent agent limit:** The "10 concurrent subagents" figure is community-reported. For papers with 8+ sections, design the dispatch loop with an explicit configurable concurrency cap (default 5) from Phase 2 onward.
- **Section-title-to-reference-leaf mapping:** The section splitter detects titles; the orchestrator must map them to the correct expression-pattern reference leaf (e.g., "Introduction" → `introduction-and-gap.md`). This lookup table is not in the research files. It should be defined explicitly in the Skill registry or ppw:team Skill as a small static mapping.
- **ppw:de-ai interactive step in parallel mode:** The de-ai Skill has a two-phase workflow (detect → user-selects → rewrite) requiring user interaction between phases. In direct mode, the recommended resolution is "auto-select Fix all High Risk + Medium Risk." This design choice should be confirmed with users before Phase 2 is finalized.

---

## Sources

### Primary (HIGH confidence)
- [Claude Code Subagents Documentation](https://code.claude.com/docs/en/sub-agents) — Agent tool parameters, subagent frontmatter fields, tool inheritance, `skills:` field behavior, nesting limitation, parallel execution, background vs. foreground modes.
- [Claude Code Agent Teams Documentation](https://code.claude.com/docs/en/agent-teams) — Agent Teams architecture, experimental status, TeamCreate/SendMessage, teammate tool restrictions, display mode limitations, Windows incompatibility.
- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills) — Skill frontmatter, `context: fork`, `agent:` field, progressive disclosure conventions.
- [Anthropic Engineering: Building a C Compiler with Parallel Claudes](https://www.anthropic.com/engineering/building-c-compiler) — Real-world validation of file-based parallel agent coordination with 16 concurrent agents; confirms the file-based data exchange pattern.
- All 13 existing ppw:* SKILL.md files — Direct codebase analysis for file write patterns, workflow memory usage, annotation formats, and reference loading behavior. Basis for the 3-of-13 parallel eligibility finding and the "zero modifications" claim.
- `references/skill-conventions.md` — Interaction modes, workflow memory protocol, Skill budget constraints, direct-mode specification.

### Secondary (MEDIUM confidence)
- [GitHub Issue #25546: Allow configuring model for built-in agents](https://github.com/anthropics/claude-code/issues/25546) — `CLAUDE_CODE_SUBAGENT_MODEL` env var limitation; per-agent `model` field is preferred.
- [GitHub Issue #28847: .claude.json corruption from concurrent writes](https://github.com/anthropics/claude-code/issues/28847) — Race condition precedent establishing that parallel file writes without locking cause corruption (fixed v2.1.61).
- [GitHub Issue #34614: TeamCreate spawns teammates that silently exit](https://github.com/anthropics/claude-code/issues/34614) — Agent Teams instability evidence (v2.1.76); supports the subagents-over-teams decision.
- [GitHub Issue #17283: Skill tool should honor context: fork and agent: fields](https://github.com/anthropics/claude-code/issues/17283) — Known issue with `context: fork` being ignored; confirms it is NOT a viable orchestration mechanism.
- [Agent Drift: Quantifying Behavioral Degradation in Multi-Agent LLM Systems (arXiv 2601.04170)](https://arxiv.org/abs/2601.04170) — Formal quantification of semantic drift in parallel agent systems; directly supports Pitfall P2.
- [Emergent Convergence in Multi-Agent LLM Annotation (ACL 2025)](https://aclanthology.org/2025.blackboxnlp-1.12.pdf) — Consistency patterns in multi-agent annotation.
- [AI Agent Orchestration Patterns - Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns) — Sequential pipeline, parallel dispatch, and routing patterns; validates the stage-gated pipeline approach.
- Community sources: claudefa.st sub-agent guide, laozhang.ai agent teams guide, alexop.dev agent teams swarm patterns, stephenvantran.com custom subagents guide.

### Tertiary (LOW confidence)
- "10 concurrent subagent limit" — community-reported (stephenvantran.com). Not in official docs; practical limit may vary by subscription tier. Design the dispatch loop with a configurable cap regardless.
- [aaddrick/claude-pipeline](https://github.com/aaddrick/claude-pipeline) — Open-source reference for Claude Code pipeline patterns; useful for precedent but not authoritative.

---
*Research completed: 2026-03-19*
*Ready for roadmap: yes*
