# -*- mode: python; python-indent: 4 -*-
import ncs
import ncs.experimental
import _ncs
from ncs.dp import Action
import re
from time import strftime
import time


class RunAction(Action):
    @Action.action
    def cb_action(self, uinfo, name, kp, input, output):
        #if the your actions take more than 240 seconds, increase the action_set_timeout
        _ncs.dp.action_set_timeout(uinfo,240)
        with ncs.maapi.single_write_trans(uinfo.username, uinfo.context) as trans:
            action = ncs.maagic.get_node(trans, kp)
            self.log.info('actions: ', name)
            output.result = ''
            #time.sleep(210)
            # if we run a specific command
            if input.command:
                run_command(action, input.command, trans, output, self)
            else:
                # If no command is specified we will run all the tests
                for cmd in action.commands:
                    run_command(action, cmd.name, trans, output, self)
            self.log.info('commiting action: ', name)
            trans.apply()
            self.log.info('commiting done action: ', name)


def set_status(service, command, status):
    # set the operational values status and time.
    if hasattr(service, 'selftest_result'):
        cmd_result = service.selftest_result.command.create(command)
        cmd_result.result = status
        cmd_result.time = strftime("%Y-%m-%d %H:%M:%S")
    else:
        print('selftest-result grouping has not been referenced under ', str(service.name))


def run_command(action, cmd_string, trans, output, self):
    devices = action.commands[cmd_string].devices
    #if normal live-status exec command
    if action.commands[cmd_string].command and action.commands[cmd_string].arguments:
        command = action.commands[cmd_string].command
        arguments = action.commands[cmd_string].arguments
        result = '\noutput from ' + command.string
    else:
        #if juniper RPC
        print('flippin junos ' + cmd_string)
        rpc = action.commands[cmd_string].ping
        result = '\noutput from ' + cmd_string
    fail_regexp = action.commands[cmd_string].failstring

    for device in devices:
        result += '\ndevice: ' + device + '\n'
        root = ncs.maagic.get_root(trans)
        device_module = root.ncs__devices.device[device].module
        if 'junos-rpc' in device_module:
            self.log.info(device, ' is a juniper-junos device')
            # action_input = device.live_status.vrp_stats__exec[command].get_input()
            # action_input.args = input_args
            # output = device.live_status.vrp_stats__exec[command](action_input)
            result += 'junos'
        else:
            result += run_livestatus_exec(device, command.string, arguments, trans, self)
    self.log.info('result', result)
    # ERROR means an exception was thrown. Could be that the device was down etc.
    search_result = re.search('ERROR', result)
    m = ncs.maapi.Maapi()
    try:
        service_kpath = m.xpath2kpath(str(action.service))
        service = ncs.maagic.get_node(trans, service_kpath, shared=False)
    except KeyError:
        output.result = "Error: wrong key in path (i.e no service found): " + str(action.service)
        return

    if search_result:
        self.log.info('found ERROR : ', str(search_result.group()))
        set_status(service, cmd_string, 'FAIL')
    else:
        # if no fail_regexp then just let it pass
        if fail_regexp:
            search_result = re.search(fail_regexp, result)
            if search_result:
                set_status(service, cmd_string, 'FAIL')
            else:
                set_status(service, cmd_string, 'OK')
        else:
            set_status(service, cmd_string, 'OK')
    output.result += result
    # return output


def run_livestatus_exec(device_name, command, arguments, trans, self):
    root = ncs.maagic.get_root(trans)
    device = root.ncs__devices.device[device_name]
    input_args = arguments.split(' ')
    error_string = ''
    for module in device.module:
        #Try/catch so that it continues with all the tests even though one device is down.
        try:
            if module.name == 'tailf-ned-cisco-ios':
                self.log.info(device_name, ' is a cisco-ios device')
                action_input = device.live_status.ios_stats__exec[command].get_input()
                action_input.args = input_args
                output = device.live_status.ios_stats__exec[command](action_input)
            elif module.name == 'tailf-ned-cisco-ios-xr':
                self.log.info(device_name, ' is a cisco-iosxr device')
                action_input = device.live_status.cisco_ios_xr_stats__exec[command].get_input()
                action_input.args = input_args
                output = device.live_status.cisco_ios_xr_stats__exec[command](action_input)
            elif module.name == 'tailf-ned-alu-sr':
                self.log.info(device_name, ' is a alu-sr device')
                action_input = device.live_status.alu_sr_stats__exec[command].get_input()
                action_input.args = input_args
                output = device.live_status.alu_sr_stats__exec[command](action_input)
            elif module.name == 'tailf-ned-huawei-vrp':
                self.log.info(device_name, ' is a huawei-vrp device')
                action_input = device.live_status.vrp_stats__exec[command].get_input()
                action_input.args = input_args
                output = device.live_status.vrp_stats__exec[command](action_input)

        except Exception, e:
            self.log.info(device_name, " ERROR: ", str(e))
            error_string = "ERROR: " + str(e)

    # check if its a string or an object.
    if error_string:
        return error_string
    else:
        return output.result


# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class Selftest(ncs.application.Application):
    def setup(self):
        # The application class sets up logging for us. Is is accessible
        # through 'self.log' and is a ncs.log.Log instance.
        self.log.info('Selftest RUNNING')
        self.register_action('selftest', RunAction)

    def teardown(self):
        self.log.info('Selftest FINISHED')
