# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.

require 'yaml'

Vagrant.configure(2) do |config|

  # The number of datanodes to launch
  # NODES=3

  config.vm.box = "ubuntu/trusty64"

  if File.exists?("dev/vagrant.local.yml")
    nc = YAML.load_file("dev/vagrant.local.yml")
  else
    nc = YAML.load_file("dev/vagrant.dist.yml")
  end

  # Ensure nodes and ansible config sections exist
  nc['nodes'] ||= {}
  nc['ansible'] ||= {}

  # Set default domain
  domain = nc["domain"] || "cluster.dev"

  groups = {}

  # Node index,  cannot use nc['nodes'].each_with_index because configs
  # are lazy loaded See: https://docs.vagrantup.com/v2/vagrantfile/tips.html
  i = 0
  # Loop over node definitions
  nc['nodes'].each do |name, params|

    # Add node to group roles
    params['roles'].each do |role|
      groups[role] ||= []
      groups[role] << name
    end

    # Make sure 'ports' config section is available
    params['ports'] ||= []

    config.vm.define name do |node|

      # Set port forwarding from ports
      params['ports'].each do |id, ports|
        guest, host = ports.split(":")
        node.vm.network :forwarded_port, guest: guest, host: host, id: id
      end

      node.vm.network :forwarded_port, guest: 22, host: 2220 + i, id: 'ssh'
      node.vm.network "private_network", ip: "192.168.33.2#{i}", netmask: "255.255.255.0"
      node.vm.hostname = "#{name}.#{domain}"
      node.vm.provider "virtualbox" do |vb|
        vb.memory = params["memory"] || 2048
        vb.cpus = params["cups"] || 2
      end

      # Only provision after all nodes have been spun up.
      if i == nc['nodes'].length - 1
        groups['all:children'] = groups.keys

        # ap:  ansible paramaters
        ap = nc['ansible']

        # Ensure plays exists
        ap['plays'] ||= []

        # The private network by default binds to eth1,  this apparently
        # Cannot be changed - some of these extra vars may not be
        # nessisary based on what roles are being used. We set them all
        # here to ease the configuration burdern on the user.
        extra_vars = {
          hdfs_net_interface: "eth1",
          hosts_file_net_interface: "eth1",
          mesos_net_interface: "eth1",
          spark_net_interface: "eth1",
          zookeeper_net_interface: "eth1"
        }
        
        # Vagrant requires configuration of host files
        # So this provisioning block is not optional
        config.vm.provision "ansible" do |ansible|
          ansible.groups = groups
          ansible.sudo = true
          ansible.limit = 'all'
          ansible.verbose = ap['verbose'] || nil
          ansible.extra_vars = extra_vars
          ansible.playbook = "playbooks/misc/hosts-file.yml"
        end
        
        # Loop through plays and run each provisioner
        ap['plays'].each do |play|
          config.vm.provision "ansible" do |ansible|
            ansible.groups = groups
            ansible.limit = 'all'
            ansible.sudo = true
            ansible.verbose = play['verbose'] || ap['verbose'] || nil
            ansible.extra_vars = extra_vars
            ansible.playbook = play['playbook']
          end
          
        end
        
      end
      # Update node index
      i += 1
      end
  end
end
