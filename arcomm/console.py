# -*- coding: utf-8 -*-
"""Command line interface for arcomm"""

import json
import sys
from . import __version__
from .api import connect, execute, execute_pool, get_credentials
from .exceptions import ExecuteFailed

def _makescript(path=None, variables=None):
    """Generate script from a file, list of commands or prompt user for input"""

    script = []

    if path:
        with open(path, "r") as file_handle:
            script = file_handle.read()
            script = script.splitlines()
    else:
        isatty = sys.stdin.isatty()
        if isatty:
            print "Enter commands (one per line)."
            print "Enter '.' alone to send or 'Crtl-C' to quit."
            try:
                while True:
                    line = raw_input('> ')
                    if line == ".":
                        break
                    script.append(line)
            except (KeyboardInterrupt, SystemExit):
                print "Commands aborted."
                sys.exit()
        else:
            for line in sys.stdin:
                script.append(line)

    if variables:
        import jinja2
        replacements = json.loads(variables)
        script = "\n".join(script)
        template = jinja2.Template(script)
        script = template.render(replacements)
        script = script.splitlines()

    return script

def indentblock(text, spaces=0):
    text = text.splitlines() if hasattr(text, "splitlines") else []
    return "\n".join([" " * spaces + line for line in text])

def main():
    """Main routine"""
    from argparse import ArgumentParser
    parser = ArgumentParser(prog="arcomm")
    arg = parser.add_argument
    arg("hosts", nargs="*")
    arg("-v", "--version", help="Display version info")
    arg("--authorize", action="store_true")
    arg("--protocol", default=["eapi", "ssh"],
        help=("Set the default protocol or protocols. If more than one is "
              "supplied, they will be tried in order"))
    arg("--encoding", default="text", help="accepts 'text' or 'json'")
    arg("-u", "--username", help="Specifies the username on the switch")
    arg("-p", "--password",
        help=("Specifies users password.  If not supplied, the user will be "
              "prompted"))
    arg("-a", "--authorize-password", default=None,
        help=("Use if a password is needed for elevated prvilges"))
    arg("-t", "--timeout", type=int, default=300,
        help=("Change the timeout from the default of 300 seconds"))
    arg("--script", help=("Path to a script file containing commands to "
                          "execute. template variables will be processed if "
                          "Jinja2 is installed and `--variables` is also "
                          "supplied on the command line"))
    arg("--variables", help=("Replacements for template variables in script "
                             "file (must be JSON formatted)"))
    args = parser.parse_args()

    if args.version:
        parser.exit(0, __version__)

    if not args.hosts:
        parser.error("At least one host must be specified")

    if args.authorize and not args.authorize_password:
        args.authorize_password = ""

    creds = get_credentials(username=args.username, password=args.password,
                            authorize_password=args.authorize_password)

    script = _makescript(args.script, args.variables)
    pool = execute_pool(args.hosts, creds, script, protocol=args.protocol,
                        timeout=args.timeout, encoding=args.encoding)

    for host, responses in pool:
        print "---"
        if args.encoding == "json":
            print json.dumps({
                  "host": host,
                  "commands": responses.to_dict()
            }, indent=4, separators=(',', ': '))
        else:
            print "host: {}".format(host)
            print "commands:"
            for response in responses:
                print "  - command: {}".format(response.command)
                print "    output: |"
                print indentblock(response.output, spaces=6)
                if response.error:
                    print "    errors: |"
                    print indentblock(response.error, spaces=6)
    print "..."

if __name__ == "__main__":
    main()

