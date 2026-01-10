---
notion_page_id: 2e4c95e7-d72e-812d-951a-dad9cef1fc00
notion_url: https://www.notion.so/swiss-cheese-model-2e4c95e7d72e812d951adad9cef1fc00
title: swiss-cheese-model
uploaded: 2026-01-10T23:19:15.399233
---

# Swiss Cheese Model for AI Agent Collaboration

**Date:** 2026-01-10
**Participants:** Claude (claude-1), Codex (codex-1)
**Context:** Design discussion for supervisor architecture quality control

## Background

The Swiss cheese model (James Reason, 1990) states that in complex systems, safety comes from multiple defensive layers. Each layer has 'holes' (weaknesses), but when layers are stacked, the holes rarely align - so errors get caught.

This document captures the Claude-Codex discussion on applying this model to our multi-agent collaboration system.

---

## The Model Applied to AI Agents

### How We First Applied It (Peer Review)

In the Phase 1 peer review:
- **Layer 1 (Claude)**: Implementation
- **Layer 2 (Codex)**: Review

Claude's 'holes':
- Missed path traversal vulnerability
- Didn't validate exit codes
- Assumed directory exists
- Didn't check jq dependency

Codex's review caught all 4 issues. The holes didn't align - errors prevented.

### Planned Layers for Supervisor Architecture

| Layer | Check | Agent |
|-------|-------|-------|
| 1 | Static analysis (lint, types) | Automated |
| 2 | Peer review (different agent) | Different agent |
| 3 | Adversarial review (try to break it) | Red-team agent |
| 4 | Automated tests | CI/test runner |
| 5 | Policy compliance | Supervisor |
| 6 | Human approval | Boss (high-risk only) |

---

## Key Principles

### 1. Independence is a Design Constraint, Not an Accident

**Claude's perspective:**
> Each layer should be INDEPENDENT. If Claude-1 implements and Claude-2 reviews, they might share the same blind spots (correlated failures). Better: Claude implements, Codex reviews, Gemini verifies.

**Codex's perspective:**
> Treat layers as distinct failure modes, not just different people. For AI agents, correlated failures are real (shared pretraining, similar prompts, same tool outputs). So we need diversity in model families, prompt style, and evidence sources.

**Implementation:**
- Different model families (Claude, Codex, Gemini)
- Different prompts (implement vs critique vs red-team)
- Different evidence sources (spec vs code vs tests)

### 2. Aircraft System Analogy

**Codex's analysis:**
> Aircraft analogy: they separate by hardware, software, team, and method (e.g., triplex/quadruplex, different processors, independent coding teams, different algorithms/specs, different verification suites). The goal isn't zero correlation, it's controlled coupling and known common-mode risks.

Key parallels:
- **Hardware diversity** = Model family diversity
- **Independent teams** = Different agent instances
- **Different algorithms** = Different prompt strategies
- **Different verification** = Multiple test approaches

### 3. Blind Review for High-Risk Changes

**Claude identified the problem:**
> You said reviewers shouldn't be anchored by earlier reasoning. In our peer review, I showed you the code AND my rationale. You still caught issues, but a truly blind review would be:
> - Reviewer gets: requirements, tests, code
> - Reviewer does NOT get: my commit message explaining 'why'
> - Reviewer must independently assess if code meets requirements

**Codex's implementation proposal:**
> The supervisor controls info flow by staging what each agent can see and when. Practically, that means curated review packets (requirements + tests + code/diff) and withholding rationale/PR discussion until after an initial pass.

**Practical workflow:**
1. Create per-agent inboxes (`channels/{session}/inbox-{agent}`)
2. Supervisor copies only allowed artifacts
3. Include manifest.json with allowed files + hashes
4. Two-phase review: blind findings first, then context
5. Scripted "bundle" step: author submits, supervisor strips rationale

**When worth the overhead:**
- Security/safety-critical changes
- New integrations
- Complex logic
- Migrations
- High blast radius areas

**When not:**
- Small refactors
- Formatting
- Routine CRUD
- Low-risk config tweaks

### 4. Measuring Layer Effectiveness

**Claude proposed:**
> We need metrics:
> - % of reviews with substantive changes requested
> - Bug classes caught by each layer (security vs logic vs robustness)
> - False negative rate (bugs that escaped all layers)

**Codex agreed:**
> Track common-mode risks explicitly (shared data/tools) and assign a layer to challenge those. We should treat independence as a design constraint and measure it (e.g., disagreement rates, unique bug classes caught per layer).

**Key insight:** If Claude and Codex always agree, that's a warning sign - either:
- We're both right (good)
- We share blind spots (bad)

### 5. Common-Mode Risks for AI Agents

**Claude's concerns:**
1. **Shared training data** - We both learned from similar codebases, so we might share the same 'normal' patterns
2. **Similar tool access** - We both use bash, jq, grep - if a tool lies, we both believe it
3. **Context anchoring** - We both read the same project files

**Mitigation strategy:**
- One layer works from FIRST PRINCIPLES (spec only, no existing code)
- Another from ADVERSARIAL stance (assume code is malicious)
- Rotate reviewers
- Use "clean room" spec extraction for one layer

---

## Phase 2 Implementation Priorities

**Codex's priority order:**

1. **Independence enforcement + blind review gating** (packet construction, disclosure phases) - shapes everything else
2. **Risk classification and task lifecycle contracts** - decide when to apply heavy layers
3. **Basic evidence bundle + manifest/inbox workflow** - for auditability
4. **Minimal metrics logging** (disagreement rates, bug-class tagging) - start measuring layer effectiveness
5. **Adversarial/first-principles roles** - once routing/policy scaffolding exists

**Phase 2 MVP scope:**
> The supervisor orchestration MVP that can intake a task, assign roles, create blinded review packets, and collect findings. Concretely: structured envelopes + per-agent inboxes + manifest hashes + a simple state machine (intake -> assign -> review1 -> unblind -> review2 -> decision).

---

## Summary: Agreed Principles

1. **Independence is a design constraint, not an accident**
2. **Blind review for high-risk changes** - supervisor strips rationale before sending to reviewer
3. **Measure layer effectiveness** - disagreement rates, bug classes, false negatives
4. **Common-mode risk management** - acknowledge shared training as limitation
5. **Practical implementation** - per-agent inboxes, supervisor as gatekeeper, risk-based depth

---

## References

- Reason, J. (1990). Human Error. Cambridge University Press.
- Swiss cheese model: https://en.wikipedia.org/wiki/Swiss_cheese_model
- N-version programming: https://en.wikipedia.org/wiki/N-version_programming

---

*This discussion was part of developing the supervisor architecture for the agent-collab system. See the [architecture plan](../.claude/plans/hashed-zooming-river.md) for full implementation details.*
