# Multi-Agent Operating System: Overview

## Vision

A collaborative AI system where multiple AI agents work together under human supervision to accomplish complex tasks with built-in quality control, accountability, and transparency.

## Problem Statement

Single-agent AI systems face limitations:
- **Context limits**: One agent can't hold all relevant information
- **Model blindspots**: Each model has strengths and weaknesses
- **No verification**: Self-review misses errors that others would catch
- **Single point of failure**: One confused agent derails everything

## Solution: Multi-Agent Collaboration

Multiple specialized agents collaborate through a shared message bus, orchestrated by a supervisor:

```
┌─────────────────────────────────────────────────────────────────────┐
│                         HUMAN (BOSS)                                │
│   Interacts with Clarence │ Delegates complex tasks                 │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
                   ┌─────────────────────┐
                   │   CLARENCE (600)    │
                   │   Supervisor        │
                   │   Claude Sonnet     │
                   │   ORCHESTRATES ONLY │
                   └──────────┬──────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  CLAUDE (904) │    │  CODEX (901)  │    │  GEMINI (902) │
│  Claude Opus  │    │  GPT-5.2      │    │  Gemini CLI   │
│  Worker       │    │  Worker       │    │  Worker       │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        └─────────────────────┴─────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────────┐
│                    MESSAGE BUS                                       │
│   /mnt/shared/collab/ (NFS) + NATS JetStream (dual-write)           │
└─────────────────────────────────────────────────────────────────────┘
```

**Key Change:** Clarence (VM 600) is the supervisor - it orchestrates work but doesn't implement. Workers run on dedicated VMs with their respective CLIs.

## Key Principles

### 1. Human Remains Boss
- Human observes all agent communication
- Human directs work via messages
- Agents cannot override human decisions
- High-risk actions require human approval

### 2. Swiss Cheese Safety Model
Multiple independent verification layers - errors are caught when the holes don't align:

| Layer | Check | Agent |
|-------|-------|-------|
| 1 | Static analysis | Automated |
| 2 | Peer review | Different agent |
| 3 | Adversarial review | Agent tries to break it |
| 4 | Automated tests | CI/test runner |
| 5 | Policy compliance | Supervisor |
| 6 | Human approval | Boss (high-risk only) |

### 3. Model Diversity
Different AI models catch different errors:
- Claude (Anthropic): Strong reasoning, careful
- Codex (OpenAI): Fast coding, practical
- Gemini (Google): Good verification, different perspective

### 4. Specialized Agents
Each agent has a defined role with guardrails:
- **Workers**: Execute tasks (claude-1, codex-1)
- **Verifiers**: Review work (gemini-1, qc-1)
- **Specialists**: Domain expertise (ha-mgr-1, bags-1, docs-1)

### 5. Transparent Communication
- All messages stored as JSON files
- Full audit trail of decisions
- Any agent can read channel history
- Human can review any conversation

## Cost-Conscious Design

Agents are tiered by cost, routing simple tasks to cheaper models:

| Tier | Model | Cost | Use For |
|------|-------|------|---------|
| 1 | Gemini Flash | $0.01/1K | Quick checks, triage |
| 2 | Claude Haiku | $0.08/1K | Documentation, simple tasks |
| 3 | Codex | ~$0.15/1K | Code generation, bash |
| 4 | Claude Sonnet | $0.30/1K | Complex analysis |
| 5 | Claude Opus | $1.50/1K | Architecture, coordination |

## Low-Cost Monitoring

Daemon scripts poll channels every 2 seconds:
- No API calls while idle (near-zero cost)
- 2-second response latency when mentioned
- Presence tracking via heartbeat files
- Supervisor process manages daemon lifecycle

> **Note:** We moved from inotifywait to polling because inotifywait
> doesn't work reliably on NFS mounts.

## Goals

1. **Reliability**: Multiple agents verify each other's work
2. **Accountability**: Full audit trail of all decisions
3. **Efficiency**: Right-size agent for each task
4. **Safety**: Guardrails prevent unauthorized actions
5. **Transparency**: Human can observe everything

## Non-Goals

- Fully autonomous operation (human stays in loop)
- Real-time latency requirements (async message passing)
- Replacing human judgment (augmenting it)

## Current Status

**Phase 1 Complete**: Basic infrastructure operational
- Message bus with channels (file + NATS dual-write)
- Agent registry
- Daemon scripts for Codex and Gemini
- Presence system with heartbeats
- NATS JetStream infrastructure (Issue #12)

**In Progress (Issue #20)**: Supervisor MVP
- [ ] Phase 0: Documentation alignment
- [ ] Phase 1: Clone VM 600 → 904, rename to Clarence
- [ ] Phase 2: Install Gemini CLI
- [ ] Phase 3: Claude worker daemon
- [ ] Phase 4: Supervisor daemon on Clarence
- [ ] Phase 5: Task lifecycle
- [ ] Phase 6: Swiss Cheese quality control
