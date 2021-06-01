#!/usr/bin/env python3

import argparse
import os
import os.path
import shutil
import stat
import sys

import utilutil.argparsing as argparsing
import utilutil.runcommand as runcommand

PYTHON = "python3"
CONDA = "conda"

PROGRESS_PREFIX = "==> "

VENV_DIR = ".venv"
DEV_SUFFIX = "-dev"

REQUIREMENTS_VENV = ["pip", "setuptools", "wheel"]

REQUIREMENTS_PLAIN = "requirements.txt"
REQUIREMENTS_DEV = os.path.join("dev", "requirements_dev.txt")
REQUIREMENTS_FROZEN = "requirements_frozen.txt"
REQUIREMENTS_BUILD = os.path.join("dev", "requirements_build.txt")
REQUIREMENTS_PACKAGE = "{name}"

COMMAND_CREATE = "create"
COMMAND_REMOVE = "remove"

COMMANDS = {
    COMMAND_CREATE: {
        "help": "Create a Python virtual environment",
        "aliases": ["new"],
        "reqs_required": True,
    },
    COMMAND_REMOVE: {
        "help": "Remove a Python virtual environment",
        "aliases": ["rm"],
        "reqs_required": False,
    },
}

REQS_PLAIN = "plain"
REQS_DEV = "dev"
REQS_FROZEN = "frozen"
REQS_PACKAGE = "package"

REQS = [
    REQS_PLAIN,
    REQS_DEV,
    REQS_FROZEN,
    REQS_PACKAGE,
]

ENV_TYPE_VENV = "venv"
ENV_TYPE_CONDA = "conda"

ENV_TYPES = [
    ENV_TYPE_VENV,
    ENV_TYPE_CONDA,
]

ENV_DESCRIPTIONS = {
    ENV_TYPE_VENV: "Python venv at {env_name}",
    ENV_TYPE_CONDA: "conda environment {env_name}",
}

FROM_FILES = "files"
FROM_PACKAGES = "packages"

REQUIREMENTS = {
    REQS_PLAIN: {
        FROM_FILES: [REQUIREMENTS_PLAIN],
    },
    REQS_DEV: {
        FROM_FILES: [REQUIREMENTS_PLAIN, REQUIREMENTS_BUILD, REQUIREMENTS_DEV],
    },
    REQS_FROZEN: {
        FROM_FILES: [REQUIREMENTS_FROZEN],
    },
    REQS_PACKAGE: {
        FROM_PACKAGES: [REQUIREMENTS_PACKAGE],
    },
}

DEFAULT_ENV_TYPE = ENV_TYPE_VENV

DESCRIPTION = f"""
Create or remove a Python virtual environment for the Python project in the
current directory.  We expect a 'setup.py' to exist, along with requirements in
'{REQUIREMENTS_PLAIN}', '{REQUIREMENTS_FROZEN}', and '{REQUIREMENTS_DEV}'.

Venv virtual environments are created in '{VENV_DIR}'.

Conda virtual environments are created using the name of the Python project,
with underscores ('_') replaced by hyphens ('-'), and with '{DEV_SUFFIX}'
appended for development environments.
"""


def _add_subcommands(argparser, commands, dest="command"):
    subcommands = {}
    subparsers = argparser.add_subparsers(title="subcommands", dest=dest)
    for (command, properties) in commands.items():
        subcommands[command] = subparsers.add_parser(
            command, aliases=properties.get("aliases", []), help=properties["help"]
        )
        subcommands[command].set_defaults(func=properties.get("func", None))
    return subcommands


