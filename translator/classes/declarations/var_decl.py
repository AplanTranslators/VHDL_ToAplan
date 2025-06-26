import typing
from AppModule.app.classes.declarations import Declaration
from AppModule.app.classes.protocols import BodyElement
from translator.classes.base_translator import BaseTranslator
from AppModule.app.classes.declarations import DeclTypes
from AppModule.app.classes.element_types import ElementsTypes
from AppModule.app.classes.protocols import Protocol
from antrl4_vhdl.vhdlParser import vhdlParser


class VarDeclTranslator(BaseTranslator):
    decl_index = None
    decl_unique = None
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def reset(self):
        self.decl_index = None
        self.decl_unique = None

    def translate(
        self,
        ctx: (
            vhdlParser.Signal_declarationContext
            | vhdlParser.Variable_declarationContext
        ),
    ) -> None:
        expression = None

        subtype_indication = ctx.subtype_indication()
        identifier_ctx = ctx.identifier_list().identifier(0)
        expression = ctx.expression()

        if subtype_indication:  # type: ignore
            subtype_indication: str = self.subtypeIndication_Translate(
                subtype_indication  # type: ignore
            )
            subtype_indication = DeclTypes.checkType(subtype_indication.lower(), [])  # type: ignore
            decl_type = subtype_indication
        else:
            ValueError("Not found type")

        new_decl = Declaration(
            decl_type,  # type: ignore
            identifier_ctx.getText(),  # type: ignore
            "",
            "",
            0,
            "",
            0,
            identifier_ctx.getSourceInterval(),  # type: ignore
            name_space_level=self.getLastNameSpaceLevel(),
        )
        if self.last_arch is not None:
            self.last_arch.declarations.addElement(new_decl)
        else:
            (
                self.decl_unique,
                self.decl_index,
            ) = self.design_unit.declarations.addElement(  # type: ignore
                new_decl
            )  #

        if not expression:
            return

        self.last_element_type = ElementsTypes.ASSIGN_ELEMENT
        self.last_operator = "="
        self._translator_ptr.translate(
            "expr",
            ctx,
        )

    def exit(
        self,
        ctx: (
            vhdlParser.Signal_declarationContext
            | vhdlParser.Variable_declarationContext
        ),
    ):

        if not ctx.expression():
            return

        (
            action_pointer,
            assign_name,
            source_interval,
            uniq_action,
        ) = self._translator_ptr.getTranslator("expr").exit()

        declaration = None
        if self.decl_index:
            declaration = self.design_unit.declarations.getElementByIndex(
                self.decl_index
            )

        self.findStruct()

        if self.last_struct is not None:
            if declaration:
                self.last_struct.elements.addElement(declaration)

            beh_index = self.last_struct.getLastBehaviorIndex()
            if beh_index is not None and assign_name:
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
            else:
                assign_b = "{}_B".format(action_pointer.getName(to_upper=True))
                struct_assign: Protocol = Protocol(
                    assign_b,
                    ctx.getSourceInterval(),
                    ElementsTypes.ASSIGN_OUT_OF_BLOCK_ELEMENT,
                )

                struct_assign.addBodyElement(
                    BodyElement(
                        assign_name, action_pointer, ElementsTypes.ACTION_ELEMENT
                    )
                )
                self.design_unit.out_of_block_elements.addElement(struct_assign)

        self.reset()
