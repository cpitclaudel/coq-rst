========================================================
 Syntax extensions and interpretation scopes
========================================================

:Source: https://coq.inria.fr/refman/Reference-Manual014.html
:Converted by: Clément Pit-Claudel

In this chapter, we introduce advanced commands to modify the way Coq
parses and prints objects, i.e. the translations between the concrete
and internal representations of terms and commands. The main commands
are ``Notation`` and ``Infix`` which are described in section 12.1. It also
happens that the same symbolic notation is expected in different
contexts. To achieve this form of overloading, Coq offers a notion of
interpretation scope. This is described in Section 12.2.

.. note:: The commands ``Grammar``, ``Syntax`` and ``Distfix`` which were present
          for a while in Coq are no longer available from Coq version 8.0. The
          underlying AST structure is also no longer available. The
          functionalities of the command ``Syntactic Definition`` are still
          available, see Section 12.3.

.. coqtop:: none

   Set Printing Depth 50.

Notations
=========

Basic notations
---------------

A *notation* is a symbolic abbreviation denoting some term or term
pattern.

A typical notation is the use of the infix symbol ``/\`` to denote the
logical conjunction (and). Such a notation is declared by

.. coqtop:: in

   Notation "A /\ B" := (and A B).

The expression :g:`(and A B)` is the abbreviated term and the string ``"A /\ B"``
(called a *notation*) tells how it is symbolically written.

A notation is always surrounded by double quotes (excepted when the
abbreviation is a single identifier, see 12.3). The notation is
composed of *tokens* separated by spaces. Identifiers in the string
(such as ``A`` and ``B``) are the *parameters* of the notation. They must
occur at least once each in the denoted term. The other elements of
the string (such as ``/\``) are the *symbols*.

An identifier can be used as a symbol but it must be surrounded by
simple quotes to avoid the confusion with a parameter. Similarly,
every symbol of at least 3 characters and starting with a simple quote
must be quoted (then it starts by two single quotes). Here is an
example.

.. coqtop:: in

   Notation "'IF' c1 'then' c2 'else' c3" := (IF_then_else c1 c2 c3).

A notation binds a syntactic expression to a term. Unless the parser
and pretty-printer of Coq already know how to deal with the syntactic
expression (see 12.1.7), explicit precedences and associativity rules
have to be given.


Precedences and associativity
-----------------------------

Mixing different symbolic notations in a same text may cause serious
parsing ambiguity. To deal with the ambiguity of notations, Coq uses
precedence levels ranging from 0 to 100 (plus one extra level numbered
200) and associativity rules.

Consider for example the new notation

.. coqtop:: in

   Notation "A \/ B" := (or A B).

Clearly, an expression such as :g:`forall A:Prop, True /\ A \/ A \/ False`
is ambiguous. To tell the Coq parser how to interpret the
expression, a priority between the symbols ``/\`` and ``\/`` has to be
given. Assume for instance that we want conjunction to bind more than
disjunction. This is expressed by assigning a precedence level to each
notation, knowing that a lower level binds more than a higher level.
Hence the level for disjunction must be higher than the level for
conjunction.

