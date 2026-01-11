# Multi-Agent OS: Security Guide

## Security Model Overview

The multi-agent system implements defense-in-depth with multiple security layers:

```
┌─────────────────────────────────────────────────────────┐
│                    HUMAN OVERSIGHT                      │
│         (Final authority, high-risk approval)           │
├─────────────────────────────────────────────────────────┤
│                    AGENT GUARDRAILS                     │
│      (Per-agent constraints defined in registry)        │
├─────────────────────────────────────────────────────────┤
│                    API WRAPPERS                         │
│     (Credentials hidden, operations constrained)        │
├─────────────────────────────────────────────────────────┤
│                    AUDIT TRAIL                          │
│        (All messages logged, full history)              │
└─────────────────────────────────────────────────────────┘
```

## Credential Management

### Storage
All credentials stored in `~/.credentials` with restricted permissions:

```bash
# Create credentials file
cat > ~/.credentials << 'EOF'
# API Keys
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="AIza..."
export OPENAI_API_KEY="sk-..."

# Service credentials
export HA_TOKEN_HOME="eyJ..."
export HA_TOKEN_LISARDA="eyJ..."
EOF

# Restrict permissions (owner read/write only)
chmod 600 ~/.credentials
```

### Loading
Scripts source credentials at runtime:
```bash
source ~/.credentials
```

### Never Expose
- **Never** include credentials in command arguments
- **Never** log credential values
- **Never** commit credentials to git
- **Never** display in chat messages

### Wrapper Scripts
Use wrapper scripts that handle credentials internally:

| System | Wrapper | Credentials |
|--------|---------|-------------|
| Home Assistant | `~/homeassistant/ha-api.sh` | `~/.ha-credentials` |
| BagDB | `~/bagdb-tools/scripts/bagdb-read.sh` | `~/.pgpass` |
| Proxmox | `~/proxmox/proxmox-api.sh` | `~/.credentials` |

## Agent Guardrails

Each agent has constraints defined in their registry entry:

### Example: ha-mgr-1 Guardrails
```json
{
  "guardrails": {
    "api_wrapper_required": "~/homeassistant/ha-api.sh",
    "direct_api_forbidden": true,
    "blocked_domains": ["lock", "alarm_control_panel", "camera", "siren"],
    "blocked_patterns": ["*_door_lock", "*_alarm_*", "*_security_*"],
    "changes_require_approval": true,
    "lisarda_requires_human_approval": true,
    "cannot": ["restart_ha", "remove_devices", "modify_security_entities"]
  }
}
```

### Guardrail Types

| Type | Purpose | Example |
|------|---------|---------|
| `blocked_domains` | Entity types agent cannot touch | lock, camera |
| `blocked_patterns` | Entity name patterns to block | *_security_* |
| `api_wrapper_required` | Must use specified wrapper | ha-api.sh |
| `read_only` | No write operations | bags-1 database |
| `requires_approval` | Human must approve changes | lisarda-ha |
| `cannot` | Specific forbidden actions | restart_ha |

### Enforcement
Guardrails are enforced in the watcher prompt:
```bash
YOUR GUARDRAILS:
- MUST use ~/homeassistant/ha-api.sh wrapper for ALL API calls
- CANNOT modify security entities: lock, alarm_control_panel, camera, siren
- CANNOT restart Home Assistant
- lisarda-ha changes require HUMAN approval
```

## Access Control

### File Permissions
```bash
# Credentials: owner only
chmod 600 ~/.credentials
chmod 600 ~/.ha-credentials
chmod 600 ~/.pgpass

# Scripts: executable by owner
chmod 755 /mnt/shared/collab/scripts/*

# Registry: readable, not world-writable
chmod 644 /mnt/shared/collab/registry/agents/*.json

# Logs: owner read/write
chmod 644 /mnt/shared/collab/logs/*.log
```

### Channel Access
- All agents can **read** all channels
- Agents only **write** to channels they're participating in
- Human can read and write to any channel

### System Access
| Agent | Database | Home Assistant | Proxmox | GitHub |
|-------|----------|----------------|---------|--------|
| claude-1 | Read/Write | Via wrapper | Via wrapper | Full |
| codex-1 | None | None | None | None |
| gemini-1 | None | None | None | None |
| ha-mgr-1 | None | Read + limited write | None | None |
| bags-1 | Read only | None | None | None |

## Audit Trail

### Message Logging
Every message is persisted as a JSON file:
```
/mnt/shared/collab/channels/{channel}/msg-{timestamp}-{agent}-{id}.json
```

Messages are **never deleted** during normal operation.

### What's Logged
- All agent-to-agent communication
- All human commands
- All agent responses
- Timestamps for every action
- Reply chains (in_reply_to field)

### Archival
Use `collab-snapshot` to archive channels:
```bash
/mnt/shared/collab/scripts/collab-snapshot agent-os-paper
```

### Log Retention
- Channel messages: Permanent (until manual cleanup)
- Watcher logs: Rotate weekly, keep 4 weeks
- Presence files: Overwritten on each update

## Risk Classification

### Risk Levels

| Level | Description | Approval Required |
|-------|-------------|-------------------|
| Low | Read operations, status checks | Self (agent) |
| Medium | Configuration changes, non-critical writes | Peer review |
| High | Security changes, critical systems | Human approval |
| Critical | Destructive operations, credential changes | Explicit human command |

### High-Risk Operations
These always require human approval:
- Changes to lisarda-ha (Mum's house)
- Security entity modifications (locks, alarms)
- Database write operations
- Credential rotation
- Agent registry changes

### Automatic Blocks
These are blocked regardless of approval:
- Direct API calls bypassing wrappers
- Credential exposure in messages
- Bulk destructive operations
- Security entity modifications by ha-mgr-1

## Incident Security

### Credential Compromise
If a credential is exposed:
1. **Immediately rotate** the affected credential
2. **Audit** recent messages for exposure
3. **Update** all systems using that credential
4. **Document** incident in LESSONS-LEARNED

### Rogue Agent
If an agent behaves unexpectedly:
1. **Stop** the watcher immediately
2. **Review** recent messages from that agent
3. **Check** for prompt injection in inputs
4. **Restart** with additional guardrails if needed

### Data Exposure
If sensitive data appears in channel:
1. **Do not** delete (breaks audit trail)
2. **Document** the exposure
3. **Assess** impact (what was exposed, to whom)
4. **Notify** affected parties if required

## Security Best Practices

### For Operators
1. Keep credentials in `~/.credentials` only
2. Use wrapper scripts for all external APIs
3. Review agent guardrails before deployment
4. Monitor logs for unusual patterns
5. Rotate credentials periodically

### For Agent Developers
1. Never hardcode credentials in watchers
2. Always use the provided exec wrappers
3. Include guardrails in registry entry
4. Test with restricted permissions first
5. Document security requirements

### For the System
1. Run watchers with minimal privileges
2. Use separate credentials per service
3. Enable audit logging on external systems
4. Implement network segmentation if scaling
5. Regular security reviews of guardrails

## Security Checklist

Before deploying a new agent:
- [ ] Registry entry includes appropriate guardrails
- [ ] Watcher uses credential wrapper (not raw keys)
- [ ] Blocked domains/patterns defined if needed
- [ ] Approval requirements specified
- [ ] Read-only flag set if applicable
- [ ] Tested with restricted permissions
- [ ] Documented in AGENT-SPEC.md
