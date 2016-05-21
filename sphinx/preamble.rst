.. only:: html

   .. preamble::

      \def\ensuremath#1{#1}

.. preamble::

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
