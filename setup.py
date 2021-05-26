#!/usr/bin/env python

# https://packaging.python.org/distributing/#setup-py

try:
    from setuptools import find_packages, setup
except ImportError as e:
    error_message = "Unable to find setuptools;"
    error_message += (
        " please visit https://pypi.python.org/pypi/setuptools for instructions"
    )
    raise RuntimeError(error_message, e)

import os
import os.path
import sys

####################

NAME = "markdown_toc"
DESCRIPTION = "Generate table of contents in Markdown files based on headings"

with open(os.path.join(os.path.dirname(__file__), "VERSION")) as version_file:
    VERSION = version_file.read().strip()

README_FILENAME = "README.md"

TEAM = "jmknoble"
TEAM_EMAIL = "jmknoble@pobox.com"

AUTHOR = TEAM
AUTHOR_EMAIL = TEAM_EMAIL

MAINTAINER = AUTHOR
MAINTAINER_EMAIL = AUTHOR_EMAIL

URL = "https://github.com/jmknoble/markdown-toc"

PACKAGE_INCLUDES = ["*"]
PACKAGE_EXCLUDES = [
    "build",
    "dist",
    "docs",
    "examples",
    "tests",
    "tests.*",
    "*.egg-info",
]
PACKAGES = find_packages(include=PACKAGE_INCLUDES, exclude=PACKAGE_EXCLUDES)

PROVIDES = PACKAGES

# Pre-written scripts
SCRIPTS = []

# Auto-generated scripts with entry points
SCRIPT_NAMES = []
# or: SCRIPT_NAMES = ["markdown_toc"]

SCRIPT_ALIASES = {}
# or: SCRIPT_ALIASES = {"markdown_toc": ["alias"]}

SCRIPT_ENTRY_POINTS = {}
# or: SCRIPT_ENTRY_POINTS = {
#     "markdown_toc": "markdown_toc.__main__:main",
# }

PACKAGE_DATA = {"": ["*.config", "*.json", "*.cfg"]}

SETUP_DIR = os.path.dirname(os.path.realpath(__file__))


def get_requirements_from_file(dirname, basename, default=None):
    reqs_path = os.path.join(dirname, basename)
    if os.path.isfile(reqs_path):
        with open(reqs_path) as f:
            return [x.strip() for x in f if not x.strip().startswith("#")]
    else:
        return [] if default is None else default


REQUIREMENTS = get_requirements_from_file(SETUP_DIR, "requirements.txt")
DEV_DIR = "dev"
TEST_REQUIREMENTS = get_requirements_from_file(
    SETUP_DIR, os.path.join(DEV_DIR, "requirements_test.txt")
)
SETUP_REQUIREMENTS = get_requirements_from_file(
    SETUP_DIR, os.path.join(DEV_DIR, "requirements_dev.txt")
)

TEST_SUITE = "tests"

KEYWORDS = "amazon aws cloud"
CLASSIFIERS = [
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Environment :: Other Environment",
    "Intended Audience :: Developers",
    "Intended Audience :: Information Technology",
    "License :: Other/Proprietary License",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Topic :: System :: Distributed Computing",
    "Topic :: System :: Installation/Setup",
    "Topic :: Utilities",
]

####################

if README_FILENAME.endswith(".md"):
    README_CONTENT_TYPE = "text/markdown"
elif README_FILENAME.endswith(".rst"):
    README_CONTENT_TYPE = "text/x-rst"
else:
    README_CONTENT_TYPE = "text/plain"

readme_path = os.path.join(os.path.dirname(__file__), README_FILENAME)
if os.path.exists(readme_path):
    with open(readme_path, "r") as readme_file:
        README = readme_file.read()
else:
    README = None

####################


def default_entry_point(name):
    """Generate a default entry point for package `name`."""
    return "{name}.__main__:main".format(name=name)


def scripts_for_entry_point(name, script_name, entry_point=None, aliases=None):
    """Return a list of one or more scripts referring to `entry_point`"""
    if entry_point is None:
        entry_point = default_entry_point(name)
    if aliases is None:
        aliases = []
    return [
        "{x}={entry_point}".format(x=x, entry_point=entry_point)
        for x in [script_name] + aliases
    ]


