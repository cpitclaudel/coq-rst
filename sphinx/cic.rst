======================================
Example 2: The typing rules of the CIC
======================================

Corresponding page: https://coq.inria.fr/refman/Reference-Manual006.html#Typing-rules

.. preamble::

   \def\ensuremath#1{#1}

   \newcommand{\WF}[2]{\ensuremath{{\cal W\!F}(#1)[#2]}}
   \newcommand{\WFE}[1]{\WF{E}{#1}}
   \newcommand{\WT}[4]{\ensuremath{#1[#2] \vdash #3 : #4}}
   \newcommand{\WTE}[3]{\WT{E}{#1}{#2}{#3}}
   \newcommand{\WTEG}[2]{\WTE{\Gamma}{#1}{#2}}

   \newcommand{\letin}[3]{\kw{let}~#1:=#2~\kw{in}~#3}
   \newcommand{\subst}[3]{#1\{#2/#3\}}

   \newcommand{\mto}{.\;}
   \newcommand{\kw}[1]{\textsf{#1}}
   \newcommand{\lb}{\lambda}
   \newcommand{\Sort}{\cal S}

   \newcommand{\alors}{\textsf{then}}
   \newcommand{\alter}{\textsf{alter}}
   \newcommand{\bool}{\textsf{bool}}
   \newcommand{\conc}{\textsf{conc}}
   \newcommand{\cons}{\textsf{cons}}
   \newcommand{\consf}{\textsf{consf}}
   \newcommand{\emptyf}{\textsf{emptyf}}
   \newcommand{\EqSt}{\textsf{EqSt}}
   \newcommand{\false}{\textsf{false}}
   \newcommand{\filter}{\textsf{filter}}
   \newcommand{\forest}{\textsf{forest}}
   \newcommand{\from}{\textsf{from}}
   \newcommand{\hd}{\textsf{hd}}
   \newcommand{\haslength}{\textsf{has\_length}}
   \newcommand{\length}{\textsf{length}}
   \newcommand{\List}{\textsf{list}}
   \newcommand{\nilhl}{\textsf{nil\_hl}}
   \newcommand{\conshl}{\textsf{cons\_hl}}
   \newcommand{\nat}{\textsf{nat}}
   \newcommand{\nO}{\textsf{O}}
   \newcommand{\nS}{\textsf{S}}
   \newcommand{\node}{\textsf{node}}
   \newcommand{\Nil}{\textsf{nil}}
   \newcommand{\Prop}{\textsf{Prop}}
   \newcommand{\Set}{\textsf{Set}}
   \newcommand{\si}{\textsf{if}}
   \newcommand{\sinon}{\textsf{else}}
   \newcommand{\Str}{\textsf{Stream}}
   \newcommand{\tl}{\textsf{tl}}
   \newcommand{\tree}{\textsf{tree}}
   \newcommand{\true}{\textsf{true}}
   \newcommand{\Type}{\textsf{Type}}
   \newcommand{\unfold}{\textsf{unfold}}
   \newcommand{\zeros}{\textsf{zeros}}
   \newcommand{\even}{\textsf{even}}
   \newcommand{\odd}{\textsf{odd}}
   \newcommand{\evenO}{\textsf{even\_O}}
   \newcommand{\evenS}{\textsf{even\_S}}
   \newcommand{\oddS}{\textsf{odd\_S}}
   \newcommand{\Prod}{\textsf{prod}}
   \newcommand{\Pair}{\textsf{pair}}

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
   ---------------
   \WFE{\Gamma::(x:T)}

.. inference:: W-Local-Def

   \WTEG{t}{T}
   x \not\in \Gamma % \cup E
   -----------------
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
   ------------------------------------------------------
   \WTEG{x}{T}

.. inference:: Const

   \WFE{\Gamma}
   (c:T) \in E~~\mbox{or}~~(c:=t:T) \in E~\mbox{for some $t$}
   ------------------------------------------------------
   \WTEG{c}{T}

.. inference:: Prod-Pro

   \WTEG{T}{s}
   s \in \Sort
   \WTE{\Gamma::(x:T)}{U}{\Prop}
   ------------------------
   \WTEG{\forall~x:T,U}{\Prop}

.. inference:: Prod-Set

   \WTEG{T}{s}
   s \in \{\Prop, \Set\}
   \WTE{\Gamma::(x:T)}{U}{\Set}
   -----------------------
   \WTEG{\forall~x:T,U}{\Set}

.. inference:: Prod-Type

   \WTEG{T}{\Type(i)}
   \WTE{\Gamma::(x:T)}{U}{\Type(i)}
   ---------------------------
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
