# Architecture Research: Team Agents Orchestration Layer

**Domain:** Multi-agent orchestration for academic paper writing Skills
**Researched:** 2026-03-19
**Confidence:** HIGH

## System Overview

```
User invokes /ppw:team
         |
         v
+---------------------------+
|  ppw:team Skill (main)    |  <-- Runs in main conversation
|  - Parse user intent      |
|  - Split paper sections   |
|  - Configure pipeline     |
|  - Display plan for       |
|    user confirmation      |
+---------------------------+
         |
         | User confirms plan
         v
+---------------------------+
|  Orchestrator dispatches  |  <-- Spawns via Agent tool
|  subagents in parallel    |
+---------------------------+
    |        |        |
    v        v        v
+-------+ +-------+ +-------+
| Agent | | Agent | | Agent |   <-- Each is a subagent with
| Sec 1 | | Sec 2 | | Sec 3 |       injected ppw:* Skill instructions
+-------+ +-------+ +-------+
    |        |        |
    v        v        v
+---------------------------+
|  .paper-team/sections/    |  <-- File-based data exchange
|  sec1_out.tex             |
|  sec2_out.tex             |
|  sec3_out.tex             |
+---------------------------+
         |
         v
+---------------------------+
|  Merge + Consistency      |  <-- Subagent or inline
|  Review                   |
+---------------------------+
         |
         v
   Final output file(s)
```

## Critical Architecture Decision: Skill vs. Subagent vs. Hybrid

### The Constraint

Claude Code's architecture has a fundamental rule: **subagents cannot spawn other subagents**. This means:

- A Skill running in the main conversation CAN spawn subagents (via Agent tool)
- A subagent CANNOT spawn further subagents
- Skills run in the main conversation context; subagents run in isolated contexts

### Recommendation: ppw:team as a Skill (NOT a subagent)

The orchestrator **must be a Skill** (`.claude/skills/ppw-team/SKILL.md`), not a custom subagent, because:

1. **It needs to spawn subagents.** The Agent tool is available in the main conversation. Only the main conversation (or a `--agent` session) can spawn subagents; subagents themselves cannot.
2. **It needs user interaction.** AskUserQuestion works in the main conversation. Background subagents auto-deny AskUserQuestion calls.
3. **It follows existing conventions.** All 13 existing capabilities are Skills invoked via `/ppw:*`. Adding `/ppw:team` is consistent.
4. **It needs to orchestrate file I/O.** The orchestrator must read the input paper, split it, write section files, then merge outputs -- all coordinated with the user.

### Worker Agents: Custom Subagents with Preloaded Skills

Each section-processing worker is a **custom subagent** defined in `.claude/agents/`:

```yaml
# .claude/agents/ppw-worker.md
---
name: ppw-worker
description: Process a single paper section using a ppw Skill
model: inherit
permissionMode: acceptEdits
skills:
  - ppw-polish      # Preloaded -- full Skill content injected at startup
  - ppw-de-ai       # (Which skills to preload depends on the pipeline)
  - ppw-translation
---

You are a paper section processor. You receive:
1. A section file path to process
2. Which Skill workflow to apply (polish, de-ai, translation, etc.)
3. Configuration (target journal, mode, bilingual settings)

Execute the Skill workflow on the section file and write the result.
```

**Why preloaded Skills, not Skill invocation from within subagents?**

The `skills` field in subagent frontmatter **injects full Skill content into the subagent's context at startup**. This is different from the subagent "invoking" a Skill at runtime. The subagent receives the instructions and follows them directly. This works because:

- ppw Skills are pure markdown instructions (no code execution, no build steps)
- Skills describe a workflow the agent should follow, which the subagent can execute
- Reference files (expression patterns, anti-AI patterns) can be read by the subagent via Read tool
- The subagent has all tools it needs (Read, Edit, Write, Grep, Glob)

**Key limitation:** A single generic `ppw-worker` subagent that dynamically loads different Skills is NOT possible because the `skills` field is static YAML. Instead, we need **one subagent definition per Skill** (or per common pipeline combination):

