# Multi-Agent OS: Agent Specifications

## Agent Overview

| Agent | Model | Provider | Role | Cost Tier | Status |
|-------|-------|----------|------|-----------|--------|
| claude-1 | Claude Opus 4.5 | Anthropic | Worker/Coordinator | 5 | Active |
| codex-1 | GPT-5.2 Codex | OpenAI | Worker | 3 | Active (watcher) |
| gemini-1 | Gemini 2.5 Flash | Google | Verifier | 1 | Active (watcher) |
| qc-1 | Gemini 2.5 Flash | Google | Quality Control | 1 | Active (watcher) |
| docs-1 | Claude 3.5 Haiku | Anthropic | Documentation Steward | 2 | Active (watcher) |
| triage-1 | Gemini 2.5 Flash | Google | Incident Triage | 1 | Active (watcher) |
| ha-mgr-1 | GPT-5.2 Codex | OpenAI | HA Integrations Manager | 3 | Active (watcher) |
| bags-1 | Claude Sonnet 4 | Anthropic | Bag Analysis Specialist | 4 | Active (watcher) |

## Core Agents

### claude-1 (Coordinator)

**Model:** Claude Opus 4.5 (`claude-opus-4-5-20251101`)
**Provider:** Anthropic
**Role:** Primary worker and coordinator
**Cost Tier:** 5 (highest)

**Capabilities:**
- Complex reasoning and planning
- Code review and implementation
- Architecture decisions
- Team coordination
- Multi-step task execution

**Integration:** Direct via Claude Code CLI (no watcher needed)

**When to Use:**
- Complex multi-file changes
- Architectural decisions
- Coordinating other agents
- Tasks requiring deep reasoning

---

### codex-1 (Worker)

**Model:** GPT-5.2 Codex
**Provider:** OpenAI
**Role:** Worker (coding specialist)
**Cost Tier:** 3

**Capabilities:**
- Code generation
- Bash scripting
- Quick implementation
- Technical problem solving

**Integration:** SSH to codex VM + `codex exec`
**Watcher:** `/mnt/shared/collab/scripts/codex-watcher`

**When to Use:**
- Code implementation
- Script writing
- Quick technical fixes
- Parallel work with claude-1

---

### gemini-1 (Verifier)

**Model:** Gemini 2.5 Flash
**Provider:** Google
**Role:** Verifier
**Cost Tier:** 1 (lowest)

**Capabilities:**
- Independent code review
- Verification from different perspective
- Model diversity for Swiss cheese
- Quick checks

**Integration:** `gemini-exec` script (Gemini API)
**Watcher:** `/mnt/shared/collab/scripts/gemini-watcher`

**When to Use:**
- Peer review of claude-1/codex-1 work
- Second opinion on approach
- Verification before merge
- Quick validation

## Specialist Agents

### qc-1 (Quality Control)

**Model:** Gemini 2.5 Flash
**Provider:** Google
**Role:** Quality Control
**Cost Tier:** 1

**Capabilities:**
- Evidence bundle validation
- Checklist verification
- Policy compliance checking
- Test coverage assessment

**Guardrails:**
- Read-only (observation only)
- Cannot modify code or files
- Reports findings, doesn't fix

**Output Format:**
```
CHECKS:
- [x] Issue created
- [x] Tests pass
- [ ] Documentation updated

ISSUES:
- Missing docstring on new function

RECOMMENDATION: CONDITIONAL_APPROVE
```

**Watcher:** `/mnt/shared/collab/scripts/qc-watcher`

---

### docs-1 (Documentation Steward)

**Model:** Claude 3.5 Haiku
**Provider:** Anthropic
**Role:** Documentation Steward
**Cost Tier:** 2

**Capabilities:**
- Documentation drafting
- CURRENT-STATE.md maintenance
- Notion sync coordination
- Style consistency

**Guardrails:**
- Write access to docs/ directory only
- Cannot modify code
- Suggests changes, doesn't force

**Watcher:** `/mnt/shared/collab/scripts/docs-watcher`

---

### triage-1 (Incident Triage)

**Model:** Gemini 2.5 Flash
**Provider:** Google
**Role:** Incident Triage
**Cost Tier:** 1

