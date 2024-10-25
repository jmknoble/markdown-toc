"""
Provide IOFile class and related exceptions.
"""

import io
import sys


class IOFileError(Exception):
    """
    Provide base exception for IOFile objects.

    :Args:
        path
            The path to the file that is a subject of the exception.

        message
            A string containing an explanation of the exception.
    """

    def __init__(self, path, message):
        self.path = path
        message = "{path}: {message}".format(path=path, message=message)
        super(IOFileError, self).__init__(message)


class IOFileOpenError(IOFileError):
    """
    Provide exception raised for errors opening IOFiles.

    :Args:
        path
            The path to the file that is a subject of the exception

        mode:
            The mode of the file (in the sense used by `open()`:py:func:)

        purpose:
            A string with a value of either ``input`` or ``output``
    """

    def __init__(self, path, mode, purpose):
        self.mode = mode
        self.purpose = purpose
        message = "error opening for {purpose} (mode: {mode})".format(
            mode=self.mode, purpose=purpose
        )
        super(IOFileOpenError, self).__init__(path, message)


class IOFile(object):
    """
    Provide object model for files that should be read, then written in place.

    :Args:
        path
            The path to the file to open for input or output
    """

    def __init__(self, path):
        self.path = path
        self.mode = None
        self.file = None
        self.printable_name = path

        self._io_properties = {
            "input": {
                "target_mode": "r",
                "stdio_stream": sys.stdin,
                "stdio_printable_name": "<stdin>",
            },
            "output": {
                "target_mode": "w",
                "stdio_stream": sys.stdout,
                "stdio_printable_name": "<stdout>",
            },
        }

    def _get_io_property(self, purpose, property_name):
        """
        Get an I/O property by name for a given purpose.

        :Args:
            purpose
                A string with a value of either ``input`` or ``output``

            property_name
                The name of the property to get

        :Returns:
            The value of the given property

        :Raises:
            - `ValueError` if `purpose` is not a recognized value
            - `KeyError` if `property_name` is not a recognized property name
        """
        if purpose not in self._io_properties:
            raise ValueError(
                "{purpose}: unrecognized IOFile purpose".format(purpose=purpose)
            )
        return self._io_properties[purpose][property_name]

    def _raise_open_error(self, purpose):
        """
        Raise an error when opening `self.path`:py:attr:.

        :Args:
            purpose
                A string with a value of either ``input`` or ``output``
        """
        raise IOFileOpenError(path=self.path, mode=self.mode, purpose=purpose)

    def _open_for_purpose(self, purpose):
        """
        Open `self.file`:py:attr: for the given purpose.

        :Args:
            purpose
                A string with a value of either ``input`` or ``output``

        :Returns:
            `self.file`

        :Raises:
            `KeyError`:py:exc: if `purpose` is not one of either ``input`` or ``output``
        """
        target_mode = self._get_io_property(purpose, "target_mode")
        if self.mode not in {None, target_mode}:
            self._raise_open_error(purpose)
        if self.file is None:
            if self.path == "-":
                self.file = self._get_io_property(purpose, "stdio_stream")
                self.printable_name = self._get_io_property(
                    purpose, "stdio_printable_name"
                )
            else:
                self.file = open(self.path, target_mode)
            self.mode = target_mode
        return self.file

    def open_for_input(self):
        """Open `self.file`:py:attr: for input."""
        return self._open_for_purpose("input")

    def open_for_output(self):
        """Open `self.file`:py:attr: for output."""
        return self._open_for_purpose("output")

    def close(self):
        """Close `self.file`:py:attr:."""
        if self.file is not None:
            if self.path != "-":
                self.file.close()
            self.file = None
            self.mode = None


class TextIOFile(IOFile):
    """
    Provide object model for files that should be read, then written in place.

    :Args:
        path
            The path to the file to open for input or output

        input_newline
            (optional) The newline convention used on input (see
            `io.open()`:py:meth:)

        output_newline
            (optional) The newline convention used on output (see
            `io.open()`:py:meth:)
    """

    def __init__(self, path, input_newline=None, output_newline=None):
        super(TextIOFile, self).__init__(path)

        self._io_properties["input"]["target_mode"] = "rt"
        self._io_properties["input"]["newline"] = input_newline
        self._io_properties["output"]["target_mode"] = "wt"
        self._io_properties["output"]["newline"] = output_newline

    def _open_for_purpose(self, purpose):
        """
        Open `self.file`:py:attr: for the given purpose.

        :Args:
            purpose
                A string with a value of either ``input`` or ``output``

        :Returns:
            `self.file`

        :Raises:
            `KeyError`:py:exc: if `purpose` is not one of either ``input`` or ``output``
        """
        target_mode = self._get_io_property(purpose, "target_mode")
        newline = self._get_io_property(purpose, "newline")
        if self.mode not in {None, target_mode}:
            self._raise_open_error(purpose)
        if self.file is None:
            if self.path == "-":
                self.printable_name = self._get_io_property(
                    purpose, "stdio_printable_name"
                )
                fileish = self._get_io_property(purpose, "stdio_stream").fileno()
                closefd = False
            else:
                fileish = self.path
                closefd = True
            self.file = io.open(
                fileish, mode=target_mode, newline=newline, closefd=closefd
            )
            self.mode = target_mode
        return self.file
