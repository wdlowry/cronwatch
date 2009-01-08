all: wrapper

wrapper: wrapper.sh
	cat wrapper.sh | sed 's#%QUEUEDIR%#/var/lib/cronwatch/wrapper#' \
	    | awk '/BEGIN_DEBUG/{ while(! /END_DEBUG/){getline;}next} {print}'\
	    > wrapper
	chmod +x wrapper

test:
	./test_wrapper.sh

clean:
	rm -rf wrapper
