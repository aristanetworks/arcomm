ArComm
======

Enable communications with Arista switches using a simple API or command line
utility

Installation
------------

Note: Jinja2 is required for templating

    pip install jinja2
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

    $ arcomm -u admin -p "" vn-leaf-1a
    Enter commands (one per line).
    Enter '.' alone to send or 'Crtl-C' to quit.
    > show clock
    > .
    ---
    host: vn-leaf-1a
    commands:
      - show clock: |
          Fri May 29 06:34:14 2015
          Timezone: UTC
          Clock source: local
    ...

**or pipe in the commands...**

    $ echo "show version" | arcomm -u admin -p "" vn-leaf-1a
    ---
    host: vn-leaf-1a
    commands:
      - show version: |
          Arista vEOS
          Hardware version:    
          Serial number:       
          System MAC address:  000c.2944.288b
      
          Software image version: 4.15.0F
          Architecture:           i386
          Internal build version: 4.15.0F-2387143.4150F
          Internal build ID:      1d97861d-09c7-4fc3-b38d-a98c99b77ae9
      
          Uptime:                 8 hours and 2 minutes
          Total memory:           2027964 kB
          Free memory:            100532 kB
      
    ...

**even multiple hosts in parallel...**

    $ echo "show clock" | arcomm -u admin -p "" vn-leaf-1a vn-leaf-2a
    ---
    host: vn-leaf-1a
    commands:
      - show clock: |
          Fri May 29 06:34:48 2015
          Timezone: UTC
          Clock source: local
    ---
    host: vn-leaf-2a
    commands:
      - show clock: |
          Fri May 29 06:34:52 2015
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

    $ cat examples/sw-upgrade.script | arcomm vn-leaf-1a -u admin -p "" \
      --variables='{"image": "vEOS-lab.swi"}' --protocol=eapi
    ---
    host: vn-leaf-1a
    commands:
      - dir flash:vEOS-lab.swi: |
          Directory of flash:/vEOS-lab.swi
      
                 -rwx   234460332           Apr 20 09:40  vEOS-lab.swi
      
          1907843072 bytes total (1437716480 bytes free)
      - show ip interface brief: |
          Interface              IP Address         Status     Protocol         MTU
          Ethernet1              172.16.19.1/31     up         up              1500
          Ethernet2              172.16.18.1/31     up         up              1500
          Loopback0              1.1.0.1/32         up         up             65535
          Management1            172.16.130.21/24   up         up              1500
      - configure: |

      - boot system flash:vEOS-lab.swi: |

      - end: |

      - show boot-config: |
          Software image: flash:/vEOS-lab.swi
          Console speed: (not set)
          Aboot password (encrypted): (not set)
          Memory test iterations: (not set)
    ...


API Usage
---------

    $ python
    Python 2.7.10 (default, May 26 2015, 13:01:57) 
    [GCC 4.2.1 Compatible Apple LLVM 6.1.0 (clang-602.0.53)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import arcomm
    >>> creds = arcomm.get_credentials(username="admin", password="")
    >>> conn = arcomm.connect("vn-leaf-2a", creds, protocol="eapi")
    >>> conn.authorize()
    >>>
    >>> responses = arcomm.execute(conn, "show version")
    >>> print responses
    #show version
    Arista vEOS
    Hardware version:    
    Serial number:       
    System MAC address:  000c.29d0.2356

    Software image version: 4.15.0F
    Architecture:           i386
    Internal build version: 4.15.0F-2387143.4150F
    Internal build ID:      1d97861d-09c7-4fc3-b38d-a98c99b77ae9

    Uptime:                 8 hours and 49 minutes
    Total memory:           2027964 kB
    Free memory:            106892 kB
    >>>
    >>> responses = arcomm.execute(conn, "show version", encoding="json")
    >>> pp(responses.to_dict())
    [{'show version': {u'architecture': u'i386',
                       u'bootupTimestamp': 1432850726.49,
                       u'hardwareRevision': u'',
                       u'internalBuildId': u'1d97861d-09c7-4fc3-b38d-a98c99b77ae9',
                       u'internalVersion': u'4.15.0F-2387143.4150F',
                       u'memFree': 107076,
                       u'memTotal': 2027964,
                       u'modelName': u'vEOS',
                       u'serialNumber': u'',
                       u'systemMacAddress': u'00:0c:29:d0:23:56',
                       u'version': u'4.15.0F'}}]
    
    >>> # eAPI over SSH!
    >>> conn = arcomm.connect("vn-leaf-2a", creds, protocol="ssh")
    >>> responses = arcomm.execute(conn, "show version", encoding="json")
    >>> pp(responses.to_dict())
    [{'show version': {u'architecture': u'i386',
                       u'bootupTimestamp': 1432850726.49,
                       u'hardwareRevision': u'',
                       u'internalBuildId': u'1d97861d-09c7-4fc3-b38d-a98c99b77ae9',
                       u'internalVersion': u'4.15.0F-2387143.4150F',
                       u'memFree': 79392,
                       u'memTotal': 2027964,
                       u'modelName': u'vEOS',
                       u'serialNumber': u'',
                       u'systemMacAddress': u'00:0c:29:d0:23:56',
                       u'version': u'4.15.0F'}}]

