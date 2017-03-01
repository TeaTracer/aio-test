# -*- mode: ruby -*-
# vi: set ft=ruby :

NAME = "aio"

Vagrant.configure("2") do |config|
    config.vm.box = "geerlingguy/ubuntu1604"

    config.vm.define "#{NAME}" do |dev|
        config.vm.network "forwarded_port", guest: 443,  host: 1236, auto_correct: true
        config.vm.hostname = "#{NAME}"
        config.vm.provider "virtualbox" do |vb|
            vb.gui = false
            vb.name = "#{NAME}"
            vb.memory = "512"
            vb.cpus = "2"
        end
    end
end
