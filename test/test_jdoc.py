import sys

import pytest

import jdoc

from . import test_module

at_most_3_6 = pytest.mark.skipif(
    sys.version_info >= (3, 6),
    reason="Python 3.6 and below returns different function signatures",
)
at_least_3_7 = pytest.mark.skipif(
    sys.version_info < (3, 7),
    reason="Python 3.6 and below returns different function signatures",
)


def test_object_wrapper_defaults():
    obj = 1
    assert jdoc.ObjectWrapper(obj).oneliner() == ""
    assert jdoc.ObjectWrapper.from_object(obj) == jdoc.ObjectWrapper(obj)


def test_object_wrapper_equivalence():
    obj = 1
    assert jdoc.ObjectWrapper(obj) == jdoc.ObjectWrapper(obj)
    assert jdoc.ObjectWrapper(obj) != "42"


def test_object_wrapper_repr():
    obj = 1
    assert repr(jdoc.ObjectWrapper(obj)) == "<ObjectWrapper >"


def test_function_import(function):
    assert function.obj is test_module.function


def test_function_heading_level(function):
    assert function.heading_level == 2


def test_function_doc(function):
    assert function.text() == """This is a test function!"""


def test_function_children(function):
    assert function.children() == []


@at_least_3_7
def test_function_signature(function):
    assert function.oneliner() == "function(x: int, y: str)"


@at_least_3_7
def test_function_assemble(function):
    assert (
        function.full_doc().strip()
        == """## `function(x: int, y: str)`

This is a test function!"""
    )


def test_method_import(init, method, method_nodoc):
    assert init.obj is test_module.Class.__init__
    assert method.obj is test_module.Class.method
    assert method_nodoc.obj is test_module.Class.method_nodoc


def test_method_heading_level(init, method, method_nodoc):
    assert init.heading_level == 2
    assert method.heading_level == 2
    assert method_nodoc.heading_level == 2


def test_method_doc(init, method, method_nodoc):
    assert init.text() == """This is a test init!"""
    assert method.text() == """This is a test method!"""
    assert method_nodoc.text() == """"""


def test_method_children(init, method, method_nodoc):
    assert init.children() == []
    assert method.children() == []
    assert method_nodoc.children() == []


@at_least_3_7
def test_method_signature(init, method, method_nodoc):
    assert init.oneliner() == "__init__(self, x: float)"
    assert method.oneliner() == "method(self, y: float)"
    assert method_nodoc.oneliner() == "method_nodoc(self)"


@at_least_3_7
def test_method_assemble(init, method, method_nodoc):
    assert (
        method.full_doc().strip()
        == """## `method(self, y: float)`

This is a test method!"""
    )
    assert method_nodoc.full_doc().strip() == """## `method_nodoc(self)`"""
    assert (
        init.full_doc().strip()
        == """## `__init__(self, x: float)`

This is a test init!"""
    )


def test_import_builtins():
    import math
    import re

    assert [jdoc.ModuleWrapper(math).obj, jdoc.ModuleWrapper(re).obj] == [math, re]


def test_class_import(class_):
    assert class_.obj is test_module.Class


def test_class_heading_level(class_):
    assert class_.heading_level == 2


def test_class_doc(class_):
    assert class_.text() == """This is a test class!"""


@at_least_3_7
def test_class_signature(class_):
    assert class_.oneliner() == "Class(x: float)"


@at_least_3_7
def test_class_children(class_, init, method, classmethod, staticmethod, method_nodoc):
    assert class_.children() == [init, method, classmethod, staticmethod, method_nodoc]


def test_module_import(module):
    assert module.obj is test_module


def test_module_heading_level(module):
    assert module.heading_level == 1


def test_module_doc(module):
    assert module.text() == """This is a test module!"""


def test_module_signature(module):
    assert module.oneliner() == "test.test_module"


def test_module_children(module, class_, class_nodoc, function, function_nodoc):
    assert module.children() == [class_, class_nodoc, function, function_nodoc]


def test_markdown_heading_level(markdown):
    assert markdown.heading_level == 0


def test_markdown_doc(markdown):
    with open(markdown.filename) as file:
        assert markdown.text() == file.read()


def test_markdown_children(markdown):
    assert markdown.children() == []


def test_markdown_signature(markdown):
    assert markdown.oneliner() == ""


def test_markdown_assemble(markdown):
    assert markdown.full_doc() == markdown.text()


def test_package_heading_level(package):
    assert package.heading_level == 0


def test_package_children(package, markdown, module, sub_module_file):
    assert package.children() == [markdown, module, sub_module_file]


def test_package_signature(package):
    assert package.oneliner() == ""


def test_plugin_base():
    assert jdoc.PackageWrapper([jdoc.Plugin()]).children() == [jdoc.ObjectWrapper(None)]


def test_indent():
    assert jdoc.PackageWrapper([jdoc.Indent()]).children() == [jdoc.IndentWrapper()]


def test_dedent():
    assert jdoc.PackageWrapper([jdoc.Dedent()]).children() == [jdoc.DedentWrapper()]


def test_horizontal_line():
    assert jdoc.PackageWrapper([jdoc.HorizontalLine()]).children() == [
        jdoc.HorizontalLineWrapper()
    ]


def test_table_of_contents():
    toc_header = "Toc"
    assert jdoc.PackageWrapper([jdoc.TableOfContents(toc_header)]).children() == [
        jdoc.TableOfContentsWrapper(toc_header)
    ]


def test_document_empty(output_md_filename):
    jdoc.document([], output_md_filename)

    with open(output_md_filename) as file:
        assert file.read() == ""


def test_integration(output_md_filename):
    class Class(object):
        def method(self):
            pass

    objects = [
        jdoc.TableOfContents("Toc"),
        jdoc.HorizontalLine(),
        jdoc.IncludeChildren(Class),
        jdoc.HorizontalLine(),
        Class,
        jdoc.Indent(),
        Class.method,
        jdoc.Dedent(),
    ]

    expected_out = """# Toc

* `Class(*args, **kwargs)`
    * `method(self)`
* `Class(*args, **kwargs)`
    * `method(self)`

---

## `Class(*args, **kwargs)`

### `method(self)`

---

## `Class(*args, **kwargs)`

### `method(self)`"""

    jdoc.document(objects, output_md_filename)

    with open(output_md_filename) as file:
        assert file.read().strip() == expected_out

    assert jdoc.PackageWrapper(objects).full_doc().strip() == expected_out
