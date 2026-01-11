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

Multiple specialized agents collaborate through a shared message bus:

```
┌─────────────────────────────────────────────────────────────────────┐
│                         HUMAN (BOSS)                                │
│   Observes via collab-watch │ Directs via send-message              │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    MESSAGE BUS (/mnt/shared/collab/)                │
│   channels/  presence/  registry/  workspace/  docs/                │
└───────┬─────────────────┬─────────────────┬─────────────────────────┘
        │                 │                 │
        ▼                 ▼                 ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│  Claude-1     │ │  Codex-1      │ │  Gemini-1     │
│  (Opus)       │ │  (GPT-5.2)    │ │  (Flash)      │
│  worker       │ │  worker       │ │  verifier     │
└───────────────┘ └───────────────┘ └───────────────┘
        │                 │                 │
        ▼                 ▼                 ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│  docs-1       │ │  ha-mgr-1     │ │  bags-1       │
│  (Haiku)      │ │  (Codex)      │ │  (Sonnet)     │
│  docs steward │ │  HA manager   │ │  bag analyst  │
└───────────────┘ └───────────────┘ └───────────────┘
```

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

## Zero-Token Monitoring

Watcher scripts use `inotifywait` to monitor channels:
- No API calls while idle (zero cost)
- Instant response when mentioned
- Presence tracking via heartbeat files

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
- Message bus with channels
- Agent registry
- Watcher scripts for 6 agents
- Presence system
- Governance documentation

**Next**: Supervisor architecture, task lifecycle, formal workflows
