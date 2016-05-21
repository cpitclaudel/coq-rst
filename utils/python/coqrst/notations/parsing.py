from .TacticNotationsLexer import TacticNotationsLexer
from .TacticNotationsParser import TacticNotationsParser

from antlr4 import CommonTokenStream, InputStream

def substitute(notation):
    substitutions = [("@bindings_list", "{+ (@id := @val) }"),
                     ("@qualid_or_string", "@id|@string")]
    for (src, dst) in substitutions:
        notation = notation.replace(src, dst)
    return notation

def parse(notation):
    substituted = substitute(notation)
    lexer = TacticNotationsLexer(InputStream(substituted))
    return TacticNotationsParser(CommonTokenStream(lexer)).top()
