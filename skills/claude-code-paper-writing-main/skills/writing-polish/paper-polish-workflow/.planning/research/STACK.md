# Stack Research: v2.1 Team Agents Orchestration

**Domain:** Claude Code Skill suite for academic paper writing -- v2.1 orchestration layer
**Researched:** 2026-03-19
**Confidence:** HIGH (official docs verified for all core APIs)

> The v1.0/v2.0 stack (pure markdown Skills, shared reference library, Semantic Scholar MCP, AskUserQuestion, Workflow Memory) is validated and unchanged. This document covers ONLY the stack additions needed for v2.1: team agents orchestration via Claude Code's built-in Agent tool and subagent infrastructure. **No external dependencies are added.**

---

## Validated Stack (DO NOT re-research)

| Component | Status | Notes |
|-----------|--------|-------|
| 13 SKILL.md files in `.claude/skills/ppw-*/` | Validated | ppw:* namespace, all convention-compliant |
| Shared reference library (`references/`) | Validated | Expression patterns, anti-AI, journals, bilingual spec |
| Semantic Scholar MCP | Validated | BibTeX-from-MCP-only rule |
| AskUserQuestion tool | Validated | Structured interaction for user decisions |
| Workflow Memory system | Validated | `.planning/workflow-memory.json` |
| Platform: Claude Code only | Validated | No npm packages, no build steps |

---

## New Stack Components for v2.1

### 1. The Agent Tool (Primary Orchestration Primitive)

**What:** Claude Code's built-in `Agent` tool (renamed from `Task` in v2.1.63; `Task(...)` still works as an alias) spawns isolated subagent instances. This is the ONLY mechanism for the `ppw:team` orchestrator Skill to parallelize work across paper sections.

**Agent Tool Input Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | Yes | The task for the subagent to perform |
| `description` | string | Yes | Short (3-5 word) description of the task |
| `subagent_type` | string | Yes | Which subagent definition to use (built-in: `Explore`, `Plan`, `general-purpose`; or custom name from `.claude/agents/`) |
| `model` | enum | No | `"sonnet"`, `"opus"`, `"haiku"`, or full model ID (e.g., `claude-sonnet-4-6`). Defaults to `inherit` (parent model) |
| `run_in_background` | boolean | No | `true` = async execution, parent continues. `false` = blocking. Default: `false` |
| `max_turns` | number | No | Maximum agentic turns before the subagent stops |
| `name` | string | No | Display name for the subagent |
| `mode` | enum | No | `"acceptEdits"`, `"bypassPermissions"`, `"default"`, `"dontAsk"`, `"plan"` |
| `resume` | string | No | Agent ID to resume a previously stopped subagent |
| `team_name` | string | No | For Agent Teams only (NOT used for basic subagents) |
| `isolation` | enum | No | `"worktree"` = run in temporary git worktree |

**Agent Tool Output:**

The return value is discriminated on `status`:
- `"completed"` -- subagent finished, result contains final message
- `"async_launched"` -- background subagent started, returns agent ID for later resume
- `"sub_agent_entered"` -- interactive subagent (foreground)

**Confidence:** HIGH -- parameters verified against official Claude Code docs (code.claude.com/docs/en/sub-agents) and SDK reference.

### 2. Custom Subagent Definitions (`.claude/agents/`)

**What:** Markdown files with YAML frontmatter that define reusable subagent configurations. The `ppw:team` orchestrator will use these to spawn section-processing agents with the right tool access and preloaded skills.

**File format:**

```markdown
---
name: ppw-section-worker
description: Process a single paper section with a specified ppw Skill
tools: Read, Write, Edit, Grep, Glob, Bash
model: inherit
skills:
  - ppw-polish
  - ppw-translation
maxTurns: 50
---

You are a paper section processor. You receive a section of an academic paper
and a skill to apply. Process the section according to the skill's instructions.

[System prompt content here]
```

