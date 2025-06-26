import typing
from AppModule.app.classes.declarations import DeclTypes, Declaration
from AppModule.app.classes.design_unit import DesignUnit
from AppModule.app.classes.element_types import ElementsTypes
from AppModule.app.classes.structure import Structure
from AppModule.app.classes.typedef import Typedef
from translator.classes.base_translator import BaseTranslator
from antrl4_vhdl.vhdlParser import vhdlParser


class ProcessDeclTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(self, ctx: vhdlParser.Process_statementContext) -> None:
        sensetivivty_list: vhdlParser.Sensitivity_listContext = ctx.sensitivity_list()
        if sensetivivty_list:
            raise TypeError("Unhandled for sensetiv process")

        identifier: str = ctx.identifier()
        name = "PROCESS"
        if identifier:
            name += f"_{identifier.upper()}"

        self.createStatement(name, ElementsTypes.NONE_ELEMENT, sensetivivty_list)
        self.findStruct()
        pass

    def exit(self, ctx: vhdlParser.Process_statementContext):
        self.removeLastStructPointer()
        pass
