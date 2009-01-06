all: wrapper

wrapper: wrapper.sh
	cat wrapper.sh | sed 's#%QUEUEDIR%#/var/lib/cronwatch/wrapper#' \
	    > wrapper
	chmod +x wrapper

test: wrapper
	./test_wrapper.sh

clean:
	rm -rf wrapper
