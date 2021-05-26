#!/bin/sh

set -e
set -u

HERE="`pwd`"
VENV_DIR=".venv"

if [ -e "${VENV_DIR}" ]; then
    if [ -d "${VENV_DIR}" ]; then
        echo "==> Removing Python venv at '${HERE}/${VENV_DIR}' ..."
    else
        echo "$0: error: '${VENV_DIR}' exists, but is not a directory" >&2
        echo "$0: (You must remove it by hand)" >&2
        exit 1
    fi
else
    echo "==> Good news! There is no Python virtual environment at ${VENV_DIR}"
    exit 0
fi

(
    set -x
    rm -r -f "${VENV_DIR}"
)