Since connectives are the less tight articulation points of a text, it
is reasonable to choose levels not so far from the higher level which
is 100, for example 85 for disjunction and 80 for conjunction [#and_or_levels]_.

Similarly, an associativity is needed to decide whether :g:`True /\ False /\ False`
defaults to :g:`True /\ (False /\ False)` (right associativity) or to
:g:`(True /\ False) /\ False` (left associativity). We may even consider that the
expression is not well- formed and that parentheses are mandatory (this is a “no
associativity”) [#no_associativity]_. We don't know of a special convention of
the associativity of disjunction and conjunction, let's apply for instance a
right associativity (which is the choice of Coq).

Precedence levels and associativity rules of notations have to be
given between parentheses in a list of modifiers that the ``Notation``
command understands. Here is how the previous examples refine.

.. coqtop:: in

   Notation "A /\ B" := (and A B) (at level 80, right associativity).
   Notation "A \/ B" := (or A B) (at level 85, right associativity).

By default, a notation is considered non associative, but the
precedence level is mandatory (except for special cases whose level is
canonical). The level is either a number or the mention next level
whose meaning is obvious. The list of levels already assigned is on
Figure 3.1.

.. TODO I don't find it obvious -- CPC

Complex notations
-----------------

Notations can be made from arbitrarily complex symbols. One can for
instance define prefix notations.

.. coqtop:: in

   Notation "~ x" := (not x) (at level 75, right associativity).

One can also define notations for incomplete terms, with the hole
expected to be inferred at typing time.

.. coqtop:: in

   Notation "x = y" := (@eq _ x y) (at level 70, no associativity).

One can define *closed* notations whose both sides are symbols. In this case,
the default precedence level for inner subexpression is 200.

.. coqtop:: in

   Notation "( x , y )" := (@pair _ _ x y) (at level 0).

One can also define notations for binders.

.. coqtop:: in

   Notation "{ x : A | P }" := (sig A (fun x => P)) (at level 0).

In the last case though, there is a conflict with the notation for
type casts. This last notation, as shown by the command :cmd:`Print Grammar constr`
is at level 100. To avoid ``x : A`` being parsed as a type cast,
it is necessary to put x at a level below 100, typically 99. Hence, a
correct definition is

.. coqtop:: all

   Notation "{ x : A | P }" := (sig A (fun x => P)) (at level 0, x at level 99).

See the next section for more about factorization.

Simple factorization rules
--------------------------

Coq extensible parsing is performed by *Camlp5* which is essentially a
LL1 parser. Hence, some care has to be taken not to hide already
existing rules by new rules. Some simple left factorization work has
to be done. Here is an example.

.. coqtop:: all

   Notation "x < y" := (lt x y) (at level 70).
   Notation "x < y < z" := (x < y /\ y < z) (at level 70).

In order to factorize the left part of the rules, the subexpression
referred by y has to be at the same level in both rules. However the
default behavior puts y at the next level below 70 in the first rule
(no associativity is the default), and at the level 200 in the second
rule (level 200 is the default for inner expressions). To fix this, we
need to force the parsing level of y, as follows.

.. coqtop:: all

   Notation "x < y" := (lt x y) (at level 70).
   Notation "x < y < z" := (x < y /\ y < z) (at level 70, y at next level).

For the sake of factorization with Coq predefined rules, simple rules
have to be observed for notations starting with a symbol: e.g. rules
starting with “{” or “(” should be put at level 0. The list of Coq
predefined notations can be found in Chapter 3.

.. cmd:: Print Grammar constr.

   This command displays the current state of the Coq term parser.

.. cmd:: Print Grammar pattern.

   This displays the state of the subparser of patterns (the parser used in the
   grammar of the match with constructions).


Displaying symbolic notations
-----------------------------

The command ``Notation`` has an effect both on the Coq parser and on the
Coq printer. For example:

.. coqtop:: all

   Check (and True True).

However, printing, especially pretty-printing, requires more care than
parsing. We may want specific indentations, line breaks, alignment if
on several lines, etc.

The default printing of notations is very rudimentary. For printing a
notation, a *formatting box* is opened in such a way that if the
notation and its arguments cannot fit on a single line, a line break
is inserted before the symbols of the notation and the arguments on
the next lines are aligned with the argument on the first line.

A first, simple control that a user can have on the printing of a
notation is the insertion of spaces at some places of the notation.
This is performed by adding extra spaces between the symbols and
parameters: each extra space (other than the single space needed to
separate the components) is interpreted as a space to be inserted by
the printer. Here is an example showing how to add spaces around the
bar of the notation.

.. coqtop:: in

   Notation "{{ x : A | P }}" := (sig (fun x : A => P)) (at level 0, x at level 99).

.. coqtop:: all

   Check (sig (fun x : nat => x=x)).

The second, more powerful control on printing is by using the format
modifier. Here is an example

.. coqtop:: all

   Notation "'If' c1 'then' c2 'else' c3" := (IF_then_else c1 c2 c3)
   (at level 200, right associativity, format
   "'[v   ' 'If'  c1 '/' '[' 'then'  c2  ']' '/' '[' 'else'  c3 ']' ']'").

A *format* is an extension of the string denoting the notation with
the possible following elements delimited by single quotes:

- extra spaces are translated into simple spaces

- tokens of the form ``'/ '`` are translated into breaking point, in
  case a line break occurs, an indentation of the number of spaces after
  the “ ``/``” is applied (2 spaces in the given example)

- token of the form ``'//'`` force writing on a new line

- well-bracketed pairs of tokens of the form ``'[ '`` and ``']'`` are
  translated into printing boxes; in case a line break occurs, an extra
  indentation of the number of spaces given after the “ ``[``” is applied
  (4 spaces in the example)

- well-bracketed pairs of tokens of the form ``'[hv '`` and ``']'`` are
  translated into horizontal-orelse-vertical printing boxes; if the
  content of the box does not fit on a single line, then every breaking
  point forces a newline and an extra indentation of the number of
  spaces given after the “ ``[``” is applied at the beginning of each
  newline (3 spaces in the example)

- well-bracketed pairs of tokens of the form ``'[v '`` and ``']'`` are
  translated into vertical printing boxes; every breaking point forces a
  newline, even if the line is large enough to display the whole content
  of the box, and an extra indentation of the number of spaces given
  after the “``[``” is applied at the beginning of each newline

Thus, for the previous example, we get

.. coqtop:: all

   Check
    (IF_then_else (IF_then_else True False True)
      (IF_then_else True False True)
      (IF_then_else True False True)).

Notations do not survive the end of sections. No typing of the denoted
expression is performed at definition time. Type-checking is done only
at the time of use of the notation.

.. note:: Sometimes, a notation is expected only for the parser. To do
          so, the option ``only parsing`` is allowed in the list of modifiers
          of ``Notation``.

The Infix command
-----------------

The ``Infix`` command is a shortening for declaring notations of infix
symbols.

.. cmd:: Infix "@symbol" := @qualid ({+, @modifier}).

   This command is equivalent to

       :n:`Notation "x @symbol y" := (@qualid x y) ({+, @modifier}).`

   where ``x`` and ``y`` are fresh names distinct from ``qualid``. Here is an
   example.

   .. coqtop:: in

      Infix "/\" := and (at level 80, right associativity).

Reserving notations
-------------------

A given notation may be used in different contexts. Coq expects all
uses of the notation to be defined at the same precedence and with the
same associativity. To avoid giving the precedence and associativity
every time, it is possible to declare a parsing rule in advance
without giving its interpretation. Here is an example from the initial
state of Coq.

.. coqtop:: in

   Reserved Notation "x = y" (at level 70, no associativity).

Reserving a notation is also useful for simultaneously defining an
inductive type or a recursive constant and a notation for it.

.. note:: The notations mentioned on Figure 3.1 are reserved. Hence
          their precedence and associativity cannot be changed.

Simultaneous definition of terms and notations
----------------------------------------------

Thanks to reserved notations, the inductive, co-inductive, recursive
and corecursive definitions can benefit of customized notations. To do
this, insert a where notation clause after the definition of the
(co)inductive type or (co)recursive term (or after the definition of
each of them in case of mutual definitions). The exact syntax is given
on Figure 12.1. Here are examples:

.. coqtop:: in

   Inductive and (A B:Prop) : Prop := conj : A -> B -> A /\ B
   where "A /\ B" := (and A B).

   Fixpoint plus (n m:nat) {struct n} : nat :=
     match n with
     | O => m
     | S p => S (p+m)
     end
   where "n + m" := (plus n m).

Displaying informations about notations
---------------------------------------

.. opt:: Printing Notations

   To deactivate the printing of all notations, use the command
   ``Unset Printing Notations``. To reactivate it, use the command
   ``Set Printing Notations``.

   The default is to use notations for printing terms wherever possible.

.. seealso::

   :opt:`Printing All`
      To disable other elements in addition to notations.

Locating notations
------------------

.. cmd:: Locate @symbol

   To know to which notations a given symbol belongs to, use the command
   ``Locate symbol``, where symbol is any (composite) symbol surrounded by double
   quotes. To locate a particular notation, use a string where the variables of the
   notation are replaced by “_” and where possible single quotes inserted around
   identifiers or tokens starting with a single quote are dropped.

   .. coqtop:: all

      Locate "exists".
      Locate "exists _ .. _ , _".

   .. todo:: See also: Section 6.3.10.

Notations and simple binders
----------------------------

Notations can be defined for binders as in the example:

.. coqtop:: in

   Notation "{ x : A | P }" := (sig (fun x : A => P)) (at level 0).

The binding variables in the left-hand-side that occur as a parameter
of the notation naturally bind all their occurrences appearing in
their respective scope after instantiation of the parameters of the
notation.

Contrastingly, the binding variables that are not a parameter of the
notation do not capture the variables of same name that could appear
in their scope after instantiation of the notation. E.g., for the
notation

.. coqtop:: in

   Notation "'exists_different' n" := (exists p:nat, p<>n) (at level 200).

the next command fails because p does not bind in the instance of n.

.. coqtop:: all

   Fail Check (exists_different p).

.. note:: Binding variables must not necessarily be parsed using the ``ident``
          entry. For factorization purposes, they can be said to be parsed at
          another level (e.g. x in ``"{ x : A | P }"`` must be parsed at level 99
          to be factorized with the notation ``"{ A } + { B }"`` for which ``A`` can
          be any term). However, even if parsed as a term, this term must at the
          end be effectively a single identifier.


Notations with recursive patterns
---------------------------------

A mechanism is provided for declaring elementary notations with
recursive patterns. The basic example is:

.. coqtop:: all

   Notation "[ x ; .. ; y ]" := (cons x .. (cons y nil) ..).

On the right-hand side, an extra construction of the form ``.. t ..`` can
be used. Notice that ``..`` is part of the Coq syntax and it must not be
confused with the three-dots notation “``…``” used in this manual to denote
a sequence of arbitrary size.

On the left-hand side, the part “``x s .. s y``” of the notation parses
any number of time (but at least one time) a sequence of expressions
separated by the sequence of tokens ``s`` (in the example, ``s`` is just “``;``”).

In the right-hand side, the term enclosed within ``..`` must be a pattern
with two holes of the form :math:`φ([~]_E , [~]_I)` where the first hole is
occupied either by ``x`` or by ``y`` and the second hole is occupied by an
arbitrary term ``t`` called the terminating expression of the recursive
notation. The subterm ``.. φ(x,t) ..`` (or ``.. φ(y,t) ..``) must itself occur
at second position of the same pattern where the first hole is
occupied by the other variable, ``y`` or ``x``. Otherwise said, the right-hand
side must contain a subterm of the form either ``φ(x, .. φ(y,t) ..)`` or
``φ(y, .. φ(x,t) ..)``. The pattern ``φ`` is the *iterator* of the recursive
notation and, of course, the name ``x`` and ``y`` can be chosen arbitrarily.

The parsing phase produces a list of expressions which are used to
fill in order the first hole of the iterating pattern which is
repeatedly nested as many times as the length of the list, the second
hole being the nesting point. In the innermost occurrence of the
nested iterating pattern, the second hole is finally filled with the
terminating expression.

In the example above, the iterator :math:`φ([~]_E , [~]_I)` is :math:`cons [~]_E [~]_I`
and the terminating expression is ``nil``. Here are other examples:

.. coqtop:: in

   Notation "( x , y , .. , z )" := (pair .. (pair x y) .. z) (at level 0).

   Notation "[| t * ( x , y , .. , z ) ; ( a , b , .. , c )  * u |]" :=
     (pair (pair .. (pair (pair t x) (pair t y)) .. (pair t z))
           (pair .. (pair (pair a u) (pair b u)) .. (pair c u)))
     (t at level 39).

Notations with recursive patterns can be reserved like standard
notations, they can also be declared within interpretation scopes (see
section 12.2).


Notations with recursive patterns involving binders
---------------------------------------------------

Recursive notations can also be used with binders. The basic example
is:

.. coqtop:: all

   Notation "'exists' x .. y , p" := (ex (fun x => .. (ex (fun y => p)) ..))
     (at level 200, x binder, y binder, right associativity).

The principle is the same as in Section 12.1.12 except that in the
iterator :math:`φ([~]_E , [~]_I)`, the first hole is a placeholder occurring
at the position of the binding variable of a ``fun`` or a ``forall``.

To specify that the part “``x .. y``” of the notation parses a sequence of
binders, ``x`` and ``y`` must be marked as binder in the list of modifiers of
the notation. Then, the list of binders produced at the parsing phase
are used to fill in the first hole of the iterating pattern which is
repeatedly nested as many times as the number of binders generated. If
ever the generalization operator ``'`` (see Section 2.7.19) is used in
the binding list, the added binders are taken into account too.

Binders parsing exist in two flavors. If ``x`` and ``y`` are marked as binder,
then a sequence such as :g:`a b c : T` will be accepted and interpreted as
the sequence of binders :g:`(a:T) (b:T) (c:T)`. For instance, in the
notation above, the syntax :g:`exists a b : nat, a = b` is provided.

The variables ``x`` and ``y`` can also be marked as closed binder in which
case only well-bracketed binders of the form :g:`(a b c:T)` or :g:`{a b c:T}`
etc. are accepted.

With closed binders, the recursive sequence in the left-hand side can
be of the general form ``x s .. s y`` where ``s`` is an arbitrary sequence of
tokens. With open binders though, ``s`` has to be empty. Here is an
example of recursive notation with closed binders:

.. coqtop:: in

   Notation "'mylet' f x .. y :=  t 'in' u":=
     (let f := fun x => .. (fun y => t) .. in u)
     (x closed binder, y closed binder, at level 200, right associativity).

Summary
-------

Syntax of notations
~~~~~~~~~~~~~~~~~~~

The different syntactic variants of the command Notation are given on the
following figure. The optional :token:`scope` is described in the Section 12.2.

.. productionlist:: coq
   notation      : [Local] Notation `string` := `term` [`modifiers`] [: `scope`].
                 : | [Local] Infix `string` := `qualid` [`modifiers`] [: `scope`].
                 : | [Local] Reserved Notation `string` [`modifiers`] .
                 : | Inductive `ind_body` [`decl_notation`] with … with `ind_body` [`decl_notation`].
                 : | CoInductive `ind_body` [`decl_notation`] with … with `ind_body` [`decl_notation`].
                 : | Fixpoint `fix_body` [`decl_notation`] with … with `fix_body` [`decl_notation`].
                 : | CoFixpoint `cofix_body` [`decl_notation`] with … with `cofix_body` [`decl_notation`].
   decl_notation : [where `string` := `term` [: `scope`] and … and `string` := `term` [: `scope`]].
   modifiers     : `ident` , … , `ident` at level natural
                 : | `ident` , … , `ident` at next level
                 : | at level natural
                 : | left associativity
                 : | right associativity
                 : | no associativity
                 : | `ident` ident
                 : | `ident` binder
                 : | `ident` closed binder
                 : | `ident` global
                 : | `ident` bigint
                 : | only parsing
                 : | format `string`

.. note:: No typing of the denoted expression is performed at definition
          time. Type-checking is done only at the time of use of the notation.

.. note:: Many examples of Notation may be found in the files composing
          the initial state of Coq (see directory :file:`$COQLIB/theories/Init`).

.. note:: The notation ``"{ x }"`` has a special status in such a way that
          complex notations of the form ``"x + { y }"`` or ``"x * { y }"`` can be
          nested with correct precedences. Especially, every notation involving
          a pattern of the form ``"{ x }"`` is parsed as a notation where the
          pattern ``"{ x }"`` has been simply replaced by ``"x"`` and the curly
          brackets are parsed separately. E.g. ``"y + { z }"`` is not parsed as a
          term of the given form but as a term of the form ``"y + z"`` where ``z``
          has been parsed using the rule parsing ``"{ x }"``. Especially, level
          and precedences for a rule including patterns of the form ``"{ x }"``
          are relative not to the textual notation but to the notation where the
          curly brackets have been removed (e.g. the level and the associativity
          given to some notation, say ``"{ y } & { z }"`` in fact applies to the
          underlying ``"{ x }"``\-free rule which is ``"y & z"``).

Persistence of notations
~~~~~~~~~~~~~~~~~~~~~~~~

Notations do not survive the end of sections.

.. cmd:: Local Notation @notation

   Notations survive modules unless the command ``Local Notation`` is used instead
   of ``Notation``.

Interpretation scopes
=====================

An *interpretation scope* is a set of notations for terms with their
interpretation. Interpretation scopes provides with a weak, purely
syntactical form of notations overloading: a same notation, for
instance the infix symbol ``+`` can be used to denote distinct
definitions of an additive operator. Depending on which interpretation
scopes is currently open, the interpretation is different.
Interpretation scopes can include an interpretation for numerals and
strings. However, this is only made possible at the Objective Caml
level.

See Figure 12.1 for the syntax of notations including the possibility
to declare them in a given scope. Here is a typical example which
declares the notation for conjunction in the scope ``type_scope``.

.. coqdoc::

   Notation "A /\ B" := (and A B) : type_scope.

.. note:: A notation not defined in a scope is called a *lonely*
          notation.

Global interpretation rules for notations
-----------------------------------------

At any time, the interpretation of a notation for term is done within
a *stack* of interpretation scopes and lonely notations. In case a
notation has several interpretations, the actual interpretation is the
one defined by (or in) the more recently declared (or open) lonely
notation (or interpretation scope) which defines this notation.
Typically if a given notation is defined in some scope ``scope`` but has
also an interpretation not assigned to a scope, then, if ``scope`` is open
before the lonely interpretation is declared, then the lonely
interpretation is used (and this is the case even if the
interpretation of the notation in scope is given after the lonely
interpretation: otherwise said, only the order of lonely
interpretations and opening of scopes matters, and not the declaration
of interpretations within a scope).

The initial state of Coq declares three interpretation scopes and no
lonely notations. These scopes, in opening order, are ``core_scope``,
``type_scope`` and ``nat_scope``.

.. cmd:: Open Scope @scope

   The command to add a scope to the interpretation scope stack is
   :n:`Open Scope @scope`.

.. cmd:: Close Scope @scope

   It is also possible to remove a scope from the interpretation scope
   stack by using the command :n:`Close Scope @scope`.

   Notice that this command does not only cancel the last :n:`Open Scope @scope`
   but all the invocation of it.

.. note:: ``Open Scope`` and ``Close Scope`` do not survive the end of sections
          where they occur. When defined outside of a section, they are exported
          to the modules that import the module where they occur.

.. cmd:: Local Open Scope @scope.
         Local Close Scope @scope.

   These variants are not exported to the modules that import the module where
   they occur, even if outside a section.

.. cmd:: Global Open Scope @scope.
         Global Close Scope @scope.

   These variants survive sections. They behave as if Global were absent when
   not inside a section.

Local interpretation rules for notations
----------------------------------------

In addition to the global rules of interpretation of notations, some
ways to change the interpretation of subterms are available.

Local opening of an interpretation scope
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is possible to locally extend the interpretation scope stack using the syntax
:g:`(term)%key` (or simply :g:`term%key` for atomic terms), where key is a
special identifier called *delimiting key* and bound to a given scope.

In such a situation, the term term, and all its subterms, are
interpreted in the scope stack extended with the scope bound tokey.

.. cmd:: Delimit Scope @scope with @ident

   To bind a delimiting key to a scope, use the command
   :n:`Delimit Scope @scope with @ident`

.. cmd:: Undelimit Scope @scope

   To remove a delimiting key of a scope, use the command
   :n:`Undelimit Scope @scope`

Binding arguments of a constant to an interpretation scope
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. cmd:: Arguments @qualid {+ @name%@scope}

   It is possible to set in advance that some arguments of a given constant have
   to be interpreted in a given scope. The command is
   :n:`Arguments @qualid {+ @name%@scope}` where the list is the list of the
   arguments of ``qualid`` eventually annotated with their ``scope``. Grouping
   round parentheses can be used to decorate multiple arguments with the same
   scope. ``scope`` can be either a scope name or its delimiting key. For
   example the following command puts the first two arguments of :g:`plus_fct`
   in the scope delimited by the key ``F`` (``Rfun_scope``) and the last
   argument in the scope delimited by the key ``R`` (``R_scope``).

   .. coqtop:: in

      Arguments plus_fct (f1 f2)%F x%R.

   The ``Arguments`` command accepts scopes decoration to all grouping
   parentheses. In the following example arguments A and B are marked as
   maximally inserted implicit arguments and are put into the type_scope scope.

   .. coqtop:: in

      Arguments respectful {A B}%type (R R')%signature _ _.

   When interpreting a term, if some of the arguments of qualid are built
   from a notation, then this notation is interpreted in the scope stack
   extended by the scope bound (if any) to this argument. The effect of
   the scope is limited to the argument itself. It does not propagate to
   subterms but the subterms that, after interpretation of the notation,
   turn to be themselves arguments of a reference are interpreted
   accordingly to the arguments scopes bound to this reference.

.. cmd:: Arguments @qualid : clear scopes

   Arguments scopes can be cleared with :n:`Arguments @qualid : clear scopes`.

.. cmdv:: Global Arguments @qualid {+ @name%@scope}

   This behaves like :n:`Arguments qualid {+ @name%@scope}` but survives when a
   section is closed instead of stopping working at section closing. Without the
   ``Global`` modifier, the effect of the command stops when the section it belongs
   to ends.

.. cmdv:: Local Arguments @qualid {+ @name%@scope}

   This behaves like :n:`Arguments @qualid {+ @name%@scope}` but does not
   survive modules and files. Without the ``Local`` modifier, the effect of the
   command is visible from within other modules or files.

.. seealso::

   :cmd:`About @qualid`
     The command to show the scopes bound to the arguments of a
     function is described in Section 2.

Binding types of arguments to an interpretation scope
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. cmd:: Bind Scope @scope with @qualid

   When an interpretation scope is naturally associated to a type (e.g.  the
   scope of operations on the natural numbers), it may be convenient to bind it
   to this type. When a scope ``scope`` is bound to a type type, any new function
   defined later on gets its arguments of type type interpreted by default in
   scope scope (this default behavior can however be overwritten by explicitly
   using the command ``Arguments``).

   Whether the argument of a function has some type ``type`` is determined
   statically. For instance, if f is a polymorphic function of type :g:`forall
   X:Type, X -> X` and type :g:`t` is bound to a scope ``scope``, then :g:`a` of
   type :g:`t` in :g:`f t a` is not recognized as an argument to be interpreted
   in scope ``scope``.

   Any global reference can be bound by default to an interpretation
   scope; the command to do it is :n:`Bind Scope @scope with @qualid`

   .. coqtop:: in

      Parameter U : Set.
      Bind Scope U_scope with U.
      Parameter Uplus : U -> U -> U.
      Parameter P : forall T:Set, T -> U -> Prop.
      Parameter f : forall T:Set, T -> U.
      Infix "+" := Uplus : U_scope.
      Unset Printing Notations.
      (* Define + on the nat as the default for + *)
      Open Scope nat_scope.

   .. coqtop:: all

      Check (fun x y1 y2 z t => P _ (x + t) ((f _ (y1 + y2) + z))).

   .. note:: The scope ``type_scope`` has also a local effect on
             interpretation. See the next section.

.. seealso::

   :cmd:`About`
     The command to show the scopes bound to the arguments of a
     function is described in Section 2.

The ``type_scope`` interpretation scope
---------------------------------------

The scope ``type_scope`` has a special status. It is a primitive
interpretation scope which is temporarily activated each time a
subterm of an expression is expected to be a type. This includes goals
and statements, types of binders, domain and codomain of implication,
codomain of products, and more generally any type argument of a
declared or defined constant.

Interpretation scopes used in the standard library of Coq
---------------------------------------------------------

We give an overview of the scopes used in the standard library of Coq.
For a complete list of notations in each scope, use the commands Print
Scopes or Print Scope scope.

``type_scope``
  This includes infix * for product types and infix + for sum types. It
  is delimited by key ``type``.

``nat_scope``
  This includes the standard arithmetical operators and relations on
  type nat. Positive numerals in this scope are mapped to their
  canonical representent built from :g:`O` and :g:`S`. The scope is delimited by
  key ``nat``.

``N_scope``
  This includes the standard arithmetical operators and relations on
  type :g:`N` (binary natural numbers). It is delimited by key ``N`` and comes
  with an interpretation for numerals as closed term of type :g:`Z`.

``Z_scope``
  This includes the standard arithmetical operators and relations on
  type :g:`Z` (binary integer numbers). It is delimited by key ``Z`` and comes
  with an interpretation for numerals as closed term of type :g:`Z`.

``positive_scope``
  This includes the standard arithmetical operators and relations on
  type :g:`positive` (binary strictly positive numbers). It is delimited by
  key ``positive`` and comes with an interpretation for numerals as closed
  term of type :g:`positive`.

``Q_scope``
  This includes the standard arithmetical operators and relations on
  type :g:`Q` (rational numbers defined as fractions of an integer and a
  strictly positive integer modulo the equality of the numerator-
  denominator cross-product). As for numerals, only 0 and 1 have an
  interpretation in scope ``Q_scope`` (their interpretations are 0/1 and 1/1
  respectively).

``Qc_scope``
  This includes the standard arithmetical operators and relations on the
  type :g:`Qc` of rational numbers defined as the type of irreducible
  fractions of an integer and a strictly positive integer.

``real_scope``
  This includes the standard arithmetical operators and relations on
  type :g:`R` (axiomatic real numbers). It is delimited by key ``R`` and comes
  with an interpretation for numerals as term of type :g:`R`. The
  interpretation is based on the binary decomposition. The numeral 2 is
  represented by 1+1. The interpretation :math:`φ(n)` of an odd positive
  numerals greater n than 3 is :math:`1+(1+1)*φ((n−1)/2)`. The interpretation
  :math:`φ(n)` of an even positive numerals greater :g:`n` than :g:`4` is :math:`(1+1)*φ(n/2)`.
  Negative numerals are represented as the opposite of the
  interpretation of their absolute value. E.g. the syntactic object :math:`-11`
  is interpreted as :math:`-(1+(1+1)*((1+1)*(1+(1+1))))` where the unit :g:`1` and
  all the operations are those of :g:`R`.

``bool_scope``
  This includes notations for the boolean operators. It is delimited by
  key ``bool``.

``list_scope``
  This includes notations for the list operators. It is delimited by key
  ``list``.

``core_scope``
  This includes the notation for pairs. It is delimited by key ``core``.

``string_scope``
  This includes notation for strings as elements of the type string.
  Special characters and escaping follow Coq conventions on strings (see
  Section 1.1). Especially, there is no convention to visualize non
  printable characters of a string. The file :file:`String.v` shows an example
  that contains quotes, a newline and a beep (i.e. the ascii character
  of code 7).

``char_scope``
  This includes interpretation for all strings of the form ``"c"``
  where :g:`c` is an ascii character, or of the form ``"nnn"`` where nnn is
  a three-digits number (possibly with leading 0's), or of the form
  ``""""``. Their respective denotations are the ascii code of c, the
  decimal ascii code nnn, or the ascii code of the character ``"`` (i.e.
  the ascii code 34), all of them being represented in the type :g:`ascii`.


Displaying informations about scopes
------------------------------------

.. cmd:: Print Visibility

   This displays the current stack of notations in scopes and lonely
   notations that is used to interpret a notation. The top of the stack
   is displayed last. Notations in scopes whose interpretation is hidden
   by the same notation in a more recently open scope are not displayed.
   Hence each notation is displayed only once.

.. cmdv:: Print Visibility scope

   This displays the current stack of notations in scopes and lonely
   notations assuming that scope is pushed on top of the stack. This is
   useful to know how a subterm locally occurring in the scope ofscope is
   interpreted.

.. cmdv:: Print Scope scope

   This displays all the notations defined in interpretation scopescope.
   It also displays the delimiting key if any and the class to which the
   scope is bound, if any.

.. cmdv:: Print Scopes

   This displays all the notations, delimiting keys and corresponding
   class of all the existing interpretation scopes. It also displays the
   lonely notations.

Abbreviations
=============

.. cmd:: {? Local} Notation @ident {+ @ident} := @term {? (only parsing)}.

   An *abbreviation* is a name, possibly applied to arguments, that
   denotes a (presumably) more complex expression. Here are examples:

   .. coqtop:: none

      Require Import List.
      Require Import Relations.
      Set Printing Notations.

   .. coqtop:: in

      Notation Nlist := (list nat).

   .. coqtop:: all

      Check 1 :: 2 :: 3 :: nil.

   .. coqtop:: in

      Notation reflexive R := (forall x, R x x).

   .. coqtop:: all

      Check forall A:Prop, A <-> A.
      Check reflexive iff.

   An abbreviation expects no precedence nor associativity, since it
   follows the usual syntax of application. Abbreviations are used as
   much as possible by the Coq printers unless the modifier ``(only
   parsing)`` is given.

   Abbreviations are bound to an absolute name as an ordinary definition
   is, and they can be referred by qualified names too.

   Abbreviations are syntactic in the sense that they are bound to
   expressions which are not typed at the time of the definition of the
   abbreviation but at the time it is used. Especially, abbreviations can
   be bound to terms with holes (i.e. with “``_``”). For example:

   .. coqtop:: none reset

      Set Strict Implicit.
      Set Printing Depth 50.

   .. coqtop:: in

      Definition explicit_id (A:Set) (a:A) := a.
      Notation id := (explicit_id _).

   .. coqtop:: all

      Check (id 0).

   Abbreviations do not survive the end of sections. No typing of the
   denoted expression is performed at definition time. Type-checking is
   done only at the time of use of the abbreviation.

Tactic Notations
================

Tactic notations allow to customize the syntax of the tactics of the
tactic language [#tacn]_. Tactic notations obey the following syntax:

.. productionlist:: coq
   tacn                 : [Local] Tactic Notation [`tactic_level`] [`prod_item` … `prod_item`] := `tactic`.
   prod_item            : `string` | `tactic_argument_type`(`ident`)
   tactic_level         : (at level `natural`)
   tactic_argument_type : ident | simple_intropattern | reference
                        : | hyp | hyp_list | ne_hyp_list
                        : | constr | uconstr | constr_list | ne_constr_list
                        : | integer | integer_list | ne_integer_list
                        : | int_or_var | int_or_var_list | ne_int_or_var_list
                        : | tactic | tactic0 | tactic1 | tactic2 | tactic3
                        : | tactic4 | tactic5

.. cmd:: {? Local} Tactic Notation {? (at level @level)} {+ @prod_item} := @tactic.

   A tactic notation extends the parser and pretty-printer of tactics with a new
   rule made of the list of production items. It then evaluates into the
   tactic expression ``tactic``. For simple tactics, it is recommended to use
   a terminal symbol, i.e. a string, for the first production item. The
   tactic level indicates the parsing precedence of the tactic notation.
   This information is particularly relevant for notations of tacticals.
   Levels 0 to 5 are available (default is 0).

   .. cmd:: Print Grammar tactic

      To know the parsing precedences of the existing tacticals, use the command
      ``Print Grammar tactic``.

   Each type of tactic argument has a specific semantic regarding how it
   is parsed and how it is interpreted. The semantic is described in the
   following table. The last command gives examples of tactics which use
   the corresponding kind of argument.

   .. list-table::
      :header-rows: 1

      * - Tactic argument type
        - parsed as
        - interpreted as
        - as in tactic

      * - ``ident``
        - identifier
        - a user-given name
        - intro

      * - ``simple_intropattern``
        - intro_pattern
        - an intro_pattern
        - intros

      * - ``hyp``
        - identifier
        - an hypothesis defined in context
        - clear

      * - ``reference``
        - qualified identifier
        - a global reference of term
        - unfold

      * - ``constr``
        - term
        - a term
        - exact

      * - ``uconstr``
        - term
        - an untyped term
        - refine

      * - ``integer``
        - integer
        - an integer
        -

      * - ``int_or_var``
        - identifier or integer
        - an integer
        - do

      * - ``tactic``
        - tactic at level 5
        - a tactic
        -

      * - ``tacticn``
        - tactic at level n
        - a tactic
        -

      * - *entry*\ ``_list``
        - list of *entry*
        - a list of how *entry* is interpreted
        -

      * - ``ne_``\ *entry*\ ``_list``
        - non-empty list of *entry*
        - a list of how *entry* is interpreted
        -

   .. note:: In order to be bound in tactic definitions, each syntactic
             entry for argument type must include the case of simple L tac
             identifier as part of what it parses. This is naturally the case for
             ``ident``, ``simple_intropattern``, ``reference``, ``constr``, ... but not for ``integer``.
             This is the reason for introducing a special entry ``int_or_var`` which
             evaluates to integers only but which syntactically includes
             identifiers in order to be usable in tactic definitions.

   .. note:: The *entry*\ ``_list`` and ``ne_``\ *entry*\ ``_list`` entries can be used in
             primitive tactics or in other notations at places where a list of the
             underlying entry can be used: entry is either ``constr``, ``hyp``, ``integer``
             or ``int_or_var``.

.. cmdv:: Local Tactic Notation

   Tactic notations do not survive the end of sections. They survive
   modules unless the command Local Tactic Notation is used instead of
   Tactic Notation.

.. rubric:: Footnotes

.. [#and_or_levels] which are the levels effectively chosen in the current
   implementation of Coq

.. [#no_associativity] Coq accepts notations declared as no associative but the parser on
   which Coq is built, namely Camlp4, currently does not implement the
   no-associativity and replace it by a left associativity; hence it is
   the same for Coq: no-associativity is in fact left associativity

.. [#tacn] Tactic notations are just a simplification of the ``Grammar tactic
   simple_tactic`` command that existed in versions prior to version 8.0.
