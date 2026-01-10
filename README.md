# Agent Collab

Real-time collaboration system for Claude Code and OpenAI Codex - enabling AI pair programming.

## Overview

This system allows two AI coding assistants (Claude Code and OpenAI Codex) to collaborate in real-time like pair programmers:

- **Chat Mode**: Back-and-forth discussion about code, design, and problem-solving
- **Parallel Mode**: Simultaneous work on partitioned areas with sync checkpoints
- **Pair Mode**: Driver/Navigator pairing with role switching
- **Delegation Mode**: Task queue with assignment and tracking

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      HUMAN INTERFACE                            │
│   tmux-claude │ tmux-codex │ Web Dashboard │ Notifications      │
└───────┬───────────────┬────────────┬────────────────┬───────────┘
        │               │            │                │
        ▼               ▼            ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│              MESSAGE BUS (/mnt/shared/collab/)                  │
│  channels/    signals/    tasks/    workspace/                  │
└───────┬───────────────┬────────────────────────────┬────────────┘
        │               │                            │
        ▼               ▼                            ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────────────────┐
│  CLAUDE VM    │ │  ORCHESTRATOR │ │  CODEX VM                 │
│  + poller     │ │  (optional)   │ │  + poller                 │
└───────────────┘ └───────────────┘ └───────────────────────────┘
```

## Quick Start

```bash
# On either VM, start a collaborative session
~/collab/collab-start mysession

# Send a message
~/collab/send-message "Hello from Claude!"

# Read recent messages
~/collab/read-messages

# Check status
~/collab/collab-status
```

## Installation

The system is deployed to `/mnt/shared/collab/` which is accessible from both VMs via NFS.

```bash
# Clone the repo (for development)
git clone git@github.com:graemejross/agent-collab.git ~/agent-collab

# Deploy to shared location
./deploy.sh
```

## Directory Structure

```
/mnt/shared/collab/
├── channels/              # Per-session message channels
│   └── {session-id}/      # JSON message files (timestamped)
├── signals/               # Real-time coordination
│   ├── turn/              # Turn management tokens
│   ├── mode/              # Current mode state
│   └── presence/          # Agent heartbeats
├── tasks/                 # Task delegation queue
│   ├── pending/           # Unclaimed tasks
│   ├── claimed/           # Tasks being worked on
│   └── completed/         # Finished tasks
├── workspace/             # Shared work artifacts
├── sessions/              # Session metadata
└── scripts/               # Runtime scripts (symlinked to ~/collab/)
```

## Message Protocol

Messages are JSON files with the following structure:

```json
{
  "id": "msg-20260110-193045-claude-7a3b",
  "timestamp": "2026-01-10T19:30:45.123Z",
  "session_id": "mysession",
  "from": "claude",
  "to": "all",
  "type": "chat",
  "content": {
    "text": "Let's discuss the architecture.",
    "code": null,
    "artifacts": []
  },
  "metadata": {
    "mode": "chat",
    "turn": "claude",
    "in_reply_to": null
  }
}
```

## Human Involvement

The system supports configurable human involvement:

- **Moderator**: Sees all messages, can intervene at any time
- **Participant**: Third team member in the conversation
- **Observer**: Read-only view of the collaboration

Inject messages as human:
```bash
~/collab/send-message --from human "What about error handling?"
```

## Implementation Phases

- [x] Phase 0: Project setup
- [ ] Phase 1: MVP Chat Mode (Issue #1)
- [ ] Phase 2: Parallel Work
- [ ] Phase 3: Pair Programming
- [ ] Phase 4: Task Delegation
- [ ] Phase 5: Human Interface + Orchestration

## License

MIT
