#lang racket

(require brag/support)
(require racket/match)
(require scribble/html/xml)
(require scribble/html/html)
(require parser-tools/lex)
(require (prefix-in : parser-tools/lex-sre))

(require "notations.rkt")

(define (tokenize str)
  (let ([ip (open-input-string str)])
    (port-count-lines! ip)
    (define lexer
      (lexer-src-pos
       ["{+" (token 'LBRACE "+")]
       ["{*" (token 'LBRACE "*")]
       ["{?" (token 'LBRACE "?")]
       ["}" (token 'RBRACE)]
       [(:+ whitespace) (token 'WHITESPACE 'wsp)]
       [(:: "@" (:+ (:or alphabetic "_"))) (token 'ID (cons 'id (substring lexeme 1)))]
       [(:+ (:~ (char-set "{}@ "))) (token 'ATOM (cons 'atom lexeme))]
       [(eof) (void)]))
    (define (next-token) (lexer ip))
    next-token))

(define (render ast)
  (match ast
    [(list 'blocks blocks ...) (map render blocks)]
    [(list 'block content) (render content)]
    [(list-rest 'box repeat-marker (cons 'atom sep) 'wsp contents _)
     (span 'class: "repeat-wrapper"
           (samp 'class: "repeat" (render contents))
           (sup repeat-marker)
           (sub sep))]
    [(list-rest 'box repeat-marker 'wsp contents _)
     (span 'class: "repeat-wrapper"
           (samp 'class: "repeat" (render contents))
           (sup repeat-marker))]
    [(cons 'id id) (span 'class: "hole" id)]
    [(cons 'atom str) str]
    ['wsp " "]))

(define pre-parsing-substitutions
  '(("@bindings_list" . "{+ (@id := @val) }")
    ("@qualid_or_string" . "@id|@string")))

(define (substitute str pairs)
  (for ([pair pairs])
    (set! str (string-replace str (car pair) (cdr pair))))
  str)

(define (process str)
  (output-xml
   (p 'class: "notation"
      (render
       (syntax->datum ;; Probably shouldn't be use
        (parse
         (tokenize
          (substitute str pre-parsing-substitutions))))))))

;; (define s "apply {+, @term with {+ (@id := @val) } } in {+, @hyp }")
;; (define ss "apply {+ (@id := @val) }")
;; (define t (tokenize ss))
;; (t)

;; (process "{? 0 or 1} {+ one or more} {* any number of time}")
;; (display "<hr/>\n")
;; (process "rewrite {? ->} {+, @term}")
;; (display "<hr/>\n")

(display "<hr/>\n")
(process "apply {+, @term with {+ (@id := @val) } } in {+, @hyp }")
(display "<hr/>\n")
(process "Global Arguments qualid {+ @name%@scope}.")
(display "<hr/>\n")
(process "set (@ident {+ @binder} := @term) in {+ @hyp}")
(display "<hr/>\n")
(process "unfold {+, @qualid|@string at {+, num}}")
(display "<hr/>\n")
(process "generalize {+, @term at {+ @num} as @ident}")
(display "<hr/>\n")

(for ([tac (file->lines "tactics")])
  (with-handlers ([(lambda (v) #t) (lambda (v) #t)])
    (when (string-contains? tac "{")
      (process tac)
      (display "<hr/>\n"))))
