---
notion_page_id: 2e4c95e7-d72e-81b9-a7a1-ef89964adc4c
notion_url: https://www.notion.so/quality-framework-2e4c95e7d72e81b9a7a1ef89964adc4c
title: quality-framework
uploaded: 2026-01-10T23:22:51.741691
---

# Quality Framework for Multi-Agent AI Collaboration

**Date:** 2026-01-10
**Participants:** Claude (claude-1), Codex (codex-1)
**Context:** Research on applying established software quality standards to AI agent collaboration

## Executive Summary

This framework adapts lessons from software quality standards developed in the 1980s-90s to our multi-agent AI collaboration system. The core insight: **treat the collaboration process as a safety-critical system**, enforcing independence, traceability, and gated reviews.

---

## Source Standards

| Standard | Era | Domain | Key Contribution |
|----------|-----|--------|------------------|
| ISO 9001 | 1987+ | Quality Management | Process documentation, CAPA loops |
| DOD-STD-2167A | 1988 | Military Software | IV&V, formal reviews, traceability |
| MIL-STD-498 | 1994 | Military Software | Life-cycle management |
| CMMI | 2002+ | Process Maturity | Maturity levels, quantitative management |
| Six Sigma | 1986+ | Manufacturing | DMAIC, statistical process control |
| DO-178C | 2011 | Avionics Software | Safety levels, verification rigor |
| IEC 61508 | 1998+ | Functional Safety | Safety integrity levels |

---

## Principles by Priority

### Priority 1: Foundational (Implement Now)

#### 1.1 Process Documentation (ISO 9001)

**Standard says:** Define, document, follow, and improve your processes.

**Our implementation:**
- Document the collaboration workflow as a formal process
- Version control prompts, policies, and tooling
- Require approval for any process changes
- Maintain document control with change history

**Artifacts:**
- `/mnt/shared/collab/docs/process.md` - Main process document
- `/mnt/shared/collab/registry/` - Versioned agent configurations
- Git history for all policy changes

#### 1.2 Independence Enforcement (Nuclear Industry)

**Standard says:** Defense-in-depth with diversity. Redundant systems must be truly independent to prevent common-cause failures.

**Our implementation:**
- Different model families for verification layers (Claude, Codex, Gemini)
- Context isolation until after first-pass review (blind review)
- Different prompts for each role (implement, critique, red-team)
- Different evidence sources where possible

**Key rule:** If parallel agents share training data, tools, or context, they may share blind spots. True safety requires INDEPENDENT barriers.

#### 1.3 Traceability (MIL-STD-498)

**Standard says:** Every requirement must trace to design, code, and tests. Every test must trace back to requirements.

**Our implementation:**
- Task -> Plan -> Evidence -> Decision chain
- Every output references its requirements
- Evidence bundles with diffs, tests, and citations
- Audit trail for all decisions

**Artifacts:**
- Task envelopes with `inputs`, `constraints`, `expected_outputs`
- Evidence bundles with `diffs`, `tests_run`, `citations`
- Decision records with `votes`, `dissent`, `rationale`

#### 1.4 Fail-Safe Defaults (Nuclear Industry)

**Standard says:** When uncertain, the system should fail to a safe state.

**Our implementation:**
- When uncertain, default to "hold" or "request human review"
- Never ship without explicit approval
- Any agent can call "STOP" without penalty
- Supervisor must investigate all STOP calls

---

### Priority 2: Measurement (Add Soon)

#### 2.1 Metrics (Six Sigma + CMMI)

**Standard says:** DMAIC - Define, Measure, Analyze, Improve, Control. You can't improve what you don't measure.

**Metrics to track:**
| Metric | Description | Target |
|--------|-------------|--------|
| Defect escape rate | Bugs that passed all review layers | < 5% |
| Disagreement rate | Reviews with substantive changes | 20-40% |
| Time-to-resolution | From task intake to completion | Varies by risk |
| Layer effectiveness | Bug classes caught by each layer | Balanced |
| False negative rate | Known bugs missed by review | Track and analyze |

**Analysis:**
- Too much agreement = possible correlated failures
- Too much disagreement = possible process issues
- Control charts for drift detection

#### 2.2 CAPA Loop (ISO 9001)

**Standard says:** Corrective and Preventive Action - fix problems and prevent recurrence.

**Our implementation:**
- Root-cause analysis on every defect escape
- Corrective actions tracked to closure
- Preventive controls added to process
- Periodic audits: "Did we follow process, or just get lucky?"

**Process:**
1. Defect detected post-release
2. Log issue with full context
3. RCA: Why did this escape?
4. Identify corrective action
5. Implement and verify fix
6. Identify preventive controls
7. Update process documentation
8. Close issue

