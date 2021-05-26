#!/bin/sh

set -e
set -u

HERE="`dirname \"$0\"`"
THIS="`basename \"$0\"`"

OUR_DIR="util"

####################

AssertRunningFromProjectRoot() {
    case "${HERE}" in
        "./${OUR_DIR}"|"${OUR_DIR}")
            return 0
            ;;
        *)
            echo "ERROR: Please run this script from the project root: ./${OUR_DIR}/${THIS}" >&2
            exit 1
            ;;
    esac
}

####################

DocSourceDirForPackage() {
    local package_name="$1"
    echo "${DOC_ROOT}/sphinx/${package_name}"
}

DocBuildDirForPackage() {
    local package_name="$1"
    echo "${DOC_ROOT}/build/${package_name}"
}

DocIndexForPackage() {
    local package_name="$1"
    local doc_build_dir="`DocBuildDirForPackage \"${package_name}\"`"
    echo "${doc_build_dir}/html/index.html"
}

####################

Clean() {
    local doc_source_dir="$1"
    local doc_build_dir="$2"
    (
        set -e -x
        rm -rf "${doc_source_dir}"
        mkdir -p "${doc_source_dir}"
        rm -rf "${doc_build_dir}"
        mkdir -p "${doc_build_dir}"
    )
}

BuildSphinxDocSource() {
    local doc_source_dir="$1"
    local doc_build_dir="$2"
    local package_name="$3"
    local package_dir="$4"

    (
        set -e -x
        python -m sphinx.ext.apidoc \
            --full \
            --separate \
            --module-first \
            --output-dir="${doc_source_dir}" \
            --doc-project="${package_name}" \
            --doc-author="${AUTHOR}" \
            --doc-version="${VERSION}" \
            "${package_dir}"
    )
}

AddLocalSphinxConfig() {
    local doc_source_dir="$1"
    echo '' >> "${doc_source_dir}/conf.py"
    echo 'from docs.config_sphinx_local import *' >> "${doc_source_dir}/conf.py"
}

BuildSphinxDocs() {
    local doc_source_dir="$1"
    local doc_build_dir="$2"
    local package_name="$3"
    (
        set -e -x
        python setup.py build_sphinx \
            --project "${package_name}" \
            --source-dir "${doc_source_dir}" \
            --build-dir "${doc_build_dir}" \
            --warning-is-error \
            --verbose --verbose
    )
}

####################

FilterPackages() {
    for package_name in "$@"; do
        case "${package_name}" in
            *.*)
                :
                ;;
            *)
                echo "${package_name}"
                ;;
        esac
    done
}

BuildDocs() {
    local package_name="$1"
    local package_dir="`echo \"${package_name}\" |sed -e 's|\.|/|g'`"
    local doc_source_dir="`DocSourceDirForPackage \"${package_name}\"`"
    local doc_build_dir="`DocBuildDirForPackage \"${package_name}\"`"

    (
        echo "==> Building docs for package '${package_name}' ..."
        set -e
        Clean "${doc_source_dir}" "${doc_build_dir}"
        BuildSphinxDocSource "${doc_source_dir}" "${doc_build_dir}" "${package_name}" "${package_dir}"
        AddLocalSphinxConfig "${doc_source_dir}"
        BuildSphinxDocs "${doc_source_dir}" "${doc_build_dir}" "${package_name}"
    )
}


PrintDocIndexLocations() {
    local doc_index=""
    local missing_indexes=""
    local status=0
    echo "========================================"
    echo
    for package_name in "$@"; do
        doc_index="`DocIndexForPackage \"${package_name}\"`"
        if [ -f "${doc_index}" ]; then
            echo "The '${package_name}' API docs are available at: ${doc_index}"
        else
            missing_indexes="${missing_indexes} ${doc_index}"
        fi
    done
    if [ x"${missing_indexes}" != x"" ]; then
        status=1
        for doc_index in ${missing_indexes}; do
            echo >&2
            echo "ERROR: Unable to find '${doc_index}'" >&2
            echo "Did the Sphinx API documentation build fail?" >&2
            echo >&2
        done
    fi
    echo
    return ${status}
}

####################

AssertRunningFromProjectRoot

set -x

DOC_ROOT="docs"
NAME="`python setup.py --name`"
AUTHOR="`python setup.py --author`"
VERSION="`python setup.py --version`"
PACKAGES="`python setup.py --provides`"

./util/check-docs.sh

set +x

TOP_LEVEL_PACKAGES="`FilterPackages ${PACKAGES}`"

for package_name in ${TOP_LEVEL_PACKAGES}; do
    BuildDocs "${package_name}"
done

PrintDocIndexLocations ${TOP_LEVEL_PACKAGES}

exit 0
