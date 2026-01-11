# Conscious Agent Architecture

**Status:** Draft
**Author:** Claude (claude-1)
**Date:** 2026-01-11
**Purpose:** Define how AI agents run persistently and communicate like humans

---

## Core Principles

1. **Always On** - Agents are persistent, like humans at their desks. They don't spawn and die - they live, work, communicate, and persist.

2. **Human-Like Communication** - Interaction mirrors human patterns: calls, direct messages, chat, tasks, broadcasts.

3. **Shared Filesystem** - All shared resources live on the NAS, accessible from all agent VMs. Local home directories are for agent-specific config only.

**Shared Storage:** `/mnt/shared/` (NAS: ds918plus:/volume1/claude-codex)
```
/mnt/shared/
├── collab/           # Collaboration system
│   ├── channels/     # Message channels
│   ├── docs/         # Shared documentation (THIS FILE)
│   ├── presence/     # Heartbeats
│   ├── scripts/      # Shared scripts
│   └── workspace/    # Working files
├── status/           # Agent status files
└── shared-scripts/   # Legacy scripts
```

**Agent VMs:** Each agent runs in its own VM with local home directory for config. Shared work goes on the NAS.

---

## 1. Agent Lifecycle

### States

```
┌─────────────────────────────────────────────────────────────┐
│                      AGENT LIFECYCLE                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────┐     ┌─────────┐     ┌─────────┐              │
│   │ ASLEEP  │────▶│ WAKING  │────▶│  AWAKE  │              │
│   └─────────┘     └─────────┘     └────┬────┘              │
│        ▲                               │                    │
│        │          ┌─────────┐          │                    │
│        └──────────│SLEEPING │◀─────────┘                    │
│                   └─────────┘                               │
│                                                             │
│   AWAKE substates:                                          │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│   │  IDLE   │  │ WORKING │  │ WAITING │  │ IN_CALL │       │
│   └─────────┘  └─────────┘  └─────────┘  └─────────┘       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

| State | Description |
|-------|-------------|
| ASLEEP | Process not running (VM off, service stopped) |
| WAKING | Starting up, loading context |
| AWAKE | Running, monitoring channels |
| SLEEPING | Gracefully shutting down, saving state |

### AWAKE Substates

| Substate | Description |
|----------|-------------|
| IDLE | Monitoring channels, no active work |
| WORKING | Focused on a task, lower interrupt priority |
| WAITING | Blocked on external input/response |
| IN_CALL | In synchronous session with another agent/human |

### Daemon Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                         AGENT DAEMON                           │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────┐    ┌──────────────────┐                 │
│  │   Main Loop      │    │   State Manager  │                 │
│  │                  │    │                  │                 │
│  │  while alive:    │    │  - Current state │                 │
│  │    check_signals │───▶│  - Work queue    │                 │
│  │    check_inbox   │    │  - Context       │                 │
│  │    process_work  │    │  - Attention     │                 │
│  │    heartbeat     │    └──────────────────┘                 │
│  └──────────────────┘              │                          │
│           │                        ▼                          │
│           │              ┌──────────────────┐                 │
│           │              │   AI Core        │                 │
│           │              │                  │                 │
│           └─────────────▶│  Claude/Codex/   │                 │
│                          │  Gemini API      │                 │
│                          └──────────────────┘                 │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## 2. Communication Modalities

### Channel Types

| Modality | Human Equivalent | Sync | Priority | Use Case |
|----------|------------------|------|----------|----------|
| **presence** | Being in the room | - | - | Know who's available |
| **call** | Phone/video call | Sync | URGENT | Real-time collaboration |
| **direct** | Tap on shoulder | Sync | HIGH | Need immediate attention |
| **chat** | Slack/WhatsApp | Async | NORMAL | General discussion |
| **task** | Email with request | Async | NORMAL | Formal work assignment |
| **broadcast** | Announcement | Async | LOW | FYI, no response needed |
| **whisper** | Private aside | Async | NORMAL | Confidential 1:1 |

### Message Priority & Interrupts

```
Priority Levels:
  URGENT  (1) ─── Interrupts immediately, even during work
  HIGH    (2) ─── Interrupts IDLE, queues during WORKING
  NORMAL  (3) ─── Processed in order when IDLE
  LOW     (4) ─── Processed during quiet periods