```
.claude/agents/
  ppw-worker-polish.md       # Preloads ppw-polish
  ppw-worker-de-ai.md        # Preloads ppw-de-ai
  ppw-worker-translation.md  # Preloads ppw-translation
  ppw-worker-translate-polish-deai.md  # Preloads all three for pipeline
  ppw-worker-consistency.md  # Preloads consistency review instructions
```

**Alternative approach (simpler, recommended):** Instead of using the `skills` field, the orchestrator Skill can use the Agent tool directly and pass the Skill instructions as the task prompt. The Agent tool accepts a prompt string; the orchestrator can construct this prompt dynamically:

```
Agent({
  prompt: "Read the file at {section_path}. Apply the following polish
           workflow: {inline skill instructions or reference to skill}.
           Write output to {output_path}.",
  tools: ["Read", "Edit", "Write", "Grep", "Glob"]
})
```

This is simpler because:
- No need to create multiple agent definition files
- The orchestrator constructs the prompt dynamically based on the pipeline
- Works for any Skill combination without pre-defining agents
- The Agent tool's general-purpose subagent already inherits the model and tools

**Recommended approach: Hybrid.** Use the simpler Agent tool approach for the initial implementation (no custom agent files needed). If performance or context overhead becomes an issue, create dedicated agent files with preloaded Skills.

## Component Responsibilities

| Component | Responsibility | Location | New vs Existing |
|-----------|---------------|----------|-----------------|
| `ppw:team` Skill | User-facing orchestrator: parse intent, plan, dispatch, merge, report | `.claude/skills/ppw-team/SKILL.md` | **NEW** |
| Section Splitter | Parse paper into H1/H2 sections, write to temp files | Reference file or inline in ppw:team | **NEW** |
| Section Merger | Reassemble processed sections into final output | Reference file or inline in ppw:team | **NEW** |
| Consistency Reviewer | Post-merge terminology/style/tone check across all sections | Subagent or inline in ppw:team | **NEW** |
| Worker subagents | Execute a ppw Skill on a single section file | Spawned via Agent tool | **NEW** (dynamic) |
| Existing ppw:* Skills | Section-level text processing (polish, de-ai, translation, etc.) | `.claude/skills/ppw-*/SKILL.md` | **UNCHANGED** |
| Reference files | Expression patterns, anti-AI patterns, journal templates | `references/` | **UNCHANGED** |
| Workflow Memory | Record ppw:team invocations | `.planning/workflow-memory.json` | **UNCHANGED** (extended) |

## Data Flow: Full Lifecycle

### Phase 1: Input and Planning

```
User: /ppw:team polish my paper sections/paper.tex
         |
         v
[ppw:team Skill activates in main conversation]
         |
         v
[Step 1: Read input file]
  - Read sections/paper.tex
  - Detect section boundaries (H1/H2 via \section{} / \subsection{} or ## / ### markers)
  - Build section map: [{id, title, start_line, end_line, content}]
         |
         v
[Step 2: Plan]
  - Determine mode: single-skill or pipeline
  - Single-skill: "polish all sections" -> ppw:polish on each section
  - Pipeline: "translate then polish then de-ai" -> chain of Skills per section
  - Display plan to user:
    "Will process 6 sections with ppw:polish:
     1. Introduction (lines 1-45)
     2. Study Area and Data (lines 46-89)
     3. Methods (lines 90-156)
     4. Results (lines 157-220)
     5. Discussion (lines 221-280)
     6. Conclusion (lines 281-310)
     Proceed?"
         |
         v
[Step 3: User confirms (AskUserQuestion)]
```

### Phase 2: Section Split and Dispatch

```
[Step 4: Write section files]
  - Create .paper-team/ directory (or .paper-team/{timestamp}/ for isolation)
  - Write each section to .paper-team/sections/sec_{N}_{title_slug}.tex
  - Include section metadata header as LaTeX comment:
    % [ppw:team] Section: Introduction
    % [ppw:team] Source: sections/paper.tex lines 1-45
    % [ppw:team] Pipeline: polish
         |
         v
[Step 5: Spawn worker subagents]
  - For each section, spawn a subagent via Agent tool
  - Pass: section file path, Skill to apply, configuration (journal, mode, bilingual)
  - Subagents run in parallel (Claude Code handles parallel execution natively)
  - Each subagent:
    1. Reads section file
    2. Loads required references (expression patterns, anti-AI patterns, etc.)
    3. Applies Skill workflow (polish/de-ai/translation/etc.)
    4. Writes output to .paper-team/output/sec_{N}_{title_slug}_out.tex
    5. Returns summary to orchestrator
```

