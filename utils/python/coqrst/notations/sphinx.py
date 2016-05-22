"""A visitor for ANDTLR notation ASTs, producing Sphinx nodes.

Unlike the HTML visitor, this produces Sphinx-friendly nodes that can be used by
all backends. If you just want HTML output, use the HTML visitor.
"""

from .parsing import parse
from .TacticNotationsParser import TacticNotationsParser
from .TacticNotationsVisitor import TacticNotationsVisitor

from docutils import nodes
from sphinx import addnodes

class TacticNotationsToSphinxVisitor(TacticNotationsVisitor):
    def defaultResult(self):
        return []

    def aggregateResult(self, aggregate, nextResult):
        if nextResult:
            aggregate.extend(nextResult)
        return aggregate

    def visitRepeat(self, ctx:TacticNotationsParser.RepeatContext):
        # Uses inline nodes instead of subscript and superscript to ensure that
        # we get the right customization hooks at the LaTeX level
        wrapper = nodes.inline('', '', classes=['repeat-wrapper'])
        wrapper += nodes.inline('', '', *self.visitChildren(ctx), classes=["repeat"])

        repeat_marker = ctx.LGROUP().getText()[1]
        wrapper += nodes.inline(repeat_marker, repeat_marker, classes=['notation-sup'])

        separator = ctx.ATOM()
        if separator:
            sep = separator.getText()
            wrapper += nodes.inline(sep, sep, classes=['notation-sub'])

        return [wrapper]

    def visitCurlies(self, ctx:TacticNotationsParser.CurliesContext):
        sp = nodes.inline('', '', classes=["curlies"])
        sp += nodes.Text("{")
        sp.extend(self.visitChildren(ctx))
        sp += nodes.Text("}")
        return [sp]

    def visitAtomic(self, ctx:TacticNotationsParser.AtomicContext):
        atom = ctx.ATOM().getText()
        return [nodes.inline(atom, atom)]

    def visitHole(self, ctx:TacticNotationsParser.HoleContext):
        hole = ctx.ID().getText()
        token_name = hole[1:]
        node = nodes.inline(hole, token_name, classes=["hole"])
        return [addnodes.pending_xref(token_name, node, reftype='token', refdomain='std', reftarget=token_name)]

    def visitWhitespace(self, ctx:TacticNotationsParser.WhitespaceContext):
        return [nodes.Text(" ")]

def sphinxify(notation):
    """Translate notation into a Sphinx document tree"""
    vs = TacticNotationsToSphinxVisitor()
    return vs.visit(parse(notation))

def main():
    print(sphinxify("a := {+, b {+ c}}"))

if __name__ == '__main__':
    main()
