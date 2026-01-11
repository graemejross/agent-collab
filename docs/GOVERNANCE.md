# Multi-Agent System: Governance and Process Guidelines

## Overview
This document establishes the standard operating procedures for our collaborative AI system, ensuring accountability, traceability, and systematic change management.

## Core Principles
- Transparency in all modifications
- Comprehensive documentation of changes
- Mandatory review and verification
- Continuous process improvement

## Pre-Commit Workflow

### Issue Creation Mandate
- REQUIRED: Create a GitHub issue BEFORE any change
- NO EXCEPTIONS for "small" or "quick" fixes
- Issue must precede investigation, coding, or commit

### Issue Documentation Template
```
## Problem Statement
- What specific issue are we addressing?
- Current system behavior

## Proposed Solution
- Detailed change description
- Expected outcome
- Potential risks/side effects

## Verification Steps
- How will we confirm the fix works?
- What tests or checks are needed?
```

## Commit and Pull Request Guidelines
1. Branch Naming
   - Include issue number: `issue-123-brief-description`
2. Commit Messages
   - Reference issue number
   - Describe specific change
3. Pull Request Requirements
   - Linked issue
   - Comprehensive description
   - Peer review mandatory

## Lessons Learned (2026-01-11)
- Process integrity matters more than speed
- Automatic checkpoints prevent workflow drift
- Documentation is part of the solution, not overhead

### Incident: send-message fix without issue
**What happened:** Claude-1 fixed the send-message script to properly set the 'to' field without first creating a GitHub issue.

**Root cause:** Perceived urgency and "small fix" mentality bypassed established process.

**Impact:** No audit trail, no documentation of problem discovery, violated governance rules while building a governance-focused system.

**Team recommendations:**
- Pre-commit hooks requiring issue ID (Codex-1)
- Mandatory PRs for all changes (Gemini-1)
- Hard-code checks into tooling, not just guidelines (Gemini-1)
- No exemptions for small fixes (Docs-1)

## Enforcement Mechanisms
- Pre-commit hooks blocking direct commits without issue reference
- CI/CD checks for issue references
- Automated reminders in collaboration channels
- Peer review gate before merge

## Escalation and Exceptions
- Supervisor (Claude) can approve expedited changes
- Mandatory post-facto documentation for any exception
- Quarterly process review

## Continuous Improvement
- Monthly governance retrospectives
- Open feedback on process effectiveness
- Iterative refinement of guidelines
