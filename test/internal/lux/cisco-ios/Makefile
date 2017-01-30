all: cisco-ios netsim start

#NCS runtime folder
NCS_RUN = ../../../ncs

build: all

#ncs-netsim add-to-network packages/cisco-ios 1 c;
netsim:
	(cd $(NCS_RUN); \
	if [ ! -d netsim ]; then \
		ncs-netsim create-device packages/cisco-ios c0; \
	else \
		ncs-netsim add-device packages/cisco-ios c0; \
	fi)
	(cd $(NCS_RUN); ncs-netsim ncs-xml-init > ncs-cdb/cisco.xml)

cisco-ios:
	@(cd $(NCS_RUN)/packages; \
	  export PATH=/usr/bin:$${PATH}; \
	  if [ ! -d cisco-ios ]; then \
	  	git clone ssh://git@stash.tail-f.com/ned/cisco-ios.git; \
	   	make -C cisco-ios/src; \
	  fi)

start:
	(cd $(NCS_RUN); \
	 ncs-netsim start)
	echo "request packages reload" | ncs_cli -u admin
	@echo "cisco-ios_netsim_started"
	(cd $(NCS_RUN); \
	 ${NCS_DIR}/bin/ncs_load -l -m -F x -u admin -g admin ncs-cdb/cisco.xml)

stop:
	(cd $(NCS_RUN); \
	ncs-netsim stop c0)

clean:
	(cd $(NCS_RUN); \
	ncs-netsim stop c0; \
	rm -rf ncs-cdb/cisco.xml; \
	rm -rf netsim; \
	rm -rf packages/cisco-ios)

test:
	~/stash.tail-f.com/lux/bin/lux run.lux

