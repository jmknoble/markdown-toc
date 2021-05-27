"""Wrapper around `~markdown_toc.cli`:py:mod:."""

from __future__ import absolute_import

import sys

from . import cli


def main():
    """Provide a generic main entry point."""
    sys.exit(cli.main(*sys.argv))


if __name__ == "__main__":
    main()
