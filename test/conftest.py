import os

import pytest

import jdoc

from . import test_module
from .test_module import sub_module_file as sub_module_file_


@pytest.fixture()
def module():
    return jdoc.ObjectWrapper.from_object(test_module)


@pytest.fixture()
def class_():
    return jdoc.ObjectWrapper.from_object(test_module.Class)


@pytest.fixture()
def class_nodoc():
    return jdoc.ObjectWrapper.from_object(test_module.ClassNoDoc)


@pytest.fixture()
def method():
    return jdoc.MethodWrapper(test_module.Class.method)


@pytest.fixture()
def method_nodoc():
    return jdoc.MethodWrapper(test_module.Class.method_nodoc)


@pytest.fixture()
def init():
    return jdoc.MethodWrapper(test_module.Class.__init__)


@pytest.fixture()
def function():
    return jdoc.ObjectWrapper.from_object(test_module.function)


@pytest.fixture()
def function_nodoc():
    return jdoc.ObjectWrapper.from_object(test_module.function_nodoc)


@pytest.fixture()
def index_md_filename():
    return os.path.join(os.path.dirname(__file__), "test_module", "header.md")


@pytest.fixture()
def markdown(index_md_filename):
    return jdoc.MarkdownWrapper(index_md_filename)


@pytest.fixture()
def package(index_md_filename):
    return jdoc.PackageWrapper(
        [jdoc.Markdown(index_md_filename), test_module, test_module.sub_module_file]
    )


@pytest.fixture()
def sub_module_file():
    return jdoc.ObjectWrapper.from_object(sub_module_file_)


@pytest.fixture()
def sub_module_function():
    return jdoc.ObjectWrapper.from_object(sub_module_file_.sub_module_function)
