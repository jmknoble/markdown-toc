#!/bin/sh

set -e
set -u
set -x

python setup.py test
