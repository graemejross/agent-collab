#!/bin/bash
#
# deploy.sh - Deploy agent-collab scripts to shared NFS location
#
# Usage:
#   ./deploy.sh           # Deploy all scripts
#   ./deploy.sh --setup   # Deploy and create ~/collab symlinks
#

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEPLOY_DIR="/mnt/shared/collab/scripts"

echo "Deploying agent-collab scripts..."

# Ensure deploy directory exists
mkdir -p "$DEPLOY_DIR"

# Scripts to deploy
SCRIPTS=(
    "poller.py"
    "send-message"
    "read-messages"
    "collab-start"
    "collab-status"
)

# Copy scripts
for script in "${SCRIPTS[@]}"; do
    if [[ -f "${SCRIPT_DIR}/${script}" ]]; then
        cp "${SCRIPT_DIR}/${script}" "${DEPLOY_DIR}/"
        chmod +x "${DEPLOY_DIR}/${script}"
        echo "  Deployed: $script"
    else
        echo "  Warning: $script not found"
    fi
done

echo "Scripts deployed to: $DEPLOY_DIR"

# Optional: set up symlinks
if [[ "$1" == "--setup" ]]; then
    echo ""
    echo "Setting up ~/collab symlinks..."
    mkdir -p ~/collab
    for script in "${SCRIPTS[@]}"; do
        ln -sf "${DEPLOY_DIR}/${script}" ~/collab/
    done
    echo "Symlinks created in ~/collab/"
    echo ""
    echo "Add to your shell profile:"
    echo "  export PATH=\"\$HOME/collab:\$PATH\""
fi

echo ""
echo "Done!"
