"""An experimental visitor for ANDTLR notation ASTs, producing regular expressions."""

import re
from io import StringIO

from .parsing import parse
from .TacticNotationsParser import TacticNotationsParser
from .TacticNotationsVisitor import TacticNotationsVisitor

class TacticNotationsToRegexpVisitor(TacticNotationsVisitor):
    def __init__(self):
        self.buffer = StringIO()

    def visitRepeat(self, ctx:TacticNotationsParser.RepeatContext):
        separator = ctx.ATOM()
        repeat_marker = ctx.LGROUP().getText()[1]

        self.buffer.write("(")
        self.visitChildren(ctx)
        self.buffer.write(")")

        if repeat_marker in ["?", "*"]:
            self.buffer.write("?")
        elif repeat_marker in ["+", "*"]:
            self.buffer.write("(")
            self.buffer.write(r"\s*" + re.escape(separator.getText() if separator else " ") + r"\s*")
            self.visitChildren(ctx)
            self.buffer.write(")*")

    def visitCurlies(self, ctx:TacticNotationsParser.CurliesContext):
        self.buffer.write(r"\{")
        self.visitChildren(ctx)
        self.buffer.write(r"\}")

    def visitAtomic(self, ctx:TacticNotationsParser.AtomicContext):
        self.buffer.write(re.escape(ctx.ATOM().getText()))

    def visitHole(self, ctx:TacticNotationsParser.HoleContext):
        self.buffer.write("([^();. \n]+)") # FIXME could allow more things

    def visitWhitespace(self, ctx:TacticNotationsParser.WhitespaceContext):
        self.buffer.write(r"\s+")

def regexpify(notation):
    """Translate notation to a Python regular expression matching it"""
    vs = TacticNotationsToRegexpVisitor()
    vs.visit(parse(notation))
    return vs.buffer.getvalue()
