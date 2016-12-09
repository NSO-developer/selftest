#### Selftest for services

This package will help you to easily create service self-test commands. It runs the commands via the live-status exec action.

Today it supports ping and show commands for cisco-ios, cisco-iosxr and alu-sr.

Short demo of it can be found at (password: aBGAd5ky): https://cisco.webex.com/ciscosales/lsr.php?RCID=1314e8a268a442f59ec72d46e95a5dcd

An example could be to show some interface status and see if it is up or down, or maybe ping between CPE:s to check VPN connectivity.

##### Example

```
admin@ncs% show selftest
selftest selftest-volvo {
    service /l3vpn:vpn/l3vpn:l3vpn[l3vpn:name='volvo'];
    commands show-interface {
        devices    [ ce0 ];
        command    show;
        arguments  "interface GigabitEthernet1";
        failstring "line protocol is down";
    }
}
```
The failstring can be any python accepted regular expression, if the string is found it will consider the action as failed (i.e setting the action status to fail).

Ive also included a small kicker example to automatically run the tests after a service has been provisioned. When executed via the kicker it will run all the tests under commands.

To make it work.

Update your service Makefile to include the selftest yang
```
YANGPATH = --yangpath yang --yangpath ../../selftest/src/yang
```
And also add the operational values to your service with "uses selftest:selftest-result;"

Something like
```yang
  import selftest {
    prefix selftest;
  }

  container vpn {

    list l3vpn {
      description "Layer3 VPN";

      uses selftest:selftest-result;

      key name;
      leaf name {
        tailf:info "Unique service id";
        tailf:cli-allow-range;
        type string;
      }

```


compile and reload NSO.

create your service instance:
```
ncs_cli -u admin
configure
set vpn l3vpn volvo as-number 65001
set vpn l3vpn volvo endpoint c1 ce device ce0
set vpn l3vpn volvo endpoint c1 ce local interface-name GigabitEthernet
set vpn l3vpn volvo endpoint c1 ce local interface-number 1
set vpn l3vpn volvo endpoint c1 ce local ip-address 192.168.0.1
set vpn l3vpn volvo endpoint c1 ce link interface-name GigabitEthernet
set vpn l3vpn volvo endpoint c1 ce link interface-number 0/2
set vpn l3vpn volvo endpoint c1 ce link ip-address 10.1.1.1
set vpn l3vpn volvo endpoint c1 pe device pe2
set vpn l3vpn volvo endpoint c1 pe link interface-name GigabitEthernet
set vpn l3vpn volvo endpoint c1 pe link interface-number 0/0/0/1
set vpn l3vpn volvo endpoint c1 pe link ip-address 10.1.1.2
set vpn l3vpn volvo endpoint c2 ce device ce2
set vpn l3vpn volvo endpoint c2 ce local interface-name GigabitEthernet
set vpn l3vpn volvo endpoint c2 ce local interface-number 2
set vpn l3vpn volvo endpoint c2 ce local ip-address 192.168.1.1
set vpn l3vpn volvo endpoint c2 ce link interface-name GigabitEthernet
set vpn l3vpn volvo endpoint c2 ce link interface-number 0/1
set vpn l3vpn volvo endpoint c2 ce link ip-address 10.2.1.1
set vpn l3vpn volvo endpoint c2 pe device pe2
set vpn l3vpn volvo endpoint c2 pe link interface-name GigabitEthernet
set vpn l3vpn volvo endpoint c2 pe link interface-number 0/0/0/2
set vpn l3vpn volvo endpoint c2 pe link ip-address 10.2.1.2
commit
```
Create your test command.
```
ncs_cli -u admin
configure
set selftest selftest-volvo service /l3vpn:vpn/l3vpn:l3vpn[l3vpn:name='volvo']
set selftest selftest-volvo commands show-interface devices [ ce0 ]
set selftest selftest-volvo commands show-interface command show
set selftest selftest-volvo commands show-interface arguments "interface GigabitEthernet1"
set selftest selftest-volvo commands show-interface failstring "line protocol is down"
commit
```
You can now try your self-test action

```
admin@ncs% request selftest selftest-volvo execute
result
output from show
device: ce0

GigabitEthernet1 is up, line protocol is up
  Hardware is CSR vNIC, address is 000c.296d.6a92 (bia 000c.296d.6a92)
  Internet address is 10.147.46.46/24
  MTU 1500 bytes, BW 1000000 Kbit/sec, DLY 10 usec
  ...
  ...
```

The last test result will be saved (operational values)
```
admin@ncs> show vpn l3vpn volvo selftest-result
NAME            RESULT  TIME
---------------------------------------------
show  OK    2016-09-14 09:14:40
```

##### Create selftest at service creation

This selftest can and should of course be created via the normal service template so that each service instance has its own tests.
```xml
admin@ncs% show selftest selftest-volvo | display xml
<config xmlns="http://tail-f.com/ns/config/1.0">
  <selftest xmlns="http://cisco.com/self-test-action">
    <name>l3vpn-volvo</name>
    <service>/l3vpn:vpn/l3vpn:l3vpn[l3vpn:name='volvo']</service>
    <commands>
      <name>show-interface</name>
      <devices>ce0</devices>
      <command>show</command>
      <arguments>interface GigabitEthernet1</arguments>
      <failstring>line protocol is down</failstring>
    </commands>
  </selftest>
</config>
```
Copy the XML and add it to your service template with the correct variables etc



```xml
vi packages/l3vpn/templates/l3vpn.xml
<config xmlns="http://tail-f.com/ns/config/1.0">
  <selftest xmlns="http://cisco.com/self-test-action">
    <name>l3vpn-{/name}</name>
    <service>/l3vpn:vpn/l3vpn:l3vpn[l3vpn:name={/name}]</service>
    <commands>
      <name>local-if-line-status-{/endpoint/ce/device}</name>
      <devices>{device}</devices>
      <command>show</command>
      <arguments>interface {local/interface-name}{local/interface-number}</arguments>
      <failstring>line protocol is down</failstring>
    </commands>
  </selftest>
....
```
If you like this can be automatically executed via a Kicker (experimental feature in NSO version > 4.2)

Enable the kicker
```xml
vi ncs.conf
  <hide-group>
       <name>debug</name>
  </hide-group>
```
```
ncs --reload
```
```
ncs_cli -u admin
unhide debug
configure

set kickers data-kicker selftest-for-l3vpn monitor /l3vpn:vpn/l3vpn:l3vpn/l3vpn:as-number
set kickers data-kicker selftest-for-l3vpn kick-node /selftest:selftest[name=concat('l3vpn-',current()/../name)]
set kickers data-kicker selftest-for-l3vpn action-name execute

commit
show kickers
data-kicker selftest-for-l3vpn {
    monitor     /l3vpn:vpn/l3vpn:l3vpn/l3vpn:as-number;
    kick-node   /selftest:selftest[name=current()/../name];
    action-name execute;
}

```
Test that the kicker works
```
delete vpn l3vpn volvo
commit no-network
rollback
commit no-network


run show vpn l3vpn volvo selftest-result
NAME                RESULT  TIME
-------------------------------------------------
local-if-line-status-ce0  OK      2016-10-26 14:52:17
local-if-line-status-ce2  FAIL    2016-10-26 14:52:18
```

### Contact

Contact Hakan Niska <hniska@cisco.com> with any suggestions or comments. If you find any bugs please fix them and send me a pull request.
