An experiment in modernizing Coq's manual
=========================================

This repo is an experiment to improve Coq's manual, using a more structured format than LaTeX. For more details about this project, browse the rendered output at http://web.mit.edu/cpitcla/www/coq-rst/index.html

Navigating the code
-------------------

Here's a quick overview of the source tree::

   sphinx                           Documentation directory; each page is a .rst file
   └── _static                        Style and script files

   utils                            Supporting scripts
   ├── python
   │   └── coqrst                     A python package for documenting Coq in rST/Sphinx
   │       ├── coqdoc                   A Coq syntax highlighter based on Coqdoc
   │       ├── notations                A parser for notations using the new notation syntax
   │       └── repl                     A simple Coqtop driver to implement the Coqtop directive
   └── racket                       A (semi-functional) racket version of the notations parser

Browsing the sources is probably the best way to get an idea of how the manual
looks in rST (there's a link on each page in the website above).  To get a good grasp of the code itself, the best starting point is ``utils/python/coqrst/coqdomain.py``.

Emacs comes bundled with a very good rST mode.  Flycheck is a useful extension (see also below), and so is elpy to edit the Python sources.

Building the code
-----------------

Dependencies
~~~~~~~~~~~~

Required on every build
+++++++++++++++++++++++

- Python 3
- The ANTLR runtime
- Sphinx and a few sphinx extensions
- “Pexpect”, a REPL-driving library
- (optional) The “dominate” library for rendering notations to raw HTML (the Sphinx renderer doesn't depend on this)

Quick setup::

   pip3 install sphinx sphinx_rtd_theme pexpect antlr4-python3-runtime

Required for pre-processing
+++++++++++++++++++++++++++

- ANTLR (a parser generator)

Building
~~~~~~~~

From the root folder::

   make docs

… or from the sphinx folder::

   make clean html

Editing the sources
-------------------

Here are a few Emacs macros to make editing nicer:

.. code:: elisp

   (defun ~/coqtop (beg end)
     (interactive (list (region-beginning) (region-end)))
     (replace-regexp "^Coq < " "      " nil beg end)
     (indent-rigidly beg end -3)
     (goto-char beg)
     (insert ".. coqtop:: all\n\n"))

   (defun ~/quote-region-1 (left right &optional beg end count)
     (unless beg
       (if (region-active-p)
           (setq beg (region-beginning) end (region-end))
         (setq beg (point) end nil)))
     (unless count
       (setq count 1))
     (save-excursion
       (goto-char (or end beg))
       (dotimes (_ count) (insert right)))
     (save-excursion
       (goto-char beg)
       (dotimes (_ count) (insert left)))
     (if (and end (characterp left)) ;; Second test handles the ::`` case
         (goto-char (+ (* 2 count) end))
       (goto-char (+ count beg))))

   (defun ~/rst-coq-action ()
     (interactive)
     (pcase (read-char "Command?")
       (?g (~/quote-region-1 ":g:`" "`"))
       (?n (~/quote-region-1 ":n:`" "`"))
       (?t (~/quote-region-1 ":token:`" "`"))
       (?m (~/quote-region-1 ":math:`" "`"))
       (?: (~/quote-region-1 "::`" "`"))
       (?` (~/quote-region-1 "``" "``"))
       (?c (~/coqtop (region-beginning) (region-end)))))

   (with-eval-after-load 'rst
     (define-key rst-mode-map (kbd "<f12>") #'~/rst-coq-action))

Then use `F12` followed by `c`, `g`, `n`, `t`, `m`, `:`, or `\`` to wrap the
current region in various types of blocks.
