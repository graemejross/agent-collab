---
notion_page_id: 2e5c95e7-d72e-8190-8fad-c199241b0f5e
notion_url: https://www.notion.so/team-management-framework-2e5c95e7d72e81908fadc199241b0f5e
title: team-management-framework
uploaded: 2026-01-11T00:12:43.386535
---

# Team Management Framework for AI Agents

**Date:** 2026-01-11
**Participants:** Claude (claude-1), Codex (codex-1)
**Context:** Applying HR and team management concepts to multi-agent AI collaboration

## Executive Summary

A framework for managing AI agent teams using adapted HR concepts. The core principle: **capability profiles with routing policies, not personality traits**. Agents are assigned roles based on measurable competence, managed via SLAs and benchmarks, and optimised for cost-efficiency.

---

## Human HR Concepts: What Transfers

| Human Concept | AI Adaptation | Notes |
|---------------|---------------|-------|
| **Belbin Team Roles** | Task-specific competence | Not enduring traits; agents can switch roles |
| **MBTI/DISC** | Prompt configuration knobs | Style parameters, not selection criteria |
| **Performance Review** | Testable SLAs + benchmarks | Objective, not subjective |
| **360 Feedback** | Multi-perspective review | With calibration and independence checks |
| **PIP** | Prompt → Tools → Model swap | Remediation ladder |
| **Firing** | Re-routing or access reduction | Not punitive; just capability matching |
| **Onboarding** | Prompt engineering + context setup | Configure, don't train |
| **Training** | Fine-tuning or RAG | Expensive; usually prefer prompt/tool changes |

---

## What Doesn't Transfer

| Human Concept | Why It Doesn't Apply |
|---------------|---------------------|
| Intrinsic motivation | Agents don't have goals beyond the prompt |
| Career development | Capabilities are fixed per model version |
| Work-life balance | Agents don't fatigue (but context does) |
| Compensation negotiation | Cost is inverse - we pay for capability |
| Cultural fit | No personality; only capability matching |
| Long-term loyalty | Model versions change; agents are ephemeral |

---

## Capability Matrix

### Structure

| Dimension | What It Measures |
|-----------|------------------|
| **Core Capabilities** | Reasoning, code, creativity, analysis |
| **Failure Modes** | Hallucination risk, tool misuse, edge cases |
| **Reliability** | Reproducibility, calibration, evidence quality |
| **Resources** | Cost, latency, context limits |
| **Domain Knowledge** | Separate from general reasoning |

### Current Team Assessment

| Capability | Claude (Opus) | Codex (GPT-5.2) | Haiku/Small | Scripts |
|------------|---------------|-----------------|-------------|---------|
| Complex reasoning | +++++ | ++++ | ++ | - |
| Code generation | ++++ | +++++ | +++ | - |
| Code review | ++++ | +++++ | ++ | + (lint) |
| Creative/divergent | +++++ | +++ | ++ | - |
| Structured output | ++++ | +++++ | +++ | +++++ |
| Speed/latency | ++ | +++ | +++++ | +++++ |
| Cost efficiency | + | ++ | ++++ | +++++ |
| Tool use | ++++ | +++++ | +++ | +++++ |
| Safety/alignment | +++++ | ++++ | +++ | N/A |
| Reproducibility | +++ | ++++ | ++++ | +++++ |
| Evidence handling | ++++ | +++++ | +++ | +++++ |

### Failure Mode Assessment

| Agent | Primary Risks | Mitigation |
|-------|---------------|------------|
| Claude (Opus) | Over-elaborate, slow | Time limits, structured prompts |
| Codex | Terse, may miss context | Require explanations, context checks |
| Haiku/Small | Shallow reasoning | Route only simple tasks |
| Scripts | Brittle, no adaptation | Clear input validation, error handling |

---

## Role Taxonomy

