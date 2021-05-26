#!/bin/bash

set -e
set -u

HERE="`pwd`"
VENV_DIR=".icebox"
VENV_PATH="${HERE}/${VENV_DIR}"

DEFAULT_REQUIREMENTS_FILE="requirements.txt"

DIST_DIR="dist"
DEFAULT_OUTPUT="requirements_frozen.txt"

PrintHelp() {
    cat <<EOF
usage: $0 [OPTIONS] --requirements [REQUIREMENTSFILE ...]
       $0 [OPTIONS] --packages PACKAGESPEC [PACKAGESPEC...]
       $0 [OPTIONS] --wheels WHEELFILE [WHEELFILE...]
       $0 --help

Create a set of "frozen" Python package requirements from the set of
specified requirements, packages, or wheel files.

sources:
    -r / --requirements (this is the default)
    -p / --packages
    -w / --wheels

options:
    -o / --output REQUIREMENTSFILE  (default: ${DEFAULT_OUTPUT})
    -c / --check REQUIREMENTSFILE
    --extra-index-url URL
EOF
    exit 42
}

Progress() {
    echo "==> $* ..." >&2
}

Done() {
    echo "==> Done." >&2
}

Error() {
    echo "$0: error: $*" >&2
}

PreflightChecks() {
    local status=0
    local thing
    local description
    Progress "Running pre-flight checks"
    case "${WHENCE}" in
        requirements)
            description="requirements file"
            ;;
        wheels)
            description="wheel file"
            ;;
    esac
    case "${WHENCE}" in
        requirements|wheels)
            for thing in "$@"; do
                if [ ! -f "${thing}" ]; then
                    Error "Cannot find ${description} '${thing}'"
                    status=1
                fi
            done
            ;;
    esac
    return ${status}
}

DeactivateVenv() {
    set +u
    if [ -n "${VIRTUAL_ENV}" ] || [ -n "${CONDA_DEFAULT_ENV}" ]; then
        case "$(type -t deactivate)" in
            function)
                Progress "Deactivating active venv"
                deactivate
                ;;
            *)
                case "$(type -t conda)" in
                    function)
                        Progress "Deactivating active conda env"
                        conda deactivate
                        ;;
                    *)
                        Progress "Deactivating active conda env via 'source'"
                        source deactivate
                        ;;
                esac
        esac
    fi
    set -u
}

Do() {
    echo "${PS4:-+ }$*" |sed -e 's|:[^/@]*@|:****@|' >&2
    "$@"
}

Cleanup() {
    DeactivateVenv
    if [ -d "${VENV_PATH}" ]; then
        Progress "Cleaning up venv"
        Do rm -rf "${VENV_PATH}"
    fi
}

CreateVenv() {
    Progress "Creating new venv at ${VENV_DIR}"
    Do python -m venv "${VENV_DIR}"
}

ActivateVenv() {
    Progress "Activating venv at ${VENV_DIR}"
    Do . "${VENV_DIR}/bin/activate"
}

UpgradePackageTools() {
    Progress "Upgrading package tools"
    Do python -m pip install --upgrade pip setuptools wheel
}

InstallThings() {
    local whence="$1"
    shift
    case "${whence}" in
        requirements)
            InstallRequirements "$@"
            ;;
        packages)
            InstallPackages "$@"
            ;;
        wheels)
            InstallWheels "$@"
            ;;
    esac
}

InstallRequirements() {
    local requirements_file
    for requirements_file in "$@"; do
        Progress "Installing requirements from '${requirements_file}'"
        Do python -m pip ${PIP_COMMAND} -r "${requirements_file}"
    done
}

InstallPackages() {
    local package
    for package in "$@"; do
        Progress "Installing package '${package}'"
        Do python -m pip ${PIP_COMMAND} "${package}"
    done
}

InstallWheels() {
    local wheel
    for wheel in "$@"; do
        Progress "Installing wheel from '${wheel}'"
        Do python -m pip ${PIP_COMMAND} "${wheel}"
    done
}

GetExcludes() {
    local whence="$1"
    shift
    set +u
    local names=""
    local thing
    case "${whence}" in
        packages)
            for thing in "$@"; do
                thing="$(echo ${thing} |sed -e 's/[^-_.a-zA-Z0-9].*$//')"
                names="${names:+${names} }--exclude ${thing}"
            done
            ;;
        wheels)
            for thing in "$@"; do
                thing="$(basename ${thing})"
                thing="$(echo ${thing} |sed -e 's/-.*$//' -e 's/-/_/g')"
                names="${names:+${names} }--exclude ${thing}"
            done
            ;;
    esac
    echo "${names}"
    set -u
}

PipFreeze() {
    if [ $# -eq 0 ]; then
        Do python -m pip freeze
    else
        Do python -m pip freeze "$@"
    fi
}

SaveFrozenRequirements() {
    Progress "Freezing requirements into ${OUTPUT}"
    PipFreeze "$@" > "${OUTPUT}"
    cat "${OUTPUT}"
}

CheckFrozenRequirements() {
    local status
    Progress "Checking frozen requirements against ${COMPARE_WITH}"
    set +e
    PipFreeze "$@" |diff -u "${COMPARE_WITH}" -
    status=$?
    set -e
    if [ ${status} -ne 0 ]; then
        Error "Frozen requirements differ from '${COMPARE_WITH}'"
        Error "Update ${COMPARE_WITH} using '$0'"
    fi
    return ${status}
}

FreezeRequirements() {
    case "${COMPARE_WITH}" in
        none)
            SaveFrozenRequirements "$@"
            ;;
        *)
            CheckFrozenRequirements "$@"
            ;;
    esac
}

####################

COMPARE_WITH=none
WHENCE=requirements
PIP_COMMAND="install"
OUTPUT="${DEFAULT_OUTPUT}"

while [ $# -gt 0 ]; do
    case "$1" in
        -h|--help)
            PrintHelp
            ;;
        -p|--packages)
            WHENCE=packages
            shift
            ;;
        -r|--requirements)
            WHENCE=requirements
            shift
            ;;
        -w|--wheels)
            WHENCE=wheels
            shift
            ;;
        -c|--check)
            COMPARE_WITH="$2"
            shift 2
            ;;
        --check=*)
            COMPARE_WITH="$(echo $1 |sed -e 's/^--check=//')"
            shift
            ;;
        -o|--output)
            OUTPUT="$2"
            shift 2
            ;;
        --output=*)
            OUTPUT="$(echo $1 |sed -e 's/^--output=//')"
            shift
            ;;
        --extra-index-url)
            PIP_COMMAND="${PIP_COMMAND} $1 $2"
            shift 2
            ;;
        --extra-index-url=*)
            PIP_COMMAND="${PIP_COMMAND} $1"
            shift
            ;;
        --)
            shift
            break
            ;;
        -*)
            Error "unrecognized option: '$1'"
            exit 1
            ;;
        *)
            break
            ;;
    esac
done

case "${WHENCE}" in
    requirements)
        if [ $# -eq 0 ]; then
            set "${DEFAULT_REQUIREMENTS_FILE}"
        fi
        ;;
    packages|wheels)
        if [ $# -eq 0 ]; then
            PrintHelp
        fi
        ;;
    *)
        Error "bug: unhandled requirements source '${WHENCE}'"
        exit 1
esac

PreflightChecks

Progress "Freezing runtime requirements"

Cleanup
CreateVenv

trap Cleanup 0 1 2 15

ActivateVenv
UpgradePackageTools

InstallThings "${WHENCE}" "$@"

FreezeRequirements $(GetExcludes ${WHENCE} "$@")
Cleanup
Done
