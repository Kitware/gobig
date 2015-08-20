
### Mesos
Provisions and manages mesos nodes

This section applies to the `mesos-master` and `mesos-slave` roles.

#### Variables

|Name                                   |Default           |Description                                                                                     |
|:--------------------------------------|:----------------:|:-----------------------------------------------------------------------------------------------|
|state                                  |started           |state of the service                                                                            |
|recompile                              |false             |whether to force recompilation of mesos                                                         |
|mesos_user                             |mesos             |user to run the mesos services as                                                               |
|mesos_group                            |mesos             |group to run the mesos services as                                                              |
|mesos_crypt_pass                       |(generated)       |hash of the password to use for the user                                                        |
|mesos_version                          |0.21.0            |version of mesos to deploy                                                                      |
|mesos_install_root                     |/opt/mesos        |root directory to install mesos under                                                           |
|mesos_data_root                        |/data/mesos       |root directory for the mesos data files                                                         |
|mesos_ansible_group                    |(required)        |ansible group name for the mesos nodes                                                          |
|zookeeper_ansible_group                |(required)        |ansible group name for the zookeeper nodes                                                      |
|mesos_net_interface                    |eth0              |interface on which to bind                                                                      |
|mesos_cluster_name                     |mesos             |name of the cluster                                                                             |
|mesos_master_port                      |5050              |port on which mesos masters should listen for connections                                       |
|mesos_slave_port                       |5051              |port on which mesos slaves should listen for connections                                        |
|mesos_quorum                           |(computed)        |minimum size of a mesos quorum                                                                  |
|mesos_slave_ping_timeout               |15secs            |duration within which each slave is expected to respond to a ping from the master               |
|mesos_offer_timeout                    |30secs            |duration after which an offer is rescinded from a framework                                     |
|mesos_registry_fetch_timeout           |1mins             |duration within which a registry fetch must complete                                            |
|mesos_registry_store_timeout           |5secs             |duration within which a registry store must complete                                            |
|mesos_slave_reregister_timeout         |10mins            |duration within which all slaves are expected to re-register with a newly-elected master leader |
|mesos_zookeeper_session_timeout        |10secs            |zookeeper session timeout                                                                       |
|mesos_executor_registration_timeout    |1mins             |duration within which an executor must register with its slave                                  |
|mesos_recovery_timeout                 |15mins            |duration within which a slave must recover                                                      |
|mesos_executor_shutdown_grace_period   |5secs             |duration to wait for an executor to shut down                                                   |
|mesos_max_slave_ping_timeouts          |5                 |number of times a slave can fail to respond to a ping from the master                           |
|mesos_allocator                        |HierarchicalDRF   |allocator to use for resource allocation to frameworks                                          |
|mesos_allocation_interval              |1secs             |amount of time to wait between performing batch allocations                                     |
|mesos_disk_watch_interval              |1mins             |frequency with which disk usage is checked                                                      |
|mesos_oversubscribed_resources_interval|15secs            |frequency with which slaves update the master with the oversubscribed resources available       |
|mesos_perf_duration                    |10secs            |duration of a perf stat sample                                                                  |
|mesos_perf_interval                    |1mins             |frequency with which a perf stat sample is obtained                                             |
|mesos_resource_monitoring_interval     |1secs             |frequency with which executor resource usage is measured                                        |
|mesos_qos_correction_interval_min      |0secs             |maximum frequency with which slaves poll and carry out QoS corrections                          |
|mesos_gc_delay                         |1weeks            |maximum duration to wait before cleaning up executor directories                                |
|mesos_hadoop_home                      |""                |location of hadoop (for fetching framework executors from HDFS)                                 |
|mesos_registration_backoff_factor      |1secs             |backoff factor at which slaves attempt to re-register with a newly-elected master leader        |
|mesos_fetcher_cache_size               |2147483648        |size of the fetcher cache in bytes (default: 2 GiB)                                             |
|mesos_fetcher_cache_dir                |/tmp/mesos/fetch  |root directory for the fetcher caches (one subdirectory per slave)                              |
|mesos_containerizers                   |mesos             |containerizers to be used by mesos                                                              |
|mesos_default_container_image          |""                |default container image to use if not specified by a task                                       |
|mesos_default_container_info           |""                |default, JSON-formatted object for executors                                                    |
|mesos_docker_remove_delay              |6hrs              |duration after which a stopped docker container is removed                                      |
|mesos_docker_mesos_image               |""                |docker image used to launch the mesos slave instance                                            |
|mesos_docker_stop_timeout              |0secs             |duration after which a stopped container is killed                                              |
|mesos_sandbox_directory                |/mnt/mesos/sandbox|absolute path for the directory in the container where the sandbox is mapped to                 |

