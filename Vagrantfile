# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty64"
  #config.vm.network "public_network"
  #config.vm.synced_folder ".", "/vagrant"
  config.vm.network "private_network", ip: "192.168.56.6", virtualbox__intnet: "Management"
  config.vm.provision "shell", inline: $script
end


$script = <<SCRIPT
#!/bin/bash
apt-get update
apt-get upgrade -y
apt-get install -y build-essential python-pip python-paramiko python-pytest git

#sudo apt-get install -y virtualbox-guest-utils

sudo apt-get install python3-setuptools python3-pip

pip install Sphinx
pip install jinja2
pip install pyyaml

apt-get install -y libssl-dev libffi6 libffi-dev
pip3 install cryptography --force-reinstall
sudo pip3 install paramiko


cd /vagrant; python setup.py develop
cd /vagrant; python3 setup.py develop
SCRIPT
