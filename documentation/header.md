# jdoc - Automatically generate documentation from Python docstrings

## Example

Say you want your `README.md` to contain some text at the top, followed by automatically generated documentation from
your docstrings, followed by some text at the end. Write your static text in `header.md` and `footer.md` respectively,
and call `document()` to generate the content automatically:

```Python
from jdoc import document, Markdown, IncludeChildren

import my_package

document([
    Markdown("header.md"),
    IncludeChildren(my_package),
    Markdown("footer.md")
], filename="README.md")
```

