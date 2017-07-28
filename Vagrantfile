# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/xenial32"
  #config.vm.network "forwarded_port", guest: 8888, host: 8009
  config.vm.network "private_network", type: "dhcp"
  config.vm.provision "shell", inline: $script
end


$script = <<SCRIPT
#!/bin/bash
apt-get update
apt-get upgrade -y
apt-get install -y build-essential git

apt-get install -y build-essential libssl-dev libffi6 libffi-dev
apt-get install -y libfreetype6 libfreetype6-dev libncurses5-dev
apt-get install -y pkg-config

# apt-get install -y python3.5 python3.5-dev

add-apt-repository -y ppa:jonathonf/python-3.6
apt-get update
apt-get install -y python3.6 python3.6-dev python3.6-venv

wget https://bootstrap.pypa.io/get-pip.py
python3.6 get-pip.py
pip3.6 install --upgrade pip

# su -l vagrant
# python3.6 -m venv ~/.venv/arcomm
# source ~/.venv/arcomm/bin/activate

pip3.6 install --upgrade pip
pip3.6 install pytest
pip3.6 install jinja2
pip3.6 install pyyaml
pip3.6 install cryptography --force-reinstall
pip3.6 install paramiko
pip3.6 install requests

# pip3 install sh
# pip3 install ipython jupyter pandas
# pip3 install Sphinx

pip freeze --local | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U

cd /vagrant; python3.6 setup.py develop
# exit


SCRIPT
