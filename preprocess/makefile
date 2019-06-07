CC      = g++
CFLAGS  = -O3 -Wall -pedantic -std=c++11
LDFLAGS = -lm

all: preprocess dust

preprocess: preprocess.o cnf_io.o
	$(CC) -o $@ $^ $(LDFLAGS)

%.o: %.cpp
	$(CC) -c $(CFLAGS) $<

.PHONY: clean cleanest

dust:
	rm *.o

clean:
	rm preprocess