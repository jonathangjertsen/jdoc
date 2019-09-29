import os

from jdoc import (
    document,
    Markdown,
    IncludeChildren,
    HorizontalLine,
    TableOfContents,
    Indent,
    Dedent,
)
import jdoc as my_package

if __name__ == "__main__":
    header_filename = os.path.join(os.path.dirname(__file__), "header.md")
    testing_filename = os.path.join(os.path.dirname(__file__), "testing.md")
    document(
        [
            Markdown(header_filename),
            HorizontalLine(),
            TableOfContents("Table of Contents"),
            HorizontalLine(),
            my_package.document,
            HorizontalLine(),
            IncludeChildren(my_package.Plugin),
            my_package.HorizontalLine,
            my_package.TableOfContents,
            my_package.IncludeChildren,
            my_package.Indent,
            my_package.Dedent,
            HorizontalLine(),
            IncludeChildren(my_package.ObjectWrapper),
            HorizontalLine(),
            Markdown(testing_filename),
        ],
        filename=os.path.join(os.getcwd(), "README.md"),
    )
