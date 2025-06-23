import typing
from AppModule.app.classes.design_unit import DesignUnit
from AppModule.app.classes.structure import Structure
from translator.classes.base_translator import BaseTranslator
from antrl4_vhdl.vhdlParser import vhdlParser


class ArchitectureBodyDeclTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(self, ctx: vhdlParser.Architecture_bodyContext) -> None:
        beh_identifier = ctx.identifier(0).getText()
        unit_identifier = ctx.identifier(1).getText()
        self.design_unit = self._program.design_units.findModuleByUniqIdentifier(
            unit_identifier
        )

        initial_name = self.design_unit.ident_uniq_name_upper + "_" + beh_identifier
        structure = Structure(
            initial_name,
            ctx.getSourceInterval(),
        )
        if self.design_unit.input_parametrs is not None:
            structure.parametrs += self.design_unit.input_parametrs
        structure.addProtocol(
            initial_name,
            inside_the_task=self.inside_the_task,
        )

        self.design_unit.structures.addElement(structure)
        self.structure_pointer_list.addElement(structure)

    def exit(self, ctx: vhdlParser.Architecture_bodyContext):
        pass


class ArchitectureDeclTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(self, ctx: vhdlParser.Architecture_declarative_partContext) -> None:
        pass

        # if not self.last_beh_name:
        #     raise ValueError("Unfound beh name")
