# Multi-Agent OS: Agent Specifications

## Core Agents (VM-Based)

These agents run natively on dedicated VMs with their respective CLIs:

| Agent | VM | Tailscale IP | Model | CLI | Role |
|-------|-----|--------------|-------|-----|------|
| **Clarence** | 600 | 100.83.146.108 | Claude Sonnet | Claude Code | Supervisor |
| **Claude** | 905 | 100.80.13.26 | Claude Opus 4.5 | Claude Code | Worker |
| **Codex** | 901 | 100.88.166.68 | GPT-5.2 | Codex CLI | Worker |
| **Gemini** | 902 | 100.88.38.38 | Gemini 2.5 | Gemini CLI v0.24.0 | Worker |

**Infrastructure on all VMs:**
- Log server: http://{hostname}:8090
- Session script: `{cli}-session` (tmux + logging)
- GitHub: `gh` CLI authenticated as graemejross

## Specialist Agents (API-Based)

These agents are invoked via API calls, not dedicated VMs:

| Agent | Model | Provider | Role | Cost Tier | Status |
|-------|-------|----------|------|-----------|--------|
| qc-1 | Gemini 2.5 Flash | Google | Quality Control | 1 | Active (watcher) |
| docs-1 | Claude 3.5 Haiku | Anthropic | Documentation Steward | 2 | Active (watcher) |
| triage-1 | Gemini 2.5 Flash | Google | Incident Triage | 1 | Active (watcher) |
| ha-mgr-1 | GPT-5.2 Codex | OpenAI | HA Integrations Manager | 3 | Active (watcher) |
| bags-1 | Claude Sonnet 4 | Anthropic | Bag Analysis Specialist | 4 | Active (watcher) |

## Core Agents (VM-Based Details)

### Clarence (Supervisor)

**VM:** 600
**Model:** Claude Sonnet (`claude-sonnet-4-20250514`)
**CLI:** Claude Code
**Role:** Supervisor - orchestrates work, doesn't implement

**Responsibilities:**
- Receive tasks from human
- Decompose into subtasks
- Assign to appropriate workers
- Monitor progress
- Aggregate results
- Escalate when uncertain

**Integration:** supervisor-daemon on VM 600
**Channel:** `human-clarence`

**Key Principle:** Clarence orchestrates but never implements. All implementation goes to workers.

---

### Claude (Worker)

**VM:** 905 (cloned from 600, Tailscale: 100.80.13.26)
**Model:** Claude Opus 4.5 (`claude-opus-4-5-20251101`)
**CLI:** Claude Code
**Role:** Worker - complex reasoning and implementation

**Capabilities:**
- Complex multi-file changes
- Architecture analysis
- Deep reasoning tasks
- Code review

**Integration:** claude-daemon + claude-supervisor on VM 905
**Command:** `claude --print "message"`
**Session:** `ssh graeme@claude` then `~/claude-session`
**Logs:** http://claude:8090

**When to Use:**
- Complex reasoning required
- Architecture decisions
- Tasks requiring deep analysis

---

### Codex (Worker)

**VM:** 901
**Model:** GPT-5.2 Codex
**CLI:** Codex CLI
**Role:** Worker - fast implementation

**Capabilities:**
- Code generation
- Bash scripting
- Quick implementation
- Technical problem solving

**Integration:** codex-daemon + codex-supervisor on VM 901
**Command:** `codex exec resume {session_id} "message"`
**Session:** `ssh graeme@codex` then `~/codex-session`
**Logs:** http://codex:8090

**When to Use:**
- Code implementation
- Script writing
- Quick technical fixes
- Parallel work

---

### Gemini (Worker)

**VM:** 902
**Model:** Gemini 2.5 Flash
**CLI:** Gemini CLI
**Role:** Worker - verification and independent perspective

**Capabilities:**
- Independent code review
- Verification from different perspective
- Model diversity for Swiss cheese
- 1M token context window

**Integration:** gemini-daemon + gemini-supervisor on VM 902
**Command:** `gemini exec "message"` or interactive `gemini`
**Session:** `ssh graeme@gemini` then `~/gemini-session`
**Logs:** http://gemini:8090

**When to Use:**
- Peer review of Claude/Codex work
- Second opinion on approach
- Tasks requiring large context
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
