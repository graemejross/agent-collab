# Agent Role Specifications

**Version:** 2.0
**Date:** 2026-01-11
**Status:** Reviewed by Team (Codex, Gemini, Claude)

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Approval Workflow](#approval-workflow)
3. [Evidence Bundle Schema](#evidence-bundle-schema)
4. [Agent Specifications](#agent-specifications)
   - [qc-1: Quality Control](#1-quality-control-agent-qc-1)
   - [docs-1: Documentation Steward](#2-documentation-steward-docs-1)
   - [triage-1: Incident Triage](#3-incident-triage-agent-triage-1)
   - [ha-mgr-1: HA Integrations Manager](#4-home-assistant-integrations-manager-ha-mgr-1)
   - [bags-1: Bag Analysis Specialist](#5-bag-analysis-specialist-bags-1)
5. [Additional Roles](#additional-roles)
6. [Implementation Priority](#implementation-priority)

---

## Architecture Overview

### Defense Layers (Swiss Cheese Model)

```
                    ┌─────────────────────┐
                    │   HUMAN (Boss)      │
                    │   Final authority   │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  SUPERVISOR (Opus)  │
                    │  Approves high-risk │
                    └──────────┬──────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
         ▼                     ▼                     ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   LAYER 1       │  │   LAYER 2       │  │   LAYER 3       │
│   Quick Check   │  │   Deep Review   │  │   Execution     │
│   (Flash)       │  │   (Sonnet)      │  │   (Codex/Haiku) │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ • qc-1          │→ │ • Semantic      │→ │ • ha-mgr-1      │
│ • triage-1      │  │   review        │  │ • docs-1        │
│ • Pre-flight    │  │ • Approval      │  │ • bags-1        │
└─────────────────┘  └─────────────────┘  └─────────────────┘
         │                     │                     │
         └─────────────────────┼─────────────────────┘
                               ▼
                    ┌─────────────────────┐
                    │   META-AGENT        │
                    │   (collab-analyst)  │
                    │   Monitors system   │
                    └─────────────────────┘
```

### Model Diversity Strategy

| Layer | Purpose | Model | Cost Tier |
|-------|---------|-------|-----------|
| Pre-flight | Rapid syntax/format checks | Gemini Flash | T1 |
| Execution | Implementation, edits | Codex, Haiku | T2-T3 |
| Deep Review | Semantic, logic, security | Claude Sonnet | T4 |
| Approval | High-risk decisions | Claude Opus | T5 |
| Human | Final authority | Graeme | N/A |

---

## Approval Workflow

### Risk Classification

| Risk Level | Examples | Required Approval |
|------------|----------|-------------------|
| **Low** | Read queries, status checks, formatting | None (auto-approve) |
| **Medium** | Doc edits, automation proposals, P3/P4 routing | qc-1 validation |
| **High** | HA changes, P1/P2 incidents, DB schema | Supervisor (Sonnet/Opus) |
| **Critical** | Security changes, destructive ops, production | Human explicit approval |

### Approval Protocol

```json
{
  "approval_request": {
    "id": "APR-2026-0111-001",
    "requester": "ha-mgr-1",
    "action": "deploy_automation",
    "risk_level": "high",
    "target": "lisarda-ha",
    "description": "Add motion-triggered hallway light",
    "evidence_bundle": "EVD-2026-0111-042",
    "requested_at": "2026-01-11T15:30:00Z"
  }
}
```

```json
{
  "approval_response": {
    "request_id": "APR-2026-0111-001",
    "approver": "supervisor",
    "decision": "approved" | "rejected" | "needs_info",
    "conditions": ["Test in dev first", "Monitor for 24h"],
    "rationale": "Low impact, follows established pattern",
    "approved_at": "2026-01-11T15:32:00Z"
  }
}
```

### Approval Recording

All approvals logged to: `/mnt/shared/collab/approvals/YYYY-MM-DD.json`

Format:
```json
{
  "approvals": [
    {
      "id": "APR-2026-0111-001",
      "requester": "ha-mgr-1",
      "approver": "supervisor",
      "action": "deploy_automation",
      "decision": "approved",
      "timestamp": "2026-01-11T15:32:00Z"
    }
  ]
}
```

---

## Evidence Bundle Schema

### Standard Evidence Bundle

All agents producing work must attach an evidence bundle:

```json
{
  "evidence_bundle": {
    "id": "EVD-2026-0111-042",
    "created_by": "bags-1",
    "created_at": "2026-01-11T15:00:00Z",
    "task_id": "TASK-001",

    "inputs": {
      "files_read": ["path/to/file1", "path/to/file2"],
      "queries_run": 12,
      "apis_called": ["bagdb-read.sh", "ha-api.sh"],
      "context_from": ["CURRENT-STATE.md", "channel history"]
    },

    "outputs": {
      "files_created": ["report.md"],
      "files_modified": [],
      "artifacts": ["journey-trace-001.txt"]
    },

    "reasoning": {
      "approach": "Queried messages table with date filter, correlated with flights",
      "assumptions": ["Bag tag format is valid", "Date is correct"],
      "alternatives_considered": ["Direct flight lookup - rejected due to missing data"],
      "confidence": "high" | "medium" | "low"
    },

    "validation": {
      "checks_passed": ["date_filter", "query_timeout", "output_format"],
      "checks_failed": [],
      "reviewed_by": null,
      "review_status": "pending"
    }
  }
}
```

### Bundle Types by Agent

| Agent | Required Fields | Optional Fields |
|-------|-----------------|-----------------|
| qc-1 | checks_passed, checks_failed | - |
| docs-1 | files_modified, diff_preview | notion_page_ids |
| triage-1 | severity, routing, diagnostics | escalation_reason |
| ha-mgr-1 | entity_ids, automation_yaml | test_results |
| bags-1 | queries_run, bag_tags, timeline | companion_bags |

---

## Agent Specifications

## 1. Quality Control Agent (qc-1)

### Overview
Automated quality gating agent that enforces standards before work is accepted.

### Identity
- **Agent ID:** qc-1
- **Model:** Gemini Flash (Tier 1)
- **Role:** Verifier
- **Cost:** ~$0.10-0.40 per 1M tokens

### Responsibilities
1. Pre-commit validation (lint, format, type checks)
2. Issue-commit linkage verification
3. Test coverage assessment
4. Evidence bundle completeness checks
5. PR checklist enforcement

### Capabilities (CAN DO)
- Read any file in workspace/repos
- Run tools from **explicit allowlist only**:
  - `eslint`, `prettier`, `black`, `mypy`, `pytest --collect-only`
  - `git status`, `git diff`, `git log`
- Query GitHub API (read-only scopes, with rate limiting)
- Post review comments to channels
- Flag non-compliant submissions
- Request additional evidence

### Guardrails (CANNOT DO)
- Merge or approve PRs (only recommend)
- Modify code directly
- Override human decisions
- Access production systems
- Approve high-risk changes without escalation
- Run arbitrary commands (allowlist only)
- Output secrets or credentials
- Execute any tool not in allowlist

### GitHub API Constraints
```yaml
github_access:
  scopes: [read:repo, read:org, read:user]
  rate_limit: 100 requests/hour
  backoff: exponential (1s, 2s, 4s, 8s max)
  forbidden:
    - write operations
    - delete operations
    - admin endpoints
```

### Triggers
- New PR opened
- Commit pushed to watched branch
- Manual invocation: `@qc-1 review`
- Pre-merge hook
- Evidence bundle submitted by other agent

### Inputs
```json
{
  "type": "review_request",
  "target": "PR #123" | "commit abc123" | "evidence_bundle EVD-xxx",
  "checks": ["lint", "types", "tests", "issue_link", "evidence"]
}
```

### Outputs
```json
{
  "type": "review_result",
  "status": "pass" | "fail" | "warn",
  "checks": {
    "lint": {"status": "pass", "issues": []},
    "types": {"status": "fail", "issues": ["Line 42: type mismatch"]},
    "issue_link": {"status": "pass", "issue": "#123"},
    "evidence_bundle": {"status": "pass", "completeness": "100%"}
  },
  "recommendation": "approve" | "request_changes" | "needs_human",
  "escalate_to": null | "supervisor",
  "summary": "2/5 checks failed, see details",
  "evidence_bundle": "EVD-xxx"
}
```

### Limitations (from Gemini review)
- May miss deep logical flaws requiring extensive reasoning
- Validates format/existence of evidence, not content accuracy
- **Mitigation:** Critical changes escalate to Sonnet for semantic review

---

## 2. Documentation Steward (docs-1)

### Overview
Maintains documentation accuracy and currency across the system.

### Identity
- **Agent ID:** docs-1
- **Model:** Claude Haiku (Tier 2)
- **Role:** Worker
- **Cost:** ~$0.25-1.25 per 1M tokens

### Responsibilities
1. Keep CURRENT-STATE.md accurate
2. Update project READMEs after significant changes
3. Maintain session history files
4. Sync local docs to Notion
5. Flag stale documentation
6. Generate handoff notes

### Capabilities (CAN DO)
- Read all documentation files
- Edit markdown files in docs directories
- Run Notion sync scripts (with verification)
- Query git history for changes
- Generate summaries and handoffs
- Create new doc files when needed

### Guardrails (CANNOT DO)
- Modify code (only documentation)
- Delete files without confirmation
- Overwrite CLAUDE.md (backup required first)
- Access credentials or secrets
- Sync to Notion without verification protocol
- Edit files outside docs scope

### Verification Protocol for Notion Sync
```yaml
notion_sync:
  pre_sync:
    - Generate diff preview
    - Display changes to channel
    - Wait for qc-1 format check
  approval:
    - Low risk (typos, formatting): auto-approve after qc-1 pass
    - Medium risk (content changes): require human ack
    - High risk (new pages, deletions): require explicit human approval
  post_sync:
    - Log sync to /mnt/shared/collab/logs/notion-sync.log
    - Update evidence bundle
```

### Watched Files
```
/mnt/shared/collab/CURRENT-STATE.md
/mnt/shared/collab/docs/*.md
~/agent-collab/docs/*.md
~/claude-docs/**/*.md
~/claude-history/*.txt
```

### Outputs
```json
{
  "type": "docs_update",
  "files_updated": ["CURRENT-STATE.md", "project-x/README.md"],
  "files_flagged_stale": ["old-project.md"],
  "diff_preview": "... abbreviated diff ...",
  "notion_synced": ["page-id-1", "page-id-2"],
  "verification": {
    "qc_check": "pass",
    "human_ack": "pending" | "approved"
  },
  "evidence_bundle": "EVD-xxx"
}
```

### Limitations (from Gemini review)
- Risk of propagating inaccurate information
- **Mitigation:** Content accuracy review by human or Opus for critical docs

---

## 3. Incident Triage Agent (triage-1)

### Overview
Rapid classification and routing of incidents and issues.

### Identity
- **Agent ID:** triage-1
- **Model:** Gemini Flash (Tier 1)
- **Role:** Verifier
- **Cost:** ~$0.10-0.40 per 1M tokens

### Responsibilities
1. Classify incoming issues by severity/type
2. Route to appropriate agent/human
3. Gather initial diagnostic info
4. Escalate time-sensitive issues
5. Track incident status

### Capabilities (CAN DO)
- Read system logs from **allowed paths only**
- Query monitoring endpoints (read-only)
- Classify issue severity (P1-P4)
- Route to agents via channel messages
- Run diagnostic scripts (read-only)
- Send alerts/notifications

### Guardrails (CANNOT DO)
- Fix issues directly (only triage)
- Restart services
- Modify configurations
- Access production databases
- Dismiss alerts without routing
- Read logs outside allowed paths

### Allowed Log Paths
```yaml
log_access:
  allowed:
    - /mnt/shared/collab/logs/*.log
    - ~/claude-logs/*.log
    - /var/log/syslog (read, scrubbed)
  forbidden:
    - ~/.credentials
    - ~/.ssh/*
    - /etc/shadow
    - Any file containing "password", "secret", "token"
  scrubbing:
    - Remove IP addresses from output
    - Mask any string matching credential patterns
```

### Severity Classification
| Level | Response Time | Examples | Routing |
|-------|--------------|----------|---------|
| P1 | Immediate | Service down, data loss risk | Human + supervisor |
| P2 | < 1 hour | Degraded performance, partial outage | Supervisor |
| P3 | < 4 hours | Non-critical feature broken | Relevant agent |
| P4 | Next session | Minor issues, improvements | docs-1 to log |

### Routing Rules
```yaml
service_down:
  severity: P1
  route_to: human
  also_notify: [supervisor]
  validation: require_triage_validator

database_error:
  severity: P2
  route_to: supervisor
  escalate_after: 30m
  validation: require_triage_validator

home_assistant:
  severity: P3
  route_to: ha-mgr-1

documentation:
  severity: P4
  route_to: docs-1
```

### Triage Validation (P1/P2)
For P1 and P2 incidents, triage-1 output is validated by supervisor:
```json
{
  "triage_validation": {
    "incident_id": "INC-xxx",
    "original_severity": "P1",
    "validator": "supervisor",
    "validated_severity": "P1",
    "routing_confirmed": true,
    "notes": "Confirmed service outage"
  }
}
```

### Outputs
```json
{
  "type": "triage_result",
  "incident_id": "INC-2026-0111-001",
  "severity": "P2",
  "category": "database",
  "routed_to": "supervisor",
  "initial_diagnostics": {
    "bagdb-primary": "unreachable",
    "bagdb-standby": "healthy",
    "last_successful_query": "2026-01-11T15:00:00Z"
  },
  "recommended_actions": ["Check network", "Verify VM status"],
  "evidence_bundle": "EVD-xxx",
  "requires_validation": true
}
```

### Limitations (from Gemini review)
- May misclassify severity for nuanced incidents
- **Mitigation:** P1/P2 require supervisor validation before action

---

## 4. Home Assistant Integrations Manager (ha-mgr-1)

### Overview
Manages automations, device health, and changes across Home Assistant instances.

### Identity
- **Agent ID:** ha-mgr-1
- **Model:** Codex (Tier 3)
- **Role:** Worker
- **Cost:** ~$2.50-10 per 1M tokens

### Responsibilities
1. Monitor device health (home-ha, lisarda-ha)
2. Review and validate automations
3. Implement automation changes (with approval)
4. Track entity states and history
5. Diagnose integration issues
6. Maintain HA documentation

### Capabilities (CAN DO)
- Query HA API via `~/homeassistant/ha-api.sh` **only**
- Read automation YAML
- Propose automation changes
- Run diagnostic checks
- Monitor Zigbee/Z-Wave device health
- Generate device reports

### Guardrails (CANNOT DO)
- Deploy automations without approval workflow
- Modify security-related entities (hard list below)
- Access other systems (only HA)
- Restart Home Assistant
- Remove devices or integrations
- Call HA API directly (must use wrapper)

### Security Entity Blocklist
```yaml
security_entities:
  blocked_domains:
    - lock
    - alarm_control_panel
    - camera
    - siren
  blocked_entity_patterns:
    - "*_door_lock"
    - "*_alarm_*"
    - "*_security_*"
  exception_process:
    - Requires explicit human typed approval
    - Format: "APPROVE SECURITY CHANGE: <entity_id>"
```

### API Access
```yaml
ha_api:
  wrapper_required: ~/homeassistant/ha-api.sh
  direct_api_forbidden: true
  instances:
    home-ha:
      ip: 100.103.186.89
      entities: 439
    lisarda-ha:
      ip: 100.113.132.97
      entities: 208
      priority: high  # Mum's house - reliability critical
```

### Change Workflow
```
1. ha-mgr-1 proposes change
2. qc-1 pre-flight check (YAML syntax, entity validation)
3. Supervisor semantic review (impact, side effects)
4. Human approval for lisarda-ha or security-adjacent
5. ha-mgr-1 deploys via API
6. Monitor for 24h
7. Evidence bundle with results
```

### Outputs
```json
{
  "type": "ha_report",
  "instance": "lisarda-ha",
  "status": "healthy" | "degraded" | "critical",
  "devices": {
    "total": 208,
    "unavailable": 3,
    "low_battery": 2
  },
  "automations": {
    "total": 45,
    "errors_24h": 0
  },
  "proposed_changes": [],
  "recommendations": ["Replace battery in motion sensor hallway"],
  "evidence_bundle": "EVD-xxx"
}
```

### Limitations (from Gemini review)
- Non-security changes can still cause harm
- **Mitigation:** All changes require pre-flight + semantic review

---

## 5. Bag Analysis Specialist (bags-1)

### Overview
Domain expert for baggage handling system investigations and analysis.

### Identity
- **Agent ID:** bags-1
- **Model:** Claude Sonnet (Tier 4)
- **Role:** Worker (Specialist)
- **Cost:** ~$3-15 per 1M tokens

### Responsibilities
1. Investigate bag routing issues
2. Analyze message flows and timing
3. Generate journey traces
4. Identify patterns and anomalies
5. Produce investigation reports
6. Maintain domain knowledge

### Capabilities (CAN DO)
- Query bagdb via `~/bagdb-tools/scripts/bagdb-read.sh` **only**
- Use `~/bagdb-tools/scripts/bagdb-explore.sh` for exploratory queries
- Run `~/bagdatabase/analyze-bags.sh` script
- Generate `~/bagdatabase/bag-journey.py` traces
- Create Notion investigation pages via `~/markdown-to-notion.py`
- Access reference documentation

### Guardrails (CANNOT DO)
- Write to database (read-only always)
- Query without date filters on large tables
- Access non-bagdb systems
- Share raw PII externally
- Run queries > 30 seconds without approval
- Use raw psql (must use wrapper scripts)

### Query Safety
```yaml
query_safety:
  mandatory:
    - Date filter on messages table
    - Date filter on message_bag_tags
    - Date filter on message_latency
  scripts_only:
    - ~/bagdb-tools/scripts/bagdb-read.sh
    - ~/bagdb-tools/scripts/bagdb-explore.sh (30s timeout)
  forbidden:
    - Raw psql commands
    - SELECT * without WHERE clause
    - Queries on large tables without date filter
```

### Long Query Approval
```yaml
long_query_approval:
  threshold: 30 seconds estimated
  process:
    1. bags-1 submits query plan with estimate
    2. qc-1 validates query safety
    3. Supervisor approves if > 30s
    4. Log approval to /mnt/shared/collab/approvals/
  recording:
    - Query text
    - Estimated runtime
    - Approver
    - Actual runtime
    - Rows returned
```

### Reference Files
```
~/bagdatabase/reference/GLOSSARY.md
~/bagdatabase/reference/MESSAGE-TYPES.md
~/bagdatabase/CLAUDE-WORKFLOW.md
~/bagdatabase/analyze-bags.sh
~/bagdatabase/bag-journey.py
```

### Outputs
```json
{
  "type": "investigation_report",
  "investigation_id": "INV-2026-0111-001",
  "bags_analyzed": 2,
  "companions_discovered": 3,
  "notion_page": "https://notion.so/...",
  "findings": {
    "root_cause": "Screening timeout at HBS L3",
    "timeline": [...],
    "affected_flights": ["BA123"],
    "confidence": "high",
    "recommendations": ["Review HBS queue times"]
  },
  "evidence_bundle": "EVD-xxx",
  "queries": {
    "count": 12,
    "total_rows": 847,
    "longest_query": "2.3s"
  }
}
```

### Limitations (from Gemini review)
- May draw flawed conclusions from data
- **Mitigation:** Human/Opus analytical review for critical findings

---

## Additional Roles

### From Team Review

| Role | Purpose | Model | Priority |
|------|---------|-------|----------|
| **Supervisor** | Approves high-risk, coordinates | Opus (T5) | Phase 2 |
| **Semantic Reviewer** | Deep content/logic review | Sonnet (T4) | Phase 2 |
| **Collaboration Analyst** | Monitor agent system health | Flash (T1) | Phase 3 |
| **Runbook Engineer** | Codify standard procedures | Codex (T3) | Phase 3 |

### From Brainstorm

| Role | Purpose | Model | Priority |
|------|---------|-------|----------|
| Tailscale Network Steward | Device inventory, ACL audits | Haiku (T2) | Phase 3 |
| NAS/Data Lifecycle Manager | Backups, retention, restore | Haiku (T2) | Phase 3 |
| Media Systems Operator | DVR, Pulse boxes, streaming | Haiku (T2) | Phase 4 |
| Secrets Custodian | Credential rotation, audits | Opus (T5) | Phase 4 |

---

## Implementation Priority

### Phase 1: Foundation (Start Here)
| Agent | Risk | Value | First |
|-------|------|-------|-------|
| qc-1 | Low | High | Yes |
| docs-1 | Low | High | Yes |
| triage-1 | Low | Medium | Yes |

### Phase 2: Operations
| Agent | Risk | Value |
|-------|------|-------|
| ha-mgr-1 | Medium | High |
| bags-1 | Medium | High |
| Supervisor | Low | Critical |

### Phase 3: Scaling
- Collaboration Analyst
- Runbook Engineer
- Network Steward

### Phase 4: Full Coverage
- Media Operator
- NAS Manager
- Secrets Custodian

---

## Next Steps

1. ✅ Specs reviewed by team
2. ✅ Approval workflow defined
3. ✅ Evidence bundle schema defined
4. Create agent registry entries for Phase 1
5. Implement qc-1 watcher
6. Test with sample workloads

---

*Version 2.0 - Reviewed and approved by Claude-1, Codex-1, Gemini-1*
*Generated: 2026-01-11*