**Supported Frontmatter Fields:**

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `name` | Yes | string | Unique identifier (lowercase, hyphens) |
| `description` | Yes | string | When Claude should delegate to this subagent |
| `tools` | No | string/list | Tools the subagent can use. **Inherits ALL tools from parent if omitted** |
| `disallowedTools` | No | string/list | Tools to deny (removed from inherited set) |
| `model` | No | string | `"sonnet"`, `"opus"`, `"haiku"`, full model ID, or `"inherit"`. Default: `"inherit"` |
| `permissionMode` | No | string | `"default"`, `"acceptEdits"`, `"dontAsk"`, `"bypassPermissions"`, `"plan"` |
| `maxTurns` | No | number | Max agentic turns before stop |
| `skills` | No | list | Skills to inject into subagent context at startup (full content, not just description) |
| `mcpServers` | No | list | MCP servers available to this subagent |
| `hooks` | No | object | Lifecycle hooks scoped to this subagent |
| `memory` | No | string | `"user"`, `"project"`, or `"local"` for persistent memory |
| `background` | No | boolean | Always run as background task. Default: `false` |
| `isolation` | No | string | `"worktree"` for git worktree isolation |

**Storage locations (priority order):**

| Location | Scope | Priority |
|----------|-------|----------|
| `--agents` CLI flag (JSON) | Current session | 1 (highest) |
| `.claude/agents/` | Current project | 2 |
| `~/.claude/agents/` | All projects | 3 |
| Plugin `agents/` dir | Where plugin is enabled | 4 (lowest) |

**For this project:** Use `.claude/agents/` (project scope, checked into version control).

**Confidence:** HIGH -- verified against official docs.

### 3. Subagent Tool Access Model

**Critical design constraint:** Subagents inherit ALL tools from the parent conversation by default, including MCP tools. This means section-processing subagents will have access to Semantic Scholar MCP, Read, Write, Edit, Glob, Grep, Bash, and AskUserQuestion -- unless explicitly restricted.

**Tool restriction mechanisms:**

| Method | Syntax | Effect |
|--------|--------|--------|
| Allowlist | `tools: Read, Grep, Glob` | Only these tools available |
| Denylist | `disallowedTools: Write, Edit` | All tools EXCEPT these |
| Spawn restriction | `tools: Agent(worker, researcher)` | Restricts which subagent types can be spawned |
| No `Agent` in tools list | `tools: Read, Write` (omit Agent) | Cannot spawn any subagents |

**CRITICAL LIMITATION: Subagents cannot spawn other subagents.** This is a hard platform constraint. The `Agent` tool is not available to subagents regardless of the `tools` field. Only the main thread can spawn subagents. This means the `ppw:team` orchestrator MUST be the main conversation, not a subagent itself.

**What subagents CAN do:**
- Read and write files
- Run Bash commands
- Use Glob, Grep for search
- Access MCP servers (Semantic Scholar)
- Use AskUserQuestion (foreground only; background subagents auto-deny AskUserQuestion)
- Read CLAUDE.md files (auto-loaded from working directory)

**What subagents CANNOT do:**
- Spawn other subagents (hard limit)
- Access parent conversation history
- Communicate with sibling subagents (unless using Agent Teams)
- Use AskUserQuestion when running in background

**Confidence:** HIGH -- verified against official docs. The "cannot spawn other subagents" constraint is explicitly documented.

### 4. Skill Injection via `skills:` Field

**What:** The `skills:` frontmatter field on a subagent definition injects the FULL CONTENT of specified skills into the subagent's system prompt at startup. This is how section-processing subagents get ppw Skill knowledge.

**How it works:**
1. Subagent definition lists `skills: [ppw-polish]` in frontmatter
2. At spawn time, Claude Code reads `.claude/skills/ppw-polish/SKILL.md` in its entirety
3. Full skill content is injected into the subagent's context (not just the description)
4. The subagent receives: its own system prompt (markdown body) + injected skill content + CLAUDE.md

**Key behaviors:**
- Subagents do NOT inherit skills from the parent conversation -- must be listed explicitly
- Full content injection means the ~300 line skill body is loaded into context
- Multiple skills can be listed: `skills: [ppw-translation, ppw-polish, ppw-de-ai]`
- This consumes subagent context proportional to combined skill sizes

**For the ppw:team orchestrator:** The orchestrator Skill runs in the main conversation. It spawns subagents using the Agent tool, passing skill content via the `prompt` parameter OR using pre-defined agent definitions with `skills:` field. The trade-off:

| Approach | Pros | Cons |
|----------|------|------|
| Inline prompt (pass skill instructions in Agent `prompt` parameter) | Flexible, no extra files | Duplicates skill content, hard to maintain |
| Pre-defined agents with `skills:` field | DRY, skill content stays in SKILL.md | Requires one `.claude/agents/` file per skill combo |
| Generic agent + dynamic skill name in prompt | Single agent definition, orchestrator tells it which skill to invoke | Subagent must `/skill-name` or load skill content itself |

**Recommended approach:** Use a SINGLE generic worker agent definition (`.claude/agents/ppw-section-worker.md`) that receives its task via the `prompt` parameter. The orchestrator constructs prompts that include: (a) the section content, (b) the skill to apply, and (c) any section-specific context. The worker agent definition sets up tools and model, while the orchestrator controls what the worker does.

**Why not pre-define per-skill agents:** The project has 13 skills. Creating 13 agent definitions (ppw-polish-worker, ppw-translation-worker, etc.) would be redundant. A single generic worker with the right tools is sufficient because the orchestrator controls the prompt.

**Confidence:** HIGH -- `skills:` field behavior verified in official docs.

### 5. Model Selection Strategy

**What:** Choosing which model subagents run on affects cost, quality, and latency.

**Available options:**

| Model | Alias | Best For | Cost |
|-------|-------|----------|------|
| Claude Opus 4.6 | `"opus"` | Complex reasoning, nuanced writing | Highest |
| Claude Sonnet 4.6 | `"sonnet"` | Balanced quality/cost for focused tasks | Medium |
| Claude Haiku 4.5 | `"haiku"` | Fast, simple tasks (exploration, search) | Lowest |
| `"inherit"` | (default) | Use parent model | Same as parent |

**Model configuration hierarchy:**
1. `model` field in `.claude/agents/` frontmatter (per-agent definition)
2. `model` parameter in Agent tool call (per-invocation override)
3. `CLAUDE_CODE_SUBAGENT_MODEL` env var (global default for agents without explicit model)
4. `inherit` (parent model)

**Recommended strategy for ppw:team:**