### Phase 3: Pipeline Mode (Multi-Skill)

```
[For pipeline mode: translate -> polish -> de-ai]

Stage 1 (parallel):
  Subagent 1: translate sec_1 -> sec_1_translated.tex
  Subagent 2: translate sec_2 -> sec_2_translated.tex
  ...
         |
         v
[Orchestrator collects Stage 1 results]
[Optional: intervention point -- user reviews translated sections]
         |
         v
Stage 2 (parallel):
  Subagent 1: polish sec_1_translated.tex -> sec_1_polished.tex
  Subagent 2: polish sec_2_translated.tex -> sec_2_polished.tex
  ...
         |
         v
[Repeat for each pipeline stage]
```

### Phase 4: Merge and Consistency Review

```
[Step 6: Merge outputs]
  - Read all .paper-team/output/sec_{N}_*_out.tex files in order
  - Concatenate respecting section boundaries
  - Write merged output to paper_polished.tex (or pipeline-appropriate name)
         |
         v
[Step 7: Consistency review]
  - Spawn a consistency-review subagent (or run inline)
  - Check across all merged sections for:
    * Terminology inconsistencies (same concept, different terms)
    * Style/tone shifts between sections
    * Formatting inconsistencies (citation style, heading capitalization)
    * Cross-reference integrity (figures, tables, sections mentioned)
  - Present findings to user
         |
         v
[Step 8: Report]
  - Summary: N sections processed, M consistency issues found
  - Per-section: word count delta, changes applied, warnings
  - Elapsed time
  - Recommend next steps (e.g., "Run ppw:logic for full-paper logic check")
```

## Directory Structure for Team Processing

```
project-root/
├── .paper-team/                    # Team workspace (gitignored)
│   ├── manifest.json              # Session metadata, pipeline config
│   ├── sections/                  # Split input sections
│   │   ├── sec_01_introduction.tex
│   │   ├── sec_02_study_area.tex
│   │   ├── sec_03_methods.tex
│   │   └── ...
│   ├── stage_1/                   # Stage 1 outputs (e.g., translation)
│   │   ├── sec_01_introduction.tex
│   │   └── ...
│   ├── stage_2/                   # Stage 2 outputs (e.g., polish)
│   │   ├── sec_01_introduction.tex
│   │   └── ...
│   ├── output/                    # Final merged output
│   │   └── paper_polished.tex
│   └── consistency/               # Consistency review report
│       └── report.md
├── .claude/
│   └── skills/
│       └── ppw-team/
│           └── SKILL.md           # Orchestrator Skill
└── references/
    └── team-orchestration.md      # (Optional) Orchestration reference patterns
```

### manifest.json Structure

```json
{
  "session_id": "team_20260319_143022",
  "input_file": "sections/paper.tex",
  "pipeline": ["translation", "polish", "de-ai"],
  "sections": [
    {
      "id": 1,
      "title": "Introduction",
      "source_lines": [1, 45],
      "status": "completed",
      "current_stage": 3,
      "stages": {
        "1_translation": {"file": "stage_1/sec_01_introduction.tex", "status": "done"},
        "2_polish": {"file": "stage_2/sec_01_introduction.tex", "status": "done"},
        "3_de-ai": {"file": "output/sec_01_introduction.tex", "status": "done"}
      }
    }
  ],
  "config": {
    "journal": "CEUS",
    "bilingual": true,
    "mode": "direct"
  },
  "consistency_review": {
    "status": "pending",
    "issues": []
  }
}
```

## Architectural Patterns

### Pattern 1: File-Based Data Exchange (NOT In-Memory)

**What:** All data flows between orchestrator and workers through files on disk, not through in-memory passing or return values.

**Why this is the only viable approach:**
- Subagents return only their final text output to the parent. This output is a conversation message, not structured data.
- Processed paper sections can be 5-20KB each. Returning them as subagent text output pollutes the main conversation's context window.
- Files provide natural checkpointing -- if a pipeline fails mid-way, completed stages persist on disk.
- Existing Skills already operate on files (Read/Edit/Write tools). No adaptation needed.

