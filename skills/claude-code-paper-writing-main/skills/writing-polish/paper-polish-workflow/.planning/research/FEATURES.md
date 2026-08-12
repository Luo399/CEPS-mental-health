# Feature Research: Team Agents Orchestration Layer

**Domain:** Multi-agent orchestration for academic paper Skill suite (Claude Code)
**Researched:** 2026-03-19
**Confidence:** MEDIUM-HIGH

## Context

This research targets v2.1 of the Paper Polish Workflow (PPW) Skill suite. The existing codebase has 13 Skills (`ppw:*` namespace) that operate on full papers serially -- one section at a time within a single Claude Code session. The v2.1 goal is to add a universal orchestration layer (`ppw:team`) that parallelizes any Skill (or Skill chain) across paper sections, with observable progress and automatic consistency review.

### Platform Constraints

PPW runs entirely within Claude Code as `.claude/skills/` markdown files. The orchestration layer must work within Claude Code's native capabilities:

- **Subagents** (via the Agent tool): spawn specialized workers in isolated context windows, return results to the caller. Subagents cannot spawn other subagents. Production-ready.
- **Agent Teams** (experimental): multi-session coordination with a shared task list and inter-agent messaging. Requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. Known limitations around session resumption and reliability.
- **Custom Agents** (`.claude/agents/`): persistent agent definitions with YAML frontmatter, custom tools, model selection, and permission modes. Can be referenced by Skills.

**Decision: Use subagents as the execution substrate, not agent teams.** Agent teams are experimental, have reliability issues, and add coordination overhead that exceeds what section-level paper processing needs. Subagents are stable, production-ready, and provide the right abstraction: independent workers that return results to an orchestrating parent.

---

## Feature Landscape

### Table Stakes (Users Expect These)

Features that must exist for the orchestrator to be useful. Missing any of these makes the feature feel broken or incomplete.

| # | Feature | Why Expected | Complexity | Dependencies | Notes |
|---|---------|--------------|------------|--------------|-------|
| T1 | **Section Splitter** | Users invoke "team polish my paper" and expect the system to parse their paper into sections automatically. Manual section specification defeats the purpose of orchestration. | MEDIUM | None (new capability) | Must handle H1 (`\section{}`) and H2 (`\subsection{}`) boundaries. Markdown `#`/`##` headers too. Must preserve LaTeX commands, math environments, and figure/table blocks across splits. Output: ordered list of `{id, title, content, heading_level}` objects. |
| T2 | **Single-Skill Parallel Dispatch** | The core promise: "run ppw:polish on all 6 sections at once." Without this, there is no orchestrator. | HIGH | T1 (Section Splitter) | Each section dispatched to a subagent running the target Skill. Subagent receives: section content, skill name, shared settings (journal, mode, glossary). Subagent returns: processed content + skill output artifacts (self-check, change annotations). Must handle the 13 existing Skills without modifying them. |
| T3 | **Result Merger** | After parallel processing, sections must be reassembled into a single coherent document. Users expect a clean merged output file, not 6 separate fragments. | MEDIUM | T2 (Parallel Dispatch) | Reassemble sections in original order. Preserve LaTeX preamble and document structure. Merge per-section artifacts (annotations, reports) into unified summaries. Handle output format differences across Skills (`.tex` files vs. conversation reports). |
| T4 | **Progress Display** | Users need to know what is happening during parallel execution. Without visibility, long-running orchestration feels like a hang. | LOW | T2 (Parallel Dispatch) | Report: which sections are queued/in-progress/done, which Skill is running, elapsed time. Use conversation output (no external UI). Bilingual status messages (Chinese + English). |
| T5 | **Error Handling per Section** | If one section fails (e.g., subagent timeout, reference file missing), the other sections should still complete. Users expect graceful degradation, not total failure. | MEDIUM | T2 (Parallel Dispatch) | Failed sections: report error, include original content in merged output with `% [Team] Error: <reason>` annotation. Option to retry failed sections individually. Never lose user content on failure. |
| T6 | **Shared Settings Propagation** | When a user says "polish my paper for CEUS", all section agents must use the same journal template, glossary, and mode. Inconsistent settings across agents = inconsistent output. | LOW | T2 (Parallel Dispatch) | Collect settings once in the orchestrator's Ask Strategy, then propagate to all subagents as part of their task prompt. Settings: target journal, interaction mode (force `direct` for subagents), glossary path, bilingual mode, section type hints. |

