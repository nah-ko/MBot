# $Id$

SOURCE=$(wildcard *.lyx)
DOCUMENT=$(basename $(SOURCE))
TARGET=$(SOURCE:.lyx=.pdf) $(SOURCE:.lyx=.html)

all: $(TARGET)

%.ps:%.lyx
	lyx -e ps $<

%.pdf:%.lyx
	lyx -e pdf $<

%.tex:%.lyx
	lyx -e latex $<

%.html:%.tex
	hevea -fix -francais ./url-fix.hva $<
	-rm *.htoc *.haux

clean:
	-rm *~
	-rm $(DOCUMENT).tex $(DOCUMENT).html $(DOCUMENT).ps $(DOCUMENT).pdf
