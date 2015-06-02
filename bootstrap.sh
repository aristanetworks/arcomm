#!/bin/bash
apt-get install -y build-essential python-pip python-paramiko
cd /vagrant; python setup.py develop
