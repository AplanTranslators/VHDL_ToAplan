import re

import antlr4
from antlr4 import *
from antlr4 import tree

from AppModule.app.classes.design_unit_call import DesignUnitCall
from antrl4_vhdl.vhdlListener import vhdlListener
from antrl4_vhdl.vhdlParser import vhdlParser

from listener.base import BaseListener


def bodyPrint(ctx):
    if not ctx:
        return
    if isinstance(ctx, antlr4.tree.Tree.TerminalNodeImpl):
        return
    for element in ctx.getChildren():
        print(element.getText(), type(element))
        bodyPrint(element)


# generate_stubbed_class need for tree printing # only for debug
class VHDL2AplanListener(BaseListener, vhdlListener):

    def __init__(self, design_unit_call: DesignUnitCall | None = None):
        BaseListener().__init__(design_unit_call)

    # =========================================================================================
    # EXPRESSIONS
    # =========================================================================================

    # Enter a parse tree produced by vhdlParser#expression.
    def enterExpression(self, ctx: vhdlParser.ExpressionContext):
        self.translator.getTranslator("expr").insertOperator()
        pass

    def enterLiteral(self, ctx: vhdlParser.LiteralContext):
        self.translator.translate("literal", ctx)

    # overrule one more time to store its text
    # basically this is all we want
    def enterIdentifier(self, ctx: vhdlParser.IdentifierContext):
        self.translator.translate("ident", ctx)
        pass
        # need for tree printing # only for debug

    # =========================================================================================
    # ENTITY
    # =========================================================================================
    # Enter a parse tree produced by vhdlParser#entity_declaration.
    def enterEntity_declaration(self, ctx: vhdlParser.Entity_declarationContext):
        self.translator.translate("entity_decl", ctx)
        pass

    # =========================================================================================
    # DECLS
    # =========================================================================================
    def enterBlock_declarative_item(
        self, ctx: vhdlParser.Block_declarative_itemContext
    ):
        self.translator.translate("block_decl", ctx)
        pass

    def exitBlock_declarative_item(self, ctx: vhdlParser.Block_declarative_itemContext):
        self.translator.exit("block_decl", ctx)
        pass

    # =========================================================================================
    # PORT
    # =========================================================================================
    def enterInterface_port_declaration(
        self, ctx: vhdlParser.Interface_port_declarationContext
    ):
        self.translator.translate("int_port_decl", ctx)
        pass

    def exitInterface_port_declaration(
        self, ctx: vhdlParser.Interface_port_declarationContext
    ):
        self.translator.exit("int_port_decl", ctx)
        pass

    # =========================================================================================
    # ACHITECTURE
    # =========================================================================================

    def enterArchitecture_body(self, ctx: vhdlParser.Architecture_bodyContext):
        self.translator.translate("arc_decl", ctx)
        pass

    def exitArchitecture_body(self, ctx: vhdlParser.Architecture_bodyContext):
        self.translator.exit("arc_decl", ctx)
        pass

    def enterArchitecture_statement_part(
        self, ctx: vhdlParser.Architecture_statement_partContext
    ):
        pass

    # Exit a parse tree produced by vhdlParser#architecture_statement_part.
    def exitArchitecture_statement_part(
        self, ctx: vhdlParser.Architecture_statement_partContext
    ):
        pass

    # =========================================================================================
    # SEC UNIT
    # =========================================================================================
    # Enter a parse tree produced by vhdlParser#secondary_unit_declaration.
    def enterSecondary_unit_declaration(
        self, ctx: vhdlParser.Secondary_unit_declarationContext
    ):
        self.logger.warning("Secondary unit declaration!")
        pass

    # Exit a parse tree produced by vhdlParser#secondary_unit_declaration.
    def exitSecondary_unit_declaration(
        self, ctx: vhdlParser.Secondary_unit_declarationContext
    ):
        pass


# def enterIdentifier(self, ctx):
