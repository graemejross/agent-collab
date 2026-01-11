# Multi-Agent OS: Frequently Asked Questions

## General Questions

### What is this system?
A supervised multi-agent AI collaboration system where multiple AI agents (Claude, Codex, Gemini) work together under human oversight. The human boss directs work, agents execute and verify each other's output, creating reliable results through layered defense.

### Why use multiple agents instead of one?
Single agents have blindspots. Multiple agents from different model families catch errors that one agent might miss. This "Swiss cheese model" ensures that even if one layer fails, others catch the problem.

### Who is in charge?
The human is always the boss. Agents cannot override human decisions, and high-risk actions require human approval. The system augments human capability, not replaces human judgment.

## Architecture Questions

### What is the message bus?
The shared filesystem at `/mnt/shared/collab/` where all agent communication happens. Messages are JSON files stored in channel directories. It's like a shared chat system but file-based.

### Where do messages live?
In channel directories:
```
/mnt/shared/collab/channels/{channel-name}/msg-*.json
```

### How do agents know about each other?
Agent metadata is stored in the registry:
```
/mnt/shared/collab/registry/agents/{agent-id}.json
```

### What is a watcher?
A background process that monitors a channel for new messages. When a message is addressed to its agent, it invokes the underlying AI model and posts the response. Watchers enable asynchronous coordination with zero cost while idle.

## Agent Questions

### How do the different agents contribute?

| Agent | Model | Role |
|-------|-------|------|
| claude-1 | Claude Opus | Complex reasoning, coordination |
| codex-1 | GPT-5.2 Codex | Code implementation |
| gemini-1 | Gemini Flash | Independent verification |
| docs-1 | Claude Haiku | Documentation |
| ha-mgr-1 | Codex | Home Assistant management |
| bags-1 | Claude Sonnet | Baggage analysis |

### How do I check who is active?
```bash
/mnt/shared/collab/scripts/who
```

### Why are there different cost tiers?
AI APIs charge by token. Simple tasks use cheap models (Gemini Flash at $0.01/1K tokens), complex tasks use expensive ones (Claude Opus at $1.50/1K tokens). This optimizes cost without sacrificing quality.

## Communication Questions

### How do I send a message to an agent?
```bash
export COLLAB_SESSION=agent-os-paper
export COLLAB_AGENT=human
/mnt/shared/collab/scripts/send-message codex-1 "Your message here"
```

### How do I address multiple agents?
Use @mentions:
```bash
send-message all "@codex-1 @gemini-1 Please review this"
```

### Why didn't an agent respond?
Check:
1. Is the watcher running? `tmux ls | grep watcher`
2. Was the message addressed correctly? Check `to` field or @mention
3. Any errors? `tail /mnt/shared/collab/logs/*-watcher.log`

## Quality & Safety Questions

### How is quality ensured?
The "Swiss cheese model" - multiple independent layers:
1. Static analysis (automated)
2. Peer review (different agent)
3. Adversarial review (agent tries to break it)
4. Automated tests
5. Policy compliance check
6. Human approval (high-risk only)

### What are guardrails?
Constraints on what each agent can do, defined in their registry entry. For example, ha-mgr-1 cannot modify locks or security cameras, and bags-1 can only read the database, not write.

### What requires human approval?
- Changes to lisarda-ha (Mum's house - reliability critical)
- Security entity modifications (locks, alarms, cameras)
- Database write operations
- Destructive operations

## Process Questions

### What governance rules must be followed?
1. Create GitHub issue BEFORE any change
2. No exceptions for "small fixes"
3. Commit messages reference issue number
4. Pull requests require peer review

### Why create an issue first?
The issue documents the journey, not just the result. Future sessions can understand what problem was solved and why, creating institutional memory.

### What if I made a change without an issue?
Document it retroactively, but try not to repeat. The process exists for good reasons - auditability, learning, and preventing mistakes.

## Troubleshooting

### Agent not responding?
1. Check watcher: `tmux ls | grep {agent}-watcher`
2. Check logs: `tail /mnt/shared/collab/logs/{agent}-watcher.log`
3. Check presence: `cat /mnt/shared/collab/presence/{agent}.json`
4. Restart: `tmux kill-session -t {agent}-watcher && tmux new-session -d -s {agent}-watcher '...'`

### Message not detected?
1. Check addressing - must use agent ID or @mention
2. Check `to` field in JSON
3. Look for "Message not for us" in watcher log

### Credentials error?
1. Check file exists: `ls -la ~/.credentials`
2. Check permissions: should be `600`
3. Verify content: `source ~/.credentials && echo $ANTHROPIC_API_KEY | head -c 10`

### Where do I get help?
1. Read the docs in `/mnt/shared/collab/docs/`
2. Ask an agent: `send-message docs-1 "How do I..."`
3. Check OPERATIONS.md for incident response
4. Ask the human (Graeme)

## Further Reading

| Topic | Document |
|-------|----------|
| System overview | [OVERVIEW.md](OVERVIEW.md) |
| Technical architecture | [ARCHITECTURE.md](ARCHITECTURE.md) |
| All agents | [AGENT-SPEC.md](AGENT-SPEC.md) |
| Getting started | [QUICKSTART.md](QUICKSTART.md) |
| Adding agents | [NEW-AGENT-GUIDE.md](NEW-AGENT-GUIDE.md) |
| Operations | [OPERATIONS.md](OPERATIONS.md) |
| Security | [SECURITY.md](SECURITY.md) |
| Process rules | [GOVERNANCE.md](GOVERNANCE.md) |
