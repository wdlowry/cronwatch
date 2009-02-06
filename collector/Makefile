all: collector

collector: collector.sh
	cat collector.sh | sed 's#%QUEUEDIR%#/var/lib/cronwatch/wrapper#' \
	    | awk '/BEGIN_DEBUG/{ while(! /END_DEBUG/){getline;}next} {print}'\
	    > collector
	chmod +x collector

test:
	./test_collector.sh

clean:
	rm -rf collector
