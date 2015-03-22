TR = rpython

all: bin/
	$(TR) --output=bin/kernel kernel.py

bin/:
	mkdir bin/
