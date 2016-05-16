.. Coq documentation master file, created by
   sphinx-quickstart on Wed May 11 11:23:13 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

An experiment in modernizing Coq's manual
=========================================

Rationale
---------

Coq's documentation is a rather complex LaTeX document, making it hard to get good HTML rendering (though the excellent *HeVeA* is doing an impressive job!), and even harder to extract structured information from it (tactic signatures, tactic documentation, lists of options, etc). In addition, tactic notations using ellipses get somewhat hard to read in the presence of nesting:

.. raw:: html

   <p><span style="font-family:monospace">pattern</span> <span style="font-style:oblique">term</span><sub>1</sub> <span style="font-style:oblique">[</span><span style="font-family:monospace">at </span> <span style="font-style:oblique">num</span><sub>1</sub><sup>1</sup> … <span style="font-style:oblique">num</span><sub><span style="font-style:italic">n</span><sub>1</sub></sub><sup>1</sup><span style="font-style:oblique">]</span> <span style="font-family:monospace">,</span> …<span style="font-family:monospace">,</span> <span style="font-style:oblique">term</span><sub><span style="font-style:italic">m</span></sub> <span style="font-style:oblique">[</span><span style="font-family:monospace">at </span> <span style="font-style:oblique">num</span><sub>1</sub><sup><span style="font-style:italic">m</span></sup> … <span style="font-style:oblique">num</span><sub><span style="font-style:italic">n</span><sub><span style="font-style:italic">m</span></sub></sub><sup><span style="font-style:italic">m</span></sup><span style="font-style:oblique">]</span></p>

.. raw:: html

   <p><span style="font-family:monospace">fix </span><span style="font-style:oblique">ident</span><sub>1</sub><span style="font-family:monospace"> </span><span style="font-style:oblique">num</span><span style="font-family:monospace"> with ( </span><span style="font-style:oblique">ident</span><sub>2</sub><span style="font-family:monospace"> </span><span style="font-style:oblique">binder</span><sub>2</sub><span style="font-family:monospace"> </span><span style="font-family:monospace">…</span><span style="font-family:monospace"> </span><span style="font-style:oblique">binder</span><sub>2</sub><span style="font-family:monospace"> </span><span style="font-family:monospace"><span style="font-style:oblique">[</span></span><span style="font-family:monospace">{ struct </span><span style="font-style:oblique">ident</span>′<sub>2</sub><span style="font-family:monospace"> }</span><span style="font-family:monospace"><span style="font-style:oblique">]</span></span><span style="font-family:monospace"> :&nbsp;</span><span style="font-style:oblique">type</span><sub>2</sub><span style="font-family:monospace"> ) … ( </span><span style="font-style:oblique">ident</span><sub><span style="font-style:italic">n</span></sub><span style="font-family:monospace"> </span><span style="font-style:oblique">binder</span><sub><span style="font-style:italic">n</span></sub><span style="font-family:monospace"> </span><span style="font-family:monospace">…</span><span style="font-family:monospace"> </span><span style="font-style:oblique">binder</span><sub><span style="font-style:italic">n</span></sub><span style="font-family:monospace"> </span><span style="font-family:monospace"><span style="font-style:oblique">[</span></span><span style="font-family:monospace">{ struct </span><span style="font-style:oblique">ident</span>′<sub><span style="font-style:italic">n</span></sub><span style="font-family:monospace"> }</span><span style="font-family:monospace"><span style="font-style:oblique">]</span></span><span style="font-family:monospace"> :&nbsp;</span><span style="font-style:oblique">type</span><sub><span style="font-style:italic">n</span></sub><span style="font-family:monospace"> )</span></p>

This website is a small experiment to see whether writing Coq documentation in
**reStructuredText** with *Sphinx* could make this better. It is **not** an
alternative to *CoqDoc*. This project includes:

A new syntax and rendering for tactic notations with repeats
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The proposal is to write the patterns above like this::

    pattern {+, @term {? at {+ @num}}}
    fix @ident @num with {+ (@ident {+ @binder} {? {struct @ident'}} : @type)}

and render them like this:

:notation:`pattern {+, @term {? at {+ @num}}}`

:notation:`fix @ident @num with {+ (@ident {+ @binder} {? {struct @ident'}} : @type)}`

A Python version of ``coq-tex``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Just like ``coq-tex``, it augments the AST of a Sphinx document to include Coq's
responses to certain queries. The input is syntax-highlighted using *Pygments*,
and the output is syntax-highlighted by parsing Coq 8.5's **colored output**.

A partial Coq *domain* for Sphinx
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This includes:

- A parser and renderer for the simple notation language above
- Coq-specific directives (directives are custom *reStructuredText* blocks),
  covering examples of interaction with ``coqtop``, documentation of tactic
  notations, variants, errors, options, and examples
- Basic support for typesetting inference rules in a semi-readable way, with
  great rendering in a web browser

Two small sections of Coq's manual, translated to *reStructuredText*.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Welcome to a tiny subset of Coq's documentation!
------------------------------------------------

.. toctree::
   :maxdepth: 2

   tactics
   cic

Each page has a link to its source; check it out!

.. TODO

   Indices and tables
   ==================

   * :ref:`genindex`
   * :ref:`modindex`
   * :ref:`search`