def list_scripts(name, script_names, entry_points=None, script_aliases=None):
    """
    Generate a list of scripts and entry points.

    This is intended for use with ``setup(entry_points={...})``.

    :Args:
        name
            The name of the package the script is for (used to generate a
            default entry point).

        script_names
            An iterable containing zero or more names of distinct "canonical"
            scripts to generate.

        entry_points
            A `dict`-ish mapping script names to entry points::

                { "{script_name}": "{package}.{module}:{callable}" }

            Example::

                { "script1": "package1.__main__:main" }

            If no mapping appears here for a given script name, a default entry
            point is assumed for that script name.

            If `None` is supplied, a default entry point is assumed for every
            script name.

        script_aliases
            A `dict`-ish mapping script names to lists of zero or more
            aliases::

                { "{script_name}": ["{alias}", ...] }

            Example::

                { "script1": ["script1-alias"], "script2": [] }

            Each alias becomes a separate script with the same entry point as
            the "canonical" script.

            If `None` is supplied, no alias scripts will be generated.

    :Returns:
        A list of zero or more scripts and entry points::

            [ "{script_name}={package}.{module}:{callable}", ... ]

    :Raises:
        - `AttributeError`:py:exc: if `entry_points` or `script_aliases` is not
          a `dict`-ish.
        - `TypeError`:py:exc: if `script_name` is not an iterable.

    :Example:
        Tell `setup()`:py:func: to generate a console script with the same name
        as the package, with the default entry point and no aliases:

        >>> setup(...,
        >>>     entry_points={
        >>>         "console_scripts": list_scripts("packagename", ["packagename"])
        >>>     },
        >>> )
    """
    if entry_points is None:
        entry_points = {}
    if script_aliases is None:
        script_aliases = {}

    scripts = []

    for script_name in script_names:
        entry_point = entry_points.get(script_name, None)
        aliases = script_aliases.get(script_name, None)
        scripts.extend(
            scripts_for_entry_point(
                name=name,
                script_name=script_name,
                entry_point=entry_point,
                aliases=aliases,
            )
        )
    return scripts


####################


def should_do_replacements():
    """
    Tell whether it is advisable to do version/author/email replacements.
    """
    setup_dir = os.path.dirname(sys.argv[0])
    # Don't do replacements if we're not running setup.py
    # from the project directory
    return setup_dir in [".", ""]


def do_replacements(
    version=VERSION, author=AUTHOR, author_email=AUTHOR_EMAIL, packages=PACKAGES
):
    """
    Treat setup.py as single source of truth for certain module-level values.

    Replace name, author, and email in each package's __init__.py
    with the given values; this allows making setup.py into a
    source of truth for those values.
    """
    if not should_do_replacements():
        return

    replacement_map = {
        "__version__": version,
        "__author__": author,
        "__email__": author_email,
    }
    init_filename = "__init__.py"
    old_suffix = "old"
    new_suffix = "new"
    for package in packages:
        package_path = os.path.join(*package.split("."))
        currentfile = os.path.join(package_path, init_filename)
        newfile = os.path.join(package_path, ".".join([init_filename, new_suffix]))
        oldfile = os.path.join(package_path, ".".join([init_filename, old_suffix]))
        assignment_op = " = "
        if os.path.exists(currentfile):
            should_replace = False
            with open(currentfile, "r") as i, open(newfile, "w") as o:
                for line in i:
                    for (key, value) in replacement_map.items():
                        if line.startswith("".join([key, assignment_op])):
                            replacement = "".join(
                                [key, assignment_op, repr(value), "\n"]
                            )
                            if line != replacement:
                                line = replacement
                                should_replace = True
                            break
                    o.write(line)
            if should_replace:
                os.rename(currentfile, oldfile)
                os.rename(newfile, currentfile)
            else:
                os.remove(newfile)


# Use setup.py as source of truth
do_replacements()

####################

setup(
    # https://packaging.python.org/distributing/#setup-args
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=README,
    long_description_content_type=README_CONTENT_TYPE,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    maintainer=MAINTAINER,
    maintainer_email=MAINTAINER_EMAIL,
    url=URL,
    packages=PACKAGES,
    scripts=SCRIPTS,
    package_data=PACKAGE_DATA,
    # package_dir={NAME: NAME},
    entry_points={
        "console_scripts": list_scripts(
            name=NAME,
            script_names=SCRIPT_NAMES,
            entry_points=SCRIPT_ENTRY_POINTS,
            script_aliases=SCRIPT_ALIASES,
        )
    },
    include_package_data=True,
    provides=PROVIDES,
    install_requires=REQUIREMENTS,
    # Install this package as individual files, not a zipped egg
    zip_safe=False,
    keywords=KEYWORDS,
    classifiers=CLASSIFIERS,
    test_suite=TEST_SUITE,
    tests_require=TEST_REQUIREMENTS,
    setup_requires=SETUP_REQUIREMENTS,
)
