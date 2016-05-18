============
Coq glossary
============

.. glossary::

   βι normal form

      A term is in βι normal form if it cannot be reduced further by simplifying
      application of lambdas (i.e. terms of the form :g:`(fun x => …) …` — this
      is β reduction), nor ``match`` forms on explicit constructors (this is ι
      reduction).  For example, the following term is not in βι normal form,
      since it contains a match on an explicit pair:

      .. coqdoc::

         match (1, 2) with
         | (x, y) => id (x + y)
         end

      One step of ι reduction, followed by one step of β reduction, yields a
      normalized term:

      .. coqtop:: all

         Eval cbv iota in match (1, 2) with
                          | (x, y) => id (x + y)
                          end.

         Eval cbv beta in (fun x y: nat => id (x + y)) 1 2.