def _add_arguments(argparser, reqs_required=False):
    """Add command-line arguments to an argument parser"""
    argparsing.add_dry_run_argument(argparser)

    reqs_group = argparser.add_argument_group(title="requirements options")
    reqs_mutex_group = reqs_group.add_mutually_exclusive_group(required=reqs_required)
    reqs_mutex_group.add_argument(
        "-r",
        "--requirements",
        action="store",
        dest="reqs",
        choices=REQS,
        default=None,
        help="Requirements to use for virtual environment",
    )
    reqs_mutex_group.add_argument(
        "-p",
        f"--{REQS_PLAIN}",
        action="store_const",
        dest="reqs",
        const=REQS_PLAIN,
        help=(
            f"Create virtual environment using {REQUIREMENTS_PLAIN}; "
            f"same as '--requirements {REQS_PLAIN}'"
        ),
    )
    reqs_mutex_group.add_argument(
        "-d",
        f"--{REQS_DEV}",
        action="store_const",
        dest="reqs",
        const=REQS_DEV,
        help=(
            f"Create virtual environment for development; "
            f"same as '--requirements {REQS_DEV}'"
        ),
    )
    reqs_mutex_group.add_argument(
        "-z",
        f"--{REQS_FROZEN}",
        action="store_const",
        dest="reqs",
        const=REQS_FROZEN,
        help=(
            f"Create virtual environment using {REQUIREMENTS_FROZEN}; "
            f"same as '--requirements {REQS_FROZEN}'"
        ),
    )
    reqs_mutex_group.add_argument(
        "-P",
        f"--{REQS_PACKAGE}",
        action="store_const",
        dest="reqs",
        const=REQS_PACKAGE,
        help=(
            f"Create virtual environment using 'pip install PACKAGE'; "
            f"same as '--requirements {REQS_PACKAGE}'"
        ),
    )

    venv_group = argparser.add_argument_group(title="environment options")
    venv_mutex_group = venv_group.add_mutually_exclusive_group()
    venv_mutex_group.add_argument(
        "-t",
        "--type",
        action="store",
        dest="env_type",
        choices=ENV_TYPES,
        default=DEFAULT_ENV_TYPE,
        help=f"The type of environment to create (default: {DEFAULT_ENV_TYPE})",
    )
    venv_mutex_group.add_argument(
        "-v",
        f"--{ENV_TYPE_VENV}",
        action="store_const",
        dest="env_type",
        const=ENV_TYPE_VENV,
        help=f"Same as '--type {ENV_TYPE_VENV}'",
    )
    venv_mutex_group.add_argument(
        "-c",
        f"--{ENV_TYPE_CONDA}",
        action="store_const",
        dest="env_type",
        const=ENV_TYPE_CONDA,
        help=f"Same as '--type {ENV_TYPE_CONDA}'",
    )
    return argparser


def _add_force_arguments(argparser):
    argparser.add_argument(
        "--force",
        action="store_true",
        help="Remove any pre-existing virtual environment",
    )


def _progress(args, message, suffix="..."):
    message_parts = [message]
    if suffix and not message.endswith("."):
        message_parts.append(suffix)
    runcommand.print_trace(
        message_parts, trace_prefix=PROGRESS_PREFIX, dry_run=args.dry_run
    )


def _get_package_name(_args):
    package_name = runcommand.run_command(
        [PYTHON, "setup.py", "--name"],
        dry_run=False,
        return_output=True,
        show_trace=False,
    )
    if package_name.endswith("\n"):
        package_name = package_name[:-1]
    return package_name


def _get_project_name(args):
    return _get_package_name(args).replace("_", "-")


def _get_env_name(name, args):
    if args.env_type == ENV_TYPE_CONDA:
        env_name = name
        if args.reqs == REQS_DEV:
            env_name += DEV_SUFFIX
    else:
        env_name = VENV_DIR
    return env_name


def _pip_requirements(name, requirements):
    pip_arguments = []
    for a_file in requirements.get(FROM_FILES, []):
        pip_arguments.append("-r")
        pip_arguments.append(a_file)
    for package_spec in requirements.get(FROM_PACKAGES, []):
        pip_arguments.append(package_spec.format(name=name))
    return pip_arguments


def _create_venv(args, name, env_name, env_description, requirements):
    _progress(args, f"Creating {env_description}")

    env_dir = env_name
    full_env_dir = os.path.abspath(env_dir)

    if os.path.isdir(env_dir):
        preexisting_message = f"Found preexisting {env_dir}"
        if args.force:
            _progress(args, preexisting_message)
            _remove_venv(args, env_name, env_description)
        else:
            raise RuntimeError(preexisting_message + ", please remove it first")
    elif os.path.exists(env_dir):
        raise RuntimeError(
            f"{full_env_dir} exists, but is not a directory; "
            "you must deal with it by hand."
        )

    runcommand.run_command(
        [PYTHON, "-m", "venv", env_dir], show_trace=True, dry_run=args.dry_run
    )
    _progress(args, f"Created {full_env_dir}", suffix=None)

    env_bin_dir = os.path.join(env_dir, "bin")
    env_python = os.path.join(env_bin_dir, PYTHON)
    env_activate = os.path.join(env_bin_dir, "activate")

    _progress(args, f"Installing {args.reqs} requirements")

    pip_install_command = [env_python, "-m", "pip", "install"]
    runcommand.run_command(
        pip_install_command + ["--upgrade"] + REQUIREMENTS_VENV,
        show_trace=True,
        dry_run=args.dry_run,
    )
    runcommand.run_command(
        pip_install_command + _pip_requirements(name, requirements),
        show_trace=True,
        dry_run=args.dry_run,
    )

    _progress(args, "Done.")
    if not args.dry_run:
        _progress(args, f"To use your virtual environment: 'source {env_activate}'.")


def _remove_venv(args, env_name, env_description):
    _progress(args, f"Removing {env_description}")

    env_dir = env_name
    full_env_dir = os.path.abspath(env_name)

    if not os.path.exists(env_dir):
        _progress(args, f"Good news!  There is no {env_description}.")
        return

    if not os.path.isdir(env_dir):
        raise RuntimeError(
            f"{full_env_dir} exists, but is not a directory; "
            "you must remove it by hand."
        )

    def retry_readonly(func, path, _excinfo):
        """Make file writable and attempt to remove again."""
        os.chmod(path, stat.S_IWRITE)
        func(path)

    verb = "Would remove" if args.dry_run else "Removing"
    _progress(args, f"{verb} {full_env_dir} and all its contents")

    if not args.dry_run:
        shutil.rmtree(env_dir, onerror=retry_readonly)

    _progress(args, "Done.")


