==================================
 Polymorphic Universes
==================================

:Author: Matthieu Sozeau
:Converted by: Clément Pit-Claudel
:Source: https://coq.inria.fr/refman/Reference-Manual032.html

.. contents::
   :local:

General Presentation
====================

.. warning::

   The status of Universe Polymorphism is experimental.

This section describes the universe polymorphic extension of Coq.
Universe polymorphism makes it possible to write generic definitions
making use of universes and reuse them at different and sometimes
incompatible universe levels.

A standard example of the difference between universe *polymorphic*
and *monomorphic* definitions is given by the identity function:

.. coqtop:: in

   Definition identity {A : Type} (a : A) := a.

By default, constant declarations are monomorphic, hence the identity
function declares a global universe (say ``Top.1``) for its domain.
Subsequently, if we try to self-apply the identity, we will get an
error:

.. coqtop:: all

   Fail Definition selfid := identity (@identity).

Indeed, the global level ``Top.1`` would have to be strictly smaller than
itself for this self-application to typecheck, as the type of
:g:`(@identity)` is :g:`forall (A : Type@Top.1), A -> A` whose type is itself
:g:`Type@Top.1+1`.

A universe polymorphic identity function binds its domain universe
level at the definition level instead of making it global.

.. coqtop:: in

   Polymorphic Definition pidentity {A : Type} (a : A) := a.

.. coqtop:: all

   About pidentity.

It is then possible to reuse the constant at different levels, like
so:

.. coqtop:: in

   Definition selfpid := pidentity (@pidentity).

Of course, the two instances of :g:`pidentity` in this definition are
different. This can be seen when the :opt:`Printing Universes` option is on:

.. coqtop:: none

   Set Printing Universes.

.. coqtop:: all

   Print selfpid.

Now :g:`pidentity` is used at two different levels: at the head of the
application it is instantiated at ``Top.3`` while in the argument position
it is instantiated at ``Top.4``. This definition is only valid as long as
``Top.4`` is strictly smaller than ``Top.3``, as show by the constraints. Note
that this definition is monomorphic (not universe polymorphic), so the
two universes (in this case ``Top.3`` and ``Top.4``) are actually global
levels.

Inductive types can also be declared universes polymorphic on
universes appearing in their parameters or fields. A typical example
is given by monoids:

.. coqtop:: in

   Polymorphic Record Monoid := { mon_car :> Type; mon_unit : mon_car;
     mon_op : mon_car -> mon_car -> mon_car }.

.. coqtop:: in

   Print Monoid.

The Monoid's carrier universe is polymorphic, hence it is possible to
instantiate it for example with :g:`Monoid` itself. First we build the
trivial unit monoid in :g:`Set`:

.. coqtop:: in

   Definition unit_monoid : Monoid :=
     {| mon_car := unit; mon_unit := tt; mon_op x y := tt |}.

From this we can build a definition for the monoid of :g:`Set`\-monoids
(where multiplication would be given by the product of monoids).

.. coqtop:: in

   Polymorphic Definition monoid_monoid : Monoid.
     refine (@Build_Monoid Monoid unit_monoid (fun x y => x)).
   Defined.

.. coqtop:: all

   Print monoid_monoid.

As one can see from the constraints, this monoid is “large”, it lives
in a universe strictly higher than :g:`Set`.

Polymorphic, Monomorphic
========================

.. cmd:: Polymorphic @definition

   As shown in the examples, polymorphic definitions and inductives can be
   declared using the ``Polymorphic`` prefix.

.. opt:: Universe Polymorphism

   Once enabled, this option will implicitly prepend ``Polymorphic`` it to any
   definition of the user.

.. cmd:: Monomorphic @definition

   When the :opt:`Universe Polymorphism` option is set, to make a definition
   producing global universe constraints, one can use the ``Monomorphic`` prefix.

Many other commands support the ``Polymorphic`` flag, including:

.. TODO add links on each of these?

- ``Lemma``, ``Axiom``, and all the other “definition” keywords support
  polymorphism.

- ``Variables``, ``Context``, ``Universe`` and ``Constraint`` in a section support
  polymorphism. This means that the universe variables (and associated
  constraints) are discharged polymorphically over definitions that use
  them. In other words, two definitions in the section sharing a common
  variable will both get parameterized by the universes produced by the
  variable declaration. This is in contrast to a “mononorphic” variable
  which introduces global universes and constraints, making the two
  definitions depend on the *same* global universes associated to the
  variable.

