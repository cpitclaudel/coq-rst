"""Use CoqDoc to highlight Coq snippets"""

import os
from tempfile import mkstemp
from subprocess import check_output

from bs4 import BeautifulSoup
from bs4.element import NavigableString

COQDOC_OPTIONS = ['--body-only', '--no-glob', '--no-index', '--no-externals',
                  '-s', '--html', '--stdout', '--utf8']

def coqdoc(coq_code, coqdoc_bin="coqdoc"):
    fd, filename = mkstemp(prefix="coqdoc-", suffix=".v")
    try:
        os.write(fd, coq_code.encode("utf-8"))
        os.close(fd)
        return check_output([coqdoc_bin] + COQDOC_OPTIONS + [filename], timeout = 2).decode("utf-8")
    finally:
        os.remove(filename)

def is_string(elem):
    return isinstance(elem, NavigableString)

def strip_soup(soup, pred):
    while soup.contents and pred(soup.contents[-1]):
        soup.contents.pop()

    skip = 0
    for elem in soup.contents:
        if not pred(elem):
            break
        skip += 1

    soup.contents[:] = soup.contents[skip:]

def lex(source):
    soup = BeautifulSoup(coqdoc(source))
    root = soup.find(class_='code')
    strip_soup(root, is_string)
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
    import sys
    for classes, text in lex(sys.stdin.read()):
        print(repr(text) + "\t" ' '.join(classes))

if __name__ == '__main__':
    main()
