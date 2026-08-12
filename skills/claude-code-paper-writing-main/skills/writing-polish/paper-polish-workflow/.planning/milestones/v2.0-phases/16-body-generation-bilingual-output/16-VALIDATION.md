---
phase: 16
slug: body-generation-bilingual-output
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-18
---

# Phase 16 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Manual validation (Claude Code Skill — no automated test framework) |
| **Config file** | None — Skills are instruction documents, not executable code |
| **Quick run command** | Trigger the Skill with a test repo and inspect `.tex` output |
| **Full suite command** | Complete workflow: scan repo → outline → literature → body generation |
| **Estimated runtime** | ~5 minutes (manual inspection) |

---

## Sampling Rate

- **After every task commit:** Visual inspection of modified SKILL.md and new reference file
- **After every plan wave:** N/A (single plan expected)
- **Before `/gsd:verify-work`:** Full workflow triggered against test repo, all output verified
- **Max feedback latency:** 5 minutes

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 16-01-01 | 01 | 1 | REPO-06, REPO-07 | manual | Inspect SKILL.md for Step 5 + `body-generation-rules.md` reference | ❌ W0 | ⬜ pending |
| 16-01-02 | 01 | 1 | REPO-06 | manual | Inspect `references/body-generation-rules.md` for claim annotation rules | ❌ W0 | ⬜ pending |
| 16-01-03 | 01 | 1 | REPO-07 | manual | Inspect `references/body-generation-rules.md` for CEUS style rules | ❌ W0 | ⬜ pending |
| 16-01-04 | 01 | 1 | BILN-01 | manual | Inspect bilingual format rules in `body-generation-rules.md` and SKILL.md Step 5 | ❌ W0 | ⬜ pending |
| 16-01-05 | 01 | 1 | REPO-06, REPO-07, BILN-01 | manual | Trigger Skill with test repo, verify `.tex` output has annotations + CEUS format + bilingual markers | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

None — no automated test infrastructure needed for Skill instruction files. Existing project structure covers all phase requirements.

*If none: "Existing infrastructure covers all phase requirements."*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Body text includes `[SOURCE: file:line]` annotations on repo-derived claims | REPO-06 | Skill is a Markdown instruction file; no executable harness | Trigger Skill with test repo, inspect `.tex` output for `[SOURCE: file:line]` patterns on quantitative/factual claims |
| Output uses CEUS journal template formatting (past tense, cautious verbs, section structure) | REPO-07 | Skill output is natural language judgment, not parseable code | Inspect `.tex` output for past tense verbs, hedging language, no promotional adjectives, correct section headings |
| Bilingual output produces paragraph-by-paragraph English + Chinese comparison | BILN-01 | Format requires visual layout verification | Inspect `.tex` output for `% --- Paragraph N ---` markers and `%` Chinese comment lines interleaved with English paragraphs |
| Quantitative claims without repo data use explicit placeholders | REPO-06 | Hallucination prevention requires human review | Inspect `.tex` output for `[RESULTS NEEDED]` and `[EXACT VALUE: metric]` where no supporting repo data exists |
| `\cite{}` references only from `.paper-refs/` files | REPO-06 | Citation boundary enforcement requires source tracing | Verify no citation key in generated `.tex` is absent from `.paper-refs/*.md` files |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5 minutes
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
