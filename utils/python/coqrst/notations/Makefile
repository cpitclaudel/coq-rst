# Parsing compact tactic notation syntax in

TEST_INPUT="unfold {+, @qualid|@string at {+, num}}"

python:
	antlr4 -Dlanguage=Python3 -visitor -no-listener TacticNotations.g

java:
	antlr4 -Dlanguage=Java TacticNotations.g && javac TacticNotations*.java

test: java
	grun TacticNotations top -tree <<< "$(TEST_INPUT)"

gui: java
	grun TacticNotations top -gui <<< "$(TEST_INPUT)"

sample:
	cd ..; python3 -m coqnotations.driver < ../tests/tactics > ../tests/antlr-notations.html
