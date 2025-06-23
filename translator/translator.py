from typing import Literal, Tuple, overload

from AppModule.app.classes.case_stmt import CaseStmt
from AppModule.app.utils.counters import CounterTypes, Counters
from AppModule.app.classes.declarations import DeclTypeArray
from AppModule.app.classes.if_stmt import IfStmt
from AppModule.app.classes.loop_stmt import ForeverStmt, LoopStmt, WhileStmt
from AppModule.app.classes.design_unit_call import DesignUnitCall
from AppModule.app.classes.node import NodeArray
from AppModule.app.classes.parametrs import ParametrArray
from AppModule.app.classes.protocols import BodyElement
from AppModule.app.classes.structure import Structure, StructureArray
from AppModule.app.classes.design_unit import DesignUnit
from AppModule.app.classes.element_types import ElementsTypes
from AppModule.app.classes.tasks import TaskStmt
from translator.classes.declarations.entity import EntityDeclTranslator
from translator.classes.declarations.port import InterfacePortDeclTranslator
from translator.classes.declarations.architecture import (
    ArchitectureBodyDeclTranslator,
    ArchitectureDeclTranslator,
)
from translator.classes.declarations.block_decl import BlockDeclTranslator
from translator.classes.expressions.expression import ExpressionTranslator
from translator.classes.expressions.identifier import IdentifierTranslator
from translator.classes.expressions.literal import LiteralTranslator

TRANSLATOR_NAMES = Literal[
    "entity_decl",
    "int_port_decl",
    "arc_decl",
    "expr",
    "literal",
    "block_decl",
    "ident",
]


