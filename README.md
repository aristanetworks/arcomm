ArComm
======

Enable communications with Arista switches using a simple API or command line
utility

Installation
------------

    pip install git+https://github.com/aristanetworks/arcomm.git

or

    git clone git@github.com:aristanetworks/arcomm.git
    cd arcomm
    python setup.py install

Console Usage
-------------

    $ arcomm -h
    usage: arcomm [-h] [--authorize] [--protocol PROTOCOL] [-u USERNAME]
                  [-p PASSWORD] [-a AUTHORIZE_PASSWORD] [-t TIMEOUT]
                  [--script SCRIPT] [--variables VARIABLES]
                  [hosts [hosts ...]]

    positional arguments:
      hosts

    optional arguments:
      -h, --help            show this help message and exit
      --authorize
      --protocol PROTOCOL   Set the default protocol or protocols. If more than
                            one is supplied, they will be tried in order
      -u USERNAME, --username USERNAME
                            Specifies the username on the switch
      -p PASSWORD, --password PASSWORD
                            Specifies users password. If not supplied, the user
                            will be prompted
      -a AUTHORIZE_PASSWORD, --authorize-password AUTHORIZE_PASSWORD
                            Use if a password for elevated prvilges
      -t TIMEOUT, --timeout TIMEOUT
                            Change the timeout from the default of 300 seconds
      --script SCRIPT       Path to a script file containing commands to execute
                            template variables will be processed if Jinja2 is
                            installed and `--variables` is also supplied on the
                            command line
      --variables VARIABLES
                            Replacements for template variables in script file
                            (must be JSON formatted)

Console Example
---------------

    $ arcomm spine2a
    Please enter username [jmather]:admin
    Password for admin:
    Enter commands (one per line).
    Enter '.' alone to send or 'Crtl-C' to quit.
    > show clock
    > .
    spine2a (command-api)>show clock
    Fri Jul 25 05:32:51 2014
    Timezone: UTC
    Clock source: local

or pipe in the commands...

    $ echo "show clock" | arcomm spine2a -u admin -p ""
    spine2a (command-api)>show clock
    Fri Jul 25 05:33:21 2014
    Timezone: UTC
    Clock source: local

even multiple hosts in parallel...

    $ echo "show ip bgp summary | include {{filter}}" | \
    > arcomm spine1a spine2a -u admin -p ""--variables='{"filter": "Active"}' \
    > --authorize
    spine2a >>> spine2a (command-api)#enable
    spine2a (command-api)#show ip bgp summary | include Active
    172.16.121.3     4  64521         0         0    0    0 13:07:17 Active

    spine1a >>> spine1a (command-api)#enable
    spine1a (command-api)#show ip bgp summary | include Active
    172.16.111.3     4  64521         0         0    0    0 14:46:48 Active


API Usage
---------

    >>> import arcomm
    >>> creds = arcomm.get_credentials(username="admin", password="",
    ...                                authorize_password="s3cr3t")
    >>> conn = arcomm.connect("spine2a", creds, protocol="capi")
    >>> arcomm.execute(conn, "show version")

    spine2a (command-api)>show version
    Arista vEOS
    Hardware version:
    Serial number:
    System MAC address:  000c.29c3.547a

    Software image version: 4.13.0-1829814.41351F.1 (engineering build)
    Architecture:           i386
    Internal build version: 4.13.0-1829814.41351F.1
    Internal build ID:      677d5a6b-0948-4590-913f-b27f83ca1a60

    Uptime:                 44 minutes
    Total memory:           2033084 kB
    Free memory:            239136 kB

    >>> # authorize to allow configure commands
    >>> arcomm.authorize(conn)

    >>> arcomm.configure(conn, ["interface range Et 1 - 4", "shutdown"])

    spine2a (command-api)#{'input': 'secr3t', 'cmd': 'enable'}
    spine2a (command-api)#configure
    spine2a (command-api)#interface range Et 1 - 4
    spine2a (command-api)#shutdown
    spine2a (command-api)#end

    >>> arcomm.configure(conn, ["interface range Et 1 - 4", "no shutdown"])

    spine2a (command-api)#{'input': 'secr3t', 'cmd': 'enable'}
    spine2a (command-api)#configure
    spine2a (command-api)#interface range Et 1 - 4
    spine2a (command-api)#no shutdown
    spine2a (command-api)#end\n"
    >>>


