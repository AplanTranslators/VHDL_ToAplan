import re

import antlr4
from antlr4 import *
from antlr4 import tree

from AppModule.app.classes.design_unit_call import DesignUnitCall
from antrl4_vhdl.vhdlListener import vhdlListener
from listener.base import BaseListener
from listener.tree_utils import TreeStorage


# function to generate overruling class
def generate_stubbed_class(klass_name, klass):
    """Returns a function call to create a class derrived from "klass",
    named "klass_name" which autogenerates a bunch of override methods
    for "klass" attributes.
    Specifically, this function will return a class which overrides all
    enterXXXX() and exitXXXX() methods from the Listener class generated
    by ANTLR so to set an attribute XXXX True upon entering and False
    upon exit.
    """

    # override enter_NAME to add a branch and cling to it
    def generate_stub_enter(name):
        def stub(self, ctx):
            self.makeBranchAndClimb(name)

        return stub  # return method

    # override exit_NAME to back down one branch
    def generate_stub_exit(name):
        def stub(self, ctx):
            self.climbBack()

        return stub  # return method

    # empty list of attributes
    attributes = {}

    for name in dir(klass):  # lists all attributes (names only)
        try:
            # match uppercase, but don't absorb it
            # split enterIdentifier in [], "enter", "Identifier", []
            oper, key = re.split("(^enter|^exit)(.*)", name, 1)[1:3]
        except ValueError:
            # not in the format of SOMETHING_SOMETHING
            continue  # try next

        # skip inherited rule which is called every time
        if key == "EveryRule":
            continue

        # additional check
        attr = getattr(klass, name)
        # make sure it's a function and name ends in _enter or _exit
        if callable(attr) and oper in ("enter", "exit"):
            # call method generation function
            if oper == "enter":  # True for 'enter', False for 'exit'
                attributes[name] = generate_stub_enter(key)
            else:
                attributes[name] = generate_stub_exit(key)
    # return a class, inheriting from klass, with generated attributes
    return type(klass_name, (klass,), attributes)


class VHDL2AplanListener(BaseListener, generate_stubbed_class("MyClass", vhdlListener)):

    def __init__(self, filename, design_unit_call: DesignUnitCall | None = None):
        # instantiate a tree storage structure
        self.root = TreeStorage(filename, "file")
        # set pointer
        self.tree = self.root

    def makeBranchAndClimb(self, type):
        self.tree = self.tree.makeChild(type)

    def climbBack(self):
        self.tree = self.tree.parent

    def printTree(self):
        self.root.printDetailedSubTree()

    # overrule one more time to store its text
    # basically this is all we want
    def enterIdentifier(self, ctx):
        super(VHDL2AplanListener, self).enterIdentifier(ctx)
        self.tree.addText(ctx.getText())
