all: packages/selftest packages/selfservice

packages/selftest:  ncs-setup
	rm -rf packages/selftest
	(cd packages; ln -s ../../../../selftest .)
	(cd packages/selftest/src; make all)

packages/selfservice:  ncs-setup
	rm -rf packages/selfservice
	(cd packages; ln -s ../../package/selfservice .)

ncs-setup:
	ncs-setup --dest .

start:
	`which ncs` || exit 0
	`which ncs-netsim` start || exit 0

stop:
	`which ncs` --stop
	`which ncs-netsim` stop

clean:
	rm -rf README.ncs logs ncs-cdb ncs.conf packages/* scripts state

cli:
	ncs_cli -u admin
