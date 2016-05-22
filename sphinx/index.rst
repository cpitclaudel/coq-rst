===========================================
 An experiment in modernizing Coq's manual
===========================================

.. include:: preamble.rst

.. contents::
   :local:

Rationale
=========

Coq's documentation is a rather complex LaTeX document, making it hard to get
good HTML rendering (though the excellent *HeVeA* is doing an impressive job!),
and even harder to extract structured information from it (tactic signatures,
tactic documentation, lists of options, etc). In addition, tactic notations
using ellipses get somewhat hard to read in the presence of nesting:

.. raw:: html

   <p><span style="font-family:monospace">pattern</span> <span style="font-style:oblique">term</span><sub>1</sub> <span style="font-style:oblique">[</span><span style="font-family:monospace">at </span> <span style="font-style:oblique">num</span><sub>1</sub><sup>1</sup> … <span style="font-style:oblique">num</span><sub><span style="font-style:italic">n</span><sub>1</sub></sub><sup>1</sup><span style="font-style:oblique">]</span> <span style="font-family:monospace">,</span> …<span style="font-family:monospace">,</span> <span style="font-style:oblique">term</span><sub><span style="font-style:italic">m</span></sub> <span style="font-style:oblique">[</span><span style="font-family:monospace">at </span> <span style="font-style:oblique">num</span><sub>1</sub><sup><span style="font-style:italic">m</span></sup> … <span style="font-style:oblique">num</span><sub><span style="font-style:italic">n</span><sub><span style="font-style:italic">m</span></sub></sub><sup><span style="font-style:italic">m</span></sup><span style="font-style:oblique">]</span></p>

.. raw:: html

   <p><span style="font-family:monospace">fix </span><span style="font-style:oblique">ident</span><sub>1</sub><span style="font-family:monospace"> </span><span style="font-style:oblique">num</span><span style="font-family:monospace"> with ( </span><span style="font-style:oblique">ident</span><sub>2</sub><span style="font-family:monospace"> </span><span style="font-style:oblique">binder</span><sub>2</sub><span style="font-family:monospace"> </span><span style="font-family:monospace">…</span><span style="font-family:monospace"> </span><span style="font-style:oblique">binder</span><sub>2</sub><span style="font-family:monospace"> </span><span style="font-family:monospace"><span style="font-style:oblique">[</span></span><span style="font-family:monospace">{ struct </span><span style="font-style:oblique">ident</span>′<sub>2</sub><span style="font-family:monospace"> }</span><span style="font-family:monospace"><span style="font-style:oblique">]</span></span><span style="font-family:monospace"> :&nbsp;</span><span style="font-style:oblique">type</span><sub>2</sub><span style="font-family:monospace"> ) … ( </span><span style="font-style:oblique">ident</span><sub><span style="font-style:italic">n</span></sub><span style="font-family:monospace"> </span><span style="font-style:oblique">binder</span><sub><span style="font-style:italic">n</span></sub><span style="font-family:monospace"> </span><span style="font-family:monospace">…</span><span style="font-family:monospace"> </span><span style="font-style:oblique">binder</span><sub><span style="font-style:italic">n</span></sub><span style="font-family:monospace"> </span><span style="font-family:monospace"><span style="font-style:oblique">[</span></span><span style="font-family:monospace">{ struct </span><span style="font-style:oblique">ident</span>′<sub><span style="font-style:italic">n</span></sub><span style="font-family:monospace"> }</span><span style="font-family:monospace"><span style="font-style:oblique">]</span></span><span style="font-family:monospace"> :&nbsp;</span><span style="font-style:oblique">type</span><sub><span style="font-style:italic">n</span></sub><span style="font-family:monospace"> )</span></p>

This website
============

This website is a small experiment to see whether writing Coq documentation in
**reStructuredText** with *Sphinx* could make this better. It is **not** an
alternative to *CoqDoc*. This project includes:

A new syntax and rendering for tactic notations with repeats
------------------------------------------------------------