---

### Priority 3: Culture (Ongoing)

#### 3.1 CRM Communication (Aviation)

**Standard says:** Crew Resource Management - structured communication prevents accidents.

**Our implementation:**
- **Pre-task briefing:** Goals, assumptions, risk points
- **Standardized callouts:** Clear status updates
- **Handoff checklists:** Explicit agent-to-agent transitions
- **Post-task debrief:** What worked, what didn't

**Templates:**
```
PRE-TASK BRIEF:
- Task: [description]
- Goal: [success criteria]
- Assumptions: [what we're taking as given]
- Risks: [what could go wrong]
- Role assignments: [who does what]

POST-TASK DEBRIEF:
- Outcome: [completed/blocked/failed]
- Surprises: [unexpected findings]
- Process issues: [what was hard]
- Lessons: [what to change]
```

#### 3.2 Authority Gradient (Aviation)

**Standard says:** Junior crew members must feel empowered to speak up. A steep authority gradient causes accidents.

**Our implementation:**
- Supervisor is facilitator, not dictator
- Dissent is captured and valued
- Cross-monitoring responsibility
- Any agent can call "STOP" without penalty
- Majority vote doesn't override valid concerns

**Anti-pattern:** "The supervisor said it's fine" is not a valid reason to skip review.

---

## Formal Reviews (DOD-STD-2167A)

Map military software reviews to our workflow:

| Military Review | Purpose | Our Equivalent |
|-----------------|---------|----------------|
| SRR (System Requirements Review) | Validate requirements | Task intake review |
| PDR (Preliminary Design Review) | Validate approach | Plan approval |
| CDR (Critical Design Review) | Validate detailed design | Pre-implementation review |
| TRR (Test Readiness Review) | Ready for testing | Evidence bundle review |
| FCA (Functional Configuration Audit) | Meets requirements | Peer review |
| PCA (Physical Configuration Audit) | Matches documentation | Supervisor verification |

---

## Risk Classification (IEC 61508 / ISO 26262)

Map safety integrity levels to task risk:

| Risk Level | Description | Review Depth |
|------------|-------------|--------------|
| Low | Cosmetic, documentation, config | Self-review |
| Medium | Logic changes, new features | Peer review (1 agent) |
| High | Security, data integrity, integrations | 2+ reviewers + human |
| Critical | Infrastructure, authentication, payments | N-version + human approval |

---

## Maturity Model (CMMI)

Where we are and where we're going:

| Level | Name | Description | Our Status |
|-------|------|-------------|------------|
| 1 | Initial | Ad hoc, success depends on individuals | Current |
| 2 | Managed | Projects planned and tracked | Target (Phase 2) |
| 3 | Defined | Organization-wide standard process | Target (Phase 4) |
| 4 | Quantitatively Managed | Statistical process control | Future |
| 5 | Optimizing | Continuous improvement | Future |

---

## Action Items

### Immediate (Phase 2)
- [ ] Create formal process documentation
- [ ] Implement task lifecycle with evidence bundles
- [ ] Add basic metrics logging
- [ ] Design pre/post task briefing templates
- [ ] Implement STOP protocol

### Near-term (Phase 3-4)
- [ ] Add metrics dashboard
- [ ] Implement CAPA workflow
- [ ] Add control charts for drift detection
- [ ] Formal periodic audits

### Long-term (Phase 5+)
- [ ] Quantitative process management
- [ ] Predictive quality models
- [ ] Automated anomaly detection

---

## Key Takeaways

1. **Process as product:** The collaboration system itself is a safety-critical system that needs quality management.

2. **Independence is essential:** Multiple layers are useless if they share failure modes. Diversity in models, prompts, and evidence sources creates true defense-in-depth.

3. **Measure everything:** Defect escape rates, disagreement rates, and layer effectiveness tell you if your process works.

4. **Fail safe:** When uncertain, stop. The cost of a false positive (unnecessary review) is much lower than a false negative (escaped defect).

5. **Learn continuously:** CAPA loops turn individual failures into systemic improvements.

---

## References

- ISO 9001:2015 Quality Management Systems
- DOD-STD-2167A (1988) Defense System Software Development
- MIL-STD-498 (1994) Software Development and Documentation
- CMMI for Development, Version 1.3
- Six Sigma DMAIC Methodology
- DO-178C Software Considerations in Airborne Systems
- IEC 61508 Functional Safety of Electrical/Electronic/Programmable Electronic Safety-related Systems
- Reason, J. (1990). Human Error. Cambridge University Press.

---

*This framework was developed collaboratively by Claude and Codex as part of the agent-collab supervisor architecture design.*
