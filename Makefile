PY = python2

all: bin/
	$(PY) /home/angus/prog/pypy-2.4.0-src/rpython/bin/rpython --output=bin/rmathics main.py 

bin/:
	mkdir bin/
