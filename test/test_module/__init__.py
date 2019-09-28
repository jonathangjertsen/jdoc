"""This is a test module!"""
from enum import Enum


class Class(object):
    """This is a test class!"""

    def __init__(self, x: float):
        """This is a test init!"""

    def method(self, y: float):
        """This is a test method!"""

    def method_nodoc(self):
        pass


class ClassNoDoc(object):
    pass


def function(x: int, y: str):
    """This is a test function!"""


def function_nodoc():
    pass