### Differentiators (Competitive Advantage)

Features that elevate the orchestrator beyond basic parallelization. Not required for launch, but high value.

| # | Feature | Value Proposition | Complexity | Dependencies | Notes |
|---|---------|-------------------|------------|--------------|-------|
| D1 | **Automatic Consistency Review** | After parallel merge, a dedicated review pass checks for terminology inconsistencies, tone drift, style mismatches, and numbering errors introduced by independent agents working on sections in isolation. This is THE key concern with parallel paper processing -- each agent may choose different synonyms, hedging levels, or phrasing conventions. | HIGH | T3 (Result Merger) | Runs as a post-merge analysis step. Checks: (1) terminology -- same concept must use same term across all sections; (2) tone -- hedging level and formality should be uniform; (3) style -- sentence length variance, passive/active voice ratio consistency; (4) cross-references -- `\ref{}`, `\cite{}` consistency, figure/table numbering. Outputs a consistency report with specific fix suggestions. Optionally auto-applies terminology unification. |
| D2 | **Multi-Skill Pipeline Mode** | Chain Skills sequentially on each section: e.g., `translate -> polish -> de-ai`. Each section flows through the full pipeline, and all sections execute their pipelines in parallel. | HIGH | T1, T2, T3 | Pipeline definition: ordered list of Skill names. Each stage passes output to next stage's input. Inter-stage artifacts (e.g., translation's `self_check_summary`) are collected but not passed forward. Must handle Skills with different output formats (translation produces `.tex`, de-ai produces in-place edits). Pipeline-level error handling: if stage N fails for a section, halt that section's pipeline but continue others. |
| D3 | **User Intervention Points Between Pipeline Stages** | Between pipeline stages (e.g., after translate, before polish), pause and show the user intermediate results. User can approve, modify, or skip sections before the next stage begins. | MEDIUM | D2 (Pipeline Mode) | Use AskUserQuestion with per-section options: "Approve all" / "Review section X" / "Skip section Y for this stage". Only meaningful in pipeline mode. In single-skill mode, intervention happens after merge (the final output). Keeps the user in control without requiring per-section-per-stage approval (which would be 6 sections x 3 stages = 18 approvals -- too many). |
| D4 | **Workflow Memory Integration** | The orchestrator records its own invocations to workflow memory and detects patterns like "user always runs team translate -> team polish -> team de-ai" to offer one-click full pipeline execution. | LOW | Existing Workflow Memory system | Straightforward extension of the existing pattern detection. Record `ppw:team` with metadata about which Skills and mode were used. Detect repeated team invocations and offer streamlined re-runs. |
| D5 | **Smart Section Grouping** | Not all sections benefit from parallel processing. Short sections (Abstract, Conclusion) can be grouped together for a single agent. Very long sections can be further split at H2 level. Adaptive splitting based on content length and structure. | MEDIUM | T1 (Section Splitter) | Rules: sections under ~200 words can be grouped with adjacent short sections. Sections over ~3000 words should be split at H2 boundaries. User can override grouping. Reduces subagent count (cost savings) while maintaining quality. |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem useful but create problems in this specific context. Explicitly excluded with rationale.

