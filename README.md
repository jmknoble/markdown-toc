# python-make-markdown-toc #

This is a Python script which will create a table of contents for a Markdown
document using the headings in the document as in-document hypertext link
references.

[begintoc]: #

# Contents

- [How Does It Work?](#how-does-it-work)
    - [Example](#example)
- [Generating the Table of Contents](#generating-the-table-of-contents)
    - [More Options](#more-options)

[endtoc]: # (Generated by markdown-toc)

## How Does It Work? ##

It uses jiggerypokery to interpret and create "pseudo-comments" in the
document text which are not rendered in most flavors of
[Markdown](https://gitlab.com/help/user/markdown) (including [GitLab-Flavored
Markdown](https://gitlab.com/help/user/markdown)).

> :pushpin: **NOTE:** This script only handles the "atx"-style headings beginning
> with `#`, not the "setext"-style using "underlines" with `=` or `-`.

To insert a table of contents in your document, add the following text, at the
beginning of an otherwise blank line and surrounded by blank lines, in the
spot where you want the table of contents to appear:

```
[toc]: #
```

This is the "table of contents token".

Alternatively, you can use a "begin table of contents token" with a matching
"end table of contents token":

```
[begintoc]: #
...
[endtoc]: #
```

Anything between the "begin" and "end" tokens will be replaced with the
generated table of contents.

### Example ###

The [source document for this README](docsrc/README.md) serves as an example.

## Generating the Table of Contents ##

Once the token is in your Markdown file, run this script to generate a new
document which includes a table of contents in place of the token.  For
example:

```
python ./make-markdown-toc.py
```

The result is currently printed to the standard output.

You can rerun this tool using a resulting document as the input, and the
existing table of contents will be replaced by a new one in the output.

### More Options ###

For help on the various options, use:

```
python ./make-markdown-toc.py --help
```
