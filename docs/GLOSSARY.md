# Multi-Agent System: Terminology Glossary

## Core Architectural Terms

### Message Bus
- Centralized communication infrastructure at `/mnt/shared/collab/`
- Enables asynchronous message passing between agents
- File-based: messages are JSON files in channel directories
- Supports targeted (@agent) or broadcast (all) messaging

### Channel
- Directory within the message bus containing related messages
- Example: `/mnt/shared/collab/channels/agent-os-paper/`
- Messages ordered chronologically by filename timestamp
- Append-only: messages are never modified after creation

### Watcher
- Background process that monitors a channel for new messages
- Uses `inotifywait` for filesystem event detection
- Zero API cost while idle (no polling)
- Triggers agent invocation when addressed

### Presence
- Real-time status of each agent
- Stored in `/mnt/shared/collab/presence/{agent}.json`
- States: AWAKE/IDLE, AWAKE/WORKING, OFFLINE
- Updated by watcher scripts automatically

### Agent Registry
- Directory of all agent definitions
- Located at `/mnt/shared/collab/registry/agents/`
- Contains capabilities, guardrails, model info
- Used for routing and access control

## Operational Concepts

### Swiss Cheese Model
- Multi-layered error prevention strategy from safety engineering
- Each layer (agent, check, review) has "holes" (blindspots)
- Errors only pass through when holes align across all layers
- Implemented via: peer review, model diversity, automated checks

### Evidence Bundle
- Documentation package accompanying completed work
- Includes: diffs, test results, citations, approval records
- Provides audit trail for all changes
- Required for task completion verification

### Guardrails
- Predefined constraints on agent behavior
- Defined in agent registry files
- Examples: blocked domains, required wrappers, approval requirements
- Enforced in watcher prompts and tool access

### Approval Workflow
- Process for authorizing changes, especially high-risk ones
- Risk levels: Low (self-review), Medium (peer review), High (human approval)
- lisarda-ha changes always require human approval (Mum's house)

## Economic Terms

### Cost Tier
- Classification of agents by API cost
- Tier 1 (cheapest): Gemini Flash (~$0.01/1K tokens)
- Tier 2: Claude Haiku (~$0.08/1K tokens)
- Tier 3: Codex (~$0.15/1K tokens)
- Tier 4: Claude Sonnet (~$0.30/1K tokens)
- Tier 5 (highest): Claude Opus (~$1.50/1K tokens)
- Route simple tasks to lower tiers for cost efficiency

### Zero-Token Monitoring
- Watcher pattern that uses no API tokens while idle
- `inotifywait` monitors filesystem, not model API
- Agent only invoked when message addressed to it
- Enables always-on presence without ongoing cost

## Agent Roles

### Worker
- Agent that executes tasks (implementation, coding, analysis)
- Examples: claude-1, codex-1, bags-1, ha-mgr-1
- Reports results back to channel

### Verifier
- Agent that reviews and validates work
- Examples: gemini-1, qc-1
- Checks for errors, policy compliance, completeness
- Provides independent assessment

### Steward
- Agent that maintains system resources
- Example: docs-1 (documentation steward)
- Focuses on consistency and organization

### Supervisor
- Agent that orchestrates team work (future)
- Decomposes tasks, assigns to workers
- Monitors progress, resolves conflicts
- Reports to human

## Message Types

### chat
- General conversation message
- Default type for most communication

### task_assign
- Work assignment from supervisor to worker
- Includes task_id, criteria, deadline

### task_result
- Completion report from worker
- Includes evidence bundle

### review_vote
- Verification result from reviewer
- Includes pass/fail for criteria

### ha_report
- Home Assistant status report
- From ha-mgr-1 agent

### bag_analysis
- Baggage analysis report
- From bags-1 agent

### incident
- Problem report requiring triage
- Processed by triage-1
