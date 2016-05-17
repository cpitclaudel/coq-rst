..

An experiment in modernizing Coq's manual
=========================================

**TL;DR: click the links on in the navigation bar (left).**

Rationale
---------

Coq's documentation is a rather complex LaTeX document, making it hard to get
good HTML rendering (though the excellent *HeVeA* is doing an impressive job!),
and even harder to extract structured information from it (tactic signatures,
tactic documentation, lists of options, etc). In addition, tactic notations
using ellipses get somewhat hard to read in the presence of nesting:

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

Just like ``coq-tex``, but for Sphinx: it augments the AST of a Sphinx document
to include Coq's responses to certain queries. The queries are
syntax-highlighted by sending them to Coqdoc and parsing the result, and the
results are syntax-highlighted by parsing Coq 8.5's ANSI color codes.

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

I'm a Coq developer, what's in for me?
--------------------------------------

Transitioning the manual would make it:

- Easier to write and maintain: the input format is much simpler than LaTeX, and
  the proposed (regexp-style) tactic notation format is much simpler than the
  current collection of LaTeX macros.

- Easier to contribute to: the contents are more consistent, and easier to copy
  from (contrast with the current manual's macros — ``\nelist`` etc. —, which are
  very inconsistently used anyway: search for ``\dots``, ``\ldots``, ``...``,
  and ``..`` in ``RefMan-tac.tex`` for example).

- Easier to extend: reStructuredText directives are relatively simple Python
  functions (contrast with writing LaTeX macros).  For a simple example, see the
  source of the *CIC typing rules* example below, or the ``coqtop`` directive in
  the tactics example (it does essentially the same as ``coq-tex``).  Some
  random ideas:

  - A “run this example in jsCoq” button.

  - Little pop-ups for describing holes in tactic notations.

  - A script that imports documentation for TACTIC EXTEND patterns straight from
    source comments (*à la* autodoc)

- Easier to machine-read: it's virtually impossible to reliably extract tactic
  notations, options, and vernacs from the current manual.

- Prettier and more user-friendly (hopefully!)

Welcome to a tiny subset of Coq's documentation!
------------------------------------------------

.. toctree::
   :maxdepth: 2

   tactics
   cic

Each page has a link to its source; check it out!

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