| Agent Role | Model | Rationale |
|------------|-------|-----------|
| Orchestrator (main conversation) | Opus (user's default) | Complex coordination, decision-making |
| Section processing workers | `"sonnet"` | Focused text processing tasks, good quality at lower cost |
| Consistency reviewer | `"sonnet"` or `"opus"` | Cross-section analysis needs stronger reasoning |
| Section splitter/parser | `"haiku"` | Simple structural parsing, low cost |

**IMPORTANT: `CLAUDE_CODE_SUBAGENT_MODEL` only affects agents without an explicit model defined.** It does NOT override the `model` field in agent definitions or built-in agents.

**Cost implications:** Multi-agent workflows use 3-7x more tokens than single sessions. For a paper with 6 sections processed in parallel with Sonnet workers, expect ~4x the token cost of sequential processing with one session. This is acceptable because the time savings are substantial.

**Confidence:** HIGH -- model options verified against official docs and GitHub issue #25546.

### 6. Parallel Execution Model

**What:** How the Agent tool handles concurrent subagent execution.

**Mechanism:**
- Set `run_in_background: true` to launch non-blocking subagents
- The parent receives an agent ID for each background subagent
- Parent can continue spawning more subagents or doing other work
- When a background subagent completes, the parent is notified
- Use `SendMessage` with the agent ID to resume a completed subagent

**Practical limits:**
- Platform cap: ~10 concurrent subagents (community-reported, not in official docs)
- Recommended for most workflows: 3-5 concurrent agents
- Each subagent has its own context window (~200K tokens)
- Token costs scale linearly with number of concurrent agents

**For ppw:team -- parallel section processing:**

```
Orchestrator spawns N background subagents (one per section):

Agent({
  description: "Polish introduction section",
  subagent_type: "ppw-section-worker",
  model: "sonnet",
  prompt: "Apply ppw:polish workflow to this section:\n\n[section content]\n\nFollow these instructions:\n[skill instructions]\n\nOutput the polished text only.",
  run_in_background: true
})

Agent({
  description: "Polish methods section",
  subagent_type: "ppw-section-worker",
  model: "sonnet",
  prompt: "Apply ppw:polish workflow to this section:\n\n[section content]\n...",
  run_in_background: true
})

// ... one per section

// Orchestrator waits for all to complete, then runs consistency review
```

**Background vs Foreground trade-offs for this project:**

| Mode | Use When | AskUserQuestion | Permission Prompts |
|------|----------|-----------------|-------------------|
| Background (`run_in_background: true`) | Parallel section processing | Auto-denied (fails silently) | Pre-approved at spawn time |
| Foreground (blocking) | Consistency review, single-section with user interaction | Works normally | Interactive prompts |

**Critical implication:** Background subagents CANNOT use AskUserQuestion. This means section workers running in parallel cannot ask the user for clarification. The orchestrator must provide all necessary context upfront in the prompt. This aligns well with the ppw workflow because:
- The user has already made all decisions (journal, mode, settings) before the orchestrator dispatches
- Section content is fully specified before dispatch
- Workers apply a deterministic skill pipeline

**Confidence:** HIGH for mechanism. MEDIUM for the "10 concurrent" limit (community-reported, not in official docs -- practical limit may vary by subscription tier and system resources).

### 7. Agent Teams vs Subagents Decision

**Decision: Use SUBAGENTS, not Agent Teams.**

| Factor | Subagents | Agent Teams |
|--------|-----------|-------------|
| Complexity | Simple spawn-and-collect | Complex team lifecycle management |
| Communication needs | Report back to parent only | Inter-agent messaging, shared task list |
| Our use case | Section workers report polished text back | Workers don't need to talk to each other |
| Stability | Stable, production-ready | Experimental, known limitations |
| Requirements | None | `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` env var |
| Session resumption | Works | Known issues with in-process teammates |
| Nested spawning | N/A (workers don't need to spawn) | No nested teams allowed |
| Cost | 3-4x for parallel | 3-7x with coordination overhead |
| Platform support | All terminals | Split panes require tmux/iTerm2 (not Windows Terminal) |

**Why NOT Agent Teams:**
1. Section workers are independent -- they don't need to communicate with each other
2. Agent Teams are experimental with documented reliability issues
3. The project runs on Windows (split pane mode not supported on Windows Terminal)
4. Agent Teams add coordination overhead without benefit for our embarrassingly parallel workload
5. The orchestrator can collect results from subagents and do cross-section consistency review itself

**When Agent Teams WOULD make sense (future consideration):**
- If section workers needed to share terminology decisions in real-time
- If the consistency review needed iterative back-and-forth between workers
- Neither of these is required for the current design

**Confidence:** HIGH -- this is a clear architectural decision based on verified feature comparison.

### 8. `context: fork` in Skills (Relevant but NOT the primary mechanism)

**What:** Skills can set `context: fork` in frontmatter to run in an isolated subagent context. This is an alternative to the orchestrator-spawns-Agent approach.

**How it works:**
```yaml
---
name: ppw:polish
context: fork
agent: ppw-section-worker
---
```

When invoked, the skill content becomes the subagent's prompt, and the specified `agent:` type provides tools/model/permissions.

**Why NOT use `context: fork` for orchestration:**
1. `context: fork` runs ONE subagent per skill invocation -- no parallel dispatch
2. The orchestrator needs to spawn MULTIPLE subagents simultaneously
3. `context: fork` is invoked by the Skill tool, not the Agent tool -- different mechanics
4. The orchestrator needs control over prompt construction (include section content, skill instructions, cross-section context)
5. Known issue: GitHub #17283 reports `context: fork` and `agent:` fields can be ignored when invoked via the Skill tool

**Where `context: fork` IS useful:** Individual skill invocation (non-orchestrated). A user running `/ppw:polish` on a long document could benefit from `context: fork` to isolate the polishing context. This is orthogonal to the orchestration layer.

**Confidence:** HIGH -- verified against official docs and known issues.

### 9. Subagent Resume Mechanism (SendMessage)

**What:** After a background subagent completes, the orchestrator receives its agent ID. The orchestrator can resume the subagent using `SendMessage` with the agent ID.

**How it works:**
1. Background subagent completes -> parent notified with agent ID
2. Parent calls `SendMessage({ to: "<agent-id>", message: "..." })` to resume
3. Resumed subagent retains full conversation history from previous run
4. Subagent transcripts persist at `~/.claude/projects/{project}/{sessionId}/subagents/agent-{agentId}.jsonl`

**Use case for ppw:team:**
- After initial polish pass, orchestrator reviews consistency
- Finds a terminology issue in Section 3
- Resumes Section 3's subagent with correction instructions
- Subagent already has the section context, applies targeted fix

**Confidence:** HIGH -- documented in official docs.

---

## Recommended Architecture for ppw:team

### File Structure

```
.claude/
  agents/
    ppw-section-worker.md    # Generic worker agent definition
  skills/
    ppw-team/
      SKILL.md               # Orchestrator skill (the new one)
```

### ppw-section-worker.md (Agent Definition)

```markdown
---
name: ppw-section-worker
description: Processes a single paper section with specified ppw skill instructions. Used by ppw:team orchestrator.
tools: Read, Write, Edit, Grep, Glob
model: sonnet
maxTurns: 50
---

You are a paper section processor for the Paper Polish Workflow.

You receive:
1. A section of academic text to process
2. Skill instructions describing how to process it
3. Any section-specific context (journal style, terminology glossary, etc.)

Execute the skill instructions faithfully on the provided section.
Output ONLY the processed text result. Do not add commentary.
```

### ppw:team/SKILL.md (Orchestrator Skill -- Conceptual)

The orchestrator Skill runs in the main conversation (NOT forked). It:

1. Receives user request (which skill(s) to apply, to which paper)
2. Reads the paper and splits by H1/H2 sections
3. Asks user to confirm section split and skill selection
4. Spawns N background subagents (one per section) via Agent tool
5. Collects results as subagents complete
6. Runs consistency review (terminology, style, tone)
7. Presents results to user with intervention option
8. Applies corrections if needed (resume subagents or inline fix)

---

## What NOT to Add

| Temptation | Why Resist |
|-----------|------------|
| Agent Teams (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) | Experimental, Windows Terminal unsupported, unnecessary for independent section processing |
| External orchestration framework (claude-code-workflow-orchestration, etc.) | Adds dependency; built-in Agent tool is sufficient |
| npm packages for task queue/scheduling | Pure markdown Skill constraint; Agent tool handles async natively |
| Custom MCP server for inter-agent communication | Subagents don't need to communicate; orchestrator collects results |
| Multiple agent definitions (one per skill) | Single generic worker + orchestrator-controlled prompt is simpler |
| Database for tracking agent state | Agent transcripts persist in `~/.claude/projects/`; markdown state files suffice |
| Git worktree isolation per section | Sections don't conflict on files; worktree overhead is unnecessary for text processing |
| `memory` field on section workers | Workers are ephemeral (one-shot section processing); no cross-session learning needed |

---

## Alternatives Considered

| Decision | Recommended | Alternative | Why Not Alternative |
|----------|-------------|-------------|---------------------|
| Orchestration mechanism | Agent tool (subagents) | Agent Teams | Experimental, inter-agent messaging not needed, Windows Terminal unsupported |
| Worker definition | Single generic `ppw-section-worker` | Per-skill agents (ppw-polish-worker, ppw-translation-worker, ...) | 13 redundant files; orchestrator prompt handles skill specialization |
| Skill injection | Pass instructions in Agent `prompt` parameter | Use `skills:` frontmatter to preload skills | `skills:` loads FULL skill content (~300 lines) into every worker's context; prompt-based is more targeted and lighter |
| Model for workers | `sonnet` | `inherit` (opus) | Sonnet is sufficient for focused text tasks; opus would 3x the cost for marginal quality gain |
| Background vs foreground | Background for parallel sections | All foreground (sequential) | Sequential defeats the purpose of orchestration; parallel is 3-5x faster |
| Section splitting | Orchestrator parses H1/H2 in main conversation | Dedicated splitter subagent | Splitting is simple regex/parsing; doesn't justify subagent overhead |
| Consistency review | Orchestrator runs it inline (main conversation) | Dedicated reviewer subagent | Reviewer needs cross-section context that is naturally available in the main conversation |
| User interaction | AskUserQuestion in orchestrator (main conversation) before/after dispatch | AskUserQuestion in workers | Background workers auto-deny AskUserQuestion; all user decisions must happen before dispatch |

---

## Compatibility with v1.0/v2.0 Stack

| Existing Component | v2.1 Impact | Action |
|-------------------|-------------|--------|
| 13 existing SKILL.md files | No changes | Skill content is read by orchestrator and passed to workers |
| `references/` library | No changes | Workers can read reference files via Read tool |
| skill-conventions.md | May need orchestration section | Document Agent tool usage patterns |
| Workflow Memory system | Extended | Record `ppw:team` invocations and skill chain patterns |
| CLAUDE.md | No changes | Workers auto-load CLAUDE.md from working directory |
| Semantic Scholar MCP | Available to workers | Workers inherit MCP access if not restricted |
| AskUserQuestion | Used by orchestrator only | Workers in background cannot use it |

**Breaking changes:** None. The orchestrator is a new Skill (`ppw:team`); the worker is a new agent definition (`ppw-section-worker`). All existing Skills continue to work independently.

---

## Version Compatibility

| Component | Minimum Version | Notes |
|-----------|----------------|-------|
| Claude Code | v2.1.32+ | Required for Agent Teams (not used, but good baseline) |
| Claude Code | v2.1.63+ | Agent tool name (Task still works as alias) |
| `.claude/agents/` format | Current | YAML frontmatter + markdown body |
| `.claude/skills/` format | Current | No format changes needed |
| `CLAUDE_CODE_SUBAGENT_MODEL` env var | Current | Optional; per-agent `model` field is preferred |

---

## Sources

### Official Documentation (HIGH confidence)
- [Create custom subagents -- Claude Code Docs](https://code.claude.com/docs/en/sub-agents) -- Complete subagent API, frontmatter fields, tool access, model selection, `skills:` field, `context: fork`, nesting limitation
- [Orchestrate teams of Claude Code sessions -- Claude Code Docs](https://code.claude.com/docs/en/agent-teams) -- Agent Teams architecture, TeamCreate/TaskCreate/SendMessage, limitations, comparison with subagents
- [Extend Claude with skills -- Claude Code Docs](https://code.claude.com/docs/en/skills) -- Skill frontmatter reference, `context: fork`, `agent:` field, progressive disclosure

### GitHub Issues (HIGH confidence)
- [Issue #25546: Allow configuring model for built-in agents](https://github.com/anthropics/claude-code/issues/25546) -- `CLAUDE_CODE_SUBAGENT_MODEL` limitation with built-in agents
- [Issue #32723: TeamCreate/TeamDelete available to standalone subagents](https://github.com/anthropics/claude-code/issues/32723) -- Subagents have TeamCreate in toolset but cannot populate teams (no Agent tool)
- [Issue #17283: Skill tool should honor context: fork and agent: fields](https://github.com/anthropics/claude-code/issues/17283) -- Known issue with `context: fork` being ignored

### Community Sources (MEDIUM confidence)
- [Claude Code Sub-Agents: Parallel vs Sequential Patterns](https://claudefa.st/blog/guide/agents/sub-agent-best-practices) -- Parallel execution patterns, merge conflict warnings
- [Claude Code Agent Teams: The Practical Guide](https://blog.laozhang.ai/en/posts/claude-code-agent-teams) -- Agent Teams architecture, cost analysis
- [From Tasks to Swarms: Agent Teams in Claude Code](https://alexop.dev/posts/from-tasks-to-swarms-agent-teams-in-claude-code/) -- TeamCreate/TaskCreate/SendMessage parameters, swarm patterns
- [Master Claude Code Custom Subagents](https://stephenvantran.com/posts/2025-07-25-claude-code-custom-subagents/) -- 10 concurrent subagent limit (community-reported)

---
*Stack research for: v2.1 Team Agents Orchestration*
*Researched: 2026-03-19*
