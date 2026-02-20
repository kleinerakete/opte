#!/usr/bin/env bash
set -e
# Start server using bundled cert/key.
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
PORT="${1:-4443}"
python3 server.py "$PORT"
