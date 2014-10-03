# -*- coding: utf-8 -*-
"""Command line interface for arcomm"""

import json
import sys
from .api import connect, execute, execute_pool, get_credentials
from .exceptions import ExecuteFailed

def makescript(path=None, variables=None):
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

    try:
        # pylint: disable=import-error
        import jinja2
        replacements = {}
        if variables:
            replacements = json.loads(variables)

        script = "\n".join(script)
        template = jinja2.Template(script)
        script = template.render(replacements)
        script = script.splitlines()
    except ImportError:
        pass

    return script

def main():
    """Main routine"""
    from argparse import ArgumentParser
    parser = ArgumentParser(prog="arcomm")
    arg = parser.add_argument
    arg("hosts", nargs="*")
    arg("--authorize", action="store_true")
    arg("--protocol", default=["capi", "ssh"],
        help=("Set the default protocol or protocols. If more than one is "
              "supplied, they will be tried in order"))
    arg("-u", "--username", help="Specifies the username on the switch")
    arg("-p", "--password",
        help=("Specifies users password.  If not supplied, the user will be "
              "prompted"))
    arg("-a", "--authorize-password", default=None,
        help=("Use if a password for elevated prvilges"))
    arg("-t", "--timeout", type=int, default=300,
        help=("Change the timeout from the default of 300 seconds"))
    arg("--script", help=("Path to a script file containing commands to "
                          "execute. template variables will be processed if "
                          "Jinja2 is installed and `--variables` is also "
                          "supplied on the command line"))
    arg("--variables", help=("Replacements for template variables in script "
                             "file (must be JSON formatted)"))
    args = parser.parse_args()

    if args.authorize and not args.authorize_password:
        args.authorize_password = ""

    creds = get_credentials(username=args.username, password=args.password,
                            authorize_password=args.authorize_password)
    conn = None

    if len(args.hosts) == 1:
        conn = connect(args.hosts[0], creds, protocol=args.protocol,
                       timeout=args.timeout)

    script = makescript(args.script, args.variables)

    if conn:
        try:
            print execute(conn, script)
        except ExecuteFailed as exc:
            print exc.message
    else:
        pool = execute_pool(args.hosts, creds, script, protocol=args.protocol,
                            timeout=args.timeout)
        for host, response in pool:
            print host, ">>>", response

if __name__ == "__main__":
    main()

