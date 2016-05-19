#!/usr/bin/env python3
import sys

import dominate
from dominate import tags

from .main import htmlize_p, regexpify

def main():
    doc = dominate.document(title="Coq Notations")

    with doc.head:
        tags.meta(charset="utf-8")
        tags.link(rel="stylesheet", href="../../sphinx/_static/notations.css")
        tags.link(href='https://fonts.googleapis.com/css?family=Ubuntu:400,700',
                  rel='stylesheet', type='text/css')
        tags.link(href='https://fonts.googleapis.com/css?family=Ubuntu+Mono:400,700',
                  rel='stylesheet', type='text/css')

    with doc:
        tags.attr(lang="en")

    with doc.body:
        tags.h2("How to read this page")
        intro = tags.div(_class="intro")
        intro.add_raw_string("""
          <p>Each line is one Coq <strong>tactic notation</strong>.
            <span class="notation"><span class="hole">Green italics</span></span> indicate holes to fill; the rest is fixed syntax.</p>
          <p>Boxes indicate <strong>repeated patterns</strong>.
            The top-right symbol indicates the number of repetitions:
              <span class="notation"><span class="repeat-wrapper"><span class="repeat">0 or 1</span><sup>?</sup></span>,
              <span class="notation"><span class="repeat-wrapper"><span class="repeat">one or more</span><sup>+</sup></span>, or
              <span class="notation"><span class="repeat-wrapper"><span class="repeat">any number of time</span><sup>*</sup></span>.
            The bottom symbol indicates the separator.</p>
          <p>For example,
              “<span class="notation">rewrite H</span>”,
              “<span class="notation">rewrite -> H</span>”, and
              “<span class="notation">rewrite H1, H2</span>”
            are all matches for
              “<span class="notation">rewrite <span class="repeat-wrapper"><span class="repeat">-&gt;</span><sup>?</sup></span> <span class="repeat-wrapper"><span class="repeat"><span class="hole">term</span></span><sup>+</sup><sub>,</sub></span></span>”.</p>
            <br/>""")

        tags.hr()
        htmlize_p("apply {+, @term with {+ (@id := @val) } } in {+, @hyp }")
        tags.hr()
        htmlize_p("Global Arguments qualid {+ @name%@scope}.")
        tags.hr()
        htmlize_p("{? simple} apply {+, @term {? with @bindings_list}} in @ident {? as @intro_pattern}")
        tags.hr()
        htmlize_p("set (@ident {+ @binder} := @term) in {+ @hyp}")
        tags.hr()
        htmlize_p("unfold {+, @qualid at {+, num}}")
        tags.hr()
        htmlize_p("generalize {+, @term at {+ @num} as @ident}")
        tags.hr()

        for line in sys.stdin:
            if "{" in line:
                htmlize_p(line)
                tags.hr()

    print(doc.render(pretty=False))

def regexps():
    import os, re
    for line in sys.stdin:
        line = line.strip()
        if "@" not in line and "{" not in line:
            continue
        r = re.compile(regexpify(line))
        print(">>", line)
        print("-"*80)
        for dirpath, _, filenames in os.walk("/build/coq-8.5/theories/"):
            for fn in filenames:
                if fn.endswith(".v"):
                    fulln = os.path.join(dirpath, fn)
                    with open(fulln) as source:
                        for m in r.finditer(source.read()):
                            print("{}:{}: {}".format(fulln, m.start(), m.group(0)))
        print("="*80 + "\n")

if __name__ == '__main__':
    main()