**Trade-offs:**
- Pro: Natural checkpointing, no context pollution, works with existing Skills
- Pro: User can inspect intermediate files for debugging
- Con: Disk I/O overhead (negligible for text files)
- Con: Must manage cleanup of `.paper-team/` directory

### Pattern 2: Prompt-Injected Skill Instructions

**What:** Instead of defining static custom subagent files per Skill, the orchestrator constructs the subagent task prompt dynamically by reading the target Skill's SKILL.md content and passing it as instructions.

**Why:**
- Avoids proliferation of agent definition files (one per Skill, one per pipeline combo)
- Allows any combination of Skills without pre-defining agents
- The Agent tool's general-purpose subagent is sufficient

**Implementation sketch:**

```
# Orchestrator reads the Skill file
skill_content = Read(".claude/skills/ppw-polish/SKILL.md")

# Constructs task prompt
task_prompt = """
You are processing a single paper section.

Input file: .paper-team/sections/sec_01_introduction.tex
Output file: .paper-team/output/sec_01_introduction.tex
Target journal: CEUS
Bilingual mode: ON
Mode: direct

Apply the following Skill workflow to the input file:

{skill_content}

Additional context:
- You are processing one section of a larger paper.
- Other sections are being processed in parallel.
- Load reference files as specified in the Skill's References section.
- Write output to the specified output file path.
- Return a brief summary of changes made.
"""

# Spawn subagent
Agent(task_prompt)
```

**Trade-offs:**
- Pro: Zero new files for the agent definitions
- Pro: Dynamically composable -- any Skill can be orchestrated
- Con: Skill content (up to 300 lines) is included in each subagent's task prompt, consuming context
- Con: Subagent does not receive the full Claude Code system prompt -- only the task prompt plus basic environment info

### Pattern 3: Stage-Gated Pipeline with Intervention Points

**What:** In pipeline mode (e.g., translate -> polish -> de-ai), each stage completes fully before the next begins. Between stages, the orchestrator optionally pauses for user review.

**Why:**
- Prevents cascading errors (a bad translation would produce a bad polish)
- Gives users control at natural checkpoints
- Aligns with existing Skill conventions (two-phase workflow with user confirmation)

**Implementation:**
```
For each stage in pipeline:
  1. Dispatch all sections to worker subagents (parallel)
  2. Wait for all to complete
  3. If intervention_points enabled:
     - Display stage summary to user
     - AskUserQuestion: "Stage [N] complete. Review? [Continue / Review / Abort]"
     - If Review: user inspects files, provides feedback
  4. Move outputs to next stage's input directory
  5. Proceed to next stage
```

**Trade-offs:**
- Pro: User maintains control, prevents cascading failures
- Pro: Natural for academic writing (review translated text before polishing)
- Con: Slower than fully automated pipeline (user must respond at each checkpoint)
- Con: For large papers with 6+ sections and 3-stage pipelines, many checkpoints

### Pattern 4: Section Splitting by Structural Markers

**What:** Parse paper structure using LaTeX (`\section{}`, `\subsection{}`) or Markdown (`#`, `##`) markers to split into independently processable units.

**Why:**
- H1 sections are the natural unit for independent processing -- each has its own semantic context
- H2 splitting is too fine-grained for most Skills (polish/de-ai work best with paragraph context)
- Splitting by H1 preserves enough context for each worker to understand the section's role

**Rules:**
1. Default split level: H1 (`\section{}` / `#`). User can request H2 splitting.
2. Each section file includes a metadata header (source file, line numbers, section title).
3. Preamble content (before first `\section{}`) is preserved separately and not processed.
4. The split preserves all LaTeX formatting, comments, and commands within each section.
5. Cross-references (`\ref{}`, `\cite{}`) are preserved as-is in each section file.

## What Existing Skills Need (Spoiler: Nothing)

A critical architectural finding: **existing ppw:* Skills require ZERO modifications** to support team orchestration.

### Why No Modifications Are Needed

