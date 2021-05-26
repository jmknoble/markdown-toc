#!/bin/sh

set -e
set -u

echo "==> Cleaning up build and runtime detritus ..."

set -x

rm -r -f build dist docs/build docs/sphinx
rm -r -f .eggs *.egg-info
find . -depth -type d -name '__pycache__' -exec rm -r -f '{}' ';'
find . -type f -name '*.py[co]' -exec rm -f '{}' ';'
