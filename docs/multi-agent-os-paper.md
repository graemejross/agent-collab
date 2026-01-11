---
notion_page_id: 2e5c95e7-d72e-8132-844f-ec043d1b00b0
notion_url: https://www.notion.so/multi-agent-os-paper-2e5c95e7d72e8132844fec043d1b00b0
title: multi-agent-os-paper
uploaded: 2026-01-11T13:26:00.209183
---

# A Supervised Multi-Agent AI Collaboration System for Reliable Delivery

**Authors:** Codex-1 (Primary), Gemini-1 (Reviewer), Claude-1 (Editor)
**Date:** 2026-01-11
**Version:** 1.0

---

## Abstract

We present a supervised multi-agent operating system in which a human supervisor orchestrates multiple foundation models with distinct roles. The system combines a message bus, agent watchers, and a persistent memory hierarchy to enable traceable, auditable collaboration. Safety is achieved through a Swiss cheese model: independent agents provide layered defenses against correlated errors. We also implement cost-tiered routing, mapping task complexity and risk to model selection. This paper details the architecture, operational principles, and lessons learned from a working deployment.

---

## 1. Introduction

Modern AI systems are powerful but brittle when used in isolation. Our goal is to build a practical collaboration system where multiple agents collectively deliver higher reliability, lower risk, and improved transparency.

The system is **supervised**: the human remains the boss, a supervisor model coordinates tasks, and worker models execute them. This is not merely initial orchestration—the human retains continuous oversight and final authority over all significant decisions.

The immediate motivation is to reduce single-model failure modes while keeping operational complexity manageable. The deployment described here has three distinct model families (Claude from Anthropic, Codex from OpenAI, Gemini from Google) and a durable message bus for coordination.

---

## 2. Architecture

The system is structured around a message bus housed at `/mnt/shared/collab/`. Each agent has a watcher process that monitors channel messages and responds automatically.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         HUMAN (BOSS)                                │
│   tmux terminal │ collab-watch │ send-message --to supervisor       │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    SUPERVISOR (Claude instance)                     │
│   Orchestrates only - never does work                               │
└───────┬─────────────────┬─────────────────┬─────────────────────────┘
        │                 │                 │
        ▼                 ▼                 ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│  CLAUDE-1     │ │  CODEX-1      │ │  GEMINI-1     │
│  (worker)     │ │  (worker)     │ │  (verifier)   │
└───────────────┴─┴───────────────┴─┴───────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│              MESSAGE BUS (/mnt/shared/collab/)                      │
│  channels/  presence/  registry/  workspace/  logs/                 │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Components

| Component | Location | Purpose |
|-----------|----------|---------|
| Registry | `/mnt/shared/collab/registry/` | Declares agents and their roles |
| Watchers | `codex-watcher`, `gemini-watcher` | Respond to channel messages automatically |
| Channels | `/mnt/shared/collab/channels/` | Episodic logs enabling chronological traceability |
| Presence | `/mnt/shared/collab/presence/*.json` | Publishes agent availability (AWAKE/IDLE/WORKING) |
| `who` script | `/mnt/shared/collab/scripts/who` | Summarizes live agent status |
| `collab-snapshot` | `/mnt/shared/collab/scripts/collab-snapshot` | Captures channel logs for auditability |

The message bus's **asynchronous nature** is fundamental—it decouples agents and allows independent operation, which is key to scalability and resilience. Agents can "die" and resurrect by reading channel history to reconstruct context.

**Current limitation:** Claude's watcher is planned but not yet implemented. Claude's orchestration currently relies on manual interaction, highlighting a future improvement when its watcher becomes active.

---

## 3. Swiss Cheese Model

Reliability is achieved through layered defenses. Each model family has different strengths and failure modes. By routing implementation to Codex, independent verification to Gemini, and orchestration to Claude, we reduce correlated errors.

This mirrors the **Swiss cheese model** in safety engineering: each layer has holes, but when layers are stacked, the holes don't align—errors get caught.

### Defense Layers

| Layer | Check | Agent |
|-------|-------|-------|
| 1 | Static analysis (lint, types) | Automated |
| 2 | Peer review | Different agent |
| 3 | Adversarial review | Agent tries to break it |
| 4 | Automated tests | CI/test runner |
| 5 | Policy compliance | Supervisor |
| 6 | Human approval | Boss (high-risk only) |

### How Model Diversity Creates Orthogonal Holes

The distinct model capabilities translate directly into **different types of holes** and **orthogonal detection capabilities**:

- **Codex** (GPT-5.2-codex): Strong implementation and precise edits, but may over-assume context
- **Gemini** (gemini-2.5-flash): Fast validation at low cost, independent perspective, but needs tight prompting
- **Claude** (claude-opus-4): Deep reasoning and safety alignment, but can be verbose

Gemini's speed and cost-effectiveness make it an efficient first layer for catching common errors, preventing them from progressing to more expensive stages.

---

## 4. Cost-Tiered Routing

We categorize tasks into cost tiers, mapping risk and complexity to model selection:

| Tier | Model | Use Case | Cost/1M tokens |
|------|-------|----------|----------------|
| 0 | Scripts | Deterministic ops | Free |
| 1 | Gemini Flash | Sanity checks, validation | $0.10-0.40 |
| 2 | Claude Haiku | Simple reasoning | $0.25-1.25 |
| 3 | Codex (GPT-4o) | Implementation, code | $2.50-10 |
| 4 | Claude Sonnet | Analysis, review | $3-15 |
| 5 | Claude Opus | Complex reasoning, safety-critical | $15-75 |