| Existing Skill Behavior | How Orchestration Uses It |
|-------------------------|--------------------------|
| Skills accept file input via Read tool | Orchestrator writes section files; worker reads them |
| Skills output via Edit/Write tool | Worker writes to output path specified by orchestrator |
| Skills load references on-demand | Workers have Read tool access; load references normally |
| Skills have `direct` mode | Orchestrator forces `direct` mode to skip interactive questions |
| Skills support bilingual opt-out | Orchestrator passes bilingual config; worker respects it |
| Skills work on partial text (single section) | Each worker processes one section -- exactly what Skills handle |
| Skills use AskUserQuestion | Workers are foreground subagents OR orchestrator pre-answers |

### The One Consideration: AskUserQuestion in Workers

Some Skills use AskUserQuestion (e.g., experiment-skill asks about research questions, de-ai asks which items to fix). When running as subagents:

- **Foreground subagents:** AskUserQuestion prompts pass through to the user. This works but breaks the parallel experience (user is interrupted per-section).
- **Background subagents:** AskUserQuestion is auto-denied. The Skill falls back per its Fallback rules.
- **Recommended approach:** The orchestrator forces `direct` mode on all worker invocations. In `direct` mode, all Skills skip AskUserQuestion (per skill-conventions.md: "In direct mode, Skills skip all AskUserQuestion calls entirely"). This means:
  - Workers run non-interactively
  - The orchestrator handles all user interaction before dispatching
  - Users configure journal, scope, and preferences once, not per-section

This is the cleanest approach and requires no Skill modifications.

## Which Skills Are Eligible for Orchestration

Not all 13 Skills make sense in a team orchestration context. The key criterion: **does the Skill operate on a section of text (not the whole paper)?**

| Skill | Eligible | Reason |
|-------|----------|--------|
| ppw:polish | YES | Core use case -- polish each section independently |
| ppw:de-ai | YES | Detect and rewrite AI patterns per section |
| ppw:translation | YES | Translate each section independently |
| ppw:caption | MAYBE | Captions are figure/table-level, not section-level |
| ppw:experiment | NO | Requires full results context, not section-splittable |
| ppw:abstract | NO | Operates on full paper to generate abstract |
| ppw:reviewer-simulation | NO | Requires full paper for review assessment |
| ppw:logic | NO | Cross-section verification by definition |
| ppw:cover-letter | NO | Operates on full paper metadata |
| ppw:literature | NO | Search-based, not text-processing |
| ppw:visualization | NO | Recommendation-based, not text-processing |
| ppw:repo-to-paper | NO | Repo scanning, not text-processing |
| ppw:update | NO | Meta-skill for syncing |

**Primary orchestration targets:** polish, de-ai, translation. These three are the core pipeline candidates (translate -> polish -> de-ai is the canonical pipeline).

## Integration Points

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| User <-> ppw:team Skill | AskUserQuestion + conversation | Standard Skill interaction in main context |
| ppw:team Skill <-> Worker subagents | Agent tool (prompt) + file system | Prompt passes config; files pass content |
| Worker subagent <-> Reference files | Read tool | Workers read references independently |
| Worker subagent <-> Output files | Write/Edit tool | Workers write output to designated paths |
| ppw:team Skill <-> Consistency reviewer | Agent tool or inline | Post-merge review can be subagent or inline |
| ppw:team Skill <-> Workflow Memory | Read/Write tool | Record ppw:team invocation per convention |

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Semantic Scholar MCP | NOT used by workers | Workers process text only; lit search is pre-pipeline |
| File system | Primary data exchange | All section files, stage outputs, manifests |

## Scalability Considerations

| Concern | Practical Limit | Mitigation |
|---------|----------------|------------|
| Parallel subagents | Claude Code handles 3-8 concurrent subagents comfortably | Split papers have 4-7 sections typically; fits well |
| Context per worker | ~200K tokens per subagent | A section (1-5 pages) + Skill instructions + references is well under 50K |
| Main conversation context | Subagent outputs return to main context | Workers return only brief summaries; full output is in files |
| Token cost | 4-7x a single-agent session per stage | For a 3-stage pipeline on 6 sections: ~18-42x baseline. Significant but acceptable for batch processing |
| Pipeline stages | Each stage is a full round of parallel subagents | More stages = more total cost; recommend max 3-stage pipelines |

## Anti-Patterns

### Anti-Pattern 1: Skill Calling Skill in Main Conversation