def _get_conda_env_dir(args, env_name):
    if args.dry_run:
        return "CONDA_ENV_DIR"

    env_listing = runcommand.run_command(
        [CONDA, "env", "list"],
        return_output=True,
        show_trace=False,
        dry_run=args.dry_run,
    ).splitlines()

    for line in [x.strip() for x in env_listing]:
        if line.startswith("# ") or not line:
            continue
        parts = line.split(maxsplit=1)
        if parts[0] == env_name:
            env_dir = parts[1]
            if env_dir.startswith("* "):
                env_dir = env_dir.split(maxsplit=1)[1]
            return env_dir

    raise IndexError(f"unable to find conda environment {env_name}")


def _create_conda_env(args, name, env_name, env_description, requirements):
    _progress(args, f"Creating {env_description}")

    conda_command = [CONDA, "create"]
    if args.force:
        conda_command.append("--yes")
    runcommand.run_command(
        conda_command + ["-n", env_name, "python=3"],
        show_trace=True,
        dry_run=args.dry_run,
    )

    env_dir = _get_conda_env_dir(args, env_name)
    env_bin_dir = os.path.join(env_dir, "bin")
    env_python = os.path.join(env_bin_dir, PYTHON)

    _progress(args, f"Installing {args.reqs} requirements")

    pip_install_command = [env_python, "-m", "pip", "install"]
    runcommand.run_command(
        pip_install_command + _pip_requirements(name, requirements),
        show_trace=True,
        dry_run=args.dry_run,
    )
    _progress(args, "Done.")
    if not args.dry_run:
        _progress(
            args, f"To use your virtual environment: 'source activate {env_name}'."
        )


def _remove_conda_env(args, env_name, env_description):
    _progress(args, f"Removing {env_description}")
    runcommand.run_command(
        [CONDA, "env", "remove", "-n", env_name], show_trace=True, dry_run=args.dry_run
    )
    _progress(args, "Done.")


def _check_requirements(requirements):
    missing = []
    for requirements_file in requirements.get(FROM_FILES, []):
        if not os.path.exists(requirements_file):
            missing.append(requirements_file)
    if missing:
        noun = "file" if len(missing) == 1 else "files"
        text = ", ".join(missing)
        raise RuntimeError(f"Missing requirements {noun}: {text}")


def _command_action_create(_prog, args, **_kwargs):
    requirements = REQUIREMENTS[args.reqs]
    _check_requirements(requirements)
    name = _get_project_name(args)
    env_name = _get_env_name(name, args)
    env_description = ENV_DESCRIPTIONS[args.env_type].format(env_name=env_name)
    if args.env_type == ENV_TYPE_VENV:
        _create_venv(args, name, env_name, env_description, requirements)
    elif args.env_type == ENV_TYPE_CONDA:
        _create_conda_env(args, name, env_name, env_description, requirements)


def _command_action_remove(_prog, args, **_kwargs):
    name = _get_project_name(args)
    env_name = _get_env_name(name, args)
    env_description = ENV_DESCRIPTIONS[args.env_type].format(env_name=env_name)
    if args.env_type == ENV_TYPE_VENV:
        _remove_venv(args, env_name, env_description)
    elif args.env_type == ENV_TYPE_CONDA:
        if args.reqs is None:
            raise RuntimeError(
                "Please supply the '-r/--requirements' option "
                "so we know what environment to remove."
            )
        _remove_conda_env(args, env_name, env_description)


def _populate_command_actions(commands):
    func = "func"
    commands[COMMAND_CREATE][func] = _command_action_create
    commands[COMMAND_REMOVE][func] = _command_action_remove


def main(*argv):
    """Do the thing"""
    (prog, argv) = argparsing.grok_argv(argv)
    argparser = argparsing.setup_argparse(
        prog=prog,
        description=DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    _populate_command_actions(COMMANDS)
    subcommands = _add_subcommands(argparser, COMMANDS)
    for (subcommand, subcommand_parser) in subcommands.items():
        _add_arguments(
            subcommand_parser,
            reqs_required=COMMANDS[subcommand].get("reqs_required", False),
        )
        if subcommand == COMMAND_CREATE:
            _add_force_arguments(subcommand_parser)
    args = argparser.parse_args(argv)

    try:
        if args.func is not None:
            return args.func(prog, args)
    except RuntimeError as e:
        print(f"{prog}: error: {e}", file=sys.stderr)
        return 1

    raise RuntimeError(f"Unhandled subcommand: {args.command}")


if __name__ == "__main__":
    sys.exit(main(*sys.argv))