#### Notes

  - `state` can be any one of "absent", "present", "stopped", "started",
    "reloaded", or "restarted".

  - By default, the hash for a blank password is used when creating
    a new mesos user, disabling password login.

  - mesos is installed under
    `mesos_install_root`/mesos-`mesos_version`.

  - The `mesos_master_ansible_group` variable provides mesos slave nodes with
    the knowledge of which master nodes to report to.

  - The `zookeeper_ansible_group` variable provides mesos nodes with the
    knowledge of which zookeeper nodes to use for leader election.

  - The zookeeper registry information for the mesos cluster is stored under
    zk://`zookeeper_nodes`/mesos/`mesos_cluster_name`.

  - If not provided, `mesos_quorum` is set to the smallest integer value that is
    greater than half the number of mesos master nodes, i.e.:
    `mesos_quorum = floor(N/2) + 1` where `N` is the number of mesos master
    nodes.  It is highly recommended that a mesos cluster be deployed with a
    number of mesos master nodes that is odd and at least three.

  - All the options that control containerization and use docker are not
    currently supported by these roles.

  - These roles currently install mesos from source, which can take roughly ten
    minutes for each host depending on hardware specs.

#### Examples

Install/Configure/Start.  Note that this example groups master and slave nodes
together during installation to avoid making two sequential compilation passes.
The nodes are assinged to mesos-master (`MM`), mesos-slave (`MS`), and
mesos-common (`MC`) groups.  Zookeeper is installed on all nodes running mesos,
but only the mesos master nodes run Zookeeper services.

```YAML
  - hosts: all
    vars:
        mesos_masters: masters
        mesos_slaves: slaves
        master_set: "{{ groups[mesos_masters] }}"
        slave_set: "{{ groups[mesos_slaves] }}"
        common_set: "{{ master_set | union(slave_set) }}"

    tasks:
      - group_by: key={{ inventory_hostname in master_set and "MM" or "x" }}
      - group_by: key={{ inventory_hostname in slave_set  and "MS" or "x" }}
      - group_by: key={{ inventory_hostname in common_set and "MC" or "x" }}

  - hosts: MC
    roles:
      - role: zookeeper
        zookeeper_ansible_group: MM
        state: present
    # masters and slaves both compile mesos here
      - role: mesos-install
        zookeeper_ansible_group: MM
        mesos_master_ansible_group: MM
        state: present

  - hosts: MM
    roles:
      - role: zookeeper
        zookeeper_ansible_group: MM
        state: started
      - role: mesos-master
        zookeeper_ansible_group: MM
        mesos_master_ansible_group: MM
        state: started

  - hosts: MS
    roles:
      - role: mesos-slave
        zookeeper_ansible_group: MM
        mesos_master_ansible_group: MM
        state: started
```

Stop/Remove
```YAML
  - hosts: slaves
    roles:
      - role: mesos-slave
        zookeeper_ansible_group: masters
        mesos_master_ansible_group: masters
        state: absent

  - hosts: masters
    roles:
      - role: mesos-master
        zookeeper_ansible_group: masters
        mesos_master_ansible_group: masters
        state: absent
```