| Role | Responsibility | Primary | Backup |
|------|----------------|---------|--------|
| **Supervisor** | Orchestration, escalation, human liaison | Claude | - |
| **Proposer (Complex)** | Implementation requiring creativity/reasoning | Claude | Codex |
| **Proposer (Code)** | Implementation that's code-heavy | Codex | Claude |
| **Reviewer** | Critique, improvement suggestions | Codex | Claude |
| **QA/Verifier** | Citation checks, policy compliance | Codex | Script+LLM |
| **Adversarial** | Red team, attack vectors, edge cases | Claude | Codex |
| **Utility** | Formatting, evidence collection, cleanup | Haiku/Script | - |

### Role Independence Principle

Reviewers should be different model/prompt profile from proposers to reduce correlated errors. If Claude proposes, Codex reviews (and vice versa).

---

## Cost-Tiered Routing

| Tier | Use Cases | Options | Est. Cost |
|------|-----------|---------|-----------|
| **Script** | Deterministic, no reasoning | Bash, Python, jq | $0 |
| **Micro LLM** | Simple classification, formatting | Haiku, GPT-4o-mini | ~$0.001 |
| **Standard LLM** | General tasks, moderate complexity | Sonnet, GPT-4o | ~$0.01-0.05 |
| **Premium LLM** | Complex reasoning, safety-critical | Opus, o1, GPT-5.2 | ~$0.10-0.50 |
| **Premium + Human** | Highest risk, irreversible actions | Opus + approval | ~$0.50+ |

### Routing Decision Tree

```
Is it deterministic with clear rules?
├── Yes → Script
└── No → Does it require reasoning?
    ├── Minimal → Micro LLM
    └── Yes → Is it complex or safety-critical?
        ├── No → Standard LLM
        └── Yes → Premium LLM
            └── Is it irreversible or high-risk?
                └── Yes → Premium + Human
```

### Cost Optimisation Techniques

1. **Caching** - Store and reuse common outputs
2. **Batching** - Group similar requests
3. **Early-exit** - Stop when confidence is high
4. **Compression** - Summarise context before passing
5. **Tiered fallback** - Start cheap, escalate if needed

---

## Performance Management

### SLA Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Task success rate | >95% | Peer review pass rate |
| Defect escape rate | <5% | Post-deployment issues |
| Hallucination rate | <1% | Citation verification |
| Escalation rate | <10% | Human intervention frequency |
| Cost per task | Budget-dependent | Token usage tracking |
| Latency (p95) | <60s | End-to-end timing |
| Reproducibility | >90% | Same input → same output |

### Benchmarking

**Bootstrap Process:**
1. Create thin eval suite (10-30 tasks per capability)
2. Include easy/medium/hard + adversarial cases
3. Run weekly benchmark cycle
4. Add hidden holdout set for drift detection
5. Track pass/fail with evidence packets
6. Use pairwise comparisons for subjective tasks

**Benchmark Categories:**
- Reasoning accuracy
- Code correctness
- Review quality (bugs found vs missed)
- Evidence quality
- Latency and cost

---

## 360-Degree Feedback

### What We Adapt

Traditional 360 feedback gets multi-perspective input. For AI agents:
- Peer agents rate each other's outputs
- Blind review prevents anchoring
- Calibration weights feedback by reviewer accuracy

### Feedback Dimensions

| Dimension | Question | Scale |
|-----------|----------|-------|
| Clarity | Was the handoff clear? | 1-5 |
| Accuracy | Was the output correct? | 1-5 |
| Risk flagging | Did they identify risks? | 1-5 |
| Collaboration | Would you work with them again? | Y/N |

### Rules for Using Feedback

1. **Secondary signal only** - Don't use for direct routing decisions
2. **Weight by calibration** - How often is reviewer's critique validated?
3. **Separate style from correctness** - Style is subjective
4. **Trigger evals, not demotions** - Poor feedback → targeted benchmark
5. **Check for bias** - Correlated errors can create false consensus

---

## Performance Improvement

### Remediation Ladder

When an agent underperforms:

