#lang brag

blocks: block ([WHITESPACE] block)*
block: ATOM | ID | box
box: LBRACE [ATOM] WHITESPACE blocks [WHITESPACE] RBRACE
