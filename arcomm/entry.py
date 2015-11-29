# -*- coding: utf-8 -*-
"""Command line interface for arcomm"""

import re
import sys
import arcomm

def indentblock(text, spaces=0):
    text = text.splitlines() if hasattr(text, 'splitlines') else []
    return '\n'.join([' ' * spaces + line for line in text])

def to_yaml(response):
    host = response.host
    status = response.status

    # if args.encoding == "json":
    #     result = {"host": host}
    #     if status == 'failed':
    #         result["error"] = error
    #     if hasattr(responses, "to_dict"):
    #         result["commands"] = responses.to_dict()
    #     print json.dumps(result, indent=4, separators=(',', ': '))
    # else:
    print '---'
    print 'host: {}'.format(host)
    print 'status: {}'.format(status)
    if status == 'failed':
        print 'failed: |'
        print indentblock(str(response), spaces=2)
    else:
        print 'commands:'
        for r in response:
            print '  - command: {}'.format(r.command)
            print '    output: |'
            print indentblock(r.output, spaces=6)
            if r.error:
                print '    errors: |'
                print indentblock(r.error, spaces=6)

def main():
    from argparse import ArgumentParser
    parser = ArgumentParser(prog="arcomm")
    arg = parser.add_argument

    arg("endpoints", nargs="*")

    arg("-v", "--version", action="store_true", help="Display version info")

    arg("--protocol", default=["eapi", "ssh"],
        help=("Set the default protocol or protocols. If more than one is "
              "supplied, they will be tried in order"))

    arg("--encoding", default="text", choices=["json", "text"],
        help="Control output formatting")

    arg("-u", "--username", default="admin",
        help="Specifies the username on the switch")

    arg("-p", "--password", default="",
        help=("Specifies users password.  If not supplied, the user will be "
              "prompted"))

    arg("--authorize", action="store_true")

    arg("-a", "--authorize-password", default=None,
        help=("Use if a password is needed for elevated prvilges"))

    arg("-t", "--timeout", type=int, default=30,
        help=("Change the timeout from the default of 30 seconds"))

    arg("--hosts-file", help="Path to file containing list of hosts")

    arg("--script", help=("Path to a script file containing commands to "
                          "execute. template variables will be processed if "
                          "Jinja2 is installed and `--variables` is also "
                          "supplied on the command line"))
    #
    # arg("--variables", help=("Replacements for template variables in script "
    #                          "file (must be JSON formatted)"))

    args = parser.parse_args()

    if args.version:
        parser.exit(0, arcomm.__version__ + "\n")

    if args.hosts_file:
        args.hosts = arcomm.util.load_endpoints(args.hosts_file)

    if args.authorize and not args.authorize_password:
        args.authorize_password = ""

    creds = arcomm.BasicCreds(args.username, args.password)
    script = []
    if args.script:
        with open(path, 'r') as fh:
            script = fh.read()
            script = script.splitlines()
    elif not sys.stdin.isatty():
        for line in sys.stdin:
            script.append(line)

    if script:
        for res in arcomm.pool(args.endpoints, script):
            to_yaml(res)
        print '...'
    # else:
    #     cli = arcomm.Cli()
    #     cli.cmdloop()

if __name__ == "__main__":
    main()
