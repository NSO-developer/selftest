DIRS = lux

all:
	for d in $(DIRS) ; do \
		$(MAKE) -C $$d all || exit 1; \
	done

clean:
	for d in $(DIRS) ; do \
		$(MAKE) -C $$d clean || exit 1; \
	done

test:
	for d in $(DIRS) ; do \
		$(MAKE) -C $$d test || exit 1; \
	done

desc:
	@for d in $(DIRS) ; do \
		$(MAKE) -sC $$d desc || exit 1; \
	done
