#!/usr/bin/env make

all:
	true

clean:
	rm -f dsave.dat *~ \#*
	cd lib && make clean
	cd modules && make clean

