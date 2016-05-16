.. role:: tactic(code)
   :language: coq

.. |dots| replace:: …
.. |term| replace:: *term*
.. |terms| replace:: *term*\ :sub:`1` |dots| *term*\ :sub:`n`
.. |ident| replace:: *ident*
.. |bindings| replace:: *bindings*
.. |intropattern| replace:: *intropattern*

Blah
====

:tactic:`apply |term| in |ident|`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This tactic applies to any goal.  The argument |term| is a term well-formed in
the local context and the argument |ident| is an hypothesis of the context.  The
tactic `apply |term| in |ident|` tries to match the conclusion of the type of
|ident| against a non-dependent premise of the type of |term|, trying them from
right to left.  If it succeeds, the statement of hypothesis |ident| is replaced
by the conclusion of the type of |term|. The tactic also returns as many
subgoals as the number of other non-dependent premises in the type of |term| and
of the non-dependent premises of the type of |ident|.  If the conclusion of the
type of |term| does not match the goal *and* the conclusion is an inductive type
isomorphic to a tuple type, then the tuple is (recursively) decomposed and the
first component of the tuple of which a non-dependent premise matches the
conclusion of the type of |ident|. Tuples are decomposed in a width-first
left-to-right order (for instance if the type of ``H1`` is a ``A <-> B``
statement, and the type of ``H2`` is ``A`` then ``apply H1 in H2`` transforms
the type of ``H2`` into ``B``).  The tactic ``apply`` relies on first-order
pattern-matching with dependent types.


Errors
------

.. tacerror:: Statement without assumptions

   This happens if the type of |term| has no non dependent premise.

.. tacerror:: Unable to apply

   This happens if the conclusion of |ident| does not match any of the
   non dependent premises of the type of |term|.

Variants
--------

   :tactic:`apply |term| in |ident|`

      This applies each of |term| in sequence in |ident|.

   .. tacerror:: AAA

      :tactic:`apply |term| with |bindings|, |dots|, |term| with |bindings| in |ident|`

          This does the same but uses the bindings in each |bindings| to
          instantiate the parameters of the corresponding type of |term| (see
          syntax of bindings in Section ?.

      :tactic:`apply |term| with |bindings|, |dots|, |term| with |bindings| in |ident|`

          This works like the corresponding ``apply`` form, but turns unresolved
          bindings into existential variables, if any, instead of failing.

      :tactic:`apply |term| with |bindings|, |dots|, |term| with |bindings| in |ident| as |intropattern|`

          This works as ``apply`` above, then applies the |intropattern| to the
          hypothesis |ident|.

      :tactic:`eapply |term| with |bindings|, |dots|, |term| with |bindings| in |ident| as |intropattern|`

          Same as above, using ``eapply``.

      :tactic:`simple apply |terms| in |ident|`

          This behaves like ``apply |term| in |ident|`` but it reasons modulo
          conversion only on subterms that contain no variables to instantiate. For
          instance, if ``id := fun x:nat => x`` and ``H : forall y, id y = y ->
          True`` and ``H0 : O = O`` then ``simple apply H in H0`` does not succeed
          because it would require the conversion of ``id ?1234`` and ``O`` where
          ``?1234`` is a variable to instantiate.  Tactic ``simple apply |term| in
          |ident|`` does not either traverse tuples as ``apply |term| in |ident|``
          does.
