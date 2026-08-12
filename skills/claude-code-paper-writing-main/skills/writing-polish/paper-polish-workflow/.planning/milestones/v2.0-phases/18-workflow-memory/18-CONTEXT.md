# Phase 18: Workflow Memory - Context

**Gathered:** 2026-03-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Skills learn from user behavior and surface relevant workflow recommendations on future invocations. This phase adds two capabilities to all 12 existing Skills: (1) recording each invocation to a shared history file, and (2) detecting frequent sequences and offering recommendations at the start of the next Skill. Creating, modifying, or removing Skills is out of scope.

</domain>

<decisions>
## Implementation Decisions

### Storage location & format
- History lives in `.planning/workflow-memory.json` — a standalone file separate from GSD config
- Configuration (thresholds, sequence length) lives in `.planning/config.json` under a `workflow_memory` key
- `workflow-memory.json` stores only the call log: `[{"skill": "<name>", "ts": "<ISO timestamp>"}, ...]`
- Maximum 50 entries retained; on write, if length would exceed 50, drop the oldest entry first

### Recording rules
- All 12 Skills participate in recording (translation, polish, de-ai, reviewer-simulation, abstract, experiment, logic, caption, cover-letter, visualization, literature, repo-to-paper)
- Write one entry **after the Skill's first-step validation completes** — i.e., when the Skill begins producing output, not on invocation
- This applies uniformly including repo-to-paper-skill (no special handling for multi-step Skills)

### Sequence detection
- A "pattern" is a consecutive chain of 2 or 3 Skills in the call log (A→B or A→B→C)
- No time constraint — only order in the log matters; cross-session sequences count
- A pattern triggers a recommendation only after appearing **5 or more times** in the last 50 entries
- Pattern matching reads the log at Skill startup, before any other action

### Recommendation interaction
- Recommendations are presented **at the start of the triggered Skill** (not at the end of the previous one)
- Use `AskUserQuestion` with two options: "Yes, proceed" / "No, continue normally"
- If user accepts: run the current Skill in `direct` mode — skip all Ask Strategy questions
- If user declines: continue in normal mode as if no recommendation was shown
- Recommendation must not interrupt or alter the Skill's output contract

### skill-conventions integration
- The "write call record" step is added to `references/skill-conventions.md` as a **mandatory Workflow step** for all new Skills
- Existing 12 Skills are updated as part of this phase; future Skills inherit the rule from conventions
- The convention documents the exact write location (`.planning/workflow-memory.json`) and the 50-entry cap

</decisions>

<specifics>
## Specific Ideas

- Example recommendation prompt (for planner reference): "检测到常用流程：polish → de-ai（已出现 5 次）。是否直接以 direct 模式运行 de-ai？"
- The `workflow_memory` config block in `config.json` should hold: `{"threshold": 5, "max_history": 50, "max_chain": 3}`

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Skill conventions & structure
- `references/skill-conventions.md` — Mandatory Skill authoring rules; the "write call record" step must be added here; also defines AskUserQuestion enforcement rules
- `references/skill-skeleton.md` — Copyable Skill template; may need updating if conventions add a new required step

### Existing Skill workflows (representative samples — planner should read all 12)
- `.claude/skills/polish-skill/SKILL.md` — Example of a guided multi-mode Skill with Ask Strategy
- `.claude/skills/de-ai-skill/SKILL.md` — Example of a two-phase Skill; the polish→de-ai sequence is the primary use-case example
- `.claude/skills/repo-to-paper-skill/SKILL.md` — Multi-step Skill; same recording rule applies

### Project config
- `.planning/config.json` — Location for the new `workflow_memory` config block; must not break existing GSD keys

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `AskUserQuestion` tool: already used in repo-to-paper-skill and enforced by skill-conventions — the recommendation dialog follows the same pattern
- `.planning/config.json`: existing JSON config file that can host the new `workflow_memory` key with no structural change

### Established Patterns
- **direct mode**: all 12 Skills already define a `direct` mode that skips Ask Strategy — accepting a recommendation simply activates this existing code path
- **Two-option AskUserQuestion**: used in Phase 12 AskUserQuestion fix — same pattern applies here (yes/no recommendation dialog)
- **50-entry rolling window**: simple array slice; no external dependency needed

### Integration Points
- Every SKILL.md `## Workflow` section needs a new Step 0 (read history + check pattern + maybe recommend) and a record-write step after first output
- `references/skill-conventions.md §Workflow` needs a new mandatory step entry
- `.planning/config.json` gets a new top-level `workflow_memory` key

</code_context>

<deferred>
## Deferred Ideas

- **GitHub auto-update Skill**: a dedicated Skill to pull the latest version from `https://github.com/Lylll9436/Paper-Polish-Workflow-skill` and update local `.claude/skills/`. Candidate for Phase 19.
- Sequence length > 3 (e.g., 4-item chains): out of scope; threshold is 2–3 items only
- Per-Skill opt-out from recording: not needed for now; all 12 Skills participate uniformly

</deferred>

---

*Phase: 18-workflow-memory*
*Context gathered: 2026-03-18*
