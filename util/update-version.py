#!/usr/bin/env python

from __future__ import print_function

import sys

import utilutil.argparsing as argparsing
import utilutil.runcommand as runcommand

DEFAULT_VERSION_FILENAME = "VERSION"
DEFAULT_STABLE_VERSION_FILENAME = "STABLE_VERSION"

DESCRIPTION = (
    "Compare project version with stable version, and "
    "modify project version to be a dev or pre-release "
    "version if they do not match."
)

RELEASE_TYPES = [
    "dev",
    "a",
    "alpha",
    "b",
    "beta",
    "c",
    "pre",
    "preview",
    "rc",
]

RELEASE_TYPES_REQUIRING_SEPARATOR = {"dev"}


def _get_version_from_file(version_file):
    """Return the version as read from `version_file`"""
    version = version_file.read().lstrip().splitlines()
    if not version:
        raise RuntimeError(
            "{path}: version file appears to be blank".format(path=version_file.path)
        )
    return version[0].rstrip()


def _add_arguments(argparser):
    """Add command-line arguments to an argument parser"""
    argparsing.add_dry_run_argument(argparser)
    argparser.add_argument(
        "-b",
        "--build-number",
        dest="build_number",
        action="store",
        default=None,
        required=True,
        help="Numeric suffix for dev or pre-release",
    )
    argparser.add_argument(
        "-t",
        "--release-type",
        dest="release_type",
        action="store",
        choices=RELEASE_TYPES,
        default=None,
        required=True,
        help="Type of release",
    )
    argparser.add_argument(
        "-f",
        "--version-file",
        dest="version_file",
        action="store",
        default=DEFAULT_VERSION_FILENAME,
        help="File containing version (default: '{default}' in current dir)".format(
            default=DEFAULT_VERSION_FILENAME
        ),
    )
    argparser.add_argument(
        "-F",
        "--stable-version-file",
        dest="stable_version_file",
        action="store",
        default=DEFAULT_STABLE_VERSION_FILENAME,
        help=(
            "File containing stable version " "(default: '{default}' in current dir)"
        ).format(default=DEFAULT_STABLE_VERSION_FILENAME),
    )
    return argparser


def main(*argv):
    """Do the thing"""
    (prog, argv) = argparsing.grok_argv(argv)
    argparser = argparsing.setup_argparse(prog=prog, description=DESCRIPTION)
    _add_arguments(argparser)
    args = argparser.parse_args(argv)

    with open(args.version_file, "r") as version_file:
        current_version = _get_version_from_file(version_file)

    with open(args.stable_version_file, "r") as stable_version_file:
        stable_version = _get_version_from_file(stable_version_file)

    if current_version == stable_version:
        runcommand.print_trace(
            [
                "Current version matches stable version, leaving unchanged:",
                current_version,
            ],
            trace_prefix="",
            dry_run=args.dry_run,
        )
    else:
        sep = "." if args.release_type in RELEASE_TYPES_REQUIRING_SEPARATOR else ""
        new_version = "".join(
            [current_version, sep, args.release_type, args.build_number]
        )
        runcommand.print_trace(
            ["Updating current version from", current_version, "to", new_version],
            trace_prefix="",
            dry_run=args.dry_run,
        )
        if not args.dry_run:
            with open(args.version_file, "w") as version_file:
                version_file.write(new_version + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv))