The proposal is to write the patterns above like this::

   pattern {+, @term {? at {+ @num}}}
   fix @ident @num with {+ (@ident {+ @binder} {? {struct @ident'}} : @type)}

and render them like this:

   :notation:`pattern {+, @term {? at {+ @num}}}`

   :notation:`fix @ident @num with {+ (@ident {+ @binder} {? {struct @ident'}} : @type)}`

(as a start, holes are currently hyperlinked to the corresponding grammar entries, when available.)

A Python version of ``coq-tex``
-------------------------------

Just like ``coq-tex``, but for Sphinx: it augments the AST of a Sphinx document
to include Coq's responses to certain queries. The queries are
syntax-highlighted by sending them to Coqdoc and parsing the result, and the
results are syntax-highlighted by parsing Coq 8.5's ANSI color codes.

.. coqtop:: all

   Check plus.

A partial Coq *domain* for Sphinx
---------------------------------

This includes:

- A parser and renderer for the simple notation language above:

  :notation:`pattern {+, @term {? at {+ @num}}}`

- Coq-specific directives (directives are custom *reStructuredText* blocks),
  covering examples of interaction with ``coqtop``, documentation of tactic
  notations, variants, errors, options, and examples:

  .. cmd:: Implicit Types {+ @ident} : @type.

- Basic support for typesetting inference rules in a semi-readable way, with
  great rendering in a web browser:

  .. inference:: Prod-Type

     \WTEG{T}{\Type(i)}
     \WTE{\Gamma::(x:T)}{U}{\Type(i)}
     --------------------------------
     \WTEG{\forall~x:T,U}{\Type(i)}

All the code used to build this website (and the `PDF manual
<http://web.mit.edu/cpitcla/www/coq-rst/Coq85.pdf>`_) is on `GitHub
<https://github.com/cpitclaudel/coq-rst>`_.

Three excerpts of Coq's manual, translated to *reStructuredText*.
-----------------------------------------------------------------

This gives a flavor of reStructuredText and its Coq-specific extensions (looking
at page sources), as well as a preview of what results might look like.

- The :doc:`tactics <tactics>` example shows many examples of tactic notations
  using the new pattern notation, plus examples of talking to ``coqtop``,
  “remarks”, and “notes” sections, errors and variants, etc.

- The :doc:`Typing rules of the CIC <cic>` example shows demonstrates math
  rendering (see :doc:`tricky-bits` for more examples)

- The :doc:`extended pattern matching <extended-pattern-matching>`,
  :doc:`universe polymorphism <universe-polymorphism>`, and :doc:`syntax
  extensions <syntax-extensions>` examples show the result of translating three full
  chapters of the manual (including formulas, tables, grammars, input-output
  with coqtop, etc.).

Each page has a link to its source; check it out!

I'm a Coq developer, what's in for me?
======================================

Transitioning the manual would make it:

- Easier to write and maintain: the input format is much simpler than LaTeX, and
  the proposed (regexp-style) tactic notation format is very simple. (for tricky
  cases, we can still fall back to explicit LaTeX). Coq-specific constructs make
  many things easier to write (such as grammars) and hyperlink.

- Easier to contribute to: the contents are more consistent, and the format is
  easier to learn that the current manual's macros (``\nelist`` etc.), which are
  very inconsistently used (search for ``\dots``, ``\ldots``, ``...``,
  and ``..`` in ``RefMan-tac.tex`` for examples).

- Easier to extend: reStructuredText directives are relatively simple Python
  functions (contrast with writing complex LaTeX macros).  For a simple example,
  see the source of the :doc:`CIC typing rules <cic>` example below, or the
  ``coqtop`` directive in the :doc:`tactics <tactics>` example (it does
  essentially the same as ``coq-tex``).  Some random ideas that would be
  relatively easy:

  - A “run this example in jsCoq” button.

  - Little pop-ups for describing patterns in tactic notations (currently. they
    are just hyperlinked to the corresponding grammar entries).

  - A script that imports documentation for ``TACTIC EXTEND`` patterns straight from
    source comments (*à la* ``autodoc``)

  - A link in each error pointing to the corresponding documentation

  - Small improvements: a glossary, new indices (for example, an index of
    examples), linkbacks in the reference list, etc.

- Easier to machine-read: it's virtually impossible to reliably extract tactic
  notations, options, and vernacs from the current manual, while it would be
  very easy to so in this format.

- Easier to transition: if we prefer another format later, it's much easier to
  transition to it from reStructuredText.

- More stable: every time a chapter is added, it currently breaks all links to
  later parts of the manual; for example, the addition of the “*Universe
  Polymorphism*” chapter in 8.5 broke links to the “*Micromega*” chapter
  (``ReferenceMannual024`` became ``ReferenceManual025``; see bug `#4742`_)

  .. _#4742: https://coq.inria.fr/bugs/show_bug.cgi?id=4742

- Prettier and more user-friendly (hopefully!)

Welcome to a tiny subset of Coq's documentation!
================================================

.. toctree::
   :maxdepth: 10

   tactics
   cic
   extended-pattern-matching
   universe-polymorphism
   syntax-extensions
   tricky-bits
   gallina-specification-language
   glossary

There's also an work-in-progress version of a `PDF manual <http://web.mit.edu/cpitcla/www/coq-rst/Coq85.pdf>`_.

Indices and tables
==================

* :ref:`genindex`
* :index:`cmdindex`
* :index:`tacindex`
* :index:`optindex`
* :index:`exnindex`
* :ref:`search`

.. No entries yet
  * :index:`thmindex`