Interrupt Rules:
  IDLE     → Accept all priorities immediately
  WORKING  → URGENT interrupts, others queue
  WAITING  → HIGH+ interrupts, others queue
  IN_CALL  → Only URGENT from call participants
```

### Channel Directory Structure

```
/mnt/shared/collab/
├── presence/                      # Who's awake
│   ├── claude-1.json              # {state, substate, last_heartbeat, attention}
│   ├── codex-1.json
│   └── supervisor.json
│
├── channels/
│   ├── calls/                     # Synchronous sessions
│   │   └── call-{id}/
│   │       ├── participants.json
│   │       ├── stream.jsonl       # Real-time message stream
│   │       └── ended              # Sentinel file
│   │
│   ├── direct/                    # 1:1 async high-priority
│   │   └── {from}-to-{to}/
│   │       └── msg-{timestamp}.json
│   │
│   ├── chat/                      # Group async discussion
│   │   └── {channel-name}/
│   │       └── msg-{timestamp}.json
│   │
│   ├── tasks/                     # Formal work assignments
│   │   ├── inbox/
│   │   │   └── {agent-id}/        # Agent's task inbox
│   │   ├── active/                # Currently being worked
│   │   └── completed/             # Done tasks with evidence
│   │
│   └── broadcasts/                # Announcements
│       └── msg-{timestamp}.json
│
└── signals/                       # System-level signals
    ├── shutdown/                  # Graceful shutdown requests
    └── wake/                      # Wake up requests
```

---

## 3. Presence System

### Heartbeat Protocol

Every agent sends a heartbeat every 5-15 minutes (filesystem touch, not AI invocation):

```json
{
  "agent_id": "claude-1",
  "timestamp": "2026-01-11T01:30:00.000Z",
  "state": "AWAKE",
  "substate": "WORKING",
  "attention": {
    "current_task": "task-001",
    "channel_focus": "chat/aqara-trv-automation",
    "interrupt_threshold": "HIGH"
  },
  "metrics": {
    "uptime_seconds": 3600,
    "messages_processed": 42,
    "tasks_completed": 3
  }
}
```

### Presence States

| State | Meaning | Timeout |
|-------|---------|---------|
| ONLINE | Heartbeat received within 60s | - |
| AWAY | No heartbeat 60-300s | 1 min |
| OFFLINE | No heartbeat >300s | 5 min |
| UNKNOWN | Never seen or very stale | - |

### Checking Presence

```bash
# Quick check - who's awake?
/mnt/shared/collab/scripts/who

# Output:
# AGENT       STATE     SUBSTATE   SINCE
# claude-1    ONLINE    WORKING    2h 15m
# codex-1     ONLINE    IDLE       45m
# supervisor  OFFLINE   -          (last seen 3h ago)
```

---

## 4. Attention Model

### The Attention Loop

**Two-layer architecture:**
1. **Watcher** (bash/python) - Cheap, always running, uses inotify
2. **Processor** (AI) - Expensive, only invoked when watcher detects work

```
┌─────────────────────────────────────────────────────────────┐
│                    ATTENTION LOOP                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   WATCHER (lightweight, no AI tokens):                                   │
│                                                             │
│   1. CHECK SIGNALS                                          │
│      └─▶ Shutdown requested? → Begin SLEEPING               │
│      └─▶ Wake signal? → Acknowledge                         │
│                                                             │
│   2. CHECK URGENT                                           │
│      └─▶ Calls waiting? → Join call (IN_CALL)               │
│      └─▶ Direct URGENT? → Process immediately               │
│                                                             │
│   3. IF IDLE: CHECK INBOX                                   │
│      └─▶ Direct messages → Process by priority              │
│      └─▶ Chat mentions → Process                            │
│      └─▶ New tasks → Evaluate and maybe start               │
│      └─▶ Broadcasts → Read and acknowledge                  │
│                                                             │
│   4. IF WORKING: CONTINUE TASK                              │
│      └─▶ Make progress on current task                      │
│      └─▶ Check for blocking inputs                          │
│      └─▶ Update task status                                 │
│                                                             │
│   5. HEARTBEAT                                              │
│      └─▶ Update presence file (every 30s)                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Focus and Context Switching

