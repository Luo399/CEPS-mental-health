# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v1.0 — Paper Polish Workflow

**Shipped:** 2026-03-13
**Phases:** 10 | **Plans:** 15 | **Requirements:** 16/16

### What Was Built
- 11 production Claude Code Skills covering the full academic paper writing lifecycle
- Modular reference library (expression patterns, anti-AI patterns, CEUS journal template) with on-demand loading architecture
- Two-phase detect-then-rewrite pattern (De-AI, Experiment Skills) enabling user confirmation before generation
- Bilingual output architecture: Skills trigger in Chinese/English; Reviewer + Logic Skills provide inline Chinese translations
- Complete bilingual README with Skill inventory table and end-to-end quick-start workflows

### What Worked
- **Phase velocity was high after Phase 1:** Phases 2-10 executed quickly (~3-5 min each) because Skill authoring is markdown-only with no code build steps. Phase 1 (reference design) dominated time investment at ~90 min.
- **Convention-first approach paid off:** Defining Skill conventions (Phase 2) before authoring any Skills ensured all 11 Skills are consistent. No refactoring needed across Skills.
- **Anti-hallucination pattern locked early:** Explicitly designing the literature-skill to use MCP data exclusively (from CLAUDE.md principle) prevented the most common failure mode of AI-generated BibTeX.
- **Modular reference design enables narrow context:** Each Skill loads only the 1-3 leaf files it needs. This keeps Skill prompt context lean and avoids loading a large monolithic reference every time.
- **Milestone audit caught real issues:** The pre-archive audit found 4 tech debt items before archiving, preventing them from being lost. All 4 resolved before archive.

### What Was Inefficient
- **ROADMAP.md plan status not updated during execution:** Phases 3, 4, and 6 were marked `[ ]` (not started) in the roadmap's progress table even after completion. Status tracking was only in STATE.md. Next milestone: update roadmap plan status at each plan completion.
- **Phase 1 research took 90+ minutes:** Expression patterns required significant design work (what categories, how to structure for retrieval). This was appropriate investment but not anticipated upfront. Future reference-heavy phases should be time-budgeted explicitly.
- **Accomplishments not extractable from SUMMARY.md by CLI:** The `gsd-tools milestone complete` command returned empty accomplishments because SUMMARY.md files don't have a standardized `one_liner` field. Accomplishments had to be manually authored. Add `one_liner` field to future SUMMARY.md files.

### Patterns Established
- **Two-phase analysis workflow** (Phase 1 confirm → Phase 2 generate): Used in De-AI Skill and Experiment Skill; applicable to any Skill where user should approve intermediate output before expensive generation
- **Geography-conditional Ask Strategy**: Spatial figure type question gates entire spatial metadata branch (CRS, study area, legend); non-spatial figures skip branch entirely. Avoids irrelevant questions.
- **Analysis-before-table ordering in Logic Skill**: Status column in Argument Chain table is *derived* from identified issues rather than filled optimistically. Prevents false confidence.
- **Journal-missing → refuse pattern**: Translation, Cover Letter Skills refuse with clear instructions when journal template is absent rather than falling back to generic style. Maintains quality guarantee.
- **Domain term protection via context inference**: De-AI Skill infers domain terms from surrounding context rather than hardcoded wordlist. More robust and generalizable.

### Key Lessons
1. **Reference architecture design is the highest-leverage phase.** Phase 1 decisions (modular vs. monolithic, file naming, category structure) affect every downstream Skill. Invest time here; it compounds.
2. **Define interaction mode taxonomy before first Skill.** Having 4 named modes (direct/guided/interactive/batch) in conventions prevents ad-hoc interaction design in each Skill.
3. **Anti-hallucination must be designed in, not added later.** The literature-skill's MCP-only BibTeX rule works because it was specified in the plan, not retrofitted. Retrofit is harder because Skills don't have tests.
4. **Skill budget forces good design.** The ~300-line limit forces progressive disclosure — lean SKILL.md with on-demand reference loading. Without the budget, Skills would balloon with embedded examples.
5. **Two-phase workflow pattern is reusable.** De-AI and Experiment Skills both use Phase 1 (analysis/detection) → user confirms → Phase 2 (generation). This pattern should be documented in conventions for future analysis Skills.

### Cost Observations
- Model mix: ~100% sonnet (claude-sonnet-4-6); quality profile used throughout
- Sessions: ~5-6 sessions across 3 days (2026-03-10 to 2026-03-13)
- Notable: Skill authoring phases (2-10) were extremely fast (~3-5 min/plan); all time concentrated in Phase 1 reference design and audit/tech-debt resolution

