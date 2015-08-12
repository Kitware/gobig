
# GoBig

Provisioning big data applications with Resonant

# GoBig Cluster

Collection of Ansible roles useful for provisioning a variety of services over
clusters for HPC and data-intensive applications.

## Roles
### Roles for Deploying HDFS
Provisions and manages an HDFS node.

This section applies to the `hadoop-hdfs-namenode` and `hadoop-hdfs-datanode`
roles.

#### Variables

|Name                  |Default    |Description                                |
|:---------------------|:---------:|:------------------------------------------|
|hdfs_user             |hdfs       |user to run HDFS services as               |
|hdfs_group            |hadoop     |group to run HDFS services as              |
|hdfs_crypt_pass       |(generated)|hash of the password to use for the user   |
|hdfs_net_interface    |eth0       |interface on which to bind                 |
|hdfs_data_root        |/data/hdfs |root directory for the HDFS files          |
|hdfs_block_replication|3          |replication factor                         |
|hdfs_block_size       |268435456  |block size in bytes                        |
|hdfs_io_buffer_size   |131072     |IO buffer size in bytes                    |
|state                 |started    |state of the service                       |
|format                |false      |whether to (re)format the filesystem       |
|hadoop_version        |2.7.1      |version of hadoop to deploy                |
|hadoop_install_root   |/opt/hadoop|root directory to install hadoop under     |
|hdfs_namenode_group   |(required) |ansible group name for the HDFS name nodes |

#### Notes

  - By default, the hash of a randomly generated password is used when creating
    a new Hadoop user.

  - `state` can be any one of "absent", "present", "stopped", "started",
    "reloaded", or "restarted".

  - Hadoop is installed under `hadoop_install_root`/hadoop-`hadoop_version`.

  - The `hdfs_namenode_group` variable provides HDFS data nodes with the
    knowledge of which namenodes to report to.

#### Examples

Install/Configure/Start
```YAML
  - hosts: namenodes
    roles:
      - role: hadoop-hdfs-namenode
        hdfs_namenode_group: namenodes
        state: started

  - hosts: datanodes
    roles:
      - role: hadoop-hdfs-datanode
        hdfs_namenode_group: namenodes
        state: started
```

Stop/Remove
```YAML
  - hosts: namenodes
    roles:
      - role: hadoop-hdfs-namenode
        hdfs_namenode_group: namenodes
        state: absent

  - hosts: datanodes
    roles:
      - role: hadoop-hdfs-datanode
        hdfs_namenode_group: namenodes
        state: absent
```

Reformat
```YAML
  - hosts: namenodes
    roles:
      - role: hadoop-hdfs-namenode
        hdfs_namenode_group: namenodes
        state: restart
        format: true

  - hosts: datanodes
    roles:
      - role: hadoop-hdfs-datanode
        hdfs_namenode_group: namenodes
        state: restart
        format: true
```

