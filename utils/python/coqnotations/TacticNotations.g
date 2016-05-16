grammar TacticNotations;

// Terminals are not visited, so we add non-terminals for each terminal that
// needs rendering (in particular whitespace (kept in output) vs. WHITESPACE
// (discarded)).

top: blocks EOF;
blocks: block ((whitespace)? block)*;
block: atomic | hole | repeat | curlies;
repeat: LGROUP (ATOM)? WHITESPACE blocks (WHITESPACE)? RBRACE;
curlies: LBRACE (whitespace)? blocks (whitespace)? RBRACE;
whitespace: WHITESPACE;
atomic: ATOM;
hole: ID;

LGROUP: '{' [+*?];
LBRACE: '{';
RBRACE: '}';
ATOM: ~[@{} ]+;
ID: '@' [a-zA-Z0-9_]+;
WHITESPACE: ' '+;
