#!/usr/bin/env python3
"""
Agent Collab Poller Daemon

Watches for new messages in a collaboration session and displays them.
Also sends heartbeat signals to indicate agent presence.

Usage:
    ./poller.py <session_id> <agent_name>
    ./poller.py mysession claude
"""

import os
import sys
import json
import time
import signal
import hashlib
from pathlib import Path
from datetime import datetime, timezone

# Configuration
COLLAB_DIR = Path("/mnt/shared/collab")
POLL_INTERVAL = 1.0  # seconds
HEARTBEAT_INTERVAL = 10.0  # seconds
COLORS = {
    "claude": "\033[94m",  # Blue
    "codex": "\033[92m",  # Green
    "human": "\033[93m",  # Yellow
    "system": "\033[90m",  # Gray
    "reset": "\033[0m",
    "bold": "\033[1m",
}


class Poller:
    def __init__(self, session_id: str, agent_name: str):
        self.session_id = session_id
        self.agent_name = agent_name
        self.running = True
        self.seen_messages = set()
        self.last_heartbeat = 0

        # Paths
        self.channel_dir = COLLAB_DIR / "channels" / session_id
        self.presence_dir = COLLAB_DIR / "signals" / "presence"
        self.session_file = COLLAB_DIR / "sessions" / f"{session_id}.json"

        # Ensure directories exist
        self.channel_dir.mkdir(parents=True, exist_ok=True)

        # Load existing message IDs to avoid replaying history
        self._load_seen_messages()

        # Register signal handlers
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

    def _load_seen_messages(self):
        """Load IDs of existing messages to avoid replaying on startup."""
        if self.channel_dir.exists():
            for msg_file in self.channel_dir.glob("*.json"):
                self.seen_messages.add(msg_file.name)

    def _handle_shutdown(self, signum, frame):
        """Handle graceful shutdown."""
        self.running = False
        self._remove_presence()
        print(f"\n{COLORS['system']}[Poller stopped]{COLORS['reset']}")

    def _send_heartbeat(self):
        """Send presence heartbeat."""
        now = time.time()
        if now - self.last_heartbeat >= HEARTBEAT_INTERVAL:
            heartbeat = {
                "agent": self.agent_name,
                "session": self.session_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "active",
            }
            heartbeat_file = self.presence_dir / f"{self.agent_name}.json"
            self._atomic_write(heartbeat_file, heartbeat)
            self.last_heartbeat = now

    def _remove_presence(self):
        """Remove presence file on shutdown."""
        heartbeat_file = self.presence_dir / f"{self.agent_name}.json"
        try:
            heartbeat_file.unlink(missing_ok=True)
        except Exception:
            pass

    def _atomic_write(self, path: Path, data: dict):
        """Write JSON atomically using tmp file + rename."""
        tmp_path = path.with_suffix(".tmp")
        try:
            with open(tmp_path, "w") as f:
                json.dump(data, f, indent=2)
            tmp_path.rename(path)
        except Exception as e:
            print(f"{COLORS['system']}[Error writing {path}: {e}]{COLORS['reset']}")

    def _format_message(self, msg: dict) -> str:
        """Format a message for display."""
        sender = msg.get("from", "unknown")
        color = COLORS.get(sender, COLORS["system"])
        text = msg.get("content", {}).get("text", "")
        timestamp = msg.get("timestamp", "")

        # Parse and format timestamp
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            time_str = dt.strftime("%H:%M:%S")
        except Exception:
            time_str = "??:??:??"

        # Format the message
        header = f"{COLORS['bold']}{color}[{time_str}] {sender}{COLORS['reset']}"

        # Handle code blocks
        code = msg.get("content", {}).get("code")
        if code:
            return f"{header}: {text}\n```\n{code}\n```"

        return f"{header}: {text}"

    def poll_messages(self):
        """Check for new messages and display them."""
        if not self.channel_dir.exists():
            return

        # Get all message files sorted by name (timestamp-based)
        msg_files = sorted(self.channel_dir.glob("*.json"))

        for msg_file in msg_files:
            if msg_file.name in self.seen_messages:
                continue

            try:
                with open(msg_file) as f:
                    msg = json.load(f)

                # Don't display our own messages (we already see them when sending)
                if msg.get("from") != self.agent_name:
                    print(self._format_message(msg))

                self.seen_messages.add(msg_file.name)
            except json.JSONDecodeError:
                # File might be mid-write, skip for now
                pass
            except Exception as e:
                print(
                    f"{COLORS['system']}[Error reading {msg_file}: {e}]{COLORS['reset']}"
                )

    def run(self):
        """Main polling loop."""
        print(
            f"{COLORS['system']}[Poller started for session '{self.session_id}' as '{self.agent_name}']{COLORS['reset']}"
        )
        print(
            f"{COLORS['system']}[Polling every {POLL_INTERVAL}s, heartbeat every {HEARTBEAT_INTERVAL}s]{COLORS['reset']}"
        )
        print(f"{COLORS['system']}[Press Ctrl+C to stop]{COLORS['reset']}")
        print()

        while self.running:
            try:
                self.poll_messages()
                self._send_heartbeat()
                time.sleep(POLL_INTERVAL)
            except Exception as e:
                print(f"{COLORS['system']}[Polling error: {e}]{COLORS['reset']}")
                time.sleep(POLL_INTERVAL)


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <session_id> <agent_name>")
        print(f"Example: {sys.argv[0]} mysession claude")
        sys.exit(1)

    session_id = sys.argv[1]
    agent_name = sys.argv[2]

    if agent_name not in ("claude", "codex", "human"):
        print(
            f"Warning: agent_name '{agent_name}' is not standard (claude/codex/human)"
        )

    poller = Poller(session_id, agent_name)
    poller.run()


if __name__ == "__main__":
    main()