---

## Milestone: v2.0 — Repo-to-Paper & Bilingual Enhancement

**Shipped:** 2026-03-18
**Phases:** 8 | **Plans:** 9 | **Requirements:** 18/18

### What Was Built
- Repo-to-Paper Skill (ppw:repo-to-paper): scan experiment repo → H1/H2/H3 outline with user checkpoints → body text with [SOURCE: file:line] annotations and bilingual output
- Literature integration at H2 stage: Semantic Scholar batch search saved as ref files with metadata + abstracts
- Bilingual paragraph-by-paragraph comparison output added to 7 existing Skills (default ON, opt-out with keywords)
- Shared bilingual output specification (`references/bilingual-output.md`) as single source of truth
- AskUserQuestion enforcement across all 12 Skills (replacing plain dialogue)
- Workflow Memory system: Skills record invocations to `.planning/workflow-memory.json`, detect frequent chains, offer direct mode
- ppw:* namespace prefix for all 13 Skills, avoiding name collisions
- ppw:update Skill for syncing latest skills from GitHub repo

### What Worked
- **Convention-first approach continued to pay off:** bilingual-output.md spec (Phase 13) defined before any Skill modifications (Phase 17) ensured all 7 Skills adopted identical format
- **Top-down repo-to-paper design:** H1→H2→H3→body with confirmation gates prevented wasted generation on wrong structure
- **Workflow Memory as last phase:** Adding memory after all Skills were finalized meant no re-work; Step 0 template was mechanical insertion
- **Phase parallelization:** Wave-based execution in Phase 18 (2 plans, 2 waves) worked smoothly

### What Was Inefficient
- **SUMMARY.md still lacks `one_liner` field:** Same issue as v1.0 — CLI returns empty accomplishments. Not fixed because it's a GSD framework issue, not a project issue
- **ppw:* rename happened outside phase planning:** Skill rename was done ad-hoc after Phase 18, not as a planned phase. This created tech debt (stale references in skill-conventions.md)
- **Nyquist validation mostly partial:** 7/8 phases have VALIDATION.md but none are fully compliant. Low priority since Skills are markdown-only (no code to test)

### Patterns Established
- **Bilingual output as convention (default ON):** Skills eligible for bilingual output enable it by default; users opt out with keywords ("English only", "skip Chinese", etc.)
- **Step 0 Workflow Memory pattern:** Every Skill checks workflow history before its own logic; lightweight and non-blocking
- **Reference file hierarchy:** skill-conventions.md → bilingual-output.md → body-generation-rules.md forms a layered spec chain that new Skills can follow
- **ppw:* namespace:** All project Skills use colon-prefixed namespace to avoid collisions with other skill packages

### Key Lessons
1. **Namespace Skills from the start.** The mid-milestone rename created documentation debt. Future projects should establish namespace prefix in Phase 1.
2. **Bilingual output is a convention, not a feature.** Standardizing bilingual format as a reference file (not per-Skill logic) meant Phase 17's 7-Skill update was mechanical rather than design-intensive.
3. **Workflow Memory is O(1) overhead per Skill.** Adding Step 0 to 12 Skills took one wave of execution. The pattern is lightweight enough to mandate for all Skills.
4. **Plan ad-hoc work.** The ppw:* rename was needed but should have been a planned phase to catch all cross-references properly.

### Cost Observations
- Model mix: quality profile (opus for executors, sonnet for verifiers)
- Sessions: ~4-5 sessions across 2 days (2026-03-17 to 2026-03-18)
- Notable: Phase 14 (repo-to-paper core) was the most complex single-plan phase; Phases 11-13 and 17-18 were straightforward convention/update work

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v1.0 | ~6 | 10 | First milestone — established reference architecture, Skill conventions, and two-phase workflow pattern |
| v2.0 | ~5 | 8 | Added repo-to-paper, bilingual output, workflow memory; namespace rename to ppw:* |

### Cumulative Quality

| Milestone | Requirements | Coverage | Skills Shipped |
|-----------|-------------|----------|----------------|
| v1.0 | 16/16 | 100% | 11 |
| v2.0 | 18/18 | 100% | 13 (ppw:* namespace) |

### Top Lessons (Verified Across Milestones)

1. Reference architecture is the highest-leverage design phase — invest time here before any Skill authoring
2. Convention-first approach (define standards before implementing) prevents inconsistency across Skills
3. Namespace Skills from day one — renaming later creates documentation debt across all cross-references
4. Bilingual/i18n patterns should be codified as reference files, not embedded per-Skill
