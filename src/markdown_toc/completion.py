"""Provide things needed for CLI autocompletion."""

import os.path
import shutil
import sys

INSTRUCTIONS = """
{base_prog} supports command-line tab-based autocompletion for Bash
and compatible shells.

To enable autocompletion, add the following to your ~/.bashrc or
~/.bash_profile file (or the equivalent if you're using a Bash-compatible
shell):

    eval $({full_prog} {completion_command})

Or, if {base_prog} is installed to a location on your PATH:

    eval $({base_prog} {completion_command})

(If you're seeing this message when your shell starts, double-check to make
sure you have done the above correctly).
"""


def _python_executable():
    return sys.executable


def _python_prefix(executable=False):
    if executable:
        return sys.exec_prefix
    return sys.prefix


def _python_bin_dir():
    return os.path.join(_python_prefix(), "bin")


def _infer_base_prog(prog):
    base_prog = os.path.basename(prog)
    if base_prog == "__main__.py":
        module = os.path.basename(os.path.dirname(prog))
        return module.replace("_", "-")
    return base_prog


def _contract_home(path):
    home_dir = os.path.expanduser("~")
    return path.replace(home_dir, "~", 1) if path.startswith(home_dir) else path


def _infer_full_prog(prog, with_module=False, with_relative=True, with_home=False):
    base_prog = os.path.basename(prog)

    # `python -m module_name`
    if base_prog == "__main__.py":
        if with_module:
            module = os.path.basename(os.path.dirname(prog))
            full_prog = "{python} -m {module}".format(
                python=_python_executable(), module=module
            )
        else:
            full_prog = os.path.join(_python_bin_dir(), _infer_base_prog(prog))

    # Bare command only
    elif prog == base_prog:
        full_prog = shutil.which(prog)
        if full_prog is None:
            full_prog = prog

    # Command with relative path
    elif with_relative:
        full_prog = prog

    # Command with absolute path
    else:
        full_prog = os.path.abspath(prog)

    if with_home:
        full_prog = _contract_home(full_prog)

    return full_prog


def _full_prog_if_not_on_path(prog, **kwargs):
    full_prog = _infer_full_prog(
        prog, with_module=False, with_relative=True, with_home=False
    )
    base_prog = _infer_base_prog(prog)
    path_prog = shutil.which(base_prog)
    if path_prog is not None and path_prog == full_prog:
        return base_prog
    return _infer_full_prog(prog, **kwargs)


def get_instructions(prog, completion_args):
    """
    Get instructions for setting up autocompletion.

    :Args:
        prog
            The name of the program; typically, this is ``sys.argv[0]``.

        completion_args
            A list containing the CLI arguments to `prog` to use for enabling
            completion example: ``["completion --bash"]``).

    :Returns:
        A string with templates filled in, suitable for printing as a message.
    """
    return INSTRUCTIONS.format(
        base_prog=_infer_base_prog(prog),
        full_prog=_infer_full_prog(
            prog, with_module=True, with_relative=False, with_home=True
        ),
        completion_command=" ".join(completion_args),
    )


def get_commands(prog, absolute=False):
    """Get commands needed for enabling autocompletion."""
    register_command = os.path.join(_python_bin_dir(), "register-python-argcomplete")
    if absolute:
        prog = _infer_full_prog(prog)
    else:
        prog = _infer_base_prog(prog)
    return f'eval "$({register_command} {prog})"'
