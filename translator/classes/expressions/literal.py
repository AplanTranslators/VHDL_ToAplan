import typing
from AppModule.app.classes.element_types import ElementsTypes
from AppModule.app.classes.node import Node
from translator.classes.base_translator import BaseTranslator
from antrl4_vhdl.vhdlParser import vhdlParser


class LiteralTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(self, ctx: vhdlParser.LiteralContext) -> None:
        if not self.last_node_array:
            return

        literal: vhdlParser.Enumeration_literalContext = ctx.enumeration_literal()
        numeric_literal: vhdlParser.Numeric_literalContext = ctx.numeric_literal()
        element_type = ElementsTypes.IDENTIFIER_ELEMENT
        if literal:
            value = literal.getText()
            value = self.str_formater.valuesToAplanStandart(value)
            element_type = ElementsTypes.NUMBER_ELEMENT
        elif element_type:
            value = numeric_literal.getText()
            value = self.str_formater.valuesToAplanStandart(value)
            element_type = ElementsTypes.NUMBER_ELEMENT
        else:
            text = f"Unhandled literal type  for {ctx.getText()}"
            raise TypeError(text)
        index = self.last_node_array.addElement(
            Node(value, ctx.getSourceInterval(), element_type)
        )
        node = self.last_node_array.getElementByIndex(index)
        decl = self.design_unit.declarations.getElement(node.identifier)
        if decl:
            node.design_unit_name = self.design_unit.ident_uniq_name

            # todo
            # node.identifier = self._translator_ptr.translate(
            #     "param_call", node.identifier
            # )
