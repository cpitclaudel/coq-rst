from dominate import tags

from .visitor import TacticNotationsToHTMLVisitor
from .TacticNotationsLexer import TacticNotationsLexer
from .TacticNotationsParser import TacticNotationsParser

from antlr4 import CommonTokenStream, InputStream

def parse(notation):
    lexer = TacticNotationsLexer(InputStream(notation))
    return TacticNotationsParser(CommonTokenStream(lexer)).top()

def render(tree):
    top = tags.span(_class='notation')
    with top:
        TacticNotationsToHTMLVisitor().visit(tree)
    return top

def substitute(notation):
    substitutions = [("@bindings_list", "{+ (@id := @val) }"),
                     ("@qualid_or_string", "@id|@string")]
    for (src, dst) in substitutions:
        notation = notation.replace(src, dst)
    return notation

def htmlize(notation):
    return render(parse(substitute(notation)))

def htmlize_str(notation):
    # ‘pretty=True’ introduces spurious spaces
    return htmlize(notation).render(pretty=False)

def htmlize_p(notation):
    with tags.p():
        htmlize(notation)
