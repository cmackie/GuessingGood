.PHONY: all clean

all: milestone

milestone: milestone.tex
	latexmk -f -pdf milestone.tex
	latexmk -c milestone

clean:
	latexmk -c milestone
	rm -rf milestone.pdf