class Translator:
    counters = Counters()
    design_unit_call: DesignUnitCall | None = None
    _design_unit: DesignUnit | None = None
    _structure_pointer_list: StructureArray = StructureArray()
    _cache = {}
    decl_type_array: DeclTypeArray | None = DeclTypeArray()
    last_node_array: NodeArray | None = None
    last_element_type: ElementsTypes = ElementsTypes.NONE_ELEMENT
    last_operator: str | None = None

    @property
    def current_genvar_value(self) -> bool:
        return self._current_genvar_value

    @current_genvar_value.setter
    def current_genvar_value(self, value: Tuple[str, int] | None):
        self._current_genvar_value = value

    _translators: dict[str, type] = {
        "entity_decl": EntityDeclTranslator,
        "int_port_decl": InterfacePortDeclTranslator,
        "arc_decl": ArchitectureBodyDeclTranslator,
        "expr": ExpressionTranslator,
        "literal": LiteralTranslator,
        "block_decl": BlockDeclTranslator,
        "ident": IdentifierTranslator,
    }

    def __init__(self):
        pass

    def getTranslator(self, key: TRANSLATOR_NAMES):
        cls = self._selectTranlator(key)
        if key not in self._cache:
            self._cache[key] = cls(self)
        return self._cache[key]

    def _selectTranlator(self, name: TRANSLATOR_NAMES):
        if name not in self._translators:
            raise ValueError(f"Unknown translator name: {name}")
        return self._translators[name]

    def translate(self, trnslt_name: TRANSLATOR_NAMES, *args, **kwargs):
        translator = self.getTranslator(trnslt_name)
        return translator.translate(*args, **kwargs)

    def exit(self, trnslt_name: TRANSLATOR_NAMES, *args, **kwargs):
        translator = self.getTranslator(trnslt_name)
        return translator.exit(*args, **kwargs)

    def isInsideTheTask(self):
        structure: Structure | None = self._structure_pointer_list.getLastElement()
        if isinstance(structure, TaskStmt):
            return True

        return False

    def getProtocolParams(self):
        protocol_params = None
        if self.isInsideTheTask() == True:
            task = self._design_unit.tasks.getLastTask()
            if task is not None:
                protocol_params = task.parametrs
        return protocol_params

    def getLastNameSpaceLevel(self):
        struct: Structure | None = self._structure_pointer_list.getLastElement()
        if struct:
            return struct.number
        else:
            return self._design_unit.number

    def removeLastStructPointer(self):
        if len(self._structure_pointer_list) > 0:
            self._structure_pointer_list.removeElementByIndex(
                len(self._structure_pointer_list) - 1
            )
            # Counters_Object.decriese(CounterTypes.STRUCT_COUNTER)

    def createStatement(
        self,
        name,
        element_type: ElementsTypes,
        sensetive: str | None = None,
    ):
        counter_type: CounterTypes = self.counters.types.STRUCT_COUNTER
        sv_structure: Structure | None = self._structure_pointer_list.getLastElement()

        if sv_structure:
            protocol_params = self.getProtocolParams()
            beh_index = sv_structure.getLastBehaviorIndex()
            if beh_index is not None:
                if element_type == ElementsTypes.FOREVER_ELEMENT:
                    sv_structure.behavior[beh_index].addBodyElement(
                        BodyElement(
                            identifier="Sensetive({0}_{1}, {2})".format(
                                name,
                                self.counters.get(counter_type),
                                sensetive,
                            ),
                            element_type=ElementsTypes.PROTOCOL_ELEMENT,
                            parametrs=protocol_params,
                        )
                    )
                else:
                    sv_structure.behavior[beh_index].addBodyElement(
                        BodyElement(
                            identifier="{0}_{1}".format(
                                name,
                                self.counters.get(counter_type),
                            ),
                            element_type=ElementsTypes.PROTOCOL_ELEMENT,
                            parametrs=protocol_params,
                        )
                    )

            tmp: ParametrArray = ParametrArray()
            if isinstance(sv_structure, TaskStmt):
                inside_the_task = True
            else:
                inside_the_task = False
            if (inside_the_task) is False:
                if sv_structure.parametrs is not None:
                    tmp += sv_structure.parametrs
                if protocol_params is not None:
                    tmp += protocol_params
            else:
                tmp = protocol_params

            if element_type == ElementsTypes.CASE_STATEMENT_ELEMENT:
                struct = CaseStmt(
                    name,
                    (0, 0),
                )

            elif element_type == ElementsTypes.IF_STATEMENT_ELEMENT:
                struct = IfStmt(
                    name,
                    (0, 0),
                )
            elif element_type == ElementsTypes.FOREVER_ELEMENT:
                struct = ForeverStmt(
                    name,
                    (0, 0),
                )

            elif element_type == ElementsTypes.WHILE_ELEMENT:
                struct = WhileStmt(
                    name,
                    (0, 0),
                )

            elif element_type == ElementsTypes.LOOP_ELEMENT:
                struct = LoopStmt(
                    name,
                    (0, 0),
                )
            else:
                struct = Structure(
                    name,
                    (0, 0),
                    element_type,
                )

            struct.parametrs = tmp
            struct.inside_the_task = inside_the_task
            struct.addInitProtocol()

            sv_structure.behavior.append(struct)
            self._structure_pointer_list.addElement(struct)

    # def extractSensetive(self, ctx):
    #     res = ""
    #     for child in ctx.getChildren():
    #         if type(child) is SystemVerilogParser.Edge_identifierContext:
    #             index = child.getText().find("negedge")
    #             if index != -1:
    #                 res += "!"
    #         elif type(child) is Tree.TerminalNodeImpl:
    #             index = child.getText().find("or")
    #             if index != -1:
    #                 res += " || "
    #             index = child.getText().find("and")
    #             if index != -1:
    #                 res += " && "
    #         elif type(child) is SystemVerilogParser.IdentifierContext:
    #             packages = self._design_unit.packages_and_objects.getElementsIE(
    #                 include=ElementsTypes.PACKAGE_ELEMENT
    #             )
    #             res += self._design_unit.findAndChangeNamesToAgentAttrCall(
    #                 child.getText(), packages.getElements()
    #             )
    #         else:
    #             res += self.extractSensetive(child)
    #     return res
