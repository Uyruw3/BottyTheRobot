#!/bin/bash
# Botty Prototype - Linux/macOS Launcher
# Usage: ./scripts/run_botty.sh [options]

set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

show_help() {
    cat << 'EOF'
Botty Prototype Launcher
Usage: ./scripts/run_botty.sh [options]

Options:
  -d, --debug      Enable debug logging
  -w, --windowed   Force windowed mode
  -n, --no-web     Disable web dashboard
  -m, --mode MODE  Startup mode: auto, manual, developer (default: auto)
  -h, --help       Show this help message

Examples:
  ./scripts/run_botty.sh
  ./scripts/run_botty.sh --debug --mode developer
  ./scripts/run_botty.sh --windowed --no-web
EOF
    exit 0
}

DEBUG=0
WINDOWED=0
NOWEB=0
MODE="auto"

while [[ $# -gt 0 ]]; do
    case "$1" in
        -d|--debug) DEBUG=1; shift ;;
        -w|--windowed) WINDOWED=1; shift ;;
        -n|--no-web) NOWEB=1; shift ;;
        -m|--mode) MODE="$2"; shift 2 ;;
        -h|--help) show_help ;;
        *) echo "Unknown option: $1"; show_help ;;
    esac
done

export BOTTY_FULLSCREEN=$([ "$WINDOWED" = 1 ] && echo "false" || echo "true")
export BOTTY_DEBUG=$([ "$DEBUG" = 1 ] && echo "1" || echo "0")
export BOTTY_WEB_ENABLED=$([ "$NOWEB" = 1 ] && echo "0" || echo "1")
export BOTTY_MODE="$MODE"

echo "=== Botty Prototype v0.1.0 ==="
echo "Mode: $MODE"
echo "Debug: $( [ "$DEBUG" = 1 ] && echo 'ON' || echo 'OFF')"
echo "Fullscreen: $( [ "$WINDOWED" = 1 ] && echo 'OFF' || echo 'ON')"
echo "Web: $( [ "$NOWEB" = 1 ] && echo 'OFF' || echo 'ON')"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Install Python 3.12+" >&2
    exit 1
fi

PY_VER=$(python3 --version 2>&1)
echo "Using $PY_VER"

# Activate virtual environment if exists
if [ -f ".venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

echo "Starting Botty..."
python3 -m botty

exit $?
