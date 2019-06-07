.PHONY: all clean

all: proposal

proposal: proposal.tex
	latexmk -f -pdf proposal.tex
	latexmk -c proposal

clean:
	latexmk -c proposal
	rm -rf proposal.pdf
