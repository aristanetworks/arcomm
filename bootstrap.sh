#!/bin/bash
apt-get install -y build-essential python-pip python-paramiko python-pytest
cd /vagrant; python setup.py develop

if ! grep -q vswitch /etc/hosts; then

    cat >> /etc/hosts <<EOF
192.168.56.21 vswitch1
192.168.56.22 vswitch2
EOF

fi
