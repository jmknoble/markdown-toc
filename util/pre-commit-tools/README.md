# pre-commit-tools

A set of command-line scripts/tools to aid developers in working with
[pre-commit](https://pre-commit.com/).


## Installation

This is intended to eventually be used as a [Git
submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules), but that
practice is not yet tested or documented.  For now, just copy from this Git
project into a subfolder.  For example:

    mkdir -p ../myproject/util/pre-commit-tools
    cp -p *.py ../myproject/util/pre-commit-tools/


## Dependencies

You need [pre-commit installed](https://pre-commit.com/#install) locally.


## Tools

| Tool                | Description |
|---------------------|-------------|
| install-hooks.py    | Install pre-commit hooks in the current Git project; a `.pre-commit-config.yaml` must exist. Idempotent (you can run it multiple times wwithout a problem). |
| run-hooks.py        | Run configured pre-commit hooks across all files in the current Git project.  You may supply arguments (for example, `--help`), which are passed to `pre-commit`. |
| run-manual-hooks.py | Run a manual hook across all files in the current Git project.  You must supply the alias of a hook to run.  You may supply arguments (such as `--help`). |
| seed-hook-config.py | Create a brand new pre-commit config, if one does not already exist. |
| update-hooks.py     | Update configured hooks to the latest tagged version from their respective Git repos. |


## Example

(These examples assume you installed in the example folder shown under
***Installation*** above).

First, create a sample `.pre-commit-config.yaml`:

    python ./util/pre-commit-tools/seed-hook-config.py

Then, install your hooks:

    python ./util/pre-commit-tools/install-hooks.py

Next, be sure you have the most recent hook versions:

    python ./util/pre-commit-tools/update-hooks.py

Now you can run the pre-commit hooks against your project:

    python ./util/pre-commit-tools/run-hooks.py

The hooks will also automatically run against any staged files when you try to
commit them.  A failed hook will stop the commit from happening.

If you have a manual hook defined, you can run it against your project; for
example, if you have a manual hook named `black-diff`:

    python ./util/pre-commit-tools/run-manual-hooks.py black-diff


## References

- pre-commit
    ([site](https://pre-commit.com/))
    ([github](https://github.com/pre-commit/pre-commit))
- Some [pre-commit hooks](https://github.com/pre-commit/pre-commit-hooks)
- Some more pre-commit hooks for Python:
    - [black](https://github.com/psf/black)
    - [flake8](https://gitlab.com/pycqa/flake8)
    - [isort](https://github.com/pre-commit/mirrors-isort)
    - [pylint](https://github.com/pre-commit/mirrors-pylint)
