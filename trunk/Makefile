# Makefile for cronwatch
# $Id$

CHANGEFILES=cronwatch.py test_cronwatch.py
CHANGEFILESCONFIG=simpleconfig.py test_simpleconfig.py

clean:
	rm -rf work

test:
	python test_cronwatch.py

testloop:
	unset MD5CMD ; \
	for CMD in /usr/bin/md5sum /sbin/md5 /usr/local/bin/md5sum; do \
	if [ -f "$$CMD" ] ; then MD5CMD="$$CMD"; fi; done ; \
	if [ -z "$$MD5CMD" ] ; then \
	echo 'ERROR: Could not find md5sum or md5!'; exit 1; fi ; \
	make test && true; sleep 1 ; \
	MD5=`$$MD5CMD $(CHANGEFILES)`; while true; do \
	NEWMD5=`$$MD5CMD $(CHANGEFILES)`; \
	if [ ! "$$MD5" = "$$NEWMD5" ]; then \
	make test && true; fi; sleep 1; MD5="$$NEWMD5"; done

testconfig:
	python test_simpleconfig.py

testloopconfig:
	unset MD5CMD ; \
	for CMD in /usr/bin/md5sum /sbin/md5 /usr/local/bin/md5sum; do \
	if [ -f "$$CMD" ] ; then MD5CMD="$$CMD"; fi; done ; \
	if [ -z "$$MD5CMD" ] ; then \
	echo 'ERROR: Could not find md5sum or md5!'; exit 1; fi ; \
	make testconfig && true; sleep 1 ; \
	MD5=`$$MD5CMD $(CHANGEFILESCONFIG)`; while true; do \
	NEWMD5=`$$MD5CMD $(CHANGEFILESCONFIG)`; \
	if [ ! "$$MD5" = "$$NEWMD5" ]; then \
	make testconfig && true; fi; sleep 1; MD5="$$NEWMD5"; done
