"""Model a Markdown file as an object."""

import pprint
import re

INDENT_WIDTH = 4

LABEL_TOC = "toc"
LABEL_BEGIN_TOC = "begintoc"
LABEL_END_TOC = "endtoc"

HEADING_CHAR = "#"

RE_GROUP_LEVEL = "level"
RE_GROUP_TEXT = "text"
RE_GROUP_FENCE = "fence"
RE_GROUP_LABEL = "label"
RE_GROUP_REF = "ref"
RE_GROUP_COMMENT = "comment"

HEADING_REGEX_TEMPLATE = r"^(?P<{level}>#+) *(?P<{text}>.*[^ #])( *#+)?$"
CODE_FENCE_REGEX_TEMPLATE = r"^(?P<{fence}>```+)"
TOC_ENTRY_REGEX_TEMPLATE = r"^ *[-*+] *[^ ]"
BLANK_LINE_REGEX_TEMPLATE = r"^$"
COMMENT_REGEX_TEMPLATE = (
    r"^\[(?P<{label}>[^\]]*)\]: "
    r"#(?P<{ref}>[-0-9A-Za-z]*)?( +\((?P<comment>[^\)]*)\))? *$"
)

HEADING_REGEX_PATTERN = HEADING_REGEX_TEMPLATE.format(
    level=RE_GROUP_LEVEL, text=RE_GROUP_TEXT
)
CODE_FENCE_REGEX_PATTERN = CODE_FENCE_REGEX_TEMPLATE.format(fence=RE_GROUP_FENCE)
TOC_ENTRY_REGEX_PATTERN = TOC_ENTRY_REGEX_TEMPLATE
BLANK_LINE_REGEX_PATTERN = BLANK_LINE_REGEX_TEMPLATE
COMMENT_REGEX_PATTERN = COMMENT_REGEX_TEMPLATE.format(
    label=RE_GROUP_LABEL, ref=RE_GROUP_REF, comment=RE_GROUP_COMMENT
)

HEADING_REGEX = re.compile(HEADING_REGEX_PATTERN)
CODE_FENCE_REGEX = re.compile(CODE_FENCE_REGEX_PATTERN)
TOC_ENTRY_REGEX = re.compile(TOC_ENTRY_REGEX_PATTERN)
BLANK_LINE_REGEX = re.compile(BLANK_LINE_REGEX_PATTERN)
COMMENT_REGEX = re.compile(COMMENT_REGEX_PATTERN)


####################


def _make_anchor_name(text):
    if text is None:
        return None

    anchor_text = []
    for c in text:
        if c.isalnum():
            anchor_text.append(c.lower())
        elif c.isspace() or c == "-":
            anchor_text.append("-")
    return "".join(anchor_text)


def _make_anchor_ref(text):
    return "#{text}".format(text=text)


def _make_inline_link(text, target):
    return "[{text}]({target})".format(text=text, target=target)


def _make_detached_link(text, target):
    return "[{text}]: {target}".format(text=text, target=target)


def _make_list_item(text, alt_list_char):
    list_char = "*" if alt_list_char else "-"
    return "{list_char} {text}".format(list_char=list_char, text=text)


def _make_numbered_list_item(text, n):
    return "{n}. {text}".format(n=n, text=text)


def _make_comment(text=None, label="comment"):
    comment_parts = []
    comment_parts.append("#")
    if text:
        comment_parts.append(" (")
        comment_parts.append(text)
        comment_parts.append(")")
    comment_text = "".join(comment_parts)
    return _make_detached_link(label, comment_text)


####################


class TocItem(object):
    """Model an item in a table of contents."""

    def __init__(self, text, n):
        self.text = text
        self.n = n

    def __repr__(self):
        """Print a human-readable representation of this item."""
        return "TocItem(text={text})".format(text=repr(self.text))

    def format(self, indent_level, numbered, alt_list_char, indent_width=INDENT_WIDTH):
        """Format this item at a given indent level with the given options."""
        anchor_name = _make_anchor_name(self.text)
        anchor_ref = _make_anchor_ref(anchor_name)
        link = _make_inline_link(self.text, anchor_ref)
        if numbered:
            item_text = _make_numbered_list_item(link, self.n)
        else:
            item_text = _make_list_item(link, alt_list_char=alt_list_char)
        indent_text = " " * (indent_level * indent_width)
        return "".join([indent_text, item_text])

    def print(self):
        """Print the text associated with this item."""
        return self.text


