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
├── signals/
│   └── presence/       # Agent heartbeats
│       ├── claude.json
│       ├── codex.json
│       ├── gemini.json
│       └── supervisor.json
├── registry/           # Agent definitions
│   └── agents/
│       ├── claude.json
│       ├── codex.json
│       ├── gemini.json
│       ├── supervisor.json
│       └── {specialist}-{n}.json
├── docs/               # System documentation
├── workspace/          # Shared artifacts
└── logs/               # Watcher logs
```

### 2. Agent ID Naming Convention

**Standard agent IDs:**

| Type | Pattern | Examples |
|------|---------|----------|
| Core Workers | `{model}` | `claude`, `codex`, `gemini` |
| Supervisor | `supervisor` | `supervisor` |
| Specialists | `{role}-{n}` | `qc-1`, `docs-1`, `bags-1` |

**Rules:**
- Use lowercase, no spaces
- Workers use simple model names (no version numbers)
- Specialists use role prefix with instance number
- IDs must match across: registry, presence, daemon scripts, message `from` field

**Deprecated:** `code-1`, `code-2`, `claude-1`, `codex-1` (legacy, archived)

### 3. Channels

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

### 4. Atomic Message Write Pattern

**CRITICAL:** All message writes MUST use the atomic temp-file-then-rename pattern to prevent race conditions and partial reads.

```python
# CORRECT: Atomic write pattern
import secrets
from pathlib import Path

def write_message(channel_dir: Path, message: dict) -> Path:
    msg_id = f"msg-{timestamp}-{agent}-{secrets.token_hex(2)}"

    # Step 1: Write to temporary file
    tmp_file = channel_dir / f".tmp-{msg_id}.json"
    with open(tmp_file, 'w') as f:
        json.dump(message, f, indent=2)

    # Step 2: Atomic rename (POSIX guarantees atomicity)
    final_file = channel_dir / f"{msg_id}.json"
    tmp_file.rename(final_file)

    return final_file
```

**Why this matters:**
- `rename()` is atomic on POSIX filesystems (including NFS)
- Readers never see partial/corrupt JSON
- Prevents race conditions when multiple agents write simultaneously
- Avoids the need for file locking

**Anti-patterns to AVOID:**
```python
# WRONG: Direct write (readers may see partial content)
with open(channel_dir / f"{msg_id}.json", 'w') as f:
    json.dump(message, f)

