from io import StringIO

from dominate import tags

from .TacticNotationsParser import TacticNotationsParser
from .TacticNotationsVisitor import TacticNotationsVisitor

class TacticNotationsToHTMLVisitor(TacticNotationsVisitor):
    def visitRepeat(self, ctx:TacticNotationsParser.RepeatContext):
        with tags.span(_class="repeat-wrapper"):
            with tags.span(_class="repeat"):
                self.visitChildren(ctx)
            repeat_marker = ctx.LGROUP().getText()[1]
            separator = ctx.ATOM()
            tags.sup(repeat_marker)
            if separator:
                tags.sub(separator.getText())

    def visitCurlies(self, ctx:TacticNotationsParser.CurliesContext):
        sp = tags.span(_class="curlies")
        sp.add("{")
        with sp:
            self.visitChildren(ctx)
        sp.add("}")

    def visitAtomic(self, ctx:TacticNotationsParser.AtomicContext):
        tags.span(ctx.ATOM().getText())

    def visitHole(self, ctx:TacticNotationsParser.HoleContext):
        tags.span(ctx.ID().getText()[1:], _class="hole")

    def visitWhitespace(self, ctx:TacticNotationsParser.WhitespaceContext):
        tags.span(" ")          # TODO: no need for a <span> here

class TacticNotationsToDotsVisitor(TacticNotationsVisitor):
    def __init__(self):
        self.buffer = StringIO()

    def visitRepeat(self, ctx:TacticNotationsParser.RepeatContext):
        separator = ctx.ATOM()
        self.visitChildren(ctx)
        if ctx.LGROUP().getText()[1] == "+":
            spacer = (separator + " " if separator else "")
            self.buffer.write(spacer + "…" + spacer)
            self.visitChildren(ctx)

    def visitCurlies(self, ctx:TacticNotationsParser.CurliesContext):
        self.buffer.write("{")
        self.visitChildren(ctx)
        self.buffer.write("}")

    def visitAtomic(self, ctx:TacticNotationsParser.AtomicContext):
        self.buffer.write(ctx.ATOM().getText())

    def visitHole(self, ctx:TacticNotationsParser.HoleContext):
        self.buffer.write("‘{}’".format(ctx.ID().getText()[1:]))

    def visitWhitespace(self, ctx:TacticNotationsParser.WhitespaceContext):
        self.buffer.write(" ")
