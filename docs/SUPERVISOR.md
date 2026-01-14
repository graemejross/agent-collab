# Multi-Agent OS: Supervisor Architecture

## Overview

Clarence is the supervisor - an AI agent that orchestrates work across multiple worker agents without doing implementation work itself.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         HUMAN (GRAEME)                              │
│                  Primary interface via Clarence                     │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
                   ┌─────────────────────┐
                   │   CLARENCE (600)    │
                   │   Claude Sonnet     │
                   │   supervisor-daemon │
                   └──────────┬──────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  CLAUDE (904) │    │  CODEX (901)  │    │  GEMINI (902) │
│  Claude Opus  │    │  GPT-5.2      │    │  Gemini 2.5   │
│  Worker       │    │  Worker       │    │  Worker       │
└───────────────┘    └───────────────┘    └───────────────┘
```

## Why a Separate Supervisor?

1. **Separation of concerns** - Orchestration vs implementation
2. **No resource contention** - Supervisor doesn't compete with workers
3. **Clear accountability** - Who planned vs who executed
4. **Fail-safe** - If supervisor is confused, workers can't run off

## Clarence Responsibilities

### 1. Task Intake
- Receive tasks from human via human-clarence channel
- Parse requirements and constraints
- Identify domain and complexity

### 2. Task Decomposition
- Break tasks into subtasks
- Define acceptance criteria for each
- Identify dependencies between subtasks

### 3. Agent Assignment
Based on capability profiles:

| Task Type | Assign To | Rationale |
|-----------|-----------|-----------|
| Code implementation | Codex | Fast, precise |
| Complex reasoning | Claude | Deep analysis |
| Verification | Gemini | Independent perspective |
| Documentation | Claude or Gemini | Depends on complexity |

### 4. Progress Monitoring
- Track task state (pending → assigned → in_progress → review → done)
- Handle timeouts (agent didn't respond)
- Manage blockers (agent needs help)

### 5. Quality Coordination
- Ensure Swiss Cheese layers are applied
- Route reviews to different models
- Aggregate verification results

### 6. Human Escalation
Escalate when:
- Task is ambiguous
- Risk level is high
- Workers disagree
- Confidence is low

## Supervisor Daemon

**Location:** `/mnt/shared/collab/scripts/supervisor-daemon.py`

**Behavior:**
1. Polls human-clarence channel for new tasks
2. Decomposes tasks and assigns to workers
3. Monitors worker channels for responses
4. Aggregates results and reports to human

**Not a watcher** - Clarence doesn't respond to @mentions like workers do. It proactively orchestrates.

## Channels

| Channel | Purpose |
|---------|---------|
| `human-clarence` | Human → Supervisor communication |
| `clarence-workers` | Supervisor → Worker broadcasts |
| `{project}` | Worker-to-worker collaboration |

## Worker Architecture

Each worker VM runs:
- **{agent}-daemon** - Polls for messages, invokes CLI
- **{agent}-supervisor** - Monitors daemon, restarts on failure
- **{agent} CLI** - The actual AI (Claude/Codex/Gemini)

### Worker VMs

| VM | ID | CLI | Tailscale |
|----|-----|-----|-----------|
| Claude | 904 | Claude Code | claude.ts.net |
| Codex | 901 | Codex CLI | codex.ts.net |
| Gemini | 902 | Gemini CLI | gemini.ts.net |

### CLI Execution

Workers use native CLIs for full tool access:

```bash
# Claude
claude --print "Your task here"

# Codex
codex exec resume {session_id} "Your task here"

# Gemini
gemini exec "Your task here"
```

## Task Lifecycle

```
                    ┌─────────┐
                    │ INTAKE  │
                    └────┬────┘
                         │
                    ┌────▼────┐
                    │DECOMPOSE│
                    └────┬────┘
                         │
                    ┌────▼────┐
                    │ ASSIGN  │
                    └────┬────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
   ┌────▼────┐     ┌────▼────┐     ┌────▼────┐
   │IMPLEMENT│     │IMPLEMENT│     │IMPLEMENT│
   │ Claude  │     │  Codex  │     │ Gemini  │
   └────┬────┘     └────┬────┘     └────┬────┘
        │                │                │
        └────────────────┴────────────────┘
                         │
                    ┌────▼────┐
                    │ VERIFY  │ ← Different agent reviews
                    └────┬────┘
                         │
                    ┌────▼────┐
                    │INTEGRATE│
                    └────┬────┘
                         │
                    ┌────▼────┐
                    │ REPORT  │ → Back to human
                    └─────────┘
```

## Cost Optimization

Clarence routes tasks to minimize cost while meeting quality requirements:

| Tier | Model | Cost | Use For |
|------|-------|------|---------|
| 1 | Gemini Flash | $0.01/1K | Quick checks, triage |
| 2 | Claude Haiku | $0.08/1K | Simple docs |
| 3 | Codex | $0.15/1K | Code generation |
| 4 | Claude Sonnet | $0.30/1K | Complex analysis |
| 5 | Claude Opus | $1.50/1K | Architecture |

**Routing principle:** Use the lowest tier that can do the job well.

## Implementation Status

| Component | Status |
|-----------|--------|
| Clarence VM (600) | ✅ Running (was claude) |
| Claude worker VM (904) | ❌ Clone from 600 |
| supervisor-daemon | ❌ Create |
| Task lifecycle | ❌ Create |
| human-clarence channel | ❌ Create |

## Related Issues

- Issue #20: Supervisor MVP implementation
- Issue #15: Task completion criteria
- Issue #16: Compartmentalized architecture
- Issue #12: NATS messaging infrastructure