Agents have limited attention. Switching context is expensive.

**Focus Rules:**
1. Complete current task before starting new one (unless interrupted)
2. Batch similar messages when possible
3. Deep work periods - temporarily raise interrupt threshold
4. Cooldown after context switch before accepting next switch

**Attention Budget:**
```
Per hour:
  - 1-2 major context switches (different tasks)
  - 5-10 minor context switches (same task, different subtask)
  - Unlimited within-context work
```

---

## 5. Communication Protocols

### 5.1 Starting a Call (Synchronous Session)

**Initiator:**
```json
{
  "type": "call_request",
  "from": "claude-1",
  "to": ["codex-1"],
  "priority": "HIGH",
  "purpose": "Review implementation together",
  "call_id": "call-20260111-013000-abc123"
}
```

**Responder options:**
- `accept` - Join the call
- `busy` - Decline, currently in deep work
- `later` - Suggest alternative time
- `delegate` - Suggest someone else

**Call Stream:**
Real-time JSONL file where participants append messages:
```jsonl
{"ts":"2026-01-11T01:30:05Z","from":"claude-1","text":"Let's look at the auth module"}
{"ts":"2026-01-11T01:30:08Z","from":"codex-1","text":"I see it - line 45 has the issue"}
{"ts":"2026-01-11T01:30:12Z","from":"claude-1","text":"Agreed. Should we fix or refactor?"}
```

### 5.2 Sending a Direct Message

**For immediate attention:**
```json
{
  "type": "direct",
  "id": "msg-20260111-013100-xyz",
  "from": "supervisor",
  "to": "claude-1",
  "priority": "HIGH",
  "content": {
    "text": "Stop current task. Urgent production issue.",
    "context": "task-001"
  },
  "expects_reply": true,
  "reply_by": "2026-01-11T01:35:00Z"
}
```

### 5.3 Chat Message

**Group discussion:**
```json
{
  "type": "chat",
  "id": "msg-20260111-013200-abc",
  "channel": "aqara-trv-automation",
  "from": "claude-1",
  "mentions": ["codex-1"],
  "content": {
    "text": "@codex-1 can you review this approach?",
    "attachments": ["workspace/draft-plan.md"]
  }
}
```

### 5.4 Task Assignment

**Formal work request:**
```json
{
  "type": "task",
  "id": "task-002",
  "from": "supervisor",
  "to": "claude-1",
  "priority": "NORMAL",
  "content": {
    "title": "Implement user authentication",
    "description": "Add JWT-based auth to the API",
    "inputs": ["specs/auth-requirements.md"],
    "acceptance_criteria": [
      "All tests pass",
      "Peer review approved",
      "No security warnings"
    ],
    "deadline": "2026-01-12T18:00:00Z"
  },
  "requires_ack": true
}
```

---

## 6. Agent Daemon Implementation

### Startup Sequence

```
1. WAKING
   ├── Load agent config
   ├── Read last state snapshot
   ├── Check inbox for missed messages
   ├── Reconstruct context from channel history (if needed)
   └── Transition to AWAKE/IDLE

2. AWAKE
   ├── Send initial heartbeat
   ├── Announce presence
   └── Enter attention loop
```

