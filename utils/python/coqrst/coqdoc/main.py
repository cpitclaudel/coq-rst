"""
Use CoqDoc to highlight Coq snippets
====================================

Pygment's Coq parser isn't the best; instead, use coqdoc to highlight snippets.
Only works for full, syntactically valid sentences; on shorter snippets, coqdoc
swallows parts of the input.

Works by reparsing coqdoc's output into the output that Sphinx expects from a
lexer.
"""

import os
from tempfile import mkstemp
from subprocess import check_output

from bs4 import BeautifulSoup
from bs4.element import NavigableString

COQDOC_OPTIONS = ['--body-only', '--no-glob', '--no-index', '--no-externals',
                  '-s', '--html', '--stdout', '--utf8']

COQDOC_SYMBOLS = ["->", "<-", "<->", "=>", "<=", ">=", "<>", "~", "/\\", "\\/", "|-", "*"]
COQDOC_HEADER = "".join("(** remove printing {} *)".format(s) for s in COQDOC_SYMBOLS)

def coqdoc(coq_code, coqdoc_bin="coqdoc"):
    """Get the output of coqdoc on coq_code."""
    fd, filename = mkstemp(prefix="coqdoc-", suffix=".v")
    try:
        os.write(fd, COQDOC_HEADER.encode("utf-8"))
        os.write(fd, coq_code.encode("utf-8"))
        os.close(fd)
        return check_output([coqdoc_bin] + COQDOC_OPTIONS + [filename], timeout = 2).decode("utf-8")
    finally:
        os.remove(filename)

def is_whitespace_string(elem):
    return isinstance(elem, NavigableString) and elem.strip() == ""

def strip_soup(soup, pred):
    """Strip elements maching pred from front and tail of soup."""
    while soup.contents and pred(soup.contents[-1]):
        soup.contents.pop()

    skip = 0
    for elem in soup.contents:
        if not pred(elem):
            break
        skip += 1

    soup.contents[:] = soup.contents[skip:]

def lex(source):
    """Convert source into a stream of (css_classes, token_string)."""
    soup = BeautifulSoup(coqdoc(source))
    root = soup.find(class_='code')
    strip_soup(root, is_whitespace_string)
    for elem in root.children:
        if isinstance(elem, NavigableString):
            yield [], elem
        elif elem.name == "span":
            cls = "coqdoc-{}".format(elem['type'])
            yield [cls], elem.string
        elif elem.name == 'br':
            pass
        else:
            raise ValueError(elem)

def main():
    """Lex stdin (for testing purposes)"""
    import sys
    for classes, text in lex(sys.stdin.read()):
        print(repr(text) + "\t" ' '.join(classes))

if __name__ == '__main__':
    main()
