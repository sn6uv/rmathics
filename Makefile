PY = python2
TR = /home/angus/prog/pypy-2.4.0-src/rpython/bin/rpython

all: bin/
	$(PY) $(TR) --output=bin/rmathics main.py

bin/:
	mkdir bin/
