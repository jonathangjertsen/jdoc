# jdoc - Automatically generate documentation from Python docstrings

[![Build Status](https://travis-ci.com/jonathangjertsen/jdoc.svg?branch=master)](https://travis-ci.com/jonathangjertsen/jdoc)

[![codecov](https://codecov.io/gh/jonathangjertsen/jdoc/branch/master/graph/badge.svg)](https://codecov.io/gh/jonathangjertsen/jdoc)

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

---

# Table of Contents

* `document(objects: list, filename: str)`
* `Plugin()`
    * `__init__(self)`
    * `get_wrapper(self) -> jdoc.ObjectWrapper`
    * `post_hook(self, children: List[jdoc.ObjectWrapper])`
* `HorizontalLine()`
* `TableOfContents(header: str = 'Table of Contents')`
* `IncludeChildren(obj)`
* `Indent()`
* `Dedent()`
* `ObjectWrapper(obj: object)`
    * `__init__(self, obj: object)`
    * `text(self) -> str`
    * `full_doc(self) -> str`
    * `oneliner(self) -> str`
    * `from_object(cls, obj: object) -> 'ObjectWrapper'`

---

## `document(objects: list, filename: str)`

Takes a list of objects and returns a string with documentation for all of them.

Each element of `objects` may either be a string (in which case it is considered a filename for a document),
a module, class, method or function, or an instance of a `Plugin` class:

* Instances of `Plugin` classes introduce special behaviours (see the documentation for those classes)
* Any other object is fed into `ObjectWrapper.from_object`.

---

## `Plugin()`

Base class for objects that can be added to the list passed to `document()` in order to get special behaviors.

Subclasses may implement `get_wrapper()`, and may optionally implement `post_hook`.

* `get_wrapper` should return an instance of `ObjectWrapper`. That instance's `full_doc()`, `oneliner()` and `text()`
  methods will be used to add text into the output. If not implemented, an `ObjectWrapper(None)` will be returned,
  which will not add any text to the input.
* `post_hook` takes in a list of `ObjectWrapper` objects. This is used in e.g. the `TableOfContents` plugin to let
  the corresponding `ObjectWrapper` call each of their `oneliner()` methods to generate a table of contents.

### `__init__(self)`

### `get_wrapper(self) -> jdoc.ObjectWrapper`

### `post_hook(self, children: List[jdoc.ObjectWrapper])`

## `HorizontalLine()`

Add `HorizontalLine()` to the list of objects passed to `document()` to insert a horizontal line.

## `TableOfContents(header: str = 'Table of Contents')`

Add `TableOfContents()` to the list of objects passed to `document()` to insert a table of contents.

It is only supported to have one TableOfContents.

The `header` argument, if provided, changes the heading for the table of contents.

## `IncludeChildren(obj)`

Wrap this around an object passed to `document()` to automatically include all of its children in the
documentation output.

* For a module, the children are the classes and functions defined within the module.
* For a class, the children are the methods defined within the module.

## `Indent()`

Add `Indent()` to the list of objects passed to `document()` to increase the indentation level by one in the
table of contents from this point.

Add a corresponding `Dedent()` after the section that should be indented.

## `Dedent()`

Add `Indent()` to the list of objects passed to `document()` to reduce the indentation level by one in the
table of contents from this point.

---

## `ObjectWrapper(obj: object)`

Base class for objects that should be documented.

### `__init__(self, obj: object)`

Initializes the DocumentedObject with the object that it wraps.

### `text(self) -> str`

Returns some text equivalent to a docstring for the object.

If not overridden, this returns the `__doc__` attribute of the object if it is not None.
Otherwise, empty string is returned.

### `full_doc(self) -> str`

Returns the text corresponding to the documentation of the object and all its children.

### `oneliner(self) -> str`

Returns a one-line representation of the object. For functions and method, this is the function signature.

For classes, this is the signature of the `__init__` function. For modules, this is the import statement.

### `from_object(cls, obj: object) -> 'ObjectWrapper'`

Factory function which detects the type of `obj` and returns an appropriate subclass of `DocumentedObject`.

---

# Testing

To run the tests:

```
pytest --cov-report term-missing --cov jdoc -vvv
```
