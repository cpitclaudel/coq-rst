=============================================
 A subset of Coq's tactic reference
=============================================

:Source: https://coq.inria.fr/refman/Reference-Manual010.html.
:Converted by: Clément Pit-Claudel

.. tip::

   In this documentation, :n:`@italics` indicate holes to fill; the rest is
   fixed syntax. Boxes indicate repeatable blocks. The top-right symbol
   indicates the number of repetitions:

   - :n:`{? 0 or 1}` (an optional block)
   - :n:`{+ one or more}` (a repeatable block)
   - :n:`{* any number of times}` (an optional, repeatable block)

   The bottom symbol indicates the separator to use between repeated blocks.
   For example, “``rewrite H``”, “``rewrite → H``”, and “``rewrite H1, H2``” are all
   matches for :n:`rewrite {? →} {+, term}`.

.. note::

   Scroll down for examples of ``coqtop`` output.  The bottom of this page lists all
   Coq forms that include repetitions, semi-automatically reverse-engineered from
   the manual.

.. tacn:: fix @ident @num
   :name: fix

   This tactic is a primitive tactic to start a proof by induction. In general,
   it is easier to rely on higher-level induction tactics such as the ones
   described in Section 8.5.2.

   In the syntax of the tactic, the identifier ident is the name given to the
   induction hypothesis. The natural number ``num`` tells on which premise of
   the current goal the induction acts, starting from 1 and counting both
   dependent and non dependent products. Especially, the current lemma must be
   composed of at least ``num`` products.

   Like in a ``fix`` expression, the induction hypotheses have to be used on
   structurally smaller arguments. The verification that inductive proof
   arguments are correct is done only at the time of registering the lemma in
   the environment. To know if the use of induction hypotheses is correct at
   some time of the interactive development of a proof, use the command Guarded
   (see Section 7.3.2).

   .. tacv:: fix @ident @num with {+ (@ident {+ @binder} {? {struct @ident'}} : @type)}

    This starts a proof by mutual induction. The statements to be simultaneously
    proved are each of the type :n:`forall {+ @binder}, @type`. The identifiers
    ``ident`` are the names of the induction hypotheses. The identifiers
    ``ident'`` are the respective names of the premises on which the induction
    is performed in the statements to be simultaneously proved (if not given,
    the system tries to guess itself what they are).


.. tacn:: unfold @qualid
   :name: unfold

   This tactic applies to any goal. The argument qualid must denote a defined
   transparent constant or local definition (see Sections 1.3.2 and 6.10.2). The
   tactic unfold applies the δ rule to each occurrence of the constant to which
   qualid refers in the current goal and then replaces it with its :term:`βι
   normal form`.

   .. exn:: @qualid does not denote an evaluable constant

   .. tacv:: unfold {+ @qualid}

      Replaces simultaneously each of the ``qualid`` with their definitions and
      replaces the current goal with its :term:`βι normal form`.

   .. tacv:: unfold {+, @qualid at {+, @num}}

      The lists of ``num`` specify the occurrences of ``qualid`` to be
      unfolded. Occurrences are located from left to right.

      .. exn:: bad occurrence number of @qualid

      .. exn:: @qualid does not occur

   .. tacv:: unfold @string

      If string denotes the discriminating symbol of a notation (e.g. ``"+"``)
      or an expression defining a notation (e.g. ``"_ + _"``), and this notation
      refers to an unfoldable constant, then the tactic unfolds it.

   .. tacv:: unfold @string%@key

      This is variant of unfold string where string gets its interpretation from
      the scope bound to the delimiting key key instead of its default
      interpretation (see Section 12.2.2).

   .. tacv:: unfold {+, @qualid|@string at {+, @num}}

      This is the most general form, where ``qualid_or_string`` is either a
      ``qualid`` or a ``string`` referring to a notation.


.. tacn:: apply @term
   :name: apply

   This tactic applies to any goal. The argument ``term`` is a term well-formed
   in the local context. The tactic ``apply`` tries to match the current goal
   against the conclusion of the type of ``term``. If it succeeds, then the
   tactic returns as many subgoals as the number of non-dependent premises of
   the type of term. If the conclusion of the type of term does not match the
   goal and the conclusion is an inductive type isomorphic to a tuple type, then
   each component of the tuple is recursively matched to the goal in the
   left-to-right order.

   The tactic apply relies on first-order unification with dependent types
   unless the conclusion of the type of term is of the form :g:`(P t1 … tn)`
   with :g:`P` to be instantiated. In the latter case, the behavior depends on
   the form of the goal. If the goal is of the form :g:`(fun x => Q) u1 … un`
   and the :g:`ti` and :g:`ui` unifies, then P is taken to be :g:`(fun x => Q)`.
   Otherwise, ``apply`` tries to define :g:`P` by abstracting over :g:`t1 …  tn`
   in the goal. See ``pattern`` in Section 8.7.7 to transform the goal so that
   it gets the form :g:`(fun x => Q) u1 … un`.

   .. exn:: Impossible to unify … with …

      The apply tactic failed to match the conclusion of term and the current
      goal. You can help the apply tactic by transforming your goal with the
      change or pattern tactics (see sections 8.7.7, 8.6.5).

   .. exn:: Unable to find an instance for the variables {+ @ident}

      This occurs when some instantiations of the premises of term are not
      deducible from the unification. This is the case, for instance, when you
      want to apply a transitivity property. In this case, you have to use one
      of the variants below.

   .. tacv:: apply @term with {+ @term}

      Provides apply with explicit instantiations for all dependent premises of
      the type of term that do not occur in the conclusion and consequently
      cannot be found by unification. Notice that the collection :n:`{+ @term}`
      must be given according to the order of these dependent premises of the
      type of ``term``.

      .. exn:: Not the right number of missing arguments

   .. tacv:: apply @term with {+ (@ref := @term)}

      This also provides apply with values for instantiating premises. Here,
      variables are referred by names and non-dependent products by increasing
      numbers (see syntax in Section 8.1.3).

   .. tacv:: apply {+, @term}

      This is a shortcut for ``apply term1 ; [ .. | … ; [ .. | apply termn ] … ]``,
      i.e. for the successive applications of :g:`termi+1` on the last subgoal
      generated by apply :g:`termi`, starting from the application of term1.

   .. tacv:: eapply @term

      The tactic eapply behaves like apply but it does not fail when no
      instantiations are deducible for some variables in the premises. Rather,
      it turns these variables into existential variables which are variables
      still to instantiate (see Section 2.11). The instantiation is intended to
      be found later in the proof.

   .. tacv:: simple apply @term
      :name: simple apply

      This behaves like ``apply`` but it reasons modulo conversion only on
      subterms that contain no variables to instantiate. For instance, the
      following example does not succeed because it would require the conversion
      of ``id ?foo`` and ``O``.

      .. coqtop:: in reset

         Definition id (x : nat) := x.
         Hypothesis H : forall y, id y = y.
         Goal O = O.

      .. coqtop:: all

         Fail simple apply H.

      Because it reasons modulo a limited amount of conversion, :n:`simple apply`
      fails quicker than :n:`apply` and it is then well-suited for uses in
      used-defined tactics that backtrack often. Moreover, it does not traverse
      tuples as apply does.

   .. tacv:: {? simple} apply {+, @term {? with @bindings_list}} in @ident {? as @intro_pattern}

      This summarizes the different syntaxes for apply and eapply.

   .. tacv:: lapply @term
      :name: lapply

      This tactic applies to any goal, say :g:`G`. The argument term has to be
      well-formed in the current context, its type being reducible to a
      non-dependent product :g:`A -> B` with :g:`B` possibly containing
      products. Then it generates two subgoals :g:`B->G` and :g:`A`. Applying
      ``lapply H`` (where :g:`H` has type :g:`A->B` and :g:`B` does not start
      with a product) does the same as giving the sequence ``cut B. 2:apply
      H``. where cut is described below.

      .. warning:: When ``term`` contains more than one non dependent product
                   the tactic ``lapply`` only takes into account the first
                   product.

   .. example:: Assume we have a transitive relation :g:`R` on :g:`nat`:

      .. coqtop:: reset in

         Variable R : nat -> nat -> Prop.
         Hypothesis Rtrans : forall x y z:nat, R x y -> R y z -> R x z.
         Variables n m p : nat.
         Hypothesis Rnm : R n m.
         Hypothesis Rmp : R m p.

      Consider the goal :g:`(R n p)` provable using the transitivity of :g:`R`:

      .. coqtop:: in

         Goal R n p.

      The direct application of :g:`Rtrans` with apply fails because no value
      for :g:`y` in :g:`Rtrans` is found by ``apply``:

      .. coqtop:: all

         Fail apply Rtrans.

      A solution is to apply :g:`(Rtrans n m p)` or :g:`(Rtrans n m)`.

      .. coqtop:: all undo

         apply (Rtrans n m p).

      Note that :g:`n` can be inferred from the goal, so the following would
      work too.

      .. coqtop:: in undo

         apply (Rtrans _ m).

      More elegantly, apply :g:`Rtrans` with ``(y := m)`` allows only mentioning
      the unknown :g:`m`:

      .. coqtop:: in undo

         apply Rtrans with (y := m).

      Another solution is to mention the proof of :g:`(R x y)` in :g:`Rtrans`\ …

      .. coqtop:: all undo

         apply Rtrans with (1 := Rnm).

      …or the proof of :g:`(R y z)`.

      .. coqtop:: all undo

         apply Rtrans with (2 := Rmp).

      On the opposite, one can use eapply which postpones the problem of finding
      :g:`m`. Then one can apply the hypotheses :g:`Rnm` and :g:`Rmp`. This
      instantiates the existential variable and completes the proof.

      .. coqtop:: all

         eapply Rtrans.
         apply Rnm.
         apply Rmp.

   .. note::

      When the conclusion of the type of the term to apply is an inductive type
      isomorphic to a tuple type and apply looks recursively whether a component
      of the tuple matches the goal, it excludes components whose statement
      would result in applying an universal lemma of the form ``forall A, … ->
      A``. Excluding this kind of lemma can be avoided by setting the following
      option:

      .. opt:: Universal Lemma Under Conjunction

         This option, which preserves compatibility with versions of Coq prior
         to 8.4 is also available for :n:`apply @term in @ident` (see
         :tacn:`apply … in`).

.. tacn:: apply @term in @ident
   :name: apply … in

   This tactic applies to any goal.  The argument ``term`` is a term well-formed
   in the local context and the argument ``ident`` is an hypothesis of the
   context.  The tactic ``apply`` tries to match the conclusion of the type of
   ``ident`` against a non-dependent premise of the type of ``term``, trying
   them from right to left.  If it succeeds, the statement of hypothesis
   ``ident`` is replaced by the conclusion of the type of ``term``. The tactic
   also returns as many subgoals as the number of other non-dependent premises
   in the type of ``term`` and of the non-dependent premises of the type of
   ``ident``.  If the conclusion of the type of ``term`` does not match the goal
   *and* the conclusion is an inductive type isomorphic to a tuple type, then
   the tuple is (recursively) decomposed and the first component of the tuple of
   which a non-dependent premise matches the conclusion of the type of
   ``ident``. Tuples are decomposed in a width-first left-to-right order (for
   instance if the type of :g:`H1` is a :g:`A <-> B` statement, and the type of
   :g:`H2` is :g:`A` then ``apply H1 in H2`` transforms the type of :g:`H2` into
   :g:`B`).  The tactic ``apply`` relies on first-order pattern-matching with
   dependent types.

   .. exn:: Statement without assumptions

      This happens if the type of ``term`` has no non dependent premise.

   .. exn:: Unable to apply

      This happens if the conclusion of ``ident`` does not match any of the
      non dependent premises of the type of ``term``.

   .. tacv:: apply {+, @term} in @ident

      This applies each of ``term`` in sequence in ``ident``.

   .. tacv:: apply {+, @term with {+ @bindings_list}} in {+, @hyp}

      This does the same but uses the bindings in each ``(id := val)`` to
      instantiate the parameters of the corresponding type of term (see syntax
      of bindings in Section 8.1.3).

   .. tacv:: eapply {+, @term with {+ @bindings_list}} in {+, @hyp}

      This works as above but turns unresolved bindings into existential
      variables, if any, instead of failing.

   .. tacv:: apply {+, @term with {+ (@id := @val)}} in {+, @hyp} as @intropattern

      This works as ``apply`` above, then applies the ``intropattern`` to the
      hypothesis ``ident``.

   .. tacv:: eapply {+, @term with {+ (@id := @val)}} in {+, @hyp} as @intropattern

      Same as above, but using ``eapply``.

   .. tacv:: simple apply @terms in @ident
      :name: simple apply … in

      This behaves like :n:`apply @term in @ident` but it reasons modulo
      conversion only on subterms that contain no variables to instantiate. For
      instance, if :g:`id := fun x:nat => x` and :g:`H : forall y, id y = y -> True`
      and :g:`H0 : O = O` then :n:`simple apply H in H0` does not succeed
      because it would require the conversion of :g:`id ?1234` and :g:`O` where
      :g:`?1234` is a variable to instantiate.  Tactic :n:`simple apply @term in @ident`
      does not either traverse tuples as :n:`apply @term in @ident` does.

   .. tacv:: {? simple} apply {+, @term {? with @bindings_list}} in @ident {? as @intro_pattern}

      This summarizes the different syntactic variants of :n:`apply @term
      in @ident` and :n:`eapply @term in @ident`.

.. tacn:: fresh {+ @component}
.. tacn:: fun {+ @ident} => @expr
.. tacn:: solve [{+| @expr}]
.. tacn:: apply @term with {+ @term}
.. tacn:: apply @term with {+ (@ref := @term)}
.. tacn:: apply {+, @term}
.. tacn:: apply {+, @term} in @ident
.. tacn:: apply {+, @term with @bindings_list} in @ident
.. tacn:: eapply {+, @term with @bindings_list} in @ident
.. tacn:: apply {+, @term with @bindings_list} in @ident as @intro_pattern
.. tacn:: eapply {+, @term with @bindings_list} in @ident as @intro_pattern
.. tacn:: {? simple} apply {+, @term {? with @bindings_list}} in @ident {? as @intro_pattern}
.. tacn:: exists {+, @bindings_list}
.. tacn:: intros {+ @ident}
.. tacn:: clear {+ @ident}
.. tacn:: clear - {+ @ident}
.. tacn:: revert {+ @ident}
.. tacn:: rename {+, @ident into @ident}
.. tacn:: set (@ident {+ @binder} := @term)
.. tacn:: set (@ident {+ @binder} := @term) in @goal_occurrences
.. tacn:: pose (@ident {+ @binder} := @term)
.. tacn:: decompose [{+ @qualid}] @term
.. tacn:: specialize (@ident {+ @term})
.. tacn:: generalize {+, @term}
.. tacn:: generalize @term at {+ @num}
.. tacn:: generalize {+, @term at {+ @num} as @ident}
.. tacn:: destruct {+, @term}
.. tacn:: induction {+, @term} using @qualid
.. tacn:: dependent induction @ident generalizing {+ @ident}
.. tacn:: functional induction (@qualid {+ @term})
.. tacn:: functional induction (@qualid {+ @term}) as @disj_conj_intro_pattern using @term with @bindings_list
.. tacn:: ediscriminate @term {? with @bindings_list}
.. tacn:: einjection @term {? with @bindings_list}
.. tacn:: injection @term {? with @bindings_list} as {+ @intro_pattern}
.. tacn:: injection @num as {+ @intro_pattern}
.. tacn:: injection as {+ @intro_pattern}
.. tacn:: einjection @term {? with @bindings_list} as {+ @intro_pattern}
.. tacn:: einjection @num as {+ @intro_pattern}
.. tacn:: einjection as {+ @intro_pattern}
.. tacn:: inversion @ident in {+ @ident}
.. tacn:: inversion @ident as @intro_pattern in {+ @ident}
.. tacn:: inversion_clear @ident in {+ @ident}
.. tacn:: inversion_clear @ident as @intro_pattern in {+ @ident}
.. tacn:: inversion @ident using @ident' in {+ @ident}
.. tacn:: fix @ident @num with {+ (@ident {+ @binder} {? {struct @ident'}} : @type)}
.. tacn:: cofix @ident with {+ (@ident {+ @binder} : @type)}
.. tacn:: rewrite {+, @term}
.. tacn:: subst {+ @ident}
.. tacn:: change @term at {+ @num} with @term
.. tacn:: change @term at {+ @num} with @term in @ident
.. tacn:: cbv {+ @flag}
.. tacn:: lazy {+ @flag}
.. tacn:: compute [{+ @qualid}]
.. tacn:: cbv [{+ @qualid}]
.. tacn:: compute -[{+ @qualid}]
.. tacn:: cbv -[{+ @qualid}]
.. tacn:: lazy [{+ @qualid}]
.. tacn:: lazy -[{+ @qualid}]
.. tacn:: cbn [{+ @qualid}]
.. tacn:: cbn -[{+ @qualid}]
.. tacn:: simpl @pattern at {+ @num}
.. tacn:: simpl @qualid at {+ @num}
.. tacn:: simpl @string at {+ @num}
.. tacn:: unfold {+, @qualid}
.. tacn:: unfold {+, @qualid at {+, @num}}
.. tacn:: unfold {+, @qualid_or_string at {+, @num}}
.. tacn:: pattern @term at {+ @num}
.. tacn:: pattern @term at - {+ @num}
.. tacn:: pattern {+, @term}
.. tacn:: pattern {+, @term at {+ @num}}
.. tacn:: auto with {+ @ident}
.. tacn:: auto using {+, @lemma}
.. tacn:: auto using {+, @lemma} with {+ @ident}
.. tacn:: trivial with {+ @ident}
.. tacn:: autounfold with {+ @ident}
.. tacn:: autounfold with {+ @ident} in @clause
.. tacn:: autorewrite with {+ @ident}
.. tacn:: autorewrite with {+ @ident} using @tactic
.. tacn:: autorewrite with {+ @ident} in @qualid
.. tacn:: autorewrite with {+ @ident} in @qualid using @tactic
.. tacn:: autorewrite with {+ @ident} in @clause
.. tacn:: firstorder with {+ @ident}
.. tacn:: firstorder using {+, @qualid}
.. tacn:: firstorder using {+, @qualid} with {+ @ident}
.. tacn:: congruence with {+ @term}
.. tacn:: esimplify_eq @term {? with @bindings_list}
.. tacn:: quote @ident [{+ @ident}]
.. tacn:: ring_simplify {+ @term}
.. tacn:: field_simplify {+ @term}
.. tacn:: idtac {+ @message_token}
.. tacn:: fail {+ @message_token}
.. tacn:: fail @n {+ @message_token}
.. tacn:: gfail {+ @message_token}
.. tacn:: gfail @n {+ @message_token}
.. tacn:: quote @ident [{+ @ident}] in @term using @tactic
.. tacn:: ring [{+ @term}]
.. tacn:: ring_simplify [{+ @term}] {+ @t} in @ident
.. tacn:: field [{+ @term}]
.. tacn:: field_simplify [{+ @term}]
.. tacn:: field_simplify [{+ @term}] {+ @term}
.. tacn:: field_simplify [{+ @term}] in @hyp
.. tacn:: field_simplify [{+ @term}] {+ @term} in @hyp
.. tacn:: field_simplify_eq [{+ @term}]
.. tacn:: field_simplify_eq [{+ @term}] in @hyp
.. tacn:: setoid_symmetry {? in @ident}
.. tacn:: setoid_rewrite @term {? in @ident}
.. tacn:: setoid_rewrite <- @term {? in @ident}
.. tacn:: setoid_rewrite <- @term {? at @occs} {? in @ident}
.. tacn:: setoid_rewrite {? @orientation} @term {? at @occs} {? in @ident}
.. tacn:: setoid_replace @term with @term {? in @ident} {? using relation @term} {? by @tactic}
.. tacn:: rewrite_strat @s {? in @ident}
.. tacn:: Program Fixpoint @ident @params {order} : type := @term.
.. tacn:: Add Field @name : @field ({+, @mod}).
.. tacn:: Add Ring @name : @ring ({+, @mod}).
.. tacn:: Admit Obligations {? of @ident}.
.. tacn:: Arguments @ident {+ !@arg}.
.. tacn:: Arguments @ident {+ @possibly_bracketed_ident} / {+ @possibly_bracketed_ident}.
.. tacn:: Arguments @ident {+ @possibly_bracketed_ident} : simpl never.
.. tacn:: Arguments @ident {+ @possibly_bracketed_ident} : simpl nomatch.
.. tacn:: Arguments @qualid {+ @name} : rename.
.. tacn:: Arguments @qualid {+ @name %@scope}.
.. tacn:: Arguments @qualid {+ @possibly_bracketed_ident}.
.. tacn:: Class @ident {+ @binder} : @sort:= {{+; @field}}.
.. tacn:: Class @ident {+ @binder} : @sort:= @ident : @type.
.. tacn:: Collection @ident:= {+ @ident}.
.. tacn:: Context {+ @binder}.
.. tacn:: Corollary @ident {? @binders} : @type.
.. tacn:: Create HintDb @ident {? discriminated}.
.. tacn:: Definition @ident {+ @binder}.
.. tacn:: Definition @ident {? @binders} : @type.
.. tacn:: Derive Dependent Inversion_clear @ident with forall {+ @ident: @type}, @I {+ @arg} Sort @sort.
.. tacn:: Derive Dependent Inversion @ident with forall {+ @ident: @type}, @I {+ @arg} Sort @sort.
.. tacn:: Derive Inversion_clear @ident with forall {+ @ident: @type}, @I {+ @arg} Sort @sort.
.. tacn:: Derive Inversion @ident with forall {+ @ident: @type}, @I {+ @arg} Sort @sort.
.. tacn:: Existing Instance @ident {? @priority}.
.. tacn:: Existing Instances {+ @ident} {? @priority}.
.. tacn:: Extract Constant @qualid {+ "@string"} => "@string".
.. tacn:: Extract Inductive @qualid => "@string" [{+ "@string"}] @optstring.
.. tacn:: Extraction Blacklist {+ @ident}.
.. tacn:: Extraction "@file" {+ @qualid}.
.. tacn:: Extraction Implicit @qualid [{+ @ident}].
.. tacn:: Fact @ident {? @binders} : @type.
.. tacn:: Fixpoint @ident @params {struct @ident} : type := @term.
.. tacn:: Function @ident {+ @binder} {decrease_annot} : type := @term.
.. tacn:: Generalizable Variables {+ @ident}.
.. tacn:: Global Arguments @qualid {+ @name %@scope}.
.. tacn:: Global Arguments @qualid {+ @possibly_bracketed_ident}.
.. tacn:: Global Opaque {+ @qualid}.
.. tacn:: Hint @hint_definition : {+ @ident}.
.. tacn:: Hint Local @hint_definition : {+ @ident}.
.. tacn:: Hint Rewrite {+ @term} : {+ @ident}.
.. tacn:: Hint Rewrite -> {+ @term} : {+ @ident}.
.. tacn:: Hint Rewrite <- {+ @term} : {+ @ident}.
.. tacn:: Hint Rewrite {+ @term} using @tactic : {+ @ident}.
.. tacn:: Implicit Types {+ @ident} : @type.
.. tacn:: Include {+<+ @module}.
.. tacn:: Inductive @ident {+ @binder} : @term := {+| @ident: @term}.
.. tacn:: Infix "@symbol" := @qualid ({+, @modifier}).
.. tacn:: Instance @ident {+ @binder} : Class {+ @term} {? @priority} := {{+; @field := @b}}.
.. tacn:: Instance @ident {+ @binder} : forall {+ @binder}, Class {+ @term} {? @priority} := @term.
.. tacn:: Lemma @ident {? @binders} : @type.
.. tacn:: Let CoFixpoint @ident {+ with @cofix_body}.
.. tacn:: Let Fixpoint @ident {+ with @fix_body}.
.. tacn:: Let @ident {? @binders} : @type.
.. tacn:: Local Arguments @qualid {+ @name %@scope}.
.. tacn:: Local Arguments @qualid {+ @possibly_bracketed_ident}.
.. tacn:: Local Declare ML Module {+ "@string"}.
.. tacn:: {? Local} Hint Constructors @ident{? : {+ @ident}}.
.. tacn:: {? Local} Hint Constructors {+ @ident}{? : {+ @ident}}.
.. tacn:: {? Local} Hint Cut @regexp{? : {+ @ident}}.
.. tacn:: {? Local} Hint Extern @num {? @pattern} => @tactic{? : {+ @ident}}.
.. tacn:: Local Hint @hint_definition : {+ @ident}.
.. tacn:: {? Local} Hint Immediate @term{? : {+ @ident}}.
.. tacn:: {? Local} Hint Immediate {+ @term}{? : {+ @ident}}.
.. tacn:: {? Local} Hint Resolve @term{? : {+ @ident}}.
.. tacn:: {? Local} Hint Resolve {+ @term}{? : {+ @ident}}.
.. tacn:: {? Local} Hint Unfold {+ @ident}{? : {+ @ident}}.
.. tacn:: {? Local} Hint Unfold @qualid{? : {+ @ident}}.
.. tacn:: {? Local} Notation @ident {? {+ @ident @ident}} := @term {? (only parsing)}.
.. tacn:: Module @ident @module_bindings := {+<+ @module_expression}.
.. tacn:: Module @ident @module_bindings <: {+<: @module_type}.
.. tacn:: Module @ident @module_bindings <: {+<: @module_type}:= @module_expression.
.. tacn:: Module @ident <: {+<: @module_type}.
.. tacn:: Module Type @ident @module_bindings := {+<+ @module_type}.
.. tacn:: Next Obligation {? of @ident}.
.. tacn:: Obligation num {? of @ident}.
.. tacn:: Obligations {? of @ident}.
.. tacn:: Opaque {+ @qualid}.
.. tacn:: Parameter {+ @ident} : @term.
.. tacn:: Preterm {? of @ident}.
.. tacn:: Print {? Sorted} Universes.
.. tacn:: Print {? Sorted} Universes "@string".
.. tacn:: Program Definition @ident {+ @binder} : @term := @term.
.. tacn:: Proof using @collection - ({+ @ident}).
.. tacn:: Proof using {+ @ident}.
.. tacn:: Proof using -({+ @ident}).
.. tacn:: Proof using {+ @ident} with @tactic.
.. tacn:: Proof with @tactic using {+ @ident}.
.. tacn:: Proposition @ident {? @binders} : @type.
.. tacn:: Qed exporting {+, @ident}.
.. tacn:: Record @ident @params : @sort := @ident {{+; @ident @binders : @term}}.
.. tacn:: Recursive Extraction {+ @qualid}.
.. tacn:: Remark @ident {? @binders} : @type.
.. tacn:: Remove Hints {+ @term} : {+ @ident}.
.. tacn:: SearchHead @term inside {+ @module}.
.. tacn:: SearchHead @term outside {+ @module}.
.. tacn:: SearchPattern @term inside {+ @module}.
.. tacn:: SearchPattern @term outside {+ @module}.
.. tacn:: SearchRewrite @term inside {+ @module}.
.. tacn:: SearchRewrite @term outside {+ @module}.
.. tacn:: Search {+ {? -}@search_term}.
.. tacn:: Search {+ @search_term} inside {+ @module}.
.. tacn:: Search {+ @search_term} outside {+ @module}.
.. tacn:: @selector: Search {+ {? -}@search_term}.
.. tacn:: Separate Extraction {+ @qualid}.
.. tacn:: Solve All Obligations {? with @expr}.
.. tacn:: Solve Obligations {? of @ident} {? with @expr}.
.. tacn:: Strategy @level [{+ @qualid}].
.. tacn:: Tactic Notation @tactic_level {? {+ @prod_item}} := @tactic.
.. tacn:: Theorem @ident {? @binders} : @type.
.. tacn:: Transparent {+ @qualid}.
.. tacn:: Typeclasses Opaque {+ @ident}.
.. tacn:: Typeclasses Transparent {+ @ident}.
.. tacn:: Variable {+ @ident} : @term.
.. tacn:: Variant @ident {+ @binder} : @term := {+ @constructors}.
