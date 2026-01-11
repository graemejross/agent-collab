# Multi-Agent OS: Quick Start Guide

Get up and running in 5 minutes.

## Prerequisites

- Linux system with bash
- `jq`, `tmux`, `inotify-tools` installed
- At least one API key (Anthropic, Google, or OpenAI)

## 1. Clone and Setup (1 minute)

```bash
# Clone repository
git clone https://github.com/graemejross/agent-collab.git
cd agent-collab

# Create directories
sudo mkdir -p /mnt/shared/collab/{channels,presence,registry/agents,docs,workspace,logs}
sudo chown -R $USER:$USER /mnt/shared/collab

# Deploy scripts
./deploy.sh
```

## 2. Configure Credentials (1 minute)

Create `~/.credentials`:
```bash
cat > ~/.credentials << 'EOF'
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
export GOOGLE_API_KEY="AIza-your-key-here"
EOF
chmod 600 ~/.credentials
```

## 3. Start Your First Agent (1 minute)

Let's start the Gemini verifier (cheapest option):

```bash
# Create a channel
mkdir -p /mnt/shared/collab/channels/test-channel

# Start gemini-1 watcher
tmux new-session -d -s gemini-watcher '/mnt/shared/collab/scripts/gemini-watcher test-channel'

# Verify it's running
sleep 2
/mnt/shared/collab/scripts/who
```

You should see:
```
AGENT        STATE         CHANNEL        LAST SEEN
gemini-1     AWAKE/IDLE    test-channel   2 seconds ago
```

## 4. Send Your First Message (1 minute)

```bash
# Set environment
export COLLAB_SESSION=test-channel
export COLLAB_AGENT=human

# Send a message to gemini-1
/mnt/shared/collab/scripts/send-message gemini-1 "Hello! Can you introduce yourself?"
```

## 5. See the Response (1 minute)

```bash
# Wait a moment, then check for response
sleep 10
ls -lt /mnt/shared/collab/channels/test-channel/

# Read the response
cat /mnt/shared/collab/channels/test-channel/msg-*-gemini-*.json | jq -r '.content.text'
```

## You're Done!

You now have a working multi-agent system with one agent.

## Next Steps

### Add More Agents

```bash
# Documentation steward (Claude Haiku)
tmux new-session -d -s docs-watcher '/mnt/shared/collab/scripts/docs-watcher test-channel'

# Quality control (Gemini Flash)
tmux new-session -d -s qc-watcher '/mnt/shared/collab/scripts/qc-watcher test-channel'
```

### Watch the Channel Live

```bash
/mnt/shared/collab/scripts/collab-watch test-channel
```

### Ask Multiple Agents

```bash
send-message all "@gemini-1 @docs-1 What do you think about multi-agent systems?"
```

### Check All Agent Status

```bash
/mnt/shared/collab/scripts/who
```

## Common Commands

| Command | Purpose |
|---------|---------|
| `who` | List all agents and status |
| `send-message AGENT "text"` | Send message to agent |
| `collab-watch CHANNEL` | Watch channel activity |
| `tmux ls` | List running watchers |
| `tmux kill-session -t NAME` | Stop a watcher |

## Troubleshooting

### Agent not responding?

1. Check if watcher is running: `tmux ls | grep watcher`
2. Check logs: `tail /mnt/shared/collab/logs/*-watcher.log`
3. Verify credentials: `source ~/.credentials && echo $GOOGLE_API_KEY | head -c 10`

### Message not detected?

1. Check addressing: message must include agent name or @mention
2. Check `to` field in JSON: should be agent ID or "all"
3. Check watcher log for "Message not for us"

### Permission denied?

```bash
sudo chown -R $USER:$USER /mnt/shared/collab
chmod 755 /mnt/shared/collab/scripts/*
```

## Learn More

- [OVERVIEW.md](OVERVIEW.md) - System concepts and principles
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical deep-dive
- [AGENT-SPEC.md](AGENT-SPEC.md) - All available agents
- [NEW-AGENT-GUIDE.md](NEW-AGENT-GUIDE.md) - Add your own agents