class TocLevel(object):
    """Model an entire, possibly nested, level of a table of contents."""

    def __init__(self, level, parent=None):
        self.items = []
        self.level = level
        self.parent = parent
        self.item_count = 0

    def __repr__(self):
        """Print a human-readable representation of this level."""
        items_text = pprint.pformat(self.items, indent=self.level + 1)
        text = "TocLevel(level={level}, items={items})".format(
            level=self.level, items=items_text
        )
        return text

    def add_item(self, text, level):
        """Add an item to this level."""
        if level == self.level:
            self.item_count += 1
            self.items.append(TocItem(text=text, n=self.item_count))
            return self

        if level > self.level:
            new_toc_level = TocLevel(level=self.level + 1, parent=self)
            self.items.append(new_toc_level)
            return new_toc_level.add_item(text, level)

        # level < self.level:
        return self.parent.add_item(text, level)

    def get_toc_levels(self, skip_level):
        """Get the levels for this table of contents, skipping if needed."""
        toc_levels = []
        if skip_level < self.level:
            toc_levels.append(self)
        else:
            for item in self.items:
                if isinstance(item, TocLevel):
                    for toc_level in item.get_toc_levels(skip_level):
                        toc_levels.append(toc_level)
        return toc_levels

    def format(
        self, numbered, alt_list_char, indent_width=INDENT_WIDTH, adjust_indent=0
    ):
        """Format this level and all its items with the given options."""
        formatted_items = []
        for item in self.items:
            if isinstance(item, TocLevel):
                text = item.format(
                    numbered=numbered,
                    indent_width=indent_width,
                    adjust_indent=adjust_indent,
                    alt_list_char=alt_list_char,
                )
            elif isinstance(item, TocItem):
                text = item.format(
                    indent_level=(self.level - 1 - adjust_indent),
                    numbered=numbered,
                    alt_list_char=alt_list_char,
                    indent_width=indent_width,
                )
            else:
                raise TypeError(item)
            formatted_items.append(text)
        return "\n".join(formatted_items)


class Toc(object):
    """Model an entire table of contents."""

    def __init__(self, heading_text, heading_level, skip_level):
        self.meta_heading_text = heading_text
        self.meta_heading_level = heading_level
        self.skip_level = skip_level
        self.headings = TocLevel(level=1)

    def __repr__(self):
        """Print a human-readable representation of this table of contents."""
        text = (
            "Toc(meta_heading_text={meta_heading_text}, "
            "meta_heading_level={meta_heading_level}, headings={headings})"
        ).format(
            meta_heading_text=repr(self.meta_heading_text),
            meta_heading_level=repr(self.meta_heading_level),
            headings=repr(self.headings),
        )
        return text

    def add_item(self, text, level):
        """Add an item to this table of contents at the given level."""
        return self.headings.add_item(text, level)

    def format(self, numbered, comment, alt_list_char, add_trailing_heading_chars):
        """Format this table of contents with the given options."""
        formatted_items = []
        formatted_items.append(_make_comment(label=LABEL_BEGIN_TOC))

        formatted_items.append("")

        meta_heading_markers = HEADING_CHAR * self.meta_heading_level
        meta_heading_items = [meta_heading_markers, self.meta_heading_text]
        if add_trailing_heading_chars:
            meta_heading_items.append(meta_heading_markers)
        meta_heading = " ".join(meta_heading_items)
        formatted_items.append(meta_heading)

        formatted_items.append("")

        for toc_level in self.headings.get_toc_levels(self.skip_level):
            formatted_items.append(
                toc_level.format(
                    numbered=numbered,
                    alt_list_char=alt_list_char,
                    adjust_indent=self.skip_level,
                )
            )

        formatted_items.append("")
        formatted_items.append(_make_comment(comment, label=LABEL_END_TOC))
        formatted_items.append("")

        return "\n".join(formatted_items)


####################


def _is_eof(text):
    return text == ""


def _is_code_fence(text):
    if text.endswith("\n"):
        text = text[:-1]
    match = CODE_FENCE_REGEX.search(text)
    return match is not None


def _get_comment(text):
    if text.endswith("\n"):
        text = text[:-1]
    match = COMMENT_REGEX.search(text)
    label = None
    ref = None
    comment = None
    if match is not None:
        label = match.group(RE_GROUP_LABEL)
        ref = match.group(RE_GROUP_REF)
        comment = match.group(RE_GROUP_COMMENT)
    return (label, ref, comment)


def _is_single_toc_token(line):
    if _is_eof(line):
        return False
    (label, _ref, _comment) = _get_comment(line)
    return label == LABEL_TOC


def _is_begin_toc_token(line):
    if _is_eof(line):
        return False
    (label, _ref, _comment) = _get_comment(line)
    return label == LABEL_BEGIN_TOC


def _is_end_toc_token(line):
    if _is_eof(line):
        return False
    (label, _ref, _comment) = _get_comment(line)
    return label == LABEL_END_TOC


def _is_toc_token(line):
    if _is_eof(line):
        return False
    (label, _ref, _comment) = _get_comment(line)
    return label in {LABEL_TOC, LABEL_BEGIN_TOC}


def _get_heading(text):
    # NOTE: This only handles the "atx"-style headings beginning with '#',
    # not the "setext"-style using "underlines" of '=' or '-'.
    #
    # TODO: We really should be using a full Markdown parser to detect text elements
    # instead of limited and potentially fragile regexes....
    if text.endswith("\n"):
        text = text[:-1]
    match = HEADING_REGEX.search(text)
    if match is None:
        heading_text = None
        heading_level = 0
    else:
        heading_text = match.group(RE_GROUP_TEXT)
        heading_level_text = match.group(RE_GROUP_LEVEL)
        heading_level = len(heading_level_text)
    return (heading_text, heading_level)


