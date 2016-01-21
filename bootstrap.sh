#!/bin/bash
apt-get update
apt-get upgrade -y
apt-get install -y build-essential python-pip python-paramiko python-pytest git

pip install Sphinx

cd /vagrant; python setup.py develop

if ! grep -q vswitch /etc/hosts; then

    cat >> /etc/hosts <<EOF
192.168.56.21 vswitch1 veos veos1 switch
192.168.56.22 vswitch2 veos2
EOF

fi
