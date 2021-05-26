#!/bin/sh

set -e
set -u

PYTHON="${PYTHON:-python3}"

HERE="`pwd`"
VENV_DIR=".venv"

DEV_DIR="dev"

echo "==> Creating a Python venv at '${HERE}/${VENV_DIR}' ..."

if [ -d "${VENV_DIR}" ]; then
    echo "$0: error: '${VENV_DIR}' already exists" >&2
    echo "$0: (Use 'remove-venv.sh' to remove it if you want to re-create it)" >&2
    exit 1
fi

(
    set -x
    "${PYTHON}" -m venv "${VENV_DIR}"
)

echo "==> Activating venv at '${HERE}/${VENV_DIR}' ..."
echo "${PS4:-+ }source '${VENV_DIR}/bin/activate'" >&2
source "${VENV_DIR}/bin/activate"

echo "==> Installing requirements ..."
(
    set -x
    "${PYTHON}" -m pip install --upgrade -r ${DEV_DIR}/requirements_build.txt
    "${PYTHON}" -m pip install \
        -r requirements.txt \
        -r ${DEV_DIR}/requirements_dev.txt \
        -r ${DEV_DIR}/requirements_test.txt
)

echo "==> Done."
echo "==> To use your virtual environment:  source ${VENV_DIR}/bin/activate"
