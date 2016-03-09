# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty32"
  config.vm.network "private_network", ip: "192.168.56.10",
    virtualbox__intnet: "Management"
  config.vm.provision "shell", path: "bootstrap.sh"
end
