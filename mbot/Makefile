# Mbot Makefile
APPLICATION = mbot
VERSION = 0.2
SRC = *.py
CONFFILE = *.conf

clean:
	-rm *~ *pyc

release:
	rm -fr $(APPLICATION)-$(VERSION)
	mkdir -p $(APPLICATION)-$(VERSION)
	@tar zcf tmp.tgz $(SRC) $(CONFFILE) doc/*.lyx doc/Makefile doc/*.hva \
		 			LICENSE AUTHORS INSTALL README* TODO Makefile \
					deps news/*.sql news/*.py tests/news/*.php tests/news/*.inc tests/news/*.js
	tar -C $(APPLICATION)-$(VERSION) -zxf tmp.tgz
	tar zvcf  $(APPLICATION)-$(VERSION).tar.gz $(APPLICATION)-$(VERSION)
	rm -fr $(APPLICATION)-$(VERSION)
	rm -fr tmp.tgz

