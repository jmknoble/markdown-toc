#!/bin/sh

set -e
set -u

CONDA="${CONDA:-conda}"
PYTHON="${PYTHON:-python3}"
PYTHON_VERSION="${PYTHON_VERSION:-3}"

HERE="`pwd`"
NAME="`\"${PYTHON}\" setup.py --name`"
ENV_NAME="`echo \"${NAME}\" |tr _ -`-dev"

DEV_DIR="dev"

echo "==> Creating conda environment '${ENV_NAME}' ..."

(
    set -x
    "${CONDA}" create -n "${ENV_NAME}" "python=${PYTHON_VERSION}"
)

echo "==> Activating conda environment '${ENV_NAME}' ..."
PS1="${PS1:-\$ }"
echo "${PS4:-+ }source activate '${ENV_NAME}'" >&2
source activate "${ENV_NAME}"

echo "==> Installing requirements ..."
(
    set -x
    "${PYTHON}" -m pip install \
        -r requirements.txt \
        -r ${DEV_DIR}/requirements_dev.txt \
        -r ${DEV_DIR}/requirements_test.txt
)

echo "==> Done."
echo "==> To use your virtual environment:  source activate ${ENV_NAME}"
