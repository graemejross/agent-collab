# Multi-Agent OS: Setup Guide

## Prerequisites

### System Requirements
- Linux host (Debian/Ubuntu recommended)
- Shared filesystem accessible to all agent hosts
- tmux for running watchers
- jq for JSON processing
- inotify-tools for file monitoring

### API Access
- Anthropic API key (for Claude agents)
- OpenAI/Codex access (for Codex agents)
- Google AI API key (for Gemini agents)

## Installation

### 1. Install Dependencies

```bash
sudo apt update
sudo apt install -y tmux jq inotify-tools python3 python3-pip
pip3 install --user anthropic google-generativeai
```

### 2. Clone Repository

```bash
cd ~
git clone https://github.com/graemejross/agent-collab.git
```

### 3. Create Directory Structure

```bash
sudo mkdir -p /mnt/shared/collab/{channels,presence,registry/agents,docs,workspace,logs}
sudo chown -R $USER:$USER /mnt/shared/collab
```

### 4. Deploy Scripts

```bash
cd ~/agent-collab
./deploy.sh
```

This copies scripts to `/mnt/shared/collab/scripts/` and sets permissions.

### 5. Configure Credentials

Create `~/.credentials` with API keys:

```bash
# Anthropic (Claude)
export ANTHROPIC_API_KEY="sk-ant-..."

# Google (Gemini)
export GOOGLE_API_KEY="AIza..."

# OpenAI (if using directly)
export OPENAI_API_KEY="sk-..."
```

Secure the file:
```bash
chmod 600 ~/.credentials
```

## Starting Agents

### Start Individual Watchers

```bash
# Codex worker
tmux new-session -d -s codex-watcher '/mnt/shared/collab/scripts/codex-watcher agent-os-paper'

# Gemini verifier
tmux new-session -d -s gemini-watcher '/mnt/shared/collab/scripts/gemini-watcher agent-os-paper'

# Documentation steward
tmux new-session -d -s docs-watcher '/mnt/shared/collab/scripts/docs-watcher agent-os-paper'

# Quality control
tmux new-session -d -s qc-watcher '/mnt/shared/collab/scripts/qc-watcher agent-os-paper'

# Incident triage
tmux new-session -d -s triage-watcher '/mnt/shared/collab/scripts/triage-watcher agent-os-paper'

# HA manager
tmux new-session -d -s ha-mgr-watcher '/mnt/shared/collab/scripts/ha-mgr-watcher agent-os-paper'

# Bag analyst
tmux new-session -d -s bags-watcher '/mnt/shared/collab/scripts/bags-watcher agent-os-paper'
```

### Check Running Watchers

```bash
tmux ls
```

### View Watcher Output

```bash
tmux attach -t codex-watcher
# Ctrl-B D to detach
```

### Stop a Watcher

```bash
tmux kill-session -t codex-watcher
```

## Verification

### Check Agent Presence

```bash
/mnt/shared/collab/scripts/who
```

Expected output:
```
AGENT        STATE         CHANNEL           LAST SEEN
─────────────────────────────────────────────────────────
codex-1      AWAKE/IDLE    agent-os-paper    2 seconds ago
gemini-1     AWAKE/IDLE    agent-os-paper    5 seconds ago
docs-1       AWAKE/IDLE    agent-os-paper    3 seconds ago
```

### Send Test Message

```bash
export COLLAB_SESSION=agent-os-paper
export COLLAB_AGENT=human

/mnt/shared/collab/scripts/send-message codex-1 "Hello, are you there?"
```

### Watch Channel Activity

```bash
/mnt/shared/collab/scripts/collab-watch agent-os-paper
```

## Configuration

### Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `COLLAB_SESSION` | Default channel | `agent-os-paper` |
| `COLLAB_AGENT` | Your agent ID | `human` or `claude-1` |
| `ANTHROPIC_API_KEY` | Claude API | `sk-ant-...` |
| `GOOGLE_API_KEY` | Gemini API | `AIza...` |

### Agent Registry

Each agent needs a registration file:

```bash
cat > /mnt/shared/collab/registry/agents/my-agent.json << 'EOF'
{
  "id": "my-agent",
  "model": "model-name",
  "provider": "anthropic",
  "capabilities": ["task1", "task2"],
  "role": "worker",
  "status": "active",
  "cost_tier": 3,
  "notes": "Description of agent"
}
EOF
```

## Troubleshooting

### Watcher Not Responding

1. Check if watcher is running:
   ```bash
   tmux ls | grep watcher-name
   ```

2. Check watcher logs:
   ```bash
   tail -50 /mnt/shared/collab/logs/watcher-name.log
   ```

3. Check message addressing:
   ```bash
   cat /mnt/shared/collab/channels/CHANNEL/msg-*.json | jq '.to'
   ```

### API Errors

1. Verify credentials:
   ```bash
   source ~/.credentials
   echo $ANTHROPIC_API_KEY | head -c 10
   ```

2. Test API directly:
   ```bash
   /mnt/shared/collab/scripts/haiku-exec "Hello"
   ```

### Permission Issues

```bash
# Fix ownership
sudo chown -R $USER:$USER /mnt/shared/collab

# Fix permissions
chmod 755 /mnt/shared/collab/scripts/*
chmod 644 /mnt/shared/collab/registry/agents/*.json
```

### Messages Not Detected

1. Check inotifywait is installed:
   ```bash
   which inotifywait
   ```

2. Verify channel directory exists:
   ```bash
   ls -la /mnt/shared/collab/channels/CHANNEL/
   ```

3. Check is_for_us logic matches addressing

## Multi-Host Setup

For agents on different hosts:

1. Share `/mnt/shared/collab/` via NFS:
   ```bash
   # On server
   echo "/mnt/shared/collab *(rw,sync,no_subtree_check)" >> /etc/exports
   exportfs -ra

   # On clients
   mount -t nfs server:/mnt/shared/collab /mnt/shared/collab
   ```

2. Each host runs its own watchers

3. All hosts see same message bus

## Security Considerations

- Keep API keys in `~/.credentials` (chmod 600)
- Don't commit credentials to git
- Use wrapper scripts to avoid exposing tokens
- Review guardrails in agent registry before deployment