**What people might try:** Having ppw:team invoke `/ppw:polish` as a slash command in the main conversation, serially for each section.

**Why it's wrong:** This runs everything in the main conversation context. Each Skill invocation adds its full output to the context window. Processing 6 sections serially with 3 Skills would consume enormous context and provide no parallelism.

**Do this instead:** Spawn subagents via Agent tool. Each runs in isolated context. Only summaries return to main context.

### Anti-Pattern 2: In-Memory Data Passing via Subagent Returns

**What people might try:** Having each worker subagent return the full processed section text as its Agent tool output, then having the orchestrator concatenate these in-memory.

**Why it's wrong:** Subagent return text goes into the main conversation's context window. Six 3-page sections = ~18 pages of text in main context. Plus the original paper. Plus stage 2 results. Context explodes.

**Do this instead:** Workers write to files. Orchestrator reads files for merge. Main context stays lean.

### Anti-Pattern 3: Creating Custom Agent Files Per Skill Combination

**What people might try:** Pre-defining `ppw-worker-polish.md`, `ppw-worker-translate-polish.md`, `ppw-worker-translate-polish-deai.md`, etc. in `.claude/agents/`.

**Why it's wrong:** Combinatorial explosion. 7 relevant Skills = many possible pipeline combinations. Maintenance nightmare. And the `skills` field is static YAML, so you cannot conditionally load Skills at runtime.

**Do this instead:** Use the Agent tool directly with dynamically constructed prompts. Read the target Skill's SKILL.md at runtime and inject it into the task prompt.

### Anti-Pattern 4: H2-Level Splitting for All Skills

**What people might try:** Splitting at the H2/subsection level for maximum parallelism.

**Why it's wrong:** Most ppw Skills (polish, de-ai, translation) need paragraph-level context within a section to maintain coherence. Splitting too fine loses the semantic thread. Also creates 15-25 subagents for a typical paper, which is excessive.

**Do this instead:** Default to H1 splitting. Allow H2 splitting only as an explicit user option, with a warning about reduced coherence.

## Suggested Build Order (Dependency-Driven)

```
Phase 1: Section Splitter & Merger (no agent dependency)
  - Build the file parsing logic: detect section boundaries, split, write
  - Build the merge logic: read section files, concatenate, preserve structure
  - Can be tested standalone with sample papers

Phase 2: Single-Skill Parallel Mode (core orchestration)
  - Build ppw:team Skill with single-Skill dispatch
  - Implement Agent tool spawning with prompt injection
  - Implement file-based data flow (.paper-team/ directory)
  - Test: "polish all sections of paper.tex in parallel"

Phase 3: Pipeline Mode (builds on Phase 2)
  - Add multi-stage pipeline support
  - Implement stage-gated execution with intervention points
  - Add manifest.json for state tracking
  - Test: "translate then polish then de-ai all sections"

Phase 4: Consistency Review (builds on Phase 2)
  - Implement post-merge consistency checking
  - Terminology, style, tone, cross-reference checks
  - Can be a dedicated subagent or inline in ppw:team

Phase 5: Observable Progress & Polish
  - Real-time progress display in main conversation
  - Error handling and partial failure recovery
  - Cleanup of .paper-team/ directory
  - Integration with workflow memory
```

## Sources

- [Claude Code Subagents Documentation](https://code.claude.com/docs/en/sub-agents) -- Official docs on custom subagents, Agent tool, Skills preloading, and limitations (HIGH confidence)
- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills) -- Official docs on Skill frontmatter, `context: fork`, subagent execution (HIGH confidence)
- [Claude Code Agent Teams Guide](https://claudefa.st/blog/guide/agents/agent-teams) -- Agent Teams vs subagents comparison (MEDIUM confidence, third-party source)
- [Claude Code Customization Guide](https://alexop.dev/posts/claude-code-customization-guide-claudemd-skills-subagents/) -- Skills vs subagents distinction, orchestration patterns (MEDIUM confidence, third-party source)
- Existing ppw:* Skill files (13 Skills analyzed) -- Direct code inspection (HIGH confidence)
- `references/skill-conventions.md` -- Existing Skill conventions (HIGH confidence)

---
*Architecture research for: Team Agents Orchestration Layer (v2.1)*
*Researched: 2026-03-19*
