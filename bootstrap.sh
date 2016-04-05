#!/bin/bash
apt-get update
apt-get upgrade -y
apt-get install -y build-essential python-pip python-paramiko python-pytest git

pip install Sphinx
pip install jinja2

cd /vagrant; python setup.py develop
