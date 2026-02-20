#!/usr/bin/env bash
# Unified launcher for this bundle.
# Usage: ./run.sh [demo|flask|node] [PORT]
CMD="${1:-demo}"
PORT="${2:-4443}"

case "$CMD" in
  demo)
    echo "Starting minimal demo HTTPS server (python stdlib) on port $PORT..."
    ./start.sh "$PORT"
    ;;
  flask)
    echo "Starting Flask HTTPS app on port $PORT..."
    python3 app_flask.py "$PORT"
    ;;
  node)
    echo "Starting Node/Express HTTPS on port $PORT... (requires Node.js installed)"
    node server_node.js "$PORT"
    ;;
  *)
    echo "Unknown command. Use demo, flask or node."
    ;;
esac
