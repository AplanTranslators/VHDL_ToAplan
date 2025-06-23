import typing
from AppModule.app.classes.declarations import Declaration
from AppModule.app.classes.protocols import BodyElement
from translator.classes.base_translator import BaseTranslator
from AppModule.app.classes.declarations import DeclTypes
from AppModule.app.classes.element_types import ElementsTypes
from antrl4_vhdl.vhdlParser import vhdlParser


class SignalDeclTranslator(BaseTranslator):
    decl_index = None
    decl_unique = None

    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def reset(self):
        self.decl_index = None
        self.decl_unique = None

    def translate(self, ctx: vhdlParser.Signal_declarationContext) -> None:
        subtype_indication = ctx.subtype_indication()
        if subtype_indication:
            subtype_indication: str = self.subtypeIndication_Translate(
                subtype_indication
            )
            subtype_indication = DeclTypes.checkType(subtype_indication.lower(), [])
            decl_type = subtype_indication
        else:
            ValueError("Not found type")

        identifier_ctx = ctx.identifier_list().identifier(0)
        decl = Declaration(
            decl_type,
            identifier_ctx.getText(),
            "",
            "",
            0,
            "",
            0,
            identifier_ctx.getSourceInterval(),
            name_space_level=self.getLastNameSpaceLevel(),
        )
        (
            self.decl_unique,
            self.decl_index,
        ) = self.design_unit.declarations.addElement(decl)

        expression = ctx.expression()

        if not expression:
            return

        self.last_element_type = ElementsTypes.ASSIGN_ELEMENT
        self.last_operator = "="
        self._translator_ptr.translate(
            "expr",
            ctx,
        )

    def exit(self, ctx: vhdlParser.Interface_signal_declarationContext):

        expression = ctx.expression()

        if not expression:
            return
        (
            action_pointer,
            assign_name,
            source_interval,
            uniq_action,
        ) = self._translator_ptr.getTranslator("expr").exit()

        if self.decl_index is None:
            self.reset()
            return

        declaration = self.design_unit.declarations.getElementByIndex(self.decl_index)

        self.findStruct()

        if self.last_struct is not None:
            self.last_struct.elements.addElement(declaration)
            beh_index = self.last_struct.getLastBehaviorIndex()

            if beh_index is not None and assign_name is not None:
                self.last_struct.behavior[beh_index].addBodyElement(
                    BodyElement(
                        assign_name,
                        action_pointer,
                        ElementsTypes.ACTION_ELEMENT,
                    )
                )
        else:
            if self.decl_unique:
                declaration.expression = assign_name
                declaration.action = action_pointer

        self.reset()
