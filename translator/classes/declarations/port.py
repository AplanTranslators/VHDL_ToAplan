import typing
from antrl4_vhdl.vhdlParser import vhdlParser
from AppModule.app.classes.declarations import DeclType, Declaration
from translator.classes.base_translator import BaseTranslator

from AppModule.app.classes.element_types import ElementsTypes


class InterfacePortDeclTranslator(BaseTranslator):
    need_delete_type = False
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(self, ctx: vhdlParser.Interface_port_declarationContext) -> None:
        sub_type = self.subtypeIndication_Translate(ctx.subtype_indication())

        # data_check_type = DeclTypes.checkType(sub_type, [])

        self.decl_type_array.addElement(  # type: ignore
            DeclType(
                sub_type,
                "",
                0,
                self.getLastNameSpaceLevel(),
            )
        )
        self.need_delete_type = True

        # constant_expression = ctx.expression()
        # if constant_expression is None:
        #     return

        # self.last_element_type = ElementsTypes.ASSIGN_ELEMENT
        # self.last_operator = "="
        # self._translator_ptr.translate(
        #     "expr",
        #     ctx,
        # )

    def exit(self, ctx: vhdlParser.Interface_port_declarationContext) -> None:
        action_pointer = None
        # constant_expression = ctx.expression()
        # if constant_expression is not None:
        #     (
        #         action_pointer,
        #         assign_name,
        #         source_interval,
        #         uniq_action,
        #     ) = self._translator_ptr.getTranslator("expr").exit()

        signal_mode = self.signalMode_Translate(ctx.signal_mode())

        for element in ctx.identifier_list().identifier():
            port = Declaration(
                signal_mode,
                element.getText(),
                "",
                "",
                0,
                "",
                0,
                element.getSourceInterval(),
                name_space_level=self.getLastNameSpaceLevel(),
            )
            # if action_pointer:
            #     port.expression = assign_name
            #     port.action = action_pointer
            decl_unique, self.decl_index = self.design_unit.declarations.addElement(  # type: ignore
                port
            )

        if self.need_delete_type:
            self.decl_type_array.removeLastElement()  # type: ignore
            self.need_delete_type = False
