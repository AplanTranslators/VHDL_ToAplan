import typing
from AppModule.app.classes.design_unit import DesignUnit
from translator.classes.base_translator import BaseTranslator
from antrl4_vhdl.vhdlParser import vhdlParser


class EntityDeclTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(self, ctx: vhdlParser.Entity_declarationContext) -> None:
        identifier_ctx: vhdlParser.IdentifierContext = ctx.identifier(0)
        identifier = identifier_ctx.getText()
        index = self.design_units.addElement(
            DesignUnit(identifier, ctx.getSourceInterval(), identifier)
        )
        self.design_unit = self.design_units.getElementByIndex(index)