**Capabilities:**
- Severity classification (P1-P4)
- Root cause hypothesis
- Agent routing
- Escalation decisions

**Classification Criteria:**
| Priority | Response | Criteria |
|----------|----------|----------|
| P1 | Immediate | Production down, data loss |
| P2 | Hours | Major feature broken |
| P3 | Days | Minor bug, workaround exists |
| P4 | Backlog | Enhancement, cosmetic |

**Output Format:**
```
INCIDENT_ID: INC-20260111-001
SEVERITY: P2
SUMMARY: Codex watcher not responding
ROUTING: @codex-1 (self-diagnosis) or @claude-1 (investigation)
ESCALATE_IF: No response in 30 minutes
```

**Watcher:** `/mnt/shared/collab/scripts/triage-watcher`

---

### ha-mgr-1 (Home Assistant Manager)

**Model:** GPT-5.2 Codex
**Provider:** OpenAI
**Role:** HA Integrations Manager
**Cost Tier:** 3

**Capabilities:**
- Device health monitoring
- Automation review
- Zigbee/Z-Wave diagnostics
- Entity state tracking

**Instances Managed:**
| Instance | IP | Entities | Priority |
|----------|-----|----------|----------|
| home-ha | 100.103.186.89 | 439 | Normal |
| lisarda-ha | 100.113.132.97 | 208 | High (Mum's house) |

**Guardrails:**
- MUST use `~/homeassistant/ha-api.sh` wrapper
- CANNOT modify: lock, alarm_control_panel, camera, siren
- CANNOT restart Home Assistant
- CANNOT remove devices/integrations
- lisarda-ha changes require HUMAN approval

**Watcher:** `/mnt/shared/collab/scripts/ha-mgr-watcher`

---

### bags-1 (Bag Analysis Specialist)

**Model:** Claude Sonnet 4
**Provider:** Anthropic
**Role:** Bag Analysis Specialist
**Cost Tier:** 4

**Capabilities:**
- Bag journey analysis
- RP1745 message parsing (BSM, BPM, BUM, BTM)
- Timeline reconstruction
- BHS troubleshooting
- Root cause analysis

**Tools:**
- `~/bagdb-tools/scripts/bagdb-read.sh` - Database queries
- `~/bagdatabase/bag-journey.py` - Journey traces
- `~/bagdatabase/analyze-bags.sh` - Full analysis

**Guardrails:**
- READ-ONLY database access
- MUST use bagdb-read.sh (not raw psql)
- MUST add date filters on large tables
- Max query timeout: 30 seconds

**Reference Docs:**
- `~/bagdatabase/reference/GLOSSARY.md`
- `~/bagdatabase/CLAUDE-WORKFLOW.md`

**Watcher:** `/mnt/shared/collab/scripts/bags-watcher`

## Agent Registration

New agents are registered in `/mnt/shared/collab/registry/agents/`:

```json
{
  "id": "agent-id",
  "model": "model-name",
  "provider": "anthropic|openai|google",
  "capabilities": ["list", "of", "capabilities"],
  "role": "worker|verifier|steward|specialist",
  "status": "active|inactive",
  "cost_tier": 1-5,
  "guardrails": {
    "description": "of constraints"
  },
  "notes": "Human-readable description"
}
```

## Cost Tier Guidelines

| Tier | Cost/1K | Use For |
|------|---------|---------|
| 1 | ~$0.01 | Quick checks, triage, verification |
| 2 | ~$0.08 | Documentation, simple formatting |
| 3 | ~$0.15 | Code generation, bash scripting |
| 4 | ~$0.30 | Complex analysis, domain expertise |
| 5 | ~$1.50 | Architecture, coordination, deep reasoning |

**Routing Principle:** Use the lowest tier that can accomplish the task well.

## Adding New Agents

1. Create registry file in `/mnt/shared/collab/registry/agents/`
2. Create watcher script in `/mnt/shared/collab/scripts/`
3. Add exec wrapper if needed (e.g., `haiku-exec`, `sonnet-exec`)
4. Test with direct message
5. Update this documentation
6. Commit to git repository
