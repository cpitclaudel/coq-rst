====================================
 The Gallina specification language
====================================

:Source: https://coq.inria.fr/refman/Reference-Manual003.html
:Converted by: Clément Pit-Claudel

This chapter describes Gallina, the specification language of Coq. It allows
developing mathematical theories and to prove specifications of programs. The
theories are built from axioms, hypotheses, parameters, lemmas, theorems and
definitions of constants, functions, predicates and sets. The syntax of logical
objects involved in theories is described in Section 1.2. The language of
commands, called *The Vernacular* is described in section1.3.

In Coq, logical objects are typed to ensure their logical correctness.  The
rules implemented by the typing algorithm are described in Chapter 4.


About the grammars in the manual
================================

Grammars are presented in Backus-Naur form (BNF). Terminal symbols are
set in black ``typewriter font``. In addition, there are special notations for
regular expressions.

An expression enclosed in square brackets ``[…]`` means at most one
occurrence of this expression (this corresponds to an optional
component).

The notation “``entry sep … sep entry``” stands for a non empty sequence
of expressions parsed by entry and separated by the literal “``sep``”.

Similarly, the notation “``entry … entry``” stands for a non empty
sequence of expressions parsed by the “``entry``” entry, without any
separator between.

At the end, the notation “``[entry sep … sep entry]``” stands for a
possibly empty sequence of expressions parsed by the “``entry``” entry,
separated by the literal “``sep``”.


Lexical conventions
===================

Blanks
  Space, newline and horizontal tabulation are considered as blanks.
  Blanks are ignored but they separate tokens.

Comments
  Comments in Coq are enclosed between ``(*`` and ``*)``, and can be nested.
  They can contain any character. However, string literals must be
  correctly closed. Comments are treated as blanks.

Identifiers and access identifiers
  Identifiers, written ident, are sequences of letters, digits, ``_`` and
  ``'``, that do not start with a digit or ``'``. That is, they are
  recognized by the following lexical class:

  .. productionlist:: coq
     first_letter      : a..z ∣ A..Z ∣ _ ∣ unicode-letter
     subsequent_letter : a..z ∣ A..Z ∣ 0..9 ∣ _ ∣ ' ∣ unicode-letter ∣ unicode-id-part
     ident             : `first_letter` [`subsequent_letter` … `subsequent_letter`]
     access_ident      : . `ident`

  All characters are meaningful. In particular, identifiers are case-
  sensitive. The entry ``unicode-letter`` non-exhaustively includes Latin,
  Greek, Gothic, Cyrillic, Arabic, Hebrew, Georgian, Hangul, Hiragana
  and Katakana characters, CJK ideographs, mathematical letter-like
  symbols, hyphens, non-breaking space, … The entry ``unicode-id-part`` non-
  exhaustively includes symbols for prime letters and subscripts.

  Access identifiers, written :token:`access_ident`, are identifiers prefixed by
  `.` (dot) without blank. They are used in the syntax of qualified
  identifiers.

Natural numbers and integers
  Numerals are sequences of digits. Integers are numerals optionally
  preceded by a minus sign.

  .. productionlist:: coq
     digit   : 0..9
     num     : `digit` … `digit`
     integer : [-] `num`

Strings
  Strings are delimited by ``"`` (double quote), and enclose a sequence of
  any characters different from ``"`` or the sequence ``""`` to denote the
  double quote character. In grammars, the entry for quoted strings is
  :production:`string`.

Keywords
  The following identifiers are reserved keywords, and cannot be
  employed otherwise::

    _ as at cofix else end exists exists2 fix for
    forall fun if IF in let match mod Prop return
    Set then Type using where with

