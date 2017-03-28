# -*- coding: utf-8 -*-

# Copyright (c) 2016 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""Command line interface for arcomm"""

import getpass
import json
import re
import sys
import yaml

import arcomm

def main():
    from argparse import ArgumentParser
    parser = ArgumentParser(prog="arcomm")
    arg = parser.add_argument

    arg("endpoints", nargs="*")

    arg("-v", "--version", action="store_true", help="display version info")

    arg("--protocol", help=("set the protocol. By default 'eapi' is used."),
        choices=["eapi", "eapi+https", "mock", "ssh"])

    arg("--encoding", default="text", choices=["json", "text"],
        help="control output formatting")

    arg("-u", "--username", help="specifies the username on the switch")

    arg("-p", "--password", default="", help="specifies users password")
    arg("-s", "--secret-file", help="read passwords from file")
    arg("--authorize", action="store_true")

    arg("-a", "--authorize-password", default=None,
        help=("use if a password is needed for elevated prvilges"))

    arg("-t", "--timeout", type=int, default=30,
        help=("change the timeout from the default of 30 seconds"))

    arg("--hosts-file", help="path to file containing list of hosts")

    arg("--script", help=("path to a script file containing commands to "
                          "execute. template variables will be processed if "
                          "Jinja2 is installed and `--variables` is also "
                          "supplied on the command line"))

    arg("--variables", help=("replacements for template variables in script "
                             "file (must be JSON formatted)"))

    arg("--no-verify", action="store_true", help=("when using eAPI over HTTPS, "
                                                  "don't verify certificate"))

    args = parser.parse_args()

    options = {}
    endpoints = []

    if args.version:
        parser.exit(0, arcomm.__version__ + "\n")

    if args.hosts_file:
        endpoints = arcomm.util.load_endpoints(args.hosts_file)
    else:
        endpoints = args.endpoints

    if not endpoints:
        raise ValueError('no endpoints')

    if args.authorize_password:
        options['authorize'] = args.authorize_password
    elif args.authorize:
        options['authorize'] = ''

    username = args.username
    password = args.password

    if not username:
        username = getpass.getuser()

    if args.secret_file:
        with open(args.secret_file, "r") as stream:
            secrets = yaml.load(stream)
            password = secrets.get(username)

    if not password:
        password = getpass.getpass("password for {}: ".format(username))

    options['creds'] = arcomm.BasicCreds(args.username, password)

    if args.protocol:
        options['protocol'] = args.protocol

    options['timeout'] = args.timeout

    options['encoding'] = args.encoding

    options['verify'] = not args.no_verify

    script = []

    if args.script:
        with open(args.script, 'r') as fh:
            script = fh.read()
            script = script.splitlines()
    elif not sys.stdin.isatty():
        for line in sys.stdin:
            script.append(line)
    else:
        isatty = sys.stdin.isatty()
        if isatty:
            print("Enter commands (one per line).")
            print("Enter '.' alone to send or 'Crtl-C' to quit.")
            try:
                while True:
                    line = raw_input('> ')
                    if line == ".":
                        break
                    script.append(line)
            except (KeyboardInterrupt, SystemExit):
                print("Commands aborted.")
                sys.exit()
        else:
            for line in sys.stdin:
                script.append(line)

    if args.variables:
        import jinja2
        replacements = json.loads(args.variables)
        script = "\n".join(script)
        template = jinja2.Template(script)
        script = template.render(replacements)
        script = script.splitlines()

    for res in arcomm.batch(endpoints, script, **options):
        print('---')
        if options['encoding'] == 'json':
            print(res.to_json())
        else:
            print(res.to_yaml())
    print('...')


if __name__ == "__main__":
    main()
