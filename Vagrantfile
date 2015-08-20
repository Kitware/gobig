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

  # In order to allow addressing via hostname we use the vagrant hostmanager plugin,
  # This will add each node's hostname to the launching systems /etc/hosts file
  config.hostmanager.enabled = true
  config.hostmanager.manage_host = true
  config.hostmanager.include_offline = true


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

        # Debian based boxes with vagrant add a host entry like:
        # /etc/hosts:
        # 127.0.1.1 data-01.cluster.dev
        #
        # This causes the hdfs web interface and several other
        # hdfs internal services to bind to 127.0.1.1.  Instead
        # We use the vagrant.yml file to generate our own
        # /etc/hosts file.
        config.vm.provision "ansible" do |ansible|
           ansible.groups = groups
           ansible.limit = 'all'
           ansible.sudo = true
           ansible.playbook = "vagrant.yml"
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
           
           ansible.playbook = "hadoop-hdfs-site.yml"
           
         end
      end

    end
  end
end