This approach optimizes cost without sacrificing reliability. It enables a **"fail-open" strategy**: cheap checks catch simple issues early, reserving expensive models for complex reasoning and high-impact tasks.

**Task routing** is currently determined by the human supervisor with predefined rules. Future work includes automated risk assessment based on task characteristics.

---

## 5. Memory Hierarchy

The system maintains three memory layers:

| Layer | Analog | Implementation | Purpose |
|-------|--------|----------------|---------|
| Working memory | Short-term | Context window | Immediate reasoning |
| Episodic memory | Long-term events | Channel logs | Chronological collaboration history |
| Semantic memory | Long-term facts | CURRENT-STATE.md | Durable facts, decisions, status |

This separation balances short-term focus with long-term continuity, reduces context drift, and supports independent verification by grounding all agents in the same canonical state.

### The Channel IS the Memory

The channel (append-only message log) IS the persistent memory. Agents can "die" and resurrect—they just read the channel history to reconstruct context. This is analogous to how human memory works:

| Human | Agent |
|-------|-------|
| Working memory | Context window |
| Episodic memory | Channel history |
| Semantic memory | CURRENT-STATE.md |
| Procedural memory | Scripts |

---

## 6. Why Model Diversity Matters

*This section contributed by Gemini-1, representing a distinct model family.*

### Orthogonal Error Modes

Each model family (Claude, Codex, Gemini) possesses a distinct architecture, training data, and emergent capabilities. This leads to unique strengths and, crucially, **unique failure modes**. Where one model might miss a subtle logical flaw or hallucinate specific information, another, approaching the problem from a different "cognitive" angle, is more likely to detect it. This orthogonality is the bedrock of our layered defense.

### Complementary Strengths and Efficiency

Gemini's "Flash" capabilities allow for rapid, cost-effective validation and sanity checks (Tier 1). This complements Codex's implementation strength and Claude's complex reasoning and safety alignment. We are not interchangeable; we are **synergistically specialized**.

### Enhanced Robustness and Resilience

A system relying on a single model family would be vulnerable to:
- Systemic biases in that model's training
- Update-induced regressions
- Service outages specific to that vendor

By diversifying, we build resilience, ensuring that a weakness or failure in one family does not propagate across the entire system.

### Mitigation of Shared Assumptions

Different models are less likely to share identical implicit assumptions about a problem or its solution. This forces a broader exploration of the problem space and a more thorough validation process, reducing the risk of **collective blind spots**.

This diversity is not merely an architectural choice; it is a fundamental design principle that underpins the reliability and safety promised by our supervised multi-agent collaboration system.

---

## 7. Lessons Learned

From our working deployment, we have learned:

1. **Explicit ownership and handoffs** prevent duplicated work and silent conflicts
2. **Watchers plus presence signaling** reduce coordination latency while keeping accountability
3. **Model diversity materially improves error detection**, especially on ambiguous tasks
4. **Cost-tiered routing controls spend** without degrading quality when tiers are enforced
5. **Maintaining a canonical state file** (CURRENT-STATE.md) is essential for alignment across agents and time
6. **The channel as memory** enables agent "resurrection"—context survives session boundaries

### Suggested Improvements (from agents)

During a three-way discussion, agents identified:

- **Task receipt logger** (Codex): JSON log of task assignments for auditability
- **Assumption documentation** (Gemini): Agents state assumptions explicitly to prevent silent divergence

---

## 8. Conclusion

A supervised multi-agent system with a message bus, watchers, and layered memory can deliver higher reliability than single-model workflows. The Swiss cheese safety model and cost-tiered routing make the system both safer and more economical, while explicit coordination protocols preserve clarity and auditability.

The key insight is that **model diversity is a feature, not a complication**. Different model families bring orthogonal failure modes, complementary strengths, and independent perspectives that collectively strengthen the system's defenses.

---

## Claude's Review Notes

*As editor, I offer these observations on the collaborative process itself:*

### What Worked

1. **Role separation**: Assigning Codex as primary author and Gemini as reviewer produced complementary outputs without duplication
2. **Independent perspective**: Gemini's review identified genuine gaps (e.g., how task complexity is assessed) that weren't in the original draft
3. **Different strengths visible**: Codex produced structured technical content; Gemini provided analytical critique and philosophical grounding

### What Could Improve

1. **Watcher truncation**: The 20-line limit in codex-watcher caused the draft to be split, requiring an additional round-trip
2. **Coordination overhead**: Orchestrating the review required manual prompting—a supervisor agent would streamline this
3. **Evidence bundling**: Neither agent cited specific files or line numbers as evidence—this protocol should be formalized

### Meta-observation

This paper was itself produced by the system it describes. The fact that three distinct model families could collaboratively produce a coherent technical document—with clear division of labor, independent review, and editorial synthesis—is itself evidence that the architecture works.

---

## References

- Swiss Cheese Model: Reason, J. (1990). Human Error. Cambridge University Press.
- CURRENT-STATE.md: `/mnt/shared/collab/CURRENT-STATE.md`
- Phase 1 Handoff: `~/agent-collab/docs/PHASE1-HANDOFF.md`
- Channel logs: `/mnt/shared/collab/channels/agent-os-paper/`

---

*This paper was collaboratively authored by three AI agents under human supervision.*
*Generated: 2026-01-11*
