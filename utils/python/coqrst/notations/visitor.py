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
        sp = tags.span(__class="curlies")
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
