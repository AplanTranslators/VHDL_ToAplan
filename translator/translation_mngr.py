from antlr4 import CommonTokenStream, FileStream, ParseTreeWalker
from antrl4_vhdl.vhdlLexer import vhdlLexer
from antrl4_vhdl.vhdlParser import vhdlParser
from antlr4.Token import Token

from AppModule.app.translator.base_translator_mngr import BaseTranslationManager
from AppModule.app.program.program import Program
from AppModule.app.classes.design_unit_call import DesignUnitCall


class InputStream(object):
    __slots__ = ("name", "strdata", "_index", "data", "_size")

    def __init__(self, data: str):
        self.name = "<empty>"
        self.strdata = data
        self._loadString()

    def _loadString(self):
        self._index = 0
        self.data = [ord(c) for c in self.strdata]
        self._size = len(self.data)

    @property
    def index(self):
        return self._index

    @property
    def size(self):
        return self._size

    # Reset the stream so that it's in the same state it was
    #  when the object was created *except* the data array is not
    #  touched.
    #
    def reset(self):
        self._index = 0

    def consume(self):
        if self._index >= self._size:
            assert self.LA(1) == Token.EOF
            raise Exception("cannot consume EOF")
        self._index += 1

    def LA(self, offset: int):
        if offset == 0:
            return 0  # undefined
        if offset < 0:
            offset += 1  # e.g., translate LA(-1) to use offset=0
        pos = self._index + offset - 1
        if pos < 0 or pos >= self._size:  # invalid
            return Token.EOF
        return self.data[pos]

    def LT(self, offset: int):
        return self.LA(offset)

    # mark/release do nothing; we have entire buffer
    def mark(self):
        return -1

    def release(self, marker: int):
        pass

    # consume() ahead until p==_index; can't just set p=_index as we must
    # update line and column. If we seek backwards, just set p
    #
    def seek(self, _index: int):
        if _index <= self._index:
            self._index = _index  # just jump; don't update stream state (line, ...)
            return
        # seek forward
        self._index = min(_index, self._size)

    def getText(self, start: int, stop: int):
        if stop >= self._size:
            stop = self._size - 1
        if start >= self._size:
            return ""
        else:
            return self.strdata[start : stop + 1]

    def __str__(self):
        return self.strdata


class TranslationManager(BaseTranslationManager):
    file_name = None

    def setup(self, data, file_name):
        self.logger.info("Set up translator environment \n", color="bold_yellow")
        self.file_name = file_name
        lexer = vhdlLexer(InputStream(data))

        stream = CommonTokenStream(lexer)

        parser = vhdlParser(stream)

        self.tree = parser.design_file()

        self.walker = ParseTreeWalker()

    def translate(self, design_unit_call: DesignUnitCall | None = None):
        from listener.listener import VHDL2AplanListener

        self.logger.info("Translation process start...", color="bold_yellow")

        listener: VHDL2AplanListener = VHDL2AplanListener(
            self.file_name, design_unit_call
        )
        self.walker.walk(listener, self.tree)
        program = Program()
        self.logger.info(f"File tranlation process finished!", color="bold_yellow")
        self.logger.info(
            f"File {program.file_path}  tranlation process finished!",
            color="bold_purple",
        )
        self.logger.delimetr(color="blue")
        uniq_name = "ta"
        if listener.design_unit:
            uniq_name = listener.design_unit.ident_uniq_name

        # only for debug
        tree = listener.tree

        tree.mergeSelectedName()
        tree.extractDesignUnit()

        tree.printSubTree()

        return uniq_name