- :cmd:`Hint Resolve` and :cmd:`Hint Rewrite` will use the auto/rewrite hint
  polymorphically, not at a single instance.


Global and local universes
==========================

Each universe is declared in a global or local environment before it
can be used. To ensure compatibility, every *global* universe is set
to be strictly greater than :g:`Set` when it is introduced, while every
*local* (i.e. polymorphically quantified) universe is introduced as
greater or equal to :g:`Set`.


Conversion and unification
==========================

The semantics of conversion and unification have to be modified a
little to account for the new universe instance arguments to
polymorphic references. The semantics respect the fact that
definitions are transparent, so indistinguishable from their bodies
during conversion.

This is accomplished by changing one rule of unification, the first-
order approximation rule, which applies when two applicative terms
with the same head are compared. It tries to short-cut unfolding by
comparing the arguments directly. In case the constant is universe
polymorphic, we allow this rule to fire only when unifying the
universes results in instantiating a so-called flexible universe
variables (not given by the user). Similarly for conversion, if such
an equation of applicative terms fail due to a universe comparison not
being satisfied, the terms are unfolded. This change implies that
conversion and unification can have different unfolding behaviors on
the same development with universe polymorphism switched on or off.


Minimization
============

Universe polymorphism with cumulativity tends to generate many useless
inclusion constraints in general. Typically at each application of a
polymorphic constant :g:`f`, if an argument has expected type :g:`Type@{i}`
and is given a term of type :g:`Type@{j}`, a :math:`j ≤ i` constraint will be
generated. It is however often the case that an equation :math:`j = i` would
be more appropriate, when :g:`f`\'s universes are fresh for example.
Consider the following example:

.. coqtop:: in

   Definition id0 := @pidentity nat 0.

.. coqtop:: all

   Print id0.

This definition is elaborated by minimizing the universe of :g:`id0` to
level :g:`Set` while the more general definition would keep the fresh level
:g:`i` generated at the application of :g:`id` and a constraint that :g:`Set` :math:`≤ i`.
This minimization process is applied only to fresh universe variables.
It simply adds an equation between the variable and its lower bound if
it is an atomic universe (i.e. not an algebraic max() universe).

.. opt:: Universe Minimization ToSet

   Unsetting this option disallows minimization to the sort :g:`Set` and only
   collapses floating universes between themselves.


Explicit Universes
==================

The syntax has been extended to allow users to explicitly bind names
to universes and explicitly instantiate polymorphic definitions.

.. cmd:: Universe @ident.

   In the monorphic case, this command declares a new global universe
   named :g:`ident`. It supports the polymorphic flag only in sections, meaning
   the universe quantification will be discharged on each section
   definition independently.


.. cmd:: Constraint @ident @ord @ident.

   This command declares a new constraint between named universes. The
   order relation :n:`@ord` can be one of :math:`<`, :math:`≤` or :math:`=`. If consistent, the constraint
   is then enforced in the global environment. Like ``Universe``, it can be
   used with the ``Polymorphic`` prefix in sections only to declare
   constraints discharged at section closing time.

   .. exn:: Undeclared universe @ident.

   .. exn:: Universe inconsistency.


Polymorphic definitions
-----------------------

For polymorphic definitions, the declaration of (all) universe levels
introduced by a definition uses the following syntax:

.. coqtop:: in

   Polymorphic Definition le@{i j} (A : Type@{i}) : Type@{j} := A.

.. coqtop:: all

   Print le.

During refinement we find that :g:`j` must be larger or equal than :g:`i`, as we
are using :g:`A : Type@i <= Type@j`, hence the generated constraint. At the
end of a definition or proof, we check that the only remaining
universes are the ones declared. In the term and in general in proof
mode, introduced universe names can be referred to in terms. Note that
local universe names shadow global universe names. During a proof, one
can use Show Universes to display the current context of universes.

Definitions can also be instantiated explicitly, giving their full
instance:

.. coqtop:: all

   Check (pidentity@{Set}).
   Universes k l.
   Check (le@{k l}).

User-named universes are considered rigid for unification and are
never minimized.

.. opt:: Strict Universe Declaration.

   The command ``Unset Strict Universe Declaration`` allows one to freely use
   identifiers for universes without declaring them first, with the
   semantics that the first use declares it. In this mode, the universe
   names are not associated with the definition or proof once it has been
   defined. This is meant mainly for debugging purposes.
