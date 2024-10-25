"""Wrapper around `~markdown_toc.cli`:py:mod:."""

from __future__ import absolute_import

import sys

from . import cli

__all__ = [
    "main",
]


def main():
    """Provide a generic main entry point."""
    return cli.main(*sys.argv)


if __name__ == "__main__":
    sys.exit(main())
