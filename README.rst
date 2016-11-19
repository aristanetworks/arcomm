ArComm: Remote Control for Aristas
==================================

.. image:: https://img.shields.io/pypi/v/arcomm.svg
    :target: https://pypi.python.org/pypi/arcomm

.. image:: https://img.shields.io/pypi/dm/arcomm.svg
    :target: https://pypi.python.org/pypi/arcomm

Enable communications with Arista switches using a simple API or command line
utility

.. code-block:: python

    >>> responses = arcomm.execute('eapi+https://admin@vswitch1', ['show clock', 'show version'])
    >>> print responses.to_yaml()
    host: vswitch1
    status: ok
    commands:
      - command: show clock
        output: |
          Tue Feb  9 06:04:42 2016
          Timezone: UTC
          Clock source: local

Features
--------

- Factory defaults: works with new switches (mgmt IP required...)
- Switching between protocols
- Multi-processing for batch and background operations
- Command line utility
- JSON encoding w/ eapi

Installation
------------

.. code-block:: bash

    pip install -U arcomm

or

.. code-block:: bash

    git clone https://github.com/aristanetworks/arcomm.git
    cd arcomm
    python setup.py install

Note: Jinja2 is required for templating

.. code-block:: bash

    pip install jinja2


Development
-----------

* Install Vagrant from http://www.vagrantup.com

.. code-block:: bash

    git clone https://github.com/aristanetworks/arcomm.git
    cd arcomm
    vagrant up
    vagrant ssh

Console Usage
-------------

.. code-block:: bash

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


.. code-block:: bash

    $ arcomm veos
    Enter commands (one per line).
    Enter '.' alone to send or 'Crtl-C' to quit.
    > show version
    > .
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

or pipe in the commands...


.. code-block:: bash

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

even multiple hosts in parallel...

.. code-block:: bash

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

Contents of upgrade script file:

.. code-block:: bash

    $ cat sw-upgrade.script
    ! script will stop here if file is not found.
    dir flash:{{image}}
    show ip interface brief
    configure
      boot system flash:{{image}}
    end
    show boot-config

Command-line w/ --variables argument:

.. code-block:: bash

    $ cat scaffolding/sw-upgrade.script | arcomm veos \
        --variables='{"image": "vEOS-4.15.2F.swi"}'
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

.. code-block:: python

    >>> import arcomm

    >>> conn = arcomm.connect('veos', creds=arcomm.BasicCreds('admin', ''),
        protocol='eapi+http')

    >>> responses = conn.execute(['show clock', 'show version'])

    >>> for resp in responses:
    ...     resp.output
    ...
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

    >>> responses = conn.execute(['show version'], encoding='json')
    >>> for resp in responses:
    ...     resp.output
    ...
    {u'memTotal': 1897596, u'version': u'4.15.2F',
    u'internalVersion': u'4.15.2F-2663444.4152F', u'serialNumber': u'',
    u'systemMacAddress': u'08:00:27:76:48:c5',
    u'bootupTimestamp': 1447565515.19, u'memFree': 121952,
    u'modelName': u'vEOS', u'architecture': u'i386',
    u'internalBuildId': u'0ebbad93-563f-4920-8ecb-731057802b9c',
    u'hardwareRevision': u''}


IPython Magics
--------------

.. code:: bash

    $ vagrant up
    $ vagrant ssh
    ubuntu@ubuntu-xenial:~$ jupyter notebook --no-browser --ip="*"

.. code:: python

    %reload_ext arcomm.ipython.magics

.. code:: python

    %%arcomm eapi+http://admin@switch-ip-or-hostname --askpass
    show clock

.. parsed-literal::

    admin@ck214.sjc.aristanetworks.com's password:········
    host: ck214.sjc.aristanetworks.com
    status: ok
    commands:
      - command: show clock
        output: |
          Sat Nov 19 05:36:34 2016
          Timezone: UTC
          Clock source: NTP server (172.28.131.194)




.. parsed-literal::

    [<ResponseStore [ok]>]



.. code:: python

    %%arcomm ck214.sjc.aristanetworks.com
    configure
    ip host dummy 127.0.0.1
    end
    ping ip dummy repeat 1
    configure
    no ip host dummy
    end


.. parsed-literal:: yaml

    host: ck214.sjc.aristanetworks.com
    status: ok
    commands:
      - command: configure
        output: |

      - command: ip host dummy 127.0.0.1
        output: |

      - command: end
        output: |

      - command: ping ip dummy repeat 1
        output: |
          PING dummy (127.0.0.1) 72(100) bytes of data.
          80 bytes from localhost.localdomain (127.0.0.1): icmp_req=1 ttl=64 time=0.106 ms

          --- dummy ping statistics ---
          1 packets transmitted, 1 received, 0% packet loss, time 0ms
          rtt min/avg/max/mdev = 0.106/0.106/0.106/0.000 ms
      - command: configure
        output: |

      - command: no ip host dummy
        output: |

      - command: end
        output: |


.. parsed-literal::

    [<ResponseStore [ok]>]
