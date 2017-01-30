SHELL := /bin/bash

DIRS = cisco-ios

#pvsn=$(shell grep 'package-version' ../../../package-meta-data.xml \
#	| sed -e 's\#<package-version>\([0-9\.]*\)</package-version>\#\1\#' -e 's/ //g')
#ncsvsn=$(shell ncs --version)

all:
	for d in $(DIRS) ; do \
		$(MAKE) -C $$d all || exit 1; \
	done

#cisco-ios-test:
#	@(export PATH=/usr/bin:$${PATH}; \
#	make -C cisco-ios/src

clean:
	for d in $(DIRS) ; do \
		$(MAKE) -C $$d clean || exit 1; \
	done

test:
	for d in $(DIRS) ; do \
		$(MAKE) -C $$d test || exit 1; \
	done

desc:
	for d in $(DIRS) ; do \
		$(MAKE) -C $$d desc || exit 1; \
	done
