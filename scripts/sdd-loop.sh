#!/bin/bash
set -euo pipefail

SELF_PATH="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
RESOLVED_PATH="$(readlink -f "$SELF_PATH" 2>/dev/null || echo "$SELF_PATH")"
# If symlink, resolve to the project directory (where the symlink lives, not scripts/)
LINK_DIR="$(dirname "$SELF_PATH")"
SCRIPTS_DIR="$(cd "$(dirname "$RESOLVED_PATH")" && pwd)"
if [ "$LINK_DIR" != "$SCRIPTS_DIR" ]; then
    SCRIPT_DIR="$LINK_DIR"
else
    SCRIPT_DIR="$SCRIPTS_DIR"
fi
TASK_DIR="${SCRIPT_DIR}/task"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

SKIP_PERMISSIONS=false
DRY_RUN=false

usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Runs /sdd:loop automatically until all phases are completed."
    echo ""
    echo "Options:"
    echo "  -y, --skip-permissions    Auto-approve all permissions (dangerous)"
    echo "  -n, --dry-run            Show what would be executed without running"
    echo "  -h, --help               Show this help message"
}

while [[ $# -gt 0 ]]; do
    case $1 in
        -y|--skip-permissions) SKIP_PERMISSIONS=true; shift ;;
        -n|--dry-run) DRY_RUN=true; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown option: $1"; usage; exit 1 ;;
    esac
done

if [ ! -d "$TASK_DIR" ]; then
    echo -e "${RED}Error: task/ directory not found at ${TASK_DIR}${NC}"
    echo -e "${YELLOW}Run /sdd:tech-spec first to generate phase files.${NC}"
    exit 1
fi

pending_count() {
    local count=0
    for f in "$TASK_DIR"/phase-*.md; do
        [ -f "$f" ] || continue
        grep -q "Status: PENDENTE" "$f" 2>/dev/null && count=$((count + 1))
    done
    echo "$count"
}

get_first_pending() {
    for f in "$TASK_DIR"/phase-*.md; do
        [ -f "$f" ] || continue
        if grep -q "Status: PENDENTE" "$f" 2>/dev/null; then
            echo "$f"
            return 0
        fi
    done
    return 1
}

initial_pending=$(pending_count)
if [ "$initial_pending" -eq 0 ]; then
    echo -e "${GREEN}${BOLD}No pending phases found.${NC}"
    echo ""
    for f in "$TASK_DIR"/phase-*.md; do
        [ -f "$f" ] || continue
        status=$(grep "^## Status:" "$f" | head -1 | sed 's/## Status: //')
        name=$(head -1 "$f" | sed 's/^# //')
        echo "  ${name} → ${status}"
    done
    exit 0
fi

echo -e "${BOLD}Found ${initial_pending} pending phase(s). Starting loop...${NC}"

OPENCODE_ARGS=("run" "--command" "sdd:loop")
if [ "$SKIP_PERMISSIONS" = true ]; then
    OPENCODE_ARGS+=("--dangerously-skip-permissions")
fi

iteration=0
while true; do
    current_pending=$(pending_count)

    if [ "$current_pending" -eq 0 ]; then
        echo ""
        echo -e "${GREEN}${BOLD}All phases completed!${NC}"
        break
    fi

    first_pending=$(get_first_pending)
    next_phase_name=$(basename "$first_pending")
    next_phase_title=$(head -1 "$first_pending" | sed 's/^# //')

    iteration=$((iteration + 1))

    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}  Iteration ${iteration} | ${next_phase_title} | ${current_pending} remaining${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}[DRY RUN] Would run: opencode ${OPENCODE_ARGS[*]}${NC}"
        break
    fi

    echo -e "${YELLOW}▶ Running /sdd:loop...${NC}"
    echo ""

    set +e
    opencode "${OPENCODE_ARGS[@]}"
    exit_code=$?
    set -e

    if [ $exit_code -ne 0 ]; then
        echo ""
        echo -e "${RED}${BOLD}Error: opencode exited with code ${exit_code}${NC}"
        echo -e "${RED}Stopping the loop. Fix the issue and re-run this script.${NC}"
        exit $exit_code
    fi

    current_status=$(grep "^## Status:" "$first_pending" | head -1 | sed 's/## Status: //')

    if [ "$current_status" = "PENDENTE" ]; then
        echo ""
        echo -e "${YELLOW}⚠ Phase ${next_phase_name} still PENDENTE after execution.${NC}"
        echo -e "${YELLOW}  Stopping. Check the phase file and re-run.${NC}"
        exit 1
    fi

    if [ "$current_status" = "PARCIAL" ]; then
        echo ""
        echo -e "${YELLOW}⚠ Phase ${next_phase_name} completed with PARCIAL status.${NC}"
        echo -e "${YELLOW}  Some tasks have pending items. Stopping the loop.${NC}"
        echo -e "${YELLOW}  Review the phase file and re-run when ready.${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓ ${next_phase_title} → ${current_status}${NC}"
done

echo ""
echo -e "${BOLD}Phase status summary:${NC}"
echo -e "${BLUE}──────────────────────────────────────────────────${NC}"
for f in "$TASK_DIR"/phase-*.md; do
    [ -f "$f" ] || continue
    status=$(grep "^## Status:" "$f" | head -1 | sed 's/## Status: //')
    name=$(head -1 "$f" | sed 's/^# //')
    echo "  ${name} → ${status}"
done
echo -e "${BLUE}──────────────────────────────────────────────────${NC}"