==================================
 Typing rules of the CIC
==================================

:Source: https://coq.inria.fr/refman/Reference-Manual006.html#Typing-rules
:Converted by: Clément Pit-Claudel

.. only:: html

   .. include:: preamble.rst

A term :math:`t` is well typed in a global environment :math:`E` iff there exists a
local context :math:`\Gamma` and a term :math:`T` such that the judgment :math:`\WTEG{t}{T}` can
be derived from the following rules.

.. inference:: W-Empty

   ---------
   \WF{[]}{}

.. inference:: W-Local-Assum

   \WTEG{T}{s}
   s \in \Sort
   x \not\in \Gamma % \cup E
   -------------------------
   \WFE{\Gamma::(x:T)}

.. inference:: W-Local-Def

   \WTEG{t}{T}
   x \not\in \Gamma % \cup E
   -------------------------
   \WFE{\Gamma::(x:=t:T)}

.. inference:: W-Global-Assum

   \WTE{}{T}{s}
   s \in \Sort
   c \notin E
   ------------
   \WF{E;c:T}{}

.. inference:: W-Global-Def

   \WTE{}{t}{T}
   c \notin E
   ---------------
   \WF{E;c:=t:T}{}

.. inference:: Ax-Prop

   \WFE{\Gamma}
   ----------------------
   \WTEG{\Prop}{\Type(1)}

.. inference:: Ax-Set

   \WFE{\Gamma}
   ---------------------
   \WTEG{\Set}{\Type(1)}

.. inference:: Ax-Type

   \WFE{\Gamma}
   ---------------------------
   \WTEG{\Type(i)}{\Type(i+1)}

.. inference:: Var

   \WFE{\Gamma}
   (x:T) \in \Gamma~~\mbox{or}~~(x:=t:T) \in \Gamma~\mbox{for some $t$}
   --------------------------------------------------------------------
   \WTEG{x}{T}

.. inference:: Const

   \WFE{\Gamma}
   (c:T) \in E~~\mbox{or}~~(c:=t:T) \in E~\mbox{for some $t$}
   ----------------------------------------------------------
   \WTEG{c}{T}

.. inference:: Prod-Pro

   \WTEG{T}{s}
   s \in \Sort
   \WTE{\Gamma::(x:T)}{U}{\Prop}
   -----------------------------
   \WTEG{\forall~x:T,U}{\Prop}

.. inference:: Prod-Set

   \WTEG{T}{s}
   s \in \{\Prop, \Set\}
   \WTE{\Gamma::(x:T)}{U}{\Set}
   ----------------------------
   \WTEG{\forall~x:T,U}{\Set}

.. inference:: Prod-Type

   \WTEG{T}{\Type(i)}
   \WTE{\Gamma::(x:T)}{U}{\Type(i)}
   --------------------------------
   \WTEG{\forall~x:T,U}{\Type(i)}

.. inference:: Lam

   \WTEG{\forall~x:T,U}{s}
   \WTE{\Gamma::(x:T)}{t}{U}
   ------------------------------------
   \WTEG{\lb x:T\mto t}{\forall x:T, U}

.. inference:: App

   \WTEG{t}{\forall~x:U,T}
   \WTEG{u}{U}
   ------------------------------
   \WTEG{(t\ u)}{\subst{T}{x}{u}}

.. inference:: Let

   \WTEG{t}{T}
   \WTE{\Gamma::(x:=t:T)}{u}{U}
   -----------------------------------------
   \WTEG{\letin{x}{t:T}{u}}{\subst{U}{x}{t}}
