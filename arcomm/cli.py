# -*- coding: utf-8 -*-

"""

Sample Session:

    arcomm[]# set logging ~/arcomm-cli.log
    arcomm[]# add endpoints vswitch1 {protocol: ssh}
    arcomm[vswitch1]# execute show version
    ---
    host: vswitch1
    status: ok
    commands:
      - command: show version
        output: |
          Arista vEOS
          Hardware version:
          Serial number:
          System MAC address:  0800.2776.48c5

          Software image version: 4.15.2F
          Architecture:           i386
          Internal build version: 4.15.2F-2663444.4152F
          Internal build ID:      0ebbad93-563f-4920-8ecb-731057802b9c

          Uptime:                 2 days, 19 hours and 29 minutes
          Total memory:           1897596 kB
          Free memory:            121800 kB

    ...
    arcomm[vswitch1,vswitch2]# add endpoints vswitch2
    arcomm[vswitch1,vswitch2]# show endpoints
    vswitch1 {protocol: ssh}
    vswitch2
    arcomm[vswitch1,vswitch2]# configure {rollback: 1}
    > ip host dummy 127.0.0.1
    > .
    Session-id: 12345678-1234-5678-1234-567812345678
    arcomm[vswitch2]# rollback 12345678-1234-5678-1234-567812345678
"""

import cmd
import re
import readline
import yaml

import arcomm.api as api
from arcomm.util import mpop

PROMPT_TEMPLATE = 'arcomm[{}]# '
PROMPT_LEN = 25


class Cli(cmd.Cmd):
    """
    """

    def do_exit(self, line):
        return True

    def preloop(self):
        self.prompt = PROMPT_TEMPLATE.format('')

    def default(self, line):
        """
        Called on an input line when the command prefix is not recognized.
        """
        self.stdout.write('% Unknown synta: {}\n'.format(line))

    def emptyline(self):
        return

    # def do_append(self, line):
    #     print "appending", line
    #
    # def do_clear(self, line):
    #     pass

    def do_configure(self, line):
        pass

    def do_execute(self, line):
        pass

    def do_save(self, line):
        pass

    # def do_set(self, line):
    #     """
    #     line: set <module> <module-args>
    #     """
    #     pass

    def do_EOF(self, line):
        return True

    # def do_show(self, line):
    #     pass

    def parseline(self, line):
        """
        parse this:

            set endpoints vswitch1 vswitch1 {protocol: ssh, creds: [admin, '']}
        """
        if not line:
            return None, None, line

        tokens = re.split('[\s,;\|]+', line)
#        for item in tokens:
        cmd = tokens.pop(0)

        #print "Tokens:", tokens

        return cmd, tokens, line

    def onecmd(self, line):
        """Interpret the argument as though it had been typed in response
        to the prompt.

        This may be overridden, but should not normally need to be;
        see the precmd() and postcmd() methods for useful execution hooks.
        The return value is a flag indicating whether interpretation of
        commands by the interpreter should stop.

        """
        cmd, arg, line = self.parseline(line)

        if not line:
            return

        if cmd is None:
            return self.default(line)

        self.lastcmd = line

        if line == 'EOF' :
            self.lastcmd = ''

        if cmd == '':
            return self.default(line)

        else:
            try:
                func = getattr(self, 'do_' + cmd)
            except AttributeError:
                return self.default(line)
            return func(arg)

    # def precmd(self, line):
    #     print "pre..."
    #     tokens = re.split('[\s,;\|]+', line)
    #     return tokens

class Plugin(object):
    """
    """

    keywords = {}

    def help(self):
        raise NotImplementedError

    def append(self, params):
        raise NotImplementedError

    def clear(self, params):
        raise NotImplementedError

    def remove(self, params):
        raise NotImplementedError

    def set(self, params):
        raise NotImplementedError

# class LoggerPlugin(Plugin):
#     pass
#
# class EndpointsPlugin(Plugin):
#     def __init__(self):
#         self.keywords = {
#             'username': r'\w+',
#             'password': r'\S+',
#             'protocol': r'\w+'
#         }
#
#     def set(self, params):
#         self.parse_params(params)
#
#     def _update(self, endpoints, action='add'):
#         endpoints = re.split(r'[\s,;\|]+', endpoints)
#
#         if action not in ('add', 'del'):
#             print '% action \'{}\' is invalid'.format(action)
#             return
#
#         for endpoint in endpoints:
#             if action == 'add':
#                 if endpoint in self.endpoints:
#                     print '% {} is already added'.format(endpoint)
#                 else:
#                     self.endpoints.append(endpoint)
#             elif  action == 'del':
#                 try:
#                     if re.match(r'\d+', endpoint):
#                         del(self.endpoints[int(endpoint)])
#                     else:
#                         self.endpoints.remove(endpoint)
#                 except (IndexError, ValueError) as exc:
#                     print '% {} not in endpoints'.format(endpoint)
#
#         context = ','.join(self.endpoints)
#         if len(context) > self.prompt_len:
#             context = (context[:(self.prompt_len-3)] + '...')
#
#         self.prompt = self.prompt_t.format(context)
#
# PLUGINS = {
#     'endpoints': EndpointsPlugin()
# }
if __name__ == '__main__':
    cli = Cli()
    cli.cmdloop()
"""
    prompt_t = 'arcomm[{}]# '
    prompt_len = 25
    endpoints = []



    def preloop(self):
        self.prompt = self.prompt_t.format('')

    def emptyline(self):
        return

    def do_list(self, line):
        for e in self.endpoints:
            print e

    def do_exit(self, line):
        return True

    def do_add(self, endpoints):
        self.update(endpoints, 'add')

    def do_del(self, endpoints):
        self.update(endpoints, 'del')

    def do_execute(self, line):
        commands = []

        if line:
            commands.append(line)
        else:
            print 'Enter commands (one per line).'
            print 'Enter \'.\' alone to send'

            try:
                while True:
                    line = raw_input('> ')
                    if line == ".":
                        break
                    commands.append(line)
            except KeyboardInterrupt:
                print '% Commands aborted.'
                return

        for res in api.pool(self.endpoints, commands):
            print str(res)
"""
