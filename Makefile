docs:
	make -C sphinx clean html

upload: docs
	rsync -avz --no-o --no-g ./sphinx/_build/html/ athena:~/www/coq-rst/
