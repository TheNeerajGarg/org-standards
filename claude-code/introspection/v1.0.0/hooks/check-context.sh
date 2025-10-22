#!/bin/bash
# check-context.sh - View current Claude session context stats

set -euo pipefail

TRACKER_DIR="$HOME/.claude/context_tracker"
MAX_MESSAGES="${CLAUDE_MAX_MESSAGES:-15}"
MAX_LARGE_FILES="${CLAUDE_MAX_LARGE_FILES:-2}"

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "🔍 Claude Code Context Tracker"
echo "================================"
echo ""

# Check if tracker directory exists
if [ ! -d "$TRACKER_DIR" ]; then
    echo "✅ No active session tracking found"
    echo "   (Context tracking starts on first tool use)"
    exit 0
fi

# Find all active sessions
sessions=($(ls -1 "$TRACKER_DIR"/ 2>/dev/null | grep -o 'pid-[0-9]*' | sort -u || echo ""))

if [ ${#sessions[@]} -eq 0 ] || [ -z "${sessions[0]}" ]; then
    echo "✅ No active sessions found"
    exit 0
fi

echo "📊 Active Sessions: ${#sessions[@]}"
echo ""

total_cost_estimate=0

for session in "${sessions[@]}"; do
    # Extract PID
    pid=$(echo "$session" | sed 's/pid-//')

    # Check if process is still running
    if ps -p "$pid" > /dev/null 2>&1; then
        status="${GREEN}RUNNING${NC}"
        runtime=$(ps -p "$pid" -o etime= | tr -d ' ')
    else
        status="${YELLOW}STOPPED${NC}"
        runtime="N/A"
    fi

    # Get counters
    messages=0
    large_files=0

    if [ -f "$TRACKER_DIR/${session}_messages" ]; then
        messages=$(cat "$TRACKER_DIR/${session}_messages")
    fi

    if [ -f "$TRACKER_DIR/${session}_large_files" ]; then
        large_files=$(cat "$TRACKER_DIR/${session}_large_files")
    fi

    # Estimate context size
    # Base: 15K, Messages: 2K each, Large files: 30K each
    context_tokens=$((15000 + (messages * 2000) + (large_files * 30000)))

    # Estimate cost (input only, at $3/M tokens)
    cost_per_message=$(echo "scale=3; $context_tokens * 3 / 1000000" | bc)
    session_cost=$(echo "scale=2; $cost_per_message * $messages" | bc)
    total_cost_estimate=$(echo "scale=2; $total_cost_estimate + $session_cost" | bc)

    # Status indicators
    msg_indicator=""
    if [ "$messages" -ge "$MAX_MESSAGES" ]; then
        msg_indicator="${RED}⚠️${NC}"
    elif [ "$messages" -ge $((MAX_MESSAGES - 3)) ]; then
        msg_indicator="${YELLOW}⚠️${NC}"
    else
        msg_indicator="${GREEN}✓${NC}"
    fi

    file_indicator=""
    if [ "$large_files" -ge "$MAX_LARGE_FILES" ]; then
        file_indicator="${RED}⚠️${NC}"
    elif [ "$large_files" -ge $((MAX_LARGE_FILES - 1)) ] && [ "$large_files" -gt 0 ]; then
        file_indicator="${YELLOW}⚠️${NC}"
    else
        file_indicator="${GREEN}✓${NC}"
    fi

    echo -e "Session: $session"
    echo -e "  Status: $status (PID: $pid, Runtime: $runtime)"
    echo -e "  Messages: $msg_indicator $messages/$MAX_MESSAGES"
    echo -e "  Large Files: $file_indicator $large_files/$MAX_LARGE_FILES"
    echo -e "  Est. Context: ~$(printf "%'d" $context_tokens) tokens"
    echo -e "  Cost per msg: \$$cost_per_message"
    echo -e "  Session cost: \$$session_cost (input tokens only)"

    # Recommendations
    if [ "$messages" -ge "$MAX_MESSAGES" ] || [ "$large_files" -ge "$MAX_LARGE_FILES" ]; then
        echo -e "  ${RED}💡 RECOMMEND: Exit and start fresh session${NC}"
    fi

    echo ""
done

echo "================================"
echo -e "Total estimated session cost: \$$total_cost_estimate"
echo ""

# Show cleanup command
if [ ${#sessions[@]} -gt 0 ]; then
    echo "Commands:"
    echo "  Reset all counters:  rm -rf $TRACKER_DIR/*"
    echo "  View this again:     ~/org-standards/claude-code/introspection/current/hooks/check-context.sh"
fi