# WRONG: Copy instead of rename (not atomic)
shutil.copy(tmp_file, final_file)
```

### 5. Agent Registry

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

### 6. Presence System

Agents publish heartbeat files to indicate availability:

```json
{
  "agent_id": "codex",
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

### 7. Daemon Scripts (Polling-Based)

Each agent has a daemon script that:
1. **Polls** the channel directory every 2 seconds (NFS-compatible)
2. Tracks seen messages to avoid reprocessing
3. Checks if message is addressed to this agent
4. Invokes the underlying CLI with context
5. Posts response back to channel via dual-write

> **Note:** We moved from `inotifywait` to polling because inotifywait
> doesn't work reliably on NFS mounts (misses file creation events).

**Architecture:**
```
┌─────────────────────────────────────────────────────────┐
│                    DAEMON SCRIPT                        │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ poll_loop() │→ │ is_for_us()  │→ │ invoke_cli()  │  │
│  │ (2s cycle)  │  │ (filter)     │  │ (call CLI)    │  │
│  └─────────────┘  └──────────────┘  └───────────────┘  │
│         │                                    │         │
│         ▼                                    ▼         │
│  ┌─────────────┐                    ┌───────────────┐  │
│  │ presence/   │                    │ send-message  │  │
│  │ heartbeat   │                    │ (dual-write)  │  │
│  └─────────────┘                    └───────────────┘  │
└─────────────────────────────────────────────────────────┘
```

**Daemon + Supervisor Pattern:**
Each agent runs two processes:
- **{agent}-daemon** - Polls for messages, invokes CLI, posts responses
- **{agent}-supervisor** - Monitors daemon health, restarts on failure

Example for Codex:
```
codex-supervisor.py (PID 48876)
  └── codex-daemon (PID 2143017)
      └── codex exec resume {session_id} "message"
```

### 8. NATS/JetStream Infrastructure

In addition to the filesystem message bus, we run NATS JetStream for:
- At-least-once delivery semantics
- Message persistence and replay
- Future migration to NATS-primary

**Infrastructure:**

| Component | Location | Purpose |
|-----------|----------|---------|
| NATS-JS | VM 903 (100.66.133.8:4222) | Message broker |
| MinIO | 100.80.120.97:9000 | Large payload storage (>1MB) |
| Stream | CHAT | Agent chat messages |
| Stream | EVT | System events and notifications |

**Dual-Write Mode (Current):**
Every message is written to BOTH:
1. Filesystem (`/mnt/shared/collab/channels/`)
2. NATS JetStream (stream: CHAT)

```python
# In send-message.py
messaging = SyncMessaging(channel, agent_id)
messaging.send(text, in_reply_to)  # Writes to both
```

**Migration Status (Updated 2026-01-15):**

| Phase | Description | Status | Notes |
|-------|-------------|--------|-------|
| 1 | Infrastructure | ✅ Complete | NATS VM 903, MinIO deployed |
| 2 | Dual-Write | ✅ Active | All messages written to file + NATS |
| 3 | Parity Validation | ⏳ In Progress | 116/116 checks passed Jan 13-14; observer restarted Jan 15 |
| 4 | Canary Cutover | ⏳ Pending | Enable NATS consumers for one agent |
| 5 | Full Cutover | ⏳ Pending | All agents read from NATS |
| 6 | Decommission | ⏳ Pending | Disable file writes |

**Validation Results (as of 2026-01-15):**
- Parity observer ran Jan 13-14: 116 messages checked, 0 mismatches (100% match)
- Parity observer restarted Jan 15 after transient timeout crash
- Dual-write test verified: both `file_path` and `nats_ack` returned
- Streams active: CHAT, EVT receiving messages
- Next milestone: 48+ hours of continuous parity validation for Phase 4

## Data Flows

### Message Send Flow

```
1. Agent calls send-message.py script
2. Script generates message ID and timestamp
3. Script writes JSON to .tmp file, atomically renames
4. Script publishes to NATS JetStream (dual-write)
5. Other daemons poll and detect new file (2s cycle)
6. Each daemon checks if message is for them
7. Matching daemon invokes CLI and responds
```

### Agent Invocation Flow

```
1. Daemon detects message addressed to agent
2. Daemon gathers context:
   - Recent channel messages
   - CURRENT-STATE.md memory
   - Domain-specific data (glossary, configs)
3. Daemon builds prompt with role and guardrails
4. Daemon invokes CLI (varies by agent):
   - codex: codex exec resume {session_id} "message"
   - gemini: gemini exec "message" (planned)
   - claude: claude --print "message" (planned)
5. Daemon extracts response text
6. Daemon posts response via send-message.py (dual-write)
7. Daemon updates presence heartbeat
```

## Integration Points

### CLI Execution

| Agent | VM | CLI | Command |
|-------|-----|-----|---------|
| claude | 905 | Claude Code | `claude --print "message"` |
| codex | 901 | Codex CLI | `codex exec resume {sid} "message"` |
| gemini | 902 | Gemini CLI | `gemini exec "message"` |

**CLI Benefits:**
- Full tool access (file operations, bash, etc.)
- Session persistence across messages
- Consistent interface across all agents
- Native execution on each VM (no SSH required)

### External Systems

| System | Integration |
|--------|-------------|
| GitHub | `gh` CLI for issues, PRs |
| Home Assistant | `ha-api.sh` wrapper script |
| BagDB | `bagdb-read.sh` / `bagdb-write.sh` |
| Notion | Python sync scripts |
| Proxmox | `proxmox-*.sh` helper scripts |

## Scalability Considerations

### Current Design (Multi-VM)
- Each agent runs natively on its own VM
- Shared filesystem via NFS mount (`/mnt/shared/collab/`)
- NATS JetStream for message persistence
- Suitable for small team (3-10 agents)

### VM Architecture
| VM | ID | Tailscale IP | Purpose |
|----|-----|--------------|---------|
| Clarence | 600 | 100.83.146.108 | Supervisor, human interface |
| Claude | 905 | 100.80.13.26 | Claude worker (Opus) |
| Codex | 901 | 100.88.166.68 | Codex worker (GPT-5.2) |
| Gemini | 902 | 100.88.38.38 | Gemini worker (Gemini 2.5) |
| NATS | 903 | 100.66.133.8 | NATS JetStream broker |

### Infrastructure Services
All worker VMs include:
- **Log Server** - http://{hostname}:8090 (browse session logs)
- **Session Script** - `{cli}-session` (tmux + logging)
- **GitHub CLI** - `gh` authenticated as graemejross

### Future Scaling Options
- NATS-only message bus (remove filesystem dependency)
- Container per agent (isolation)
- Kubernetes for orchestration
- MinIO for large payload storage

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