```
Level 1: Prompt Adjustment
├── Clarify instructions
├── Add examples
├── Constrain output format
└── Add guardrails

Level 2: Tool Constraints
├── Restrict tool access
├── Add validation layers
├── Require evidence
└── Add confirmation steps

Level 3: Model Swap
├── Try different model version
├── Switch to different provider
├── Add fine-tuning (expensive)
└── Use ensemble approach

Level 4: Role Removal
├── Remove from critical routing
├── Demote to backup role
├── Restrict to low-risk tasks
└── Document lessons learned
```

### Escalation Thresholds

| Condition | Action |
|-----------|--------|
| Defect escape >5% for 2 cycles | Require second-pass review |
| Persists after mitigation | Remove from critical routing |
| 3 consecutive failures | Trigger human review |
| Safety incident | Immediate human escalation |

### Incident Response

When escalation reaches human:
1. Generate incident report
2. Include evidence bundle
3. Document what was tried
4. Recommend next steps
5. Update benchmarks with new case

---

## Onboarding New Agents

### Checklist for Adding an Agent

- [ ] Define capability profile
- [ ] Run benchmark suite
- [ ] Compare to existing agents
- [ ] Assign initial role(s)
- [ ] Configure prompts and tools
- [ ] Set up monitoring
- [ ] Run shadow mode (parallel execution, no production impact)
- [ ] Graduate to production after validation

### Shadow Mode Protocol

New agents run in parallel with established agents:
1. Same inputs, separate outputs
2. Compare outputs for consistency
3. Review disagreements
4. Measure relative performance
5. Graduate when metrics match or exceed baseline

---

## Team Composition Guidelines

### Minimum Viable Team

| Role | Agents | Notes |
|------|--------|-------|
| Supervisor | 1 | Claude (best reasoning) |
| Worker | 1-2 | Claude + Codex (diversity) |
| Reviewer | 1 | Different from worker |

### Optimal Team (High-Risk Work)

| Role | Agents | Notes |
|------|--------|-------|
| Supervisor | 1 | Claude |
| Proposers | 2 | Claude + Codex (N-version) |
| Reviewer | 1 | Whichever didn't propose |
| QA/Verifier | 1 | Different model or script |
| Adversarial | 1 | Rotating |

### Model Diversity Principle

For truly independent verification, use different model families:
- Anthropic (Claude)
- OpenAI (GPT/Codex)
- Google (Gemini)
- Open source (Llama, Mistral)

Same-family agents may share training blind spots.

---

## Metrics Dashboard (Future)

### Key Indicators

| Category | Metrics |
|----------|---------|
| **Quality** | Success rate, defect rate, hallucination rate |
| **Efficiency** | Throughput, latency p50/p95/p99 |
| **Cost** | Total spend, cost per task, cost per success |
| **Team Health** | Disagreement rate, escalation rate |
| **Learning** | Benchmark improvement, new failure modes |

### Alerts

| Condition | Severity | Action |
|-----------|----------|--------|
| Success rate <90% | Warning | Review recent tasks |
| Defect escape >5% | Critical | Pause and investigate |
| Cost spike >2x | Warning | Check routing |
| Hallucination detected | Critical | Add to benchmark |

---

## Summary

### Do This

- Build explicit capability matrix
- Route by measured competence, not assumptions
- Use different models for proposer vs reviewer
- Treat 360 feedback as signal, not decision
- Remediate with prompts before model swaps
- Measure everything, improve based on data

### Don't Do This

- Assume stable personality traits
- Use MBTI for assignment decisions
- Let feedback directly control routing
- Fire (remove) without trying remediation
- Ignore cost optimisation opportunities
- Skip benchmarking new agents

---

## References

- Belbin, R.M. (2010). Team Roles at Work
- Kahneman, D. (2011). Thinking, Fast and Slow (calibration)
- Google SRE: Service Level Objectives
- Quality Framework for Multi-Agent AI (companion document)
- Project Management Framework (companion document)

---

*This framework was developed collaboratively by Claude and Codex as part of the agent-collab supervisor architecture design.*
