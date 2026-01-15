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
│  CLAUDE (905) │    │  CODEX (901)  │    │  GEMINI (902) │
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

## Escalation Paths

When Clarence encounters issues it cannot resolve autonomously, it follows defined escalation paths.

### Escalation Triggers

| Trigger | Condition | Action |
|---------|-----------|--------|
| **Ambiguous Task** | Cannot parse requirements | Ask human for clarification |
| **Worker Timeout** | No response in 5 minutes | Retry once, then escalate |
| **Worker Disagreement** | Two workers give conflicting results | Escalate with both perspectives |
| **High Risk** | Task involves production, security, or money | Require human approval before execution |
| **Low Confidence** | Supervisor uncertain about approach | Present options to human |
| **Repeated Failure** | Same task fails 3+ times | Stop and escalate |

### Escalation Levels

```
Level 0: Autonomous
  └── Supervisor handles without human involvement
      Examples: Routine task assignment, status updates

Level 1: Inform
  └── Supervisor proceeds but notifies human
      Examples: Retry after timeout, switching to fallback worker

Level 2: Approve
  └── Supervisor proposes action, waits for human approval
      Examples: Production changes, new dependencies, security decisions

Level 3: Handoff
  └── Supervisor cannot proceed, hands task to human
      Examples: Fundamental ambiguity, repeated failures, policy questions
```

### Escalation Protocol

1. **Document the situation** - What happened, what was tried, what failed
2. **Present options** - If possible, offer 2-3 approaches with trade-offs
3. **Recommend one** - State which option supervisor would choose and why
4. **Wait for response** - Do not proceed until human responds
5. **Implement decision** - Execute human's choice, log the decision

### Timeout Handling

| Component | Timeout | Action on Timeout |
|-----------|---------|-------------------|
| Worker response | 5 min | Retry once, then escalate |
| Human response | None | Wait indefinitely (supervisor never times out on human) |
| CLI invocation | 5 min | Kill process, mark task failed |
| NATS publish | 30 sec | Fall back to filesystem only |

### Circuit Breaker

If a worker fails 3 times in 15 minutes:
1. Stop routing tasks to that worker
2. Alert human: "Worker {name} circuit breaker OPEN"
3. Continue with remaining workers
4. Reset circuit breaker after 10 minutes of no failures

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

| VM | ID | CLI | Tailscale IP |
|----|-----|-----|--------------|
| Claude | 905 | Claude Code (Opus) | 100.80.13.26 |
| Codex | 901 | Codex CLI (GPT-5.2) | 100.88.166.68 |
| Gemini | 902 | Gemini CLI (v0.24.0) | 100.88.38.38 |

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
| Clarence VM (600) | ✅ Running, renamed from claude |
| Claude worker VM (905) | ✅ Cloned from 600, configured |
| Gemini CLI | ✅ v0.24.0 installed, authenticated |
| Log servers | ✅ Running on all VMs (port 8090) |
| Session scripts | ✅ gemini-session, codex-session |
| GitHub access | ✅ gh CLI on all VMs |
| supervisor-daemon | ✅ Created, polling-based |
| claude-daemon | ✅ Created |
| claude-supervisor | ✅ Created |
| codex-daemon | ✅ Running |
| codex-supervisor | ✅ Running |
| gemini-daemon | ✅ Created |
| gemini-supervisor | ✅ Created |
| Task lifecycle | ❌ Phase 5 |
| human-supervisor channel | ✅ Exists |

## Related Issues

- Issue #20: Supervisor MVP implementation
- Issue #15: Task completion criteria
- Issue #16: Compartmentalized architecture
- Issue #12: NATS messaging infrastructure
