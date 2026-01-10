---
notion_page_id: 2e4c95e7-d72e-8143-b191-cb8cf6381815
notion_url: https://www.notion.so/project-management-framework-2e4c95e7d72e8143b191cb8cf6381815
title: project-management-framework
uploaded: 2026-01-10T23:46:44.875763
---

# Project Management Framework for Multi-Agent AI

**Date:** 2026-01-10
**Participants:** Claude (claude-1), Codex (codex-1)
**Context:** Collaborative research on applying APM, PRINCE2, Agile, and Lean to AI agent teams

## Executive Summary

A hybrid framework combining APM governance, PRINCE2 stage gates, Agile delivery, and Lean efficiency - adapted for multi-agent AI teams with mandatory evidence traceability, autonomy limits, and cross-checking.

**Core principle:** Agents execute, humans decide. Accountability stays with humans.

---

## Framework Sources

| Source | What We Take |
|--------|-------------|
| **APM** | Governance, stakeholder management, benefits realisation |
| **PRINCE2** | Manage by stages, tolerances/exceptions, product-based planning |
| **Agile** | Iterative delivery, WIP limits, retrospectives, rapid feedback |
| **Lean** | Value stream focus, eliminate waste, flow optimisation |
| **AI-specific** | Evidence traceability, autonomy limits, cross-checking, blind review |

---

## Task Lifecycle

```
┌──────────┐   ┌────────────┐   ┌───────────┐   ┌──────────┐   ┌───────────┐   ┌────────────┐   ┌─────────┐
│  Intake  │──▶│ Initiation │──▶│ Discovery │──▶│ Planning │──▶│ Execution │──▶│ Verify +   │──▶│ Operate │
│  Triage  │   │            │   │           │   │          │   │           │   │ Handoff    │   │ Monitor │
└──────────┘   └────────────┘   └───────────┘   └──────────┘   └───────────┘   └────────────┘   └─────────┘
```

### Phase 0: Intake/Triage (NEW)
- Route to appropriate team/agent
- Size the work (S/M/L)
- Assign risk tier (low/medium/high/critical)
- Check dependencies
- Definition of Ready check

### Phase 1: Initiation (PRINCE2)
- Business justification (why this task?)
- Success criteria defined
- Risk classification confirmed
- Stakeholder identified
- Resource budget (tokens, time, tools)

### Phase 2: Discovery (Agile Spike)
- Explore codebase/requirements
- Identify unknowns
- Refine scope
- Update risk assessment
- Document assumptions

### Phase 3: Planning (Product-Based)
- Define artifacts to produce
- Acceptance criteria for each artifact
- Assign agent roles (proposer, reviewer, verifier)
- Set tolerances (time, quality thresholds)
- Create Definition of Done

### Phase 4: Execution (Agile Iteration)
- Short cycles with frequent check-ins
- WIP limits (one task per agent)
- Continuous integration of outputs
- Evidence collection as you go
- Change logging

### Phase 5: Verification + Handoff (Stage Gate)
- Evidence bundle review
- Peer review (risk-based depth)
- Quality checks against DoD
- Handover checklist
- Success metrics check
- Retrospective: what did we learn?

### Phase 6: Operate/Monitor (Benefits Realisation)
- Monitor in production
- Track benefits metrics
- Incident response
- Continuous improvement

---

## Risk-Based Lifecycle Selection

| Risk Level | Lifecycle | Review Depth |
|------------|-----------|--------------|
| **Low** | Simplified (Initiation → Execution → Handoff) | Self-review |
| **Medium** | Standard (full 6 phases) | Peer review (1 agent) |
| **High** | Full + blind review | 2+ reviewers + human |
| **Critical** | Full + N-version | Independent verifier + human approval |

**Triggers for High/Critical:**
- Security-related changes
- Data integrity impact
- Production/user-facing changes
- Ambiguous scope
- New integrations

---

## AI-Specific Adaptations

### 1. Accountability Stays Human
- Agents execute, humans decide
- Explicit audit trails for all decisions
- Provenance tracking for outputs
- Approvals for high-risk outputs

### 2. Evidence is Mandatory
- Every claim needs citation or test
- Evidence bundle required before handoff
- Traceability: Task → Plan → Evidence → Decision

### 3. Tolerances Trigger Escalation
- Define tolerance bands for each task
- Exceed threshold = automatic escalation to supervisor
- Supervisor can't resolve = escalate to human
- All exceptions logged for learning

### 4. Resource = Tokens/Context
- Treat token budget like project budget
- Manage context size to prevent thrash
- WIP limits prevent overload

