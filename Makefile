docs:
	make -C sphinx clean html xelatexpdf

upload: docs
	cp ./sphinx/_build/latex/Coq85.pdf ./sphinx/_build/html/
	rsync -avz --no-o --no-g ./sphinx/_build/html/ athena:~/www/coq-rst/