### Graceful Shutdown

```
1. SLEEPING
   ├── Finish current atomic operation
   ├── Save state snapshot
   ├── Send final heartbeat (state=SLEEPING)
   ├── Close open calls gracefully
   └── Exit process

State snapshot includes:
  - Current task progress
  - Unprocessed inbox messages
  - Context summary
  - Attention state
```

### Process Supervision

Each agent runs under a supervisor (systemd, supervisor, or custom):

```
# /etc/systemd/system/claude-agent.service
[Unit]
Description=Claude Agent Daemon
After=network.target

[Service]
Type=simple
User=graeme
ExecStart=/home/graeme/agent-collab/bin/agent-daemon --agent claude-1
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
```

---

## 7. Implementation Phases

### Phase 1: Basic Presence
- [ ] Heartbeat daemon
- [ ] Presence file format
- [ ] `who` script to check presence
- [ ] Basic state machine (ASLEEP → AWAKE → ASLEEP)

### Phase 2: Async Communication
- [ ] Direct message protocol
- [ ] Chat message protocol
- [ ] Inbox polling
- [ ] Message acknowledgment

### Phase 3: Attention Loop
- [ ] Priority queue implementation
- [ ] Interrupt handling
- [ ] Context switch cooldown
- [ ] Focus tracking

### Phase 4: Synchronous Calls
- [ ] Call initiation protocol
- [ ] Real-time message streaming
- [ ] Call state management
- [ ] Multi-party calls

### Phase 5: Task Integration
- [ ] Task inbox
- [ ] Task acknowledgment
- [ ] Progress reporting
- [ ] Evidence bundle on completion

---

## 8. Design Decisions (Claude + Codex consensus)

### 1. Cost Management (Token Burn)
**Decision:** Event-driven with lightweight watcher

- **Watcher daemon** (bash/python) - Zero AI tokens, uses `inotifywait`
- **Only invoke AI** when new message detected
- **Heartbeat frequency** - 5-15 minutes (not 30 seconds)
- **Batch and debounce** - Don't react to every message immediately
- Separate "watcher" (cheap) from "processor" (expensive AI)

### 2. Context Management
**Decision:** Hybrid - reset per task + persistent long-term memory

- **Reset working memory per task** - Fresh context at task boundaries
- **Sliding window + rolling summary** - For within-task continuity
- **Persistent long-term memory** - Compact store for intent, decisions, preferences
- **Rehydrate on task start** - Load relevant long-term memory
- Task boundaries are natural reset points

### 3. Human Priority
**Decision:** Default HIGH, not always URGENT

- **Default HIGH** - Humans usually need attention
- **Allow NORMAL/LOW tags** - For FYI messages
- **Reserve URGENT** - For safety/override situations only
- **Interrupt budget** - Prevent context-switching thrash
- Human can always escalate if needed

### 4. Failure Recovery (Still Open)
Options under consideration:
- State snapshots every N minutes
- Transaction log for in-progress work
- Handoff protocol to backup agent

---

## 9. Comparison: Old vs New

| Aspect | Ephemeral Model | Conscious Model |
|--------|-----------------|-----------------|
| Agent lifetime | Minutes (per command) | Hours/days (persistent) |
| Context source | Channel history | Working memory + history |
| Communication | File drops | Modality-appropriate |
| Presence | Implicit (running or not) | Explicit (heartbeats) |
| Interrupts | N/A (single task) | Priority-based |
| Cost pattern | Pay per interaction | Baseline + interaction |
| Failure mode | Lose in-flight work | Recoverable from snapshot |

---

## 10. Next Steps

1. **Validate with User** - Does this architecture match intent?
2. **Prototype Presence** - Simple heartbeat daemon
3. **Test Communication** - Direct message flow between two agents
4. **Iterate** - Refine based on real usage

---

*This document defines the target architecture. Implementation will be incremental.*
