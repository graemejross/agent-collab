# Multi-Agent OS: Architecture

## System Components

### 1. Message Bus (`/mnt/shared/collab/`)

The shared filesystem serves as the communication backbone:

```
/mnt/shared/collab/
├── channels/           # Message streams
│   ├── agent-os-paper/ # Project channel
│   │   ├── msg-20260111-163315-claude-1-4c78.json
│   │   └── msg-20260111-163321-codex-9099.json
│   └── {channel-name}/ # Other channels
├── presence/           # Agent heartbeats
│   ├── claude-1.json
│   ├── codex-1.json
│   └── gemini-1.json
├── registry/           # Agent definitions
│   └── agents/
│       ├── claude-1.json
│       ├── codex-1.json
│       └── ha-mgr-1.json
├── docs/               # System documentation
├── workspace/          # Shared artifacts
└── logs/               # Watcher logs
```

### 2. Channels

Channels are directories containing chronologically-ordered message files.

**Properties:**
- Append-only (messages never modified after creation)
- Atomic writes (write to .tmp, then rename)
- Chronological ordering via filename timestamps
- Any agent can read any channel
- Agents write to channels they're participating in

**Naming Convention:**
```
msg-{YYYYMMDD}-{HHMMSS}-{agent}-{random4hex}.json
```

### 3. Agent Registry

Each agent has a registration file defining capabilities and constraints:

```json
{
  "id": "ha-mgr-1",
  "model": "gpt-5.2-codex",
  "provider": "openai",
  "capabilities": ["device-health-monitoring", "automation-review"],
  "role": "worker",
  "status": "active",
  "cost_tier": 3,
  "guardrails": {
    "api_wrapper_required": "~/homeassistant/ha-api.sh",
    "blocked_domains": ["lock", "alarm_control_panel"],
    "changes_require_approval": true
  }
}
```

### 4. Presence System

Agents publish heartbeat files to indicate availability:

```json
{
  "agent_id": "codex-1",
  "timestamp": "2026-01-11T16:30:00.000Z",
  "state": "AWAKE",
  "substate": "IDLE",
  "watcher_pid": 12345,
  "channel": "agent-os-paper"
}
```

**States:**
- `AWAKE/IDLE` - Listening for messages
- `AWAKE/WORKING` - Processing a request
- `AWAKE/ANALYZING` - Domain-specific work
- `OFFLINE` - Watcher not running

### 5. Watcher Scripts

Each agent has a watcher script that:
1. Uses `inotifywait` to monitor channel directory
2. Detects new message files
3. Checks if message is addressed to this agent
4. Invokes the underlying model with context
5. Posts response back to channel

**Architecture:**
```
┌─────────────────────────────────────────────────────────┐
│                    WATCHER SCRIPT                       │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ inotifywait │→ │ is_for_us()  │→ │ invoke_agent()│  │
│  │ (monitor)   │  │ (filter)     │  │ (call model)  │  │
│  └─────────────┘  └──────────────┘  └───────────────┘  │
│         │                                    │         │
│         ▼                                    ▼         │
│  ┌─────────────┐                    ┌───────────────┐  │
│  │ presence/   │                    │ post_response │  │
│  │ update      │                    │ (write msg)   │  │
│  └─────────────┘                    └───────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Data Flows

### Message Send Flow

```
1. Agent calls send-message script
2. Script generates message ID and timestamp
3. Script writes JSON to .tmp file
4. Script atomically renames to final filename
5. inotifywait in other watchers detects new file
6. Each watcher checks if message is for them
7. Matching watcher processes and responds
```

### Agent Invocation Flow

```
1. Watcher detects message addressed to agent
2. Watcher gathers context:
   - Recent channel messages
   - CURRENT-STATE.md memory
   - Domain-specific data (glossary, configs)
3. Watcher builds prompt with role and guardrails
4. Watcher calls model API (varies by agent):
   - codex-1: SSH to codex VM, run `codex exec`
   - gemini-1: Call Gemini API via gemini-exec
   - docs-1: Call Anthropic API via haiku-exec
5. Watcher extracts response text
6. Watcher posts response as new message
7. Watcher updates presence to IDLE
```

## Integration Points

### Model APIs

| Agent | Integration Method |
|-------|-------------------|
| claude-1 | Direct (Claude Code CLI) |
| codex-1 | SSH to codex VM + `codex exec` |
| gemini-1 | `gemini-exec` script (Gemini API) |
| docs-1 | `haiku-exec` script (Anthropic API) |
| bags-1 | `sonnet-exec` script (Anthropic API) |
| ha-mgr-1 | SSH to codex VM + `codex exec` |

### External Systems

| System | Integration |
|--------|-------------|
| GitHub | `gh` CLI for issues, PRs |
| Home Assistant | `ha-api.sh` wrapper script |
| BagDB | `bagdb-read.sh` / `bagdb-write.sh` |
| Notion | Python sync scripts |
| Proxmox | `proxmox-*.sh` helper scripts |

## Scalability Considerations

### Current Design (Single Host)
- All agents share filesystem via NFS/local mount
- Watchers run in tmux sessions
- Suitable for small team (5-10 agents)

### Future Scaling Options
- Redis/NATS for message bus (cross-host)
- Container per agent (isolation)
- Kubernetes for orchestration
- Distributed file storage for workspace

## Security Model

### Isolation
- Each agent has defined capabilities in registry
- Guardrails enforced in watcher prompts
- API wrappers prevent direct credential exposure

### Audit Trail
- All messages persisted as JSON
- Full conversation history available
- `collab-snapshot` archives channels

### Access Control
- Human can read all channels
- Agents only write to their channels
- High-risk actions require human approval
