import typing
from AppModule.app.utils.singleton import SingletonMeta
from antrl4_vhdl.vhdlParser import vhdlParser
from antlr4.tree import Tree
from AppModule.app.classes.element_types import ElementsTypes
from AppModule.app.classes.node import Node
from translator.classes.base_translator import BaseTranslator


class OperatorTranslator(BaseTranslator, metaclass=SingletonMeta):
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(self, operator: str, source_interval: typing.Tuple[int, int]) -> None:
        if self.last_node_array is None:
            return

        operator_type = ElementsTypes.OPERATOR_ELEMENT
        if "." in operator:
            operator_type = ElementsTypes.DOT_ELEMENT

        if self.last_node_array.node_type == ElementsTypes.POSTCONDITION_ELEMENT:
            operator = self.str_formater.parallelAssignment2Assignment(operator)

        index = self.last_node_array.addElement(
            Node(operator, source_interval, operator_type)
        )
        node = self.last_node_array.getElementByIndex(index)
        decl = self.design_unit.declarations.getElement(node.identifier)
        if decl:
            node.design_unit_name = self.design_unit.ident_uniq_name


class LogicalOperatorTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)
        self.operator_translator = OperatorTranslator(self._translator_ptr)

    def translate(self, ctx: vhdlParser.Logical_operatorContext) -> None:
        if self.last_node_array is None:
            return

        operator = "None"
        if ctx.AND():
            operator = "&&"

        elif ctx.OR():
            operator = "||"
        elif ctx.NAND():
            raise TypeError("Unhandle NAND operator")

        elif ctx.NOR():
            raise TypeError("Unhandle NOR operator")
        elif ctx.XOR():
            raise TypeError("Unhandle XOR operator")
        elif ctx.XNOR():
            raise TypeError("Unhandle XNOR operator")
        else:
            raise TypeError("Unhandle operator")

        self.operator_translator.translate(operator, ctx.getSourceInterval())
