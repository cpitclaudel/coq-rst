==============================================
 A few examples of trickier syntax constructs
==============================================

Math
====

.. math::

   \sum_{k=1}^\infty \frac{1}{k^2} = \frac{\pi^2}{6}

It's also easy to define special environments when needed:

.. only:: html

   .. include:: preamble.rst

.. inference:: Prod-Type

   \WTEG{T}{\Type(i)}
   \WTE{\Gamma::(x:T)}{U}{\Type(i)}
   --------------------------------
   \WTEG{\forall~x:T,U}{\Type(i)}

Interaction with CoqTop
=======================

Done using a new directive, ``.. coqtop::``. It takes arguments saying what to
display (inputs, outputs, or both), whether to reset the environment (and
optionally whether to undo the commands of that block), highlights the input
with CoqDoc and the output by translating ANSI sequences produced by CoqTop.

.. coqtop:: reset

   Require Import Nat.

.. coqtop:: all

   Print sub.

.. coqtop:: all undo

   Definition a := 1.

.. coqtop:: all undo

   Definition a := 2.

Grammars
========

Sphinx has a construct for grammars, and it can cross-reference tokens between
grammars, too (:token:`curlies`). For example:

Parsing rules
-------------

.. productionlist:: example
   top        : `blocks` EOF
   blocks     : `block` ((`whitespace`)? `block`)*
   block      : `atomic` | `hole` | `repeat` | `curlies`
   repeat     : `LGROUP` (`ATOM`)? `WHITESPACE` `blocks` (`WHITESPACE`)? `RBRACE`
   curlies    : `LBRACE` (`whitespace`)? `blocks` (`whitespace`)? `RBRACE`
   whitespace : `WHITESPACE`
   atomic     : `ATOM`
   hole       : `ID`

Lexing rules
------------

.. productionlist:: example
   LGROUP     : { [+*?]
   LBRACE     : {
   RBRACE     : }
   ATOM       : ~[@{} ]+
   ID         : @ [a-zA-Z0-9_]+
   WHITESPACE : ( )+


Tables
======

reStructuredText support tables in three formats:

Emac's ``table-mode``:
----------------------

+----------+----------+----------+
| This     | is       | an       |
+==========+==========+==========+
| example  | of       | table    |
+----------+----------+          +
| an       | Emacs    |          |
+----------+----------+----------+

Lightweight tables:
-------------------

.. table::

   ===========  =====  ==
   This         is     an
   ===========  =====  ==
   example      of     a
   lightweight  table
   ===========  =====  ==

List tables
-----------

.. list-table::
   :header-rows: 1

   * - this
     - is
     - an

   * - example
     - of
     - a

   * - list
     - table
     -
