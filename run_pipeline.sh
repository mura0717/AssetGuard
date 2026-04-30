#!/bin/bash
# Hydra Pipeline Runner
# Usage: ./run_pipeline.sh [args]
#
# Options:
#   --dry-run, -n     Test run without making changes
#   --interactive     Show output in terminal (don't log to file)
#   --source          nmap, ms365, or all
#   --skip-snipe      Skip Snipe-IT integration
#   --skip-wazuh      Skip Wazuh integration  
#   --skip-zabbix     Skip Zabbix integration

set -euo pipefail  # Exit on error, undefined vars, pipe failures

PROJECT_DIR="/opt/diabetes/virtualization-basic-soc"

# Detect venv
if [ -f "${PROJECT_DIR}/venv/bin/python3" ]; then
    PYTHON="${PROJECT_DIR}/venv/bin/python3"
elif [ -f "${PROJECT_DIR}/.venv/bin/python3" ]; then
    PYTHON="${PROJECT_DIR}/.venv/bin/python3"
else
    PYTHON="/usr/bin/python3"
fi

LOG_DIR="${PROJECT_DIR}/logs/cron"
LOCK_FILE="/tmp/hydra_pipeline.lock"

mkdir -p "$LOG_DIR"

cd "$PROJECT_DIR"

INTERACTIVE=false
ARGS=()
for arg in "$@"; do
    if [ "$arg" = "--interactive" ] || [ "$arg" = "-i" ]; then
        INTERACTIVE=true
    else
        ARGS+=("$arg")
    fi
done

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

if [ "$INTERACTIVE" = true ]; then
    # Interactive mode
    echo "[$TIMESTAMP] Running interactively..."
    set +e
    $PYTHON -u -m soc_stack.hydra_orchestrator "${ARGS[@]}"
    EXIT_CODE=$?
    set -e
else
    # Background mode
    echo "[$TIMESTAMP] Starting: ${ARGS[*]:-all}" >> "${LOG_DIR}/cron.log"
    logger -t "hydra-pipeline" "Started: ${ARGS[*]:-all}"

    set +e
    flock -n -E 0 "$LOCK_FILE" $PYTHON -u -m soc_stack.hydra_orchestrator "${ARGS[@]}" >> "${LOG_DIR}/pipeline.log" 2>&1
    EXIT_CODE=$?
    set -e

    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    if [ $EXIT_CODE -eq 0 ]; then
        echo "[$TIMESTAMP] Completed: ${ARGS[*]:-all}" >> "${LOG_DIR}/cron.log"
        logger -t "hydra-pipeline" "Completed: ${ARGS[*]:-all}"
    else
        echo "[$TIMESTAMP] Failed (exit $EXIT_CODE): ${ARGS[*]:-all}" >> "${LOG_DIR}/cron.log"
        logger -t "hydra-pipeline" "Failed (exit $EXIT_CODE): ${ARGS[*]:-all}"
    fi
fi

exit $EXIT_CODE