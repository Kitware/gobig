
### Hadoop
Provisions and manages HDFS nodes

This section applies to the `hadoop-hdfs-namenode` and `hadoop-hdfs-datanode`
roles.

#### Variables

|Name                       |Default    |Description                                |
|:--------------------------|:---------:|:------------------------------------------|
|format                     |false      |whether to (re)format the filesystem       |
|hadoop_install_root        |(generated)|root directory to install hadoop under     |
|hadoop_version             |2.7.1      |version of hadoop to deploy                |
|hdfs_block_replication     |3          |replication factor                         |
|hdfs_block_size            |268435456  |block size in bytes                        |
|hdfs_crypt_pass            |(generated)|hash of the password to use for the user   |
|hdfs_data_root             |(generated)|root directory for the HDFS files          |
|hdfs_group                 |hadoop     |group to run HDFS services as              |
|hdfs_io_buffer_size        |131072     |IO buffer size in bytes                    |
|hdfs_namenode_ansible_group|(required) |ansible group name for the HDFS name nodes |
|hdfs_net_interface         |eth0       |interface on which to bind                 |
|hdfs_user                  |hdfs       |user to run HDFS services as               |
|state                      |started    |state of the service                       |

#### Notes

  - By default, the hash for a blank password is used when creating
    a new Hadoop user, disabling password login.

  - `state` can be any one of "absent", "present", "stopped", "started",
    "reloaded", or "restarted".

  - By default, Hadoop is installed under /opt/hadoop/`hadoop_version`.

  - By default, Hadoop's data is stored under /data/hadoop/`hadoop_version`.

  - The `hdfs_namenode_ansible_group` variable provides HDFS data nodes with the
    knowledge of which namenodes to report to.

#### Examples

Install/Configure/Start
```YAML
  - hosts: namenodes
    roles:
      - role: hadoop-hdfs-namenode
        hdfs_namenode_ansible_group: namenodes
        state: started

  - hosts: datanodes
    roles:
      - role: hadoop-hdfs-datanode
        hdfs_namenode_ansible_group: namenodes
        state: started
```

Stop/Remove
```YAML
  - hosts: namenodes
    roles:
      - role: hadoop-hdfs-namenode
        hdfs_namenode_ansible_group: namenodes
        state: absent

  - hosts: datanodes
    roles:
      - role: hadoop-hdfs-datanode
        hdfs_namenode_ansible_group: namenodes
        state: absent
```

Reformat
```YAML
  - hosts: namenodes
    roles:
      - role: hadoop-hdfs-namenode
        hdfs_namenode_ansible_group: namenodes
        state: restart
        format: true

  - hosts: datanodes
    roles:
      - role: hadoop-hdfs-datanode
        hdfs_namenode_ansible_group: namenodes
        state: restart
        format: true
```

