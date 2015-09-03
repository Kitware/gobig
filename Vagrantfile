# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.

Vagrant.configure(2) do |config|

  # The number of datanodes to launch
  DATA_NODES=3

  config.vm.box = "ubuntu/trusty64"

  # Generate a single name node
  config.vm.define "name" do |node|
    node.vm.network :forwarded_port, guest: 22, host: 2220, id: 'ssh'
    node.vm.network :forwarded_port, guest: 50080, host: 50080, id: 'hdfs'
    node.vm.network "private_network", ip: "192.168.33.20", netmask: "255.255.255.0"
    node.vm.hostname = "name.cluster.dev"
    node.vm.provider "virtualbox" do |vb|
      vb.memory = "2048"
      vb.cpus = 2
    end
  end

  # Generate DATA_NODES number of data nodes
  (1..DATA_NODES).each do |i|
    config.vm.define "data-0#{i}" do |node|
      node.vm.network :forwarded_port, guest: 22, host: 2220 + i, id: 'ssh'
      node.vm.network "private_network", ip: "192.168.33.2#{i}", netmask: "255.255.255.0"
      node.vm.hostname = "data-0#{i}.cluster.dev"
      node.vm.provider "virtualbox" do |vb|
        vb.memory = "2048"
        vb.cpus = 2
      end

      # Only provision after all nodes have been spun up.
      if i == DATA_NODES
        groups = {
            "namenodes" => ["name"],
            "datanodes" => (1..DATA_NODES).map { |j| "data-0#{j}" },
            "all:children" => ["namenodes", "datanodes"]
          }


        # Configure hostfiles
        config.vm.provision "ansible" do |ansible|
           ansible.groups = groups
           ansible.limit = 'all'
           ansible.sudo = true
           ansible.verbose = "v"
           # The private network by default binds to eth1
           ansible.extra_vars = {
             hosts_file_net_interface: "eth1"
           }
           
           ansible.playbook = "playbooks/misc/hosts-file.yml"

           
        end

        
        # Launch the gobig provisioning scripts       
         config.vm.provision "ansible" do |ansible|
           ansible.groups = groups
           ansible.limit = 'all'
           ansible.sudo = true

           # The private network by default binds to eth1
           ansible.extra_vars = {
             hdfs_net_interface: "eth1"
           }
           
           ansible.playbook = "playbooks/hadoop-hdfs/site.yml"
           
         end
      end

    end
  end
end
