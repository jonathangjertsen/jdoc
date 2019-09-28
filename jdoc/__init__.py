"""
Tools for collecting documentation
"""
import functools
import inspect
import pydoc
from textwrap import dedent
from typing import Iterable, List, Union
import types


def _clean_up_docstring(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        string = func(*args, **kwargs)

        # Dedent it
        string = dedent(string)

        # If the first line does not contain the same indent as the rest, deal with that too
        lines = string.split("\n")
        first_line = lines[0]
        all_lines_except_first = lines[1:]
        string_except_first_line = dedent("\n".join(all_lines_except_first))
        if string_except_first_line:
            string = first_line + "\n" + string_except_first_line
        else:
            string = first_line

        # Remove all instances of >=3 newlines
        while True:
            replaced = string.replace("\n\n\n", "\n\n")
            if replaced == string:
                break
            string = replaced

        return string

    return wrapper


class ObjectWrapper(object):
    """Base class for objects that should be documented."""

    heading_level = 0

    def __init__(self, obj: object):
        """Initializes the DocumentedObject with the object that it wraps."""
        self.obj = obj
        self.include_children = False
        self.includes = set()
        self.excludes = set()

    def __repr__(self):
        return "<{} {}>".format(type(self).__name__, self.oneliner())

    def __eq__(self, other: "ObjectWrapper") -> bool:
        """We regard two DocumentedObjects as equivalent if their `full_doc()` functions evaluate to the same
        documentation output."""
        try:
            equal = self.full_doc() == other.full_doc()
        except AttributeError:
            equal = False
        return equal

    @_clean_up_docstring
    def text(self) -> str:
        """Returns some text equivalent to a docstring for the object.

        If not overridden, this returns the `__doc__` attribute of the object if it is not None.
        Otherwise, empty string is returned.
        """
        doc = self.obj.__doc__

        if doc is None:
            doc = ""

        return doc

    def full_doc(self) -> str:
        """Returns the text corresponding to the documentation of the object and all its children."""
        return ""

    def oneliner(self) -> str:
        """Returns a one-line representation of the object. For functions and method, this is the function signature.

        For classes, this is the signature of the `__init__` function. For modules, this is the import statement."""
        return ""

    def children(self) -> List["ObjectWrapper"]:
        """Returns all children of `self`."""
        return []

    @classmethod
    def from_object(cls, obj: object) -> "ObjectWrapper":
        """Factory function which detects the type of `obj` and returns an appropriate subclass of `DocumentedObject`.
        """
        if inspect.ismodule(obj):
            wrapper = ModuleWrapper(obj)
        elif inspect.isclass(obj):
            wrapper = ClassWrapper(obj)
        elif inspect.isfunction(obj):
            wrapper = FunctionWrapper(obj)
        elif isinstance(obj, classmethod):
            wrapper = ClassMethodWrapper(obj.__func__)
        elif isinstance(obj, staticmethod):
            wrapper = StaticMethodWrapper(obj.__func__)
        else:
            wrapper = ObjectWrapper(obj)

        return wrapper


class FunctionWrapper(ObjectWrapper):
    """Represents a function."""

    heading_level = 2

    def oneliner(self):
        signature = str(inspect.signature(self.obj))
        return self.obj.__name__ + signature

    @_clean_up_docstring
    def full_doc(self):
        signature = self.oneliner()
        doc = self.text()
        heading = "#" * self.heading_level

        return """{heading} `{signature}`

{doc}
""".format(
            signature=signature, doc=doc, heading=heading
        )


class MethodWrapper(ObjectWrapper):
    """Represents a method."""

    heading_level = 3

    oneliner = FunctionWrapper.oneliner
    full_doc = FunctionWrapper.full_doc


class ClassMethodWrapper(MethodWrapper):
    """Represents a class method."""


class StaticMethodWrapper(MethodWrapper):
    """Represents a static method"""


class ClassWrapper(ObjectWrapper):
    """Represents a class."""

    heading_level = 2

    def __init__(self, obj):
        super().__init__(obj)

    def oneliner(self) -> str:
        signature_with_self = inspect.signature(self.obj.__init__)
        values = list(signature_with_self.parameters.values())[1:]
        signature = inspect.Signature(values)
        return self.obj.__name__ + str(signature)

    @_clean_up_docstring
    def full_doc(self) -> str:
        heading = "#" * self.heading_level
        signature = self.oneliner()
        doc = self.text()

        if self.include_children:
            method_docs = "\n".join(child.full_doc() for child in self.children())
        else:
            method_docs = ""

        return """{heading} `{signature}`

{doc}

{method_docs}

""".format(
            signature=signature, doc=doc, heading=heading, method_docs=method_docs
        )

    def _is_child(self, obj) -> bool:
        is_child = inspect.isfunction(obj)
        try:
            name = obj.__name__
        except AttributeError:
            is_child = False
        else:
            is_child &= not name.startswith("_")
            is_child |= name == "__init__"
            is_child |= name in self.includes
            is_child &= name not in self.excludes

        is_child |= isinstance(obj, classmethod)
        is_child |= isinstance(obj, staticmethod)

        return is_child

    def children(self) -> List[MethodWrapper]:
        children = [
            ObjectWrapper.from_object(obj)
            for obj in self.obj.__dict__.values()
            if self._is_child(obj)
        ]

        for i, child in enumerate(children):
            if type(child) is FunctionWrapper:
                children[i] = MethodWrapper(child.obj)
            child.include_children = self.include_children

        return children


class ModuleWrapper(ObjectWrapper):
    """Represents a module."""

    heading_level = 1

    def _is_child(self, obj: object) -> bool:
        is_child = inspect.isclass(obj) | inspect.isfunction(obj)
        is_child &= inspect.getmodule(obj) is self.obj

        try:
            is_child &= not obj.__name__.startswith("_")
            is_child &= pydoc.visiblename(obj.__name__)
            is_child |= obj.__name__ in self.includes
            is_child &= obj.__name__ not in self.excludes
        except AttributeError:
            is_child = False

        return is_child

    def children(self) -> List["ObjectWrapper"]:
        children = [
            ObjectWrapper.from_object(obj)
            for name, obj in inspect.getmembers(self.obj)
            if self._is_child(obj)
        ]

        for child in children:
            child.include_children = self.include_children

        return children

    def oneliner(self) -> str:
        return self.obj.__name__

    @_clean_up_docstring
    def full_doc(self) -> str:
        name = self.obj.__name__
        doc = self.text()
        heading = "#" * self.heading_level

        if self.include_children:
            child_docs = "\n".join(child.full_doc() for child in self.children())
        else:
            child_docs = ""
        return """{heading} `{name}`

{doc}

{child_docs}
""".format(
            name=name, doc=doc, heading=heading, child_docs=child_docs
        )


class MarkdownWrapper(ObjectWrapper):
    """Represents a Markdown document."""

    heading_level = None

    def __init__(self, filename: str):
        super().__init__(None)
        self.filename = filename
        self._text = None

    def text(self) -> str:
        if self._text is None:
            with open(self.filename) as file:
                self._text = file.read()
        return self._text

    def full_doc(self) -> str:
        return self.text()


class PackageWrapper(ObjectWrapper):
    """Represents a documented package."""

    heading_level = None

    def __init__(self, objects: List[Union[str, types.ModuleType]]):
        """Initializes the PackageWrapper with a list of objects."""
        super().__init__(None)
        self.objects = objects

    def children(self) -> List[ObjectWrapper]:
        """Converts `self.object` to a list of children, each of which is a `DocumentedObject`."""
        children = []
        magics = []

        for obj in self.objects:
            if isinstance(obj, Magic):
                child = obj.get_wrapper()
                magics.append(obj)
            else:
                child = ObjectWrapper.from_object(obj)
            children.append(child)
            if self.include_children:
                child.include_children = True

        for magic in magics:
            magic.post_hook(children)

        return children

    @_clean_up_docstring
    def full_doc(self) -> str:
        """Returns a string with documentation for the module and all classes and functions defined there."""
        return "\n".join(child.full_doc() for child in self.children())


class Magic(object):
    def __init__(self):
        pass

    def get_wrapper(self):
        raise NotImplementedError

    def post_hook(self, children: List[ObjectWrapper]):
        pass


class Markdown(Magic):
    """Add `Markdown(filename)` to the list of objects passed to `document()` to "copy-paste" the contents of that
    Markdown file into the output."""

    def __init__(self, filename):
        super().__init__()
        self.filename = filename

    def get_wrapper(self):
        return MarkdownWrapper(self.filename)


class Indent(Magic):
    """Add `Indent()` to the list of objects passed to `document()` to increase the indentation level by one in the
    table of contents from this point.

    Add a corresponding `Dedent()` after the section that should be indented.
    """

    def get_wrapper(self):
        super().__init__()
        return IndentWrapper()

    def post_hook(self, children):
        pass


class Dedent(Magic):
    """Add `Indent()` to the list of objects passed to `document()` to reduce the indentation level by one in the
    table of contents from this point."""

    def get_wrapper(self):
        super().__init__()
        return DedentWrapper()

    def post_hook(self, children):
        pass


class IncludeChildren(Magic):
    """Wrap this around an object passed to `document()` to automatically include all of its children in the
    documentation output.

    * For a module, the children are the classes and functions defined within the module.
    * For a class, the children are the methods defined within the module.
    """

    def __init__(self, obj):
        super().__init__()
        self.obj = obj

    def get_wrapper(self):
        obj = ObjectWrapper.from_object(self.obj)
        obj.include_children = True
        return obj


class HorizontalLine(Magic):
    """Add `HorizontalLine()` to the list of objects passed to `document()` to insert a horizontal line."""

    def get_wrapper(self):
        return HorizontalLineWrapper()


class TableOfContents(Magic):
    """Add `TableOfContents()` to the list of objects passed to `document()` to insert a table of contents.

    It is only supported to have one TableOfContents.

    The `header` argument, if provided, changes the heading for the table of contents.
    """

    def __init__(self, header: str = "Table of Contents"):
        super().__init__()
        self.header = header
        self.wrapper = None

    def get_wrapper(self):
        self.wrapper = TableOfContentsWrapper(self.header)
        return self.wrapper

    def post_hook(self, children):
        self.wrapper.objects = children


class IndentWrapper(ObjectWrapper):
    def __init__(self):
        super().__init__(None)


class DedentWrapper(ObjectWrapper):
    def __init__(self):
        super().__init__(None)


class TableOfContentsWrapper(ObjectWrapper):
    def __init__(self, header):
        super().__init__(None)
        self.objects = []
        self.header = header

    def full_doc(self) -> str:
        output = ["# {}".format(self.header), ""]
        indent = 0

        def add_line(obj):
            nonlocal indent

            if isinstance(obj, IndentWrapper):
                indent += 1
            elif isinstance(obj, DedentWrapper):
                indent -= 1

            oneliner = obj.oneliner()
            if oneliner:
                line = "    " * indent + "* `" + oneliner + "`"
                output.append(line)
            if obj.include_children:
                indent += 1
                for child in obj.children():
                    add_line(child)
                indent -= 1

        for obj in self.objects:
            add_line(obj)

        return "\n".join(output)


class HorizontalLineWrapper(ObjectWrapper):
    def __init__(self):
        super().__init__(None)

    def full_doc(self) -> str:
        return "\n---\n"


def document(objects: list, filename: str):
    """Takes a list of objects and returns a string with documentation for all of them.

    Each element of `objects` may either be a string (in which case it is considered a filename for a document),
    a module, class, method or function, or an instance of a `Magic` class:

    * Instances of `Magic` classes introduce special behaviours (see the documentation for those classes)
    * Any other object is fed into `ObjectWrapper.from_object`.
    """
    package = PackageWrapper(objects)
    documentation = package.full_doc()
    with open(filename, "w") as file:
        file.write(documentation)
