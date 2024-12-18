#!/bin/zsh

echo "Running in shell: $SHELL"

# get script directory
REAL_FILE=$(readlink -f $0)
SCRIPT_NAME=${REAL_FILE##*/}
SCRIPT_DIR=$(cd "$(dirname "${REAL_FILE}")"; pwd)

# run the script
python3 ${SCRIPT_DIR}/src/launch.py