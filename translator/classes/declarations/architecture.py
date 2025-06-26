import typing
from AppModule.app.classes.declarations import DeclTypes, Declaration
from AppModule.app.classes.design_unit import DesignUnit
from AppModule.app.classes.structure import Structure
from AppModule.app.classes.typedef import Typedef
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
        )  # type: ignore

        unique_identifier = f"{beh_identifier}_{self.design_unit.number}_t"
        typedef = Typedef(
            beh_identifier,
            unique_identifier,
            ctx.getSourceInterval(),
            self._program.file_path,
            DeclTypes.STRUCT_TYPE,
        )
        self.addTypedef(typedef)

        data_check_type = DeclTypes.STRUCT
   
        new_decl = Declaration(
            data_type=data_check_type,
            identifier=beh_identifier,
            size_expression=unique_identifier,
            source_interval=ctx.getSourceInterval(),
            name_space_level=self.design_unit.number,
        )

        (
            self.decl_unique,
            self.decl_index,
        ) = self.design_unit.declarations.addElement(new_decl)

        structure = Structure(
            beh_identifier.upper(),
            ctx.getSourceInterval(),
        )
        if self.design_unit.input_parametrs is not None:  # type: ignore
            structure.parametrs += self.design_unit.input_parametrs  # type: ignore
        structure.addProtocol(
            structure.getName(False),
            inside_the_task=self.inside_the_task,
        )

        self.design_unit.structures.addElement(structure)  # type: ignore
        self.structure_pointer_list.addElement(structure)
        self.last_arch = self.getLastTypedef()

    def exit(self, ctx: vhdlParser.Architecture_bodyContext):
        self.last_arch = None
