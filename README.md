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

Note: Jinja2 is required for templating

    pip install jinja2

Console Usage
-------------

    $ arcomm -h
    usage: arcomm [-h] [-v] [--protocol PROTOCOL] [--encoding {json,text}]
              [-u USERNAME] [-p PASSWORD] [--authorize]
              [-a AUTHORIZE_PASSWORD] [-t TIMEOUT] [--hosts-file HOSTS_FILE]
              [--script SCRIPT] [--variables VARIABLES]
              [endpoints [endpoints ...]]

    positional arguments:
    endpoints

    optional arguments:
    -h, --help            show this help message and exit
    -v, --version         Display version info
    --protocol PROTOCOL   Set the default protocol or protocols. If more than
                        one is supplied, they will be tried in order
    --encoding {json,text}
                        Control output formatting
    -u USERNAME, --username USERNAME
                        Specifies the username on the switch
    -p PASSWORD, --password PASSWORD
                        Specifies users password. If not supplied, the user
                        will be prompted
    --authorize
    -a AUTHORIZE_PASSWORD, --authorize-password AUTHORIZE_PASSWORD
                        Use if a password is needed for elevated prvilges
    -t TIMEOUT, --timeout TIMEOUT
                        Change the timeout from the default of 30 seconds
    --hosts-file HOSTS_FILE
                        Path to file containing list of hosts
    --script SCRIPT       Path to a script file containing commands to execute.
                        template variables will be processed if Jinja2 is
                        installed and `--variables` is also supplied on the
                        command line
    --variables VARIABLES
                        Replacements for template variables in script file
                        (must be JSON formatted)

Console Example
---------------

    $ arcomm veos
    Enter commands (one per line).
    Enter '.' alone to send or 'Crtl-C' to quit.
    > show version
    > .
    ---
    ---
    host: veos
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

      Uptime:                 13 hours and 38 minutes
      Total memory:           1897596 kB
      Free memory:            158892 kB

    ...

**or pipe in the commands...**

    $ echo "show version" | arcomm veos
    ---
    host: veos
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

      Uptime:                 13 hours and 39 minutes
      Total memory:           1897596 kB
      Free memory:            158644 kB

    ...

**even multiple hosts in parallel...**

    $ echo "show clock" | arcomm vswitch1 vswitch2
    ---
    host: vswitch1
    status: ok
    commands:
    - command: show clock
    output: |
      Mon Nov 30 16:24:07 2015
      Timezone: UTC
      Clock source: local
    ---
    host: vswitch2
    status: ok
    commands:
    - command: show clock
    output: |
      Mon Nov 30 16:23:18 2015
      Timezone: UTC
      Clock source: local
    ...

Multiple Switch Upgrade w/ Script Example
------------------------------------------

**Contents of upgrade script file:**

    $ cat sw-upgrade.script
    ! script will stop here if file is not found.
    dir flash:{{image}}
    show ip interface brief
    configure
      boot system flash:{{image}}
    end
    show boot-config

Command-line w/ --variables argument:

    $ cat scaffolding/sw-upgrade.script | arcomm veos --variables='{"image": "vEOS-4.15.2F.swi"}'
    ---
    host: veos
    status: ok
    commands:
    - command: dir flash:vEOS-4.15.2F.swi
    output: |
      Directory of flash:/vEOS-4.15.2F.swi

             -rwx   247919507           Oct 15 18:20  vEOS-4.15.2F.swi

      1907843072 bytes total (1168683008 bytes free)
    - command: show ip interface brief
    output: |
      Interface              IP Address         Status     Protocol         MTU
      Ethernet1              unassigned         up         up              1500
      Ethernet2              unassigned         up         up              1500
      Ethernet3              unassigned         up         up              1500
      Loopback0              1.1.1.1/32         up         up             65535
      Management1            192.168.56.21/24   up         up              1500
    - command: configure
    output: |

    - command: boot system flash:vEOS-4.15.2F.swi
    output: |

    - command: end
    output: |

    - command: show boot-config
    output: |
      Software image: flash:/vEOS-4.15.2F.swi
      Console speed: (not set)
      Aboot password (encrypted): (not set)
      Memory test iterations: (not set)
    ...

API Usage
---------

```
    $ ipython
    Python 2.7.6 (default, Mar 22 2014, 22:59:38)
    Type "copyright", "credits" or "license" for more information.

    IPython 4.0.0 -- An enhanced Interactive Python.
    ?         -> Introduction and overview of IPython's features.
    %quickref -> Quick reference.
    help      -> Python's own help system.
    object?   -> Details about 'object', use 'object??' for extra details.

    In [1]: import arcomm

    In [2]: conn = arcomm.connect('veos', creds=arcomm.BasicCreds('admin', ''),
        protocol='eapi+http')

    In [3]: responses = conn.execute(['show clock', 'show version'])

    In [4]: for resp in responses:
    ...:     resp.output
    ...:     
    Mon Nov 16 04:49:41 2015
    Timezone: UTC
    Clock source: local

    Arista vEOS
    Hardware version:    
    Serial number:       
    System MAC address:  0800.2776.48c5

    Software image version: 4.15.2F
    Architecture:           i386
    Internal build version: 4.15.2F-2663444.4152F
    Internal build ID:      0ebbad93-563f-4920-8ecb-731057802b9c

    Uptime:                 23 hours and 17 minutes
    Total memory:           1897596 kB
    Free memory:            121844 kB

    In [5]:
    In [6]: responses = conn.execute(['show version'], encoding='json')

    In [7]: for resp in responses:
   ...:     resp.output
   ...:     
   {u'memTotal': 1897596, u'version': u'4.15.2F',
    u'internalVersion': u'4.15.2F-2663444.4152F', u'serialNumber': u'',
    u'systemMacAddress': u'08:00:27:76:48:c5',
    u'bootupTimestamp': 1447565515.19, u'memFree': 121952,
    u'modelName': u'vEOS', u'architecture': u'i386',
    u'internalBuildId': u'0ebbad93-563f-4920-8ecb-731057802b9c',
    u'hardwareRevision': u''}

    In [8]:
```