Special tokens
  The following sequences of characters are special tokens::

    ! % & && ( () ) * + ++ , - -> . .( ..
    / /\ : :: :< := :> ; < <- <-> <: <= <> =
    => =_D > >-> >= ? ?= @ [ \/ ] ^ { | |-
    || } ~

  Lexical ambiguities are resolved according to the “longest match”
  rule: when a sequence of non alphanumerical characters can be
  decomposed into several different ways, then the first token is the
  longest possible one (among all tokens defined at this moment), and so
  on.

Terms
=====

Syntax of terms
---------------

The following grammars describe the basic syntax of the terms of the
*Calculus of Inductive Constructions* (also called Cic). The formal
presentation of Cic is given in Chapter 4. Extensions of this syntax
are given in chapter 2. How to customize the syntax is described in
Chapter 12.

.. productionlist:: coq
   term             : forall `binders` , `term`
                    : | fun `binders` => `term`
                    : | fix `fix_bodies`
                    : | cofix `cofix_bodies`
                    : | let `ident` [`binders`] [: `term`] := `term` in `term`
                    : | let fix `fix_body` in `term`
                    : | let cofix `cofix_body` in `term`
                    : | let ( [`name` , … , `name`] ) [`dep_ret_type`] := `term` in `term`
                    : | let ' `pattern` [in `term`] := `term` [`return_type`] in `term`
                    : | if `term` [`dep_ret_type`] then `term` else `term`
                    : | `term` : `term`
                    : | `term` <: `term`
                    : | `term` :>
                    : | `term` -> `term`
                    : | `term` arg … arg
                    : | @ `qualid` [`term` … `term`]
                    : | `term` % `ident`
                    : | match `match_item` , … , `match_item` [`return_type`] with
                    :   [[|] `equation` | … | `equation`] end
                    : | `qualid`
                    : | `sort`
                    : | num
                    : | _
                    : | ( `term` )
   arg              : `term`
                    : | ( `ident` := `term` )
   binders          : `binder` … `binder`
   binder           : `name`
                    : | ( `name` … `name` : `term` )
                    : | ( `name` [: `term`] := `term` )
   name             : `ident` | _
   qualid           : `ident` | `qualid` `access_ident`
   sort             : Prop | Set | Type
   fix_bodies       : `fix_body`
                    : | `fix_body` with `fix_body` with … with `fix_body` for `ident`
   cofix_bodies     : `cofix_body`
                    : | `cofix_body` with `cofix_body` with … with `cofix_body` for `ident`
   fix_body         : `ident` `binders` [annotation] [: `term`] := `term`
   cofix_body       : `ident` [`binders`] [: `term`] := `term`
   annotation       : { struct `ident` }
   match_item       : `term` [as `name`] [in `qualid` [`pattern` … `pattern`]]
   dep_ret_type     : [as `name`] `return_type`
   return_type      : return `term`
   equation         : `mult_pattern` | … | `mult_pattern` => `term`
   mult_pattern     : `pattern` , … , `pattern`
   pattern          : `qualid` `pattern` … `pattern`
                    : | @ `qualid` `pattern` … `pattern`
                    : | `pattern` as `ident`
                    : | `pattern` % `ident`
                    : | `qualid`
                    : | _
                    : | num
                    : | ( `or_pattern` , … , `or_pattern` )
   or_pattern       : `pattern` | … | `pattern`

(...)

The Vernacular
==============

.. productionlist:: coq
   sentence           : `assumption`
                      : | `definition`
                      : | `inductive`
                      : | `fixpoint`
                      : | `assertion` `proof`
   assumption         : `assumption_keyword` `assums`.
   assumption_keyword : Axiom | Conjecture
                      : | Parameter | Parameters
                      : | Variable | Variables
                      : | Hypothesis | Hypotheses
   assums             : `ident` … `ident` : `term`
                      : | ( `ident` … `ident` : `term` ) … ( `ident` … `ident` : `term` )
   definition         : [Local] Definition `ident` [`binders`] [: `term`] := `term` .
                      : | Let `ident` [`binders`] [: `term`] := `term` .
   inductive          : Inductive `ind_body` with … with `ind_body` .
                      : | CoInductive `ind_body` with … with `ind_body` .
   ind_body           : `ident` [`binders`] : `term` :=
                      : [[|] `ident` [`binders`] [:`term`] | … | `ident` [`binders`] [:`term`]]
   fixpoint           : Fixpoint `fix_body` with … with `fix_body` .
                      : | CoFixpoint `cofix_body` with … with `cofix_body` .
   assertion          : `assertion_keyword` `ident` [`binders`] : `term` .
   assertion_keyword  : Theorem | Lemma
                      : | Remark | Fact
                      : | Corollary | Proposition
                      : | Definition | Example
   proof              : Proof . … Qed .
                      : | Proof . … Defined .
                      : | Proof . … Admitted .

.. todo:: This use of … in this grammar is inconsistent

This grammar describes *The Vernacular* which is the language of
commands of Gallina. A sentence of the vernacular language, like in
many natural languages, begins with a capital letter and ends with a
dot.
