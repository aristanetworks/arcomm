# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/xenial32"
  config.vm.network "forwarded_port", guest: 8888, host: 8888
  config.vm.network "private_network", type: "dhcp"
  config.vm.provision "shell", inline: $script
end


$script = <<SCRIPT
#!/bin/bash
apt-get update
apt-get upgrade -y
apt-get install -y build-essential git

apt-get install -y build-essential libssl-dev libffi6 libffi-dev
apt-get install -y libfreetype6 libfreetype6-dev pkg-config
apt-get install -y python3.5 python3.5-dev libncurses5-dev

wget https://bootstrap.pypa.io/get-pip.py
python3.5 get-pip.py

pip3 install pytest
pip3 install jinja2
pip3 install pyyaml
pip3 install cryptography --force-reinstall
pip3 install paramiko
pip3 install requests
pip3 install sh
pip3 install ipython jupyter pandas
pip3 install Sphinx

cd /vagrant; python3 setup.py develop

SCRIPT
