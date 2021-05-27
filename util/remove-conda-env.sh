#!/bin/sh

set -e
set -u

CONDA="${CONDA:-conda}"
PYTHON="${PYTHON:-python3}"

HERE="`pwd`"
NAME="`\"${PYTHON}\" setup.py --name`"
ENV_NAME="`echo \"${NAME}\" |tr _ -`-dev"

echo "==> Removing conda environment '${ENV_NAME}' ..."
(
    set -x
    "${CONDA}" env remove -n "${ENV_NAME}"
)
