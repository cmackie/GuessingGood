.PHONY: all clean

all: main

main: main.tex
	latexmk -f -pdf main.tex
	latexmk -c main

clean:
	latexmk -c main
	rm -rf main.pdf