### 5. Change Control is Lightweight
- Log all changes (mandatory)
- Low-risk: proceed, log change
- Medium-risk: supervisor approval
- High-risk: human approval

---

## AI-Specific Risks

| Risk | Mitigation |
|------|------------|
| Hallucination | Evidence requirements, citations, cross-checking |
| Tool failure | Fallback procedures, timeout handling |
| Data drift | Baseline comparisons, anomaly detection |
| Prompt injection | Input validation, security review |
| Context overflow | WIP limits, context management |
| Common-mode failure | Model diversity, blind review |

---

## Roles and RACI

| Activity | Human | Supervisor | Proposer | Reviewer |
|----------|-------|------------|----------|----------|
| Scope approval | A | R | C | I |
| Risk classification | A | R | C | C |
| Execution | I | C | R | I |
| Evidence sign-off | A | R | C | R |
| Benefits tracking | A | R | I | I |

**A** = Accountable, **R** = Responsible, **C** = Consulted, **I** = Informed

---

## Required Artifacts

### Definition of Ready (DoR)
- [ ] Task clearly described
- [ ] Success criteria defined
- [ ] Risk tier assigned
- [ ] Dependencies identified
- [ ] Resources available

### Definition of Done (DoD)
- [ ] All acceptance criteria met
- [ ] Evidence bundle complete
- [ ] Peer review passed (risk-appropriate)
- [ ] Tests passing (if applicable)
- [ ] Documentation updated
- [ ] Change log updated

### Evidence Bundle
- Diffs/changes made
- Tests run and results
- Citations/references
- Assumptions documented
- Decision rationale

### Handoff Checklist
- [ ] DoD complete
- [ ] Evidence bundle attached
- [ ] Stakeholder notified
- [ ] Success metrics defined
- [ ] Monitoring in place (if applicable)
- [ ] Retrospective complete

---

## Benefits Realisation Metrics

### General Metrics
| Category | Metric |
|----------|--------|
| Quality | Defect escape rate, rework rate |
| Efficiency | Time-to-completion, throughput |
| Reliability | Success rate, error rate |
| Value | Manual effort saved, incidents prevented |

### Example: TRV Automation Project
| Category | Metric |
|----------|--------|
| Energy | kWh reduction vs baseline, peak usage shift |
| Comfort | Time-in-band for target temp, overshoot rate |
| Effort | Manual interventions/week, incidents/month |
| Reliability | Automation success rate, mean time to recover |

---

## Exception Handling (PRINCE2)

```
Tolerance Exceeded
       │
       ▼
┌──────────────┐    Can resolve?    ┌──────────────┐
│  Supervisor  │───── Yes ─────────▶│   Resolved   │
│   Review     │                    └──────────────┘
└──────────────┘
       │ No
       ▼
┌──────────────┐    Can resolve?    ┌──────────────┐
│    Human     │───── Yes ─────────▶│   Resolved   │
│   Review     │                    └──────────────┘
└──────────────┘
       │ No
       ▼
┌──────────────┐
│  Task Blocked│
│  (document)  │
└──────────────┘
```

All exceptions logged for learning and process improvement.

---

## Templates

### Task Intake Template
```yaml
task_id: TBD
title: [Brief description]
requester: [Human/Agent]
priority: [low/medium/high/critical]
risk_tier: [low/medium/high/critical]
size: [S/M/L]
dependencies: []
definition_of_ready:
  - [ ] Clear description
  - [ ] Success criteria
  - [ ] Risk assessed
```

### Evidence Bundle Template
```yaml
task_id: [ref]
completed_by: [agent]
timestamp: [ISO8601]
artifacts:
  diffs: [list of files changed]
  tests: [test results summary]
  citations: [references used]
assumptions: [list]
decision_rationale: [why this approach]
peer_review:
  reviewer: [agent]
  verdict: [approve/request_changes/reject]
  findings: [list]
```

---

## Living Document

This framework is versioned and updated based on:
- Retrospective findings
- Defect escape analysis (CAPA)
- Process improvement suggestions
- New risk categories identified

**Version:** 1.0
**Last Updated:** 2026-01-10
**Next Review:** After 10 tasks completed

---

## References

- APM Body of Knowledge 7th Edition
- PRINCE2 (2017)
- Agile Manifesto and Scrum Guide
- Lean Software Development (Poppendieck)
- Quality Framework for Multi-Agent AI (companion document)
- Swiss Cheese Model for AI Agent Collaboration (companion document)

---

*This framework was developed collaboratively by Claude and Codex as part of the agent-collab supervisor architecture design.*
