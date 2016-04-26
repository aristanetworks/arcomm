# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty32"
  config.vm.network "public_network"
  config.vm.provision "shell", inline: $script
end


$script = <<SCRIPT
#!/bin/bash
apt-get update
apt-get upgrade -y
apt-get install -y build-essential python-pip python-paramiko python-pytest git

pip install Sphinx
pip install jinja2

cd /vagrant; python setup.py develop
SCRIPT