| # | Feature | Why Requested | Why Problematic | Alternative |
|---|---------|---------------|-----------------|-------------|
| A1 | **Real-time Inter-Agent Communication** | "Agents should share terminology decisions as they work so all sections stay consistent." | Claude Code subagents cannot communicate with each other -- they only return results to the parent. Agent Teams support messaging but are experimental and unreliable. More fundamentally, academic section processing is embarrassingly parallel: each section is self-contained input. Real-time coordination adds latency, complexity, and failure modes for minimal benefit. | Post-merge consistency review (D1). Propagate shared glossary/terminology list upfront via settings (T6). This is the proven pattern in document processing pipelines. |
| A2 | **Automatic Skill Selection per Section** | "The orchestrator should detect that the Introduction needs translation but Results only needs polish." | Different Skills produce fundamentally different outputs. Mixing Skills across sections creates an unmergeable result: some sections in Chinese, some polished English, some with de-AI annotations. The user's intent when invoking `ppw:team polish` is uniform application, not per-section intelligence. | If users need different Skills for different sections, they should invoke the orchestrator multiple times or use pipeline mode (D2) which applies a uniform chain to all sections. |
| A3 | **Agent Teams as Execution Substrate** | "Use Claude Code's Agent Teams for multi-session parallel execution with shared task lists." | Agent Teams are experimental (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`), have known limitations around session resumption, task status can lag, and require tmux/iTerm2 for split-pane mode. They are designed for human developers coordinating across modules, not for automated Skill execution on document sections. The overhead of team creation, task lists, and teammate messaging far exceeds what section-level paper processing needs. | Subagents via the Agent tool. Production-ready, stable, and purpose-built for focused tasks that return results to a parent. The orchestrating Skill (ppw:team) acts as the coordinator, dispatching subagents per section. |
| A4 | **Paragraph-Level Parallelism** | "Split at paragraph level for maximum parallelism." | Paragraph-level splitting destroys cross-paragraph coherence within a section. Skills like polish and de-ai consider paragraph flow, topic sentence structure, and argument progression -- all of which require section-level context. Paragraph splitting also creates an explosion of subagents (a 20-paragraph paper = 20 agents vs. 6 sections = 6 agents). | Section-level (H1) splitting as default, with optional H2 sub-splitting for very long sections (D5). This preserves intra-section coherence while enabling meaningful parallelism. |
| A5 | **Persistent Agent Definitions for Each Skill** | "Create a `.claude/agents/ppw-polish-agent.md` for each Skill." | Creating 13 agent files duplicates the Skill definitions. Skills are already the authoritative prompts. Agent files would need to stay in sync with Skills, creating a maintenance burden. Subagents spawned programmatically via the Agent tool can receive Skill instructions dynamically. | The orchestrator Skill (ppw:team) dynamically constructs subagent task prompts that reference the target Skill. No static agent files needed. If Claude Code later supports `skills` field in subagent frontmatter (which it does), a single orchestrator agent definition could load Skills dynamically. |
| A6 | **Cross-Section Awareness During Processing** | "Each agent should see the full paper so it understands context." | Giving each agent the full paper defeats the purpose of parallelization (context window savings). Each agent would consume the full paper's tokens plus its processing overhead. For a 10,000-word paper with 6 sections, this means 6x the token cost vs. 1x with section-level splitting. More importantly, Skills are designed to work on individual sections -- they detect section type, load appropriate references, and produce section-scoped output. | Provide each agent with: (1) its assigned section content, (2) a brief paper abstract/summary for context, (3) shared settings (journal, glossary). The summary provides enough context without full-paper cost. Post-merge consistency review (D1) handles any coherence issues. |

---

## Feature Dependencies

```
[T1] Section Splitter
    |
    +--requires--> [T2] Single-Skill Parallel Dispatch
    |                   |
    |                   +--requires--> [T3] Result Merger
    |                   |                   |
    |                   |                   +--enhances--> [D1] Consistency Review
    |                   |
    |                   +--requires--> [T4] Progress Display
    |                   |
    |                   +--requires--> [T5] Error Handling per Section
    |                   |
    |                   +--requires--> [T6] Shared Settings Propagation
    |
    +--enhances--> [D5] Smart Section Grouping

[T2] Single-Skill Parallel Dispatch
    +--requires--> [D2] Multi-Skill Pipeline Mode
                        |
                        +--enhances--> [D3] User Intervention Points

[D4] Workflow Memory Integration (independent -- existing system)
```

### Dependency Notes

- **T1 -> T2:** Parallel dispatch cannot work without section splitting. T1 is the foundational capability.
- **T2 -> T3:** Results from parallel agents must be merged. Without T3, the user gets 6 separate outputs with no unified document.
- **T3 -> D1:** Consistency review operates on the merged document. It makes no sense to review consistency before merging.
- **T2 -> D2:** Pipeline mode is a composition of multiple sequential dispatch rounds. The single-skill dispatch mechanism must work first.
- **D2 -> D3:** Intervention points only exist in pipeline mode (between stages). Single-skill mode has no intermediate stages.
- **D5 enhances T1:** Smart grouping modifies the splitter's behavior but does not replace it.
- **D4 is independent:** Workflow memory integration uses an existing system and can be added at any point.

---

## Interaction Model

### User Invocation Patterns

The orchestrator must support these invocation patterns:

| Pattern | Example | Behavior |
|---------|---------|----------|
| Single-Skill parallel | `/ppw:team polish my-paper.tex` | Split paper, run ppw:polish on all sections in parallel, merge |
| Single-Skill with journal | `/ppw:team polish my-paper.tex for CEUS` | Same, with CEUS journal template propagated to all agents |
| Pipeline mode | `/ppw:team pipeline translate->polish->de-ai my-paper.tex` | Split paper, run 3-stage pipeline on each section, merge |
| Specific sections | `/ppw:team polish sections 2,3,5 of my-paper.tex` | Only process specified sections, leave others untouched |
| Chinese trigger | `/ppw:team 润色 my-paper.tex` | Same as single-skill polish, triggered in Chinese |

### Ask Strategy for the Orchestrator

Before dispatching, `ppw:team` should ask (maximum 3 questions):

1. **Target Skill(s):** If not specified in trigger -- "Which Skill should I run on all sections?" (AskUserQuestion with Skill list)
2. **Target journal:** If not specified -- inherited from existing Skill conventions
3. **Processing mode:** If pipeline specified -- confirm pipeline order; if single-skill -- confirm `direct` mode for subagents

**In `direct` mode:** Skip questions when trigger is sufficiently specific. `/ppw:team polish paper.tex for CEUS` requires zero questions.

### User Intervention Model

| Mode | Intervention Points | User Action |
|------|---------------------|-------------|
| Single-Skill | After merge, before consistency review | Review merged output, approve or request re-run on specific sections |
| Pipeline | Between each stage (D3) | Approve stage N output for all sections, or flag specific sections for revision before stage N+1 |
| Both | After consistency review (D1) | Accept consistency suggestions or dismiss |

**Key principle:** Intervention is opt-in, not blocking. The default flow completes without user input. Users who want control use `guided` mode; users who want speed use `direct` mode.

---

## Skill Compatibility Matrix

Not all 13 Skills are equally suitable for parallel section-level processing. This matrix categorizes them:

| Skill | Parallel-Ready | Notes |
|-------|---------------|-------|
| `ppw:translation` | YES | Each section translates independently. Output: `.tex` files per section. |
| `ppw:polish` | YES | Each section polishes independently. Output: in-place edits per section. Batch mode already exists. |
| `ppw:de-ai` | YES | Two-phase (detect+rewrite) runs per section. User selection step (Phase 1 Step 4) must be automated or pre-configured in parallel mode. |
| `ppw:abstract` | NO | Operates on the abstract only -- a single section. Parallelization is meaningless. |
| `ppw:experiment` | NO | Operates on experiment results as a whole, not per-section. |
| `ppw:caption` | PARTIAL | Could run per figure/table, but splitting by caption rather than section requires different logic. |
| `ppw:logic` | NO | Requires full-paper context for cross-section logic verification. Cannot work on isolated sections. |
| `ppw:reviewer-simulation` | NO | Requires full-paper context for holistic peer review scoring. |
| `ppw:literature` | NO | Searches for references, not section-bound text processing. |
| `ppw:cover-letter` | NO | Generates a single document, not section-parallelizable. |
| `ppw:visualization` | NO | Recommends chart types, not section-bound text processing. |
| `ppw:repo-to-paper` | NO | Multi-step guided workflow with repo scanning, not parallelizable at section level. |
| `ppw:update` | NO | Syncs files from GitHub, not text processing. |

**Parallel-ready Skills: 3 (translation, polish, de-ai).** These are the primary targets. The orchestrator should validate at invocation time that the requested Skill supports parallel section processing and refuse with a clear message for incompatible Skills.

### Handling ppw:de-ai in Parallel Mode

The de-ai Skill has a two-phase workflow (detect -> user-selects -> rewrite) that requires user interaction between phases. In parallel orchestration:

- **Option A (recommended):** Force `direct` mode and auto-select "Fix all High Risk + Medium Risk" for subagent runs. Users who want fine-grained control should run de-ai serially.
- **Option B:** Collect all detection reports from all section agents, present a unified detection report to the user, let them select across all sections, then dispatch rewrite agents.

Option A is simpler and aligns with the "speed vs. control" tradeoff: parallel mode = speed, serial mode = control.

---

## MVP Definition

### Launch With (v2.1.0)

Minimum viable orchestrator -- validates the concept with the most common use case.

- [ ] **T1: Section Splitter** -- Parse paper into H1 sections with LaTeX/Markdown awareness
- [ ] **T2: Single-Skill Parallel Dispatch** -- Run one Skill across all sections via subagents
- [ ] **T3: Result Merger** -- Reassemble processed sections into a unified document
- [ ] **T4: Progress Display** -- Bilingual status updates during execution
- [ ] **T5: Error Handling** -- Graceful per-section failure with original content preservation
- [ ] **T6: Shared Settings** -- Propagate journal, mode, glossary to all agents

**Why this set:** These 6 features form the minimum closed loop: split -> dispatch -> track -> merge -> handle errors. Without any one of them, the orchestrator is incomplete. The most common use case (parallel polish or parallel translate) is fully served.

### Add After Validation (v2.1.x)

Features to add once the core loop works reliably.

- [ ] **D1: Consistency Review** -- Add when users report terminology/style drift in merged output (expected quickly)
- [ ] **D4: Workflow Memory** -- Add when team invocations become repetitive (low effort, high polish)
- [ ] **D5: Smart Section Grouping** -- Add when users report cost concerns or short-section quality issues

### Future Consideration (v2.2+)

Features to defer until the orchestrator is battle-tested.

- [ ] **D2: Multi-Skill Pipeline Mode** -- Complex feature requiring stage-by-stage output format mapping. Defer until single-skill mode is stable.
- [ ] **D3: User Intervention Points** -- Only meaningful with pipeline mode. Defer together.

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| T1: Section Splitter | HIGH | MEDIUM | P1 |
| T2: Parallel Dispatch | HIGH | HIGH | P1 |
| T3: Result Merger | HIGH | MEDIUM | P1 |
| T4: Progress Display | MEDIUM | LOW | P1 |
| T5: Error Handling | HIGH | MEDIUM | P1 |
| T6: Shared Settings | HIGH | LOW | P1 |
| D1: Consistency Review | HIGH | HIGH | P2 |
| D4: Workflow Memory | LOW | LOW | P2 |
| D5: Smart Grouping | MEDIUM | MEDIUM | P2 |
| D2: Pipeline Mode | MEDIUM | HIGH | P3 |
| D3: Intervention Points | LOW | MEDIUM | P3 |

**Priority key:**
- P1: Must have for launch -- the core orchestration loop
- P2: Should have -- adds quality and polish after core works
- P3: Nice to have -- future evolution of the orchestrator

---

## Competitor/Prior Art Analysis

| Feature | Claude Code Subagents | Agent Teams (Experimental) | Third-Party (Claude Flow, Superpowers) | PPW Orchestrator Approach |
|---------|----------------------|---------------------------|---------------------------------------|--------------------------|
| Parallel execution | Yes (via Agent tool, background mode) | Yes (multi-session) | Yes (various modes) | Use subagents -- stable, sufficient |
| Progress tracking | Background task notifications | Shared task list, teammate status | Framework-specific dashboards | Conversation-based bilingual status |
| Result merging | Manual (caller synthesizes) | Manual (lead synthesizes) | Framework-dependent | Automatic section-order reassembly |
| Inter-agent communication | No (one-way to caller) | Yes (mailbox, broadcast) | Yes (various protocols) | Not needed -- post-merge consistency review instead |
| Pipeline composition | Manual chaining | Manual via lead instructions | Built-in (e.g., Claude Flow streams) | Deferred to v2.2 (D2) |
| Error handling | Subagent failure visible to caller | Teammate stop/error events | Framework-dependent | Per-section graceful degradation |
| Domain specificity | Generic (any coding task) | Generic (any task) | Generic | Academic paper-specific (section types, LaTeX awareness, journal constraints) |

**PPW's differentiator is domain specificity.** Generic orchestration frameworks handle arbitrary tasks. PPW's orchestrator understands paper structure (H1/H2 sections, LaTeX formatting, journal templates, expression patterns) and leverages the existing 13 Skills as pre-built, battle-tested processing units. No other tool provides parallel academic paper processing with terminology consistency review.

---

## Sources

- [Claude Code Subagents Documentation](https://code.claude.com/docs/en/sub-agents) -- Official docs on custom subagents, Agent tool, foreground/background execution [HIGH confidence]
- [Claude Code Agent Teams Documentation](https://code.claude.com/docs/en/agent-teams) -- Official docs on experimental agent teams [HIGH confidence]
- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills) -- Official docs on Skill composition and orchestration [HIGH confidence]
- [Multi-Agent Parallel Execution: Running Multiple AI Agents Simultaneously](https://skywork.ai/blog/agent/multi-agent-parallel-execution-running-multiple-ai-agents-simultaneously/) -- Patterns for parallel content processing, merge strategies, consistency checks [MEDIUM confidence]
- [AI Document Consistency and Reducing Conflicts](https://www.testmanagement.com/blog/2025/11/ai-document-consistency/) -- Consistency patterns in AI document processing [MEDIUM confidence]
- [AI Agent Orchestration Patterns - Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns) -- Sequential pipeline, parallel dispatch, routing patterns [HIGH confidence]
- [Developer's Guide to Multi-Agent Patterns in ADK](https://developers.googleblog.com/developers-guide-to-multi-agent-patterns-in-adk/) -- Google's ADK patterns for sequential and parallel agents [MEDIUM confidence]
- [Anthropic Engineering: Building a C Compiler with Parallel Claudes](https://www.anthropic.com/engineering/building-c-compiler) -- Real-world case study of 16 parallel agents, task locking, coordination [HIGH confidence]
- [Claude Code Sub-Agent Best Practices](https://claudefa.st/blog/guide/agents/sub-agent-best-practices) -- Community patterns for subagent orchestration [MEDIUM confidence]
- [aaddrick/claude-pipeline](https://github.com/aaddrick/claude-pipeline) -- Open-source Claude Code pipeline with skills, agents, orchestration scripts [LOW confidence]

---
*Feature research for: Team Agents Orchestration Layer (PPW v2.1)*
*Researched: 2026-03-19*
