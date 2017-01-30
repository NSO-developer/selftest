DIRS = external internal

ifeq ($(BUILD_JOB),realhw)
DIR = external
endif

ifeq ($(BUILD_JOB),simulated)
DIR = internal
endif

ifeq ($(BUILD_JOB),)
DIR = internal
endif

all:
	(cd ncs ; make all)
	(cd package ; make all)
	$(MAKE) -C $(DIR) all || exit 1

clean:
	(cd ncs ; make clean)
	(cd package ; make clean)
	$(MAKE) -C $(DIR) clean || exit 1

start:
	(cd ncs ; make start)

stop:
	(cd ncs ; make stop)

ncs-cli:
	(cd ncs ; make cli)

test:
	$(MAKE) -C $(DIR) test || exit 1

fett:
	(echo $(BUILD_JOB) $(DIR))



