import sys

import pytest

import jdoc

from . import test_module

at_least_3_7 = pytest.mark.skipif(sys.version_info < (3, 7), reason="Python 3.6 and below returns different function signatures")

def test_documented_object_defaults():
    obj = 1
    assert jdoc.ObjectWrapper(obj).oneliner() == ""
    assert jdoc.ObjectWrapper.from_object(obj) == jdoc.ObjectWrapper(obj)


def test_documented_object_equivalence():
    obj = 1
    assert jdoc.ObjectWrapper(obj) == jdoc.ObjectWrapper(obj)
    assert jdoc.ObjectWrapper(obj) != "42"


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
    assert init.heading_level == 3
    assert method.heading_level == 3
    assert method_nodoc.heading_level == 3


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
        == """### `method(self, y: float)`

This is a test method!"""
    )
    assert method_nodoc.full_doc().strip() == """### `method_nodoc(self)`"""
    assert (
        init.full_doc().strip()
        == """### `__init__(self, x: float)`

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


def test_class_children(class_, init, method, method_nodoc):
    assert class_.children() == [init, method, method_nodoc]


@at_least_3_7
def test_class_assemble(class_):
    class_.include_children = True
    assert (
        class_.full_doc().strip()
        == """## `Class(x: float)`

This is a test class!

### `__init__(self, x: float)`

This is a test init!

### `method(self, y: float)`

This is a test method!

### `method_nodoc(self)`"""
    )


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


@at_least_3_7
def test_module_assemble(module):
    module.include_children = True
    assert (
        module.full_doc().strip()
        == """# `test.test_module`

This is a test module!

## `Class(x: float)`

This is a test class!

### `__init__(self, x: float)`

This is a test init!

### `method(self, y: float)`

This is a test method!

### `method_nodoc(self)`

## `ClassNoDoc(*args, **kwargs)`

## `function(x: int, y: str)`

This is a test function!

## `function_nodoc()`"""
    )


def test_markdown_heading_level(markdown):
    assert markdown.heading_level is None


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
    assert package.heading_level is None


def test_package_children(package, markdown, module, sub_module_file):
    assert package.children() == [markdown, module, sub_module_file]


def test_package_signature(package):
    assert package.oneliner() == ""


@at_least_3_7
def test_package_assemble(package):
    package.include_children = True
    assert (
        package.full_doc().strip()
        == """# README.md

This is a test README.md!

# `test.test_module`

This is a test module!

## `Class(x: float)`

This is a test class!

### `__init__(self, x: float)`

This is a test init!

### `method(self, y: float)`

This is a test method!

### `method_nodoc(self)`

## `ClassNoDoc(*args, **kwargs)`

## `function(x: int, y: str)`

This is a test function!

## `function_nodoc()`

# `test.test_module.sub_module_file`

This is a test sub-module in a file!

## `sub_module_function()`"""
    )
