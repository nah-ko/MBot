# $Id$

SOURCE=$(wildcard *.lyx)
DOCUMENT=$(basename $(SOURCE))
TARGET=$(SOURCE:.lyx=.pdf) $(SOURCE:.lyx=.html)

all: man $(TARGET)

man: mbot.1 mbot.conf.5

mbot.1: mbot.1.sgml
	docbook-to-man $? > $@ 2>&1

mbot.conf.5: mbot.conf.5.sgml
	docbook-to-man $? >$@ 2>&1

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
	-rm mbot.1 mbot.conf.5
	-rm $(DOCUMENT).tex $(DOCUMENT).html $(DOCUMENT).ps $(DOCUMENT).pdf