####################


class MarkdownFile(object):
    """
    Provide a class model for a Markdown file.

    This one is rudimentary, with regex-based parsing and no AST.

    :Args:
        infile
            The input file to read from.

        infilename
            (optional) A printable name for infile, overrides `infile.name`.


        outfile
            (optional) The output file to write to; if not supplied, must be
            supplied when writing.
    """

    def __init__(self, infile, infilename=None, outfile=None):
        self.infile = infile
        self.infilename = infilename
        self.outfile = outfile
        self.line_index = None
        self.lines = None
        self.toc = None

    @property
    def filename(self):
        """Printable input filename."""
        return self.infile.name if self.infilename is None else self.infilename

    def get_file_position(self):
        """Get a printable filename and line number."""
        if self.line_index is None:
            return self.filename
        return "{filename}:{line_number}".format(
            filename=self.filename, line_number=self.line_index + 1
        )

    def get_next_line(self, reset=False):
        """Get the "next" line from the set of lines."""
        if reset or self.line_index is None:
            self.line_index = 0
        else:
            self.line_index += 1
        if self.line_index + 1 > len(self.lines):
            return ""
        return self.lines[self.line_index]

    def consume_toc(self, line):
        """
        Consume a table of contents token or tokenset.

        A table of contents is defined as either:

            `toc-comment`

        or:

            `begin-toc-comment`
            `zero-or-more-non-end-toc-comment-lines`
            `end-toc-comment`
        """
        lines = [line]
        seen_toc = False
        in_toc = False
        while not _is_eof(line):
            if _is_single_toc_token(line):
                if seen_toc:
                    raise ValueError(
                        "invalid syntax: nested [{toc}]".format(toc=LABEL_TOC),
                        self.get_file_position(),
                    )
            elif _is_begin_toc_token(line):
                if seen_toc:
                    raise ValueError(
                        "invalid syntax: nested [{begintoc}]".format(
                            begintoc=LABEL_BEGIN_TOC
                        ),
                        self.get_file_position(),
                    )
                seen_toc = True
                in_toc = True
            elif _is_end_toc_token(line):
                if not seen_toc:
                    raise ValueError(
                        "invalid syntax: dangling [{endtoc}]".format(
                            endtoc=LABEL_END_TOC
                        ),
                        self.get_file_position(),
                    )
                in_toc = False
            if not in_toc:
                break
            line = self.get_next_line()
            lines.append(line)
        return "".join(lines)

    def skip_toc(self, line):
        """Skip over a table of contents starting on `line`."""
        if _is_toc_token(line):
            self.consume_toc(line)
            line = self.get_next_line()
        return line

    def consume_code_fence(self, line):
        """Consume a code fence."""
        lines = [line]
        in_code_fence = False
        while not _is_eof(line):
            if _is_code_fence(line):
                in_code_fence = not in_code_fence
            if not in_code_fence:
                break
            line = self.get_next_line()
            lines.append(line)
        return "".join(lines)

    def skip_code_fence(self, line):
        """Skip over any code fence starting on `line`."""
        if _is_code_fence(line):
            self.consume_code_fence(line)
            line = self.get_next_line()
        return line

    def read(self, force=False):
        """Read the Markdown file and return the raw input text."""
        if force or self.lines is None:
            self.lines = self.infile.readlines()
        return "".join(self.lines)

    def parse(self, heading_text, heading_level, skip_level):
        """Parse headings out of the Markdown file and build the table of contents."""
        input_text = self.read()
        self.toc = Toc(
            heading_text=heading_text,
            heading_level=heading_level,
            skip_level=skip_level,
        )
        toclevel = self.toc
        while True:
            line = self.get_next_line()
            if _is_eof(line):
                break
            line = self.skip_toc(line)
            line = self.skip_code_fence(line)
            (heading_text, heading_level) = _get_heading(line)
            if heading_text is not None:
                toclevel = toclevel.add_item(heading_text, heading_level)
        return input_text

    def write(
        self,
        numbered,
        toc_comment,
        alt_list_char,
        add_trailing_heading_chars,
        outfile=None,
    ):
        """Write the Markdown file with the new table of contents."""
        if outfile is not None:
            self.outfile = outfile
        reset = True
        while True:
            line = self.get_next_line(reset=reset)
            reset = False
            if _is_eof(line):
                break
            if _is_code_fence(line):
                lines = self.consume_code_fence(line)
                self.outfile.write(lines)
            elif _is_toc_token(line):
                line = self.skip_toc(line)
                self.outfile.write(
                    self.toc.format(
                        numbered=numbered,
                        comment=toc_comment,
                        alt_list_char=alt_list_char,
                        add_trailing_heading_chars=add_trailing_heading_chars,
                    )
                )
                self.outfile.write(line)
            else:
                self.outfile.write(line)
