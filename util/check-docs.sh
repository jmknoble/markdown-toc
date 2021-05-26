#!/bin/sh

# TODO: This purports to "check docs", but really what it does is just grep sources.
# TODO: It really should extract docstrings and just check those, but that's more complicated.

set -e
set -u

FindTopLevelPackages() {
    local packages=''
    local i
    for i in `python setup.py --provides`; do
        case "${i}" in
            *.*)
                :
                ;;
            *)
                packages="${packages} $i"
        esac
    done
    echo ${packages}
}

PACKAGES="`FindTopLevelPackages`"

####################

FindUnterminatedDocstringRoles() {
    find ${PACKAGES} -type f -name '*.py' -exec egrep -n ':py:[^:]*$' '{}' /dev/null ';'
}

FindUnrecognizedDocstringRoles() {
    find ${PACKAGES} -type f -name '*.py' -exec egrep -n ':py:' '{}' /dev/null ';' \
        |egrep -v ':py:(mod|func|data|const|class|meth|attr|exc|obj):'
}

FindUnabbreviatedDocstringReferences() {
    for package in ${PACKAGES}; do
        find ${package} -type f -name '*.py' -exec egrep -n '`'"${package}"'\.' '{}' /dev/null ';'
    done
}

Count() {
    wc -l |sed -e 's/  *//g'
}

####################

STATUS=0

echo "==> Checking for unterminated Sphinx docstring roles ..."

UNTERMINATED_COUNT=`FindUnterminatedDocstringRoles |Count`

if [ ${UNTERMINATED_COUNT} -ne 0 ]; then
    FindUnterminatedDocstringRoles
    STATUS=1
else
    echo "==> OK"
fi

echo "==> Checking for unrecognized Sphinx docstring roles ..."

UNRECOGNIZED_COUNT=`FindUnrecognizedDocstringRoles |Count`

if [ ${UNRECOGNIZED_COUNT} -ne 0 ]; then
    FindUnrecognizedDocstringRoles
    STATUS=1
else
    echo "==> OK"
fi

echo "==> Checking for unabbreviated Sphinx docstring references ..."

UNABBREVIATED_COUNT=`FindUnabbreviatedDocstringReferences |Count`

if [ ${UNABBREVIATED_COUNT} -ne 0 ]; then
    FindUnabbreviatedDocstringReferences
    STATUS=1
else
    echo "==> OK"
fi

####################

if [ ${UNTERMINATED_COUNT} -eq 1 ]; then
    UNTERMINATED_ROLES="role"
else
    UNTERMINATED_ROLES="roles"
fi

if [ ${UNRECOGNIZED_COUNT} -eq 1 ]; then
    UNRECOGNIZED_ROLES="role"
else
    UNRECOGNIZED_ROLES="roles"
fi

if [ ${UNABBREVIATED_COUNT} -eq 1 ]; then
    UNABBREVIATED_REFERENCES="reference"
else
    UNABBREVIATED_REFERENCES="references"
fi

STATISTICS=""
STATISTICS="${STATISTICS}${UNTERMINATED_COUNT} unterminated ':py:*:' ${UNTERMINATED_ROLES}, "
STATISTICS="${STATISTICS}${UNRECOGNIZED_COUNT} unrecognized ':py:*:' ${UNRECOGNIZED_ROLES}, "
STATISTICS="${STATISTICS}${UNABBREVIATED_COUNT} unabbreviated ${UNABBREVIATED_REFERENCES}"

if [ ${STATUS} -ne 0 ]; then
    echo "ERROR: ${STATISTICS}" >&2
fi

exit ${STATUS}
