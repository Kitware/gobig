
### mongodb
Provisions and manages mongodb nodes

The `mongodb` role allows for the provisioning and management of mongodb
services supporting operation as standalone instances, replicated databases,
and a distributed cluster.

After provisioning and initial configuration, replica sets and shard clusters
can be initialized using the `mongodb-replica-set` and `mongodb-shard-cluster`
roles, respectively.

#### Variables

|Name                                |Default          |Description                                                   |
|:-----------------------------------|:---------------:|:-------------------------------------------------------------|
|mongodb_crypt_pass                  |(generated)      |hash of the password to use for the user                      |
|mongodb_data_root                   |(generated)      |root directory for the mongodb data files                     |
|mongodb_group                       |mongodb          |group to run the mongodb services as                          |
|mongodb_index_build_retry           |true             |whether to rebuild incomplete indexes on startup              |
|mongodb_install_root                |(generated)      |root directory to install mongodb under                       |
|mongodb_ipv6                        |false            |whether to enable IPv6 support                                |
|mongodb_journal_commit_interval     |100              |max time (in ms) allowed between journal operations           |
|mongodb_journal_enabled             |true             |whether to enable journaling                                  |
|mongodb_max_connections             |65536            |maximum number of simultaneous connections                    |
|mongodb_mode                        |standalone       |mode in which to deploy mongodb                               |
|mongodb_net_interface               |eth0             |interface on which to bind                                    |
|mongodb_replica_enable_majority_read|(mongodb default)|whether to enable "majority" read concern level               |
|mongodb_replica_oplog_size          |(mongodb default)|size (in MB) of the replication operation log                 |
|mongodb_replica_set                 |""               |name of the replica set to configure                          |
|mongodb_sharding_config             |""               |config database host specification                            |
|mongodb_storage_engine              |(mongodb default)|storage engine for the mongod database                        |
|mongodb_sync_period                 |(mongodb default)|amount of time (in sec) before written data is flushed to disk|
|mongodb_user                        |mongodb          |user to run the mongodb services as                           |
|mongodb_verbosity                   |0                |log message verbosity                                         |
|mongodb_version                     |3.2.0            |version of mongodb to deploy                                  |
|mongodb_wire_object_check           |true             |whether to validate all client requests for well-formed BSON  |
|state                               |started          |state of the service                                          |

#### Notes

  - By default, the hash for a blank password is used when creating
    a new mongodb user, disabling password login.

  - By default, mongodb is installed under /opt/mongodb/`mongodb_version`.

  - By default, mongodb's data is stored under /data/mongodb/`mongodb_version`.

  - `mongodb_mode` can be any one of the values given in the table below.  All
    modes except for `router` can be deployed over a collection of hosts
    participating in a replica set.

|Value         |Replicatable|Description                                                                                                  |
|:------------:|:----------:|:------------------------------------------------------------------------------------------------------------|
|standalone    |Y           |for a non-sharded database                                                                                   |
|cluster-config|Y           |as in `standalone`, but specifically for serving the configuration data for a larger sharded database cluster|
|shard         |Y           |as in `standalone`, but specifically to serve the data for one shard in a larger sharded database cluster    |
|router        |N           |for the query router service of a sharded database cluster                                                   |

  - `mongodb_sharding_config` represents the host specification for the config
    server of a sharded cluster.  Only has effect when
    `mongodb_mode == "router"`.
      - If set directly to a string, the value of `mongodb_sharding_config`
        must be that of an ansible group in the current playbook.  It is then
        taken to represent a non-replicated mongodb server hosted on the first
        host listed as a member of the referenced group.  Users should fashion a
        special-purpose group with only one member to ensure that host is chosen
        as the config server.
      - If set to a mapping, `mongodb_sharding_config` must map values to the
        `rs` and `group` keys.  It is then taken to represent a replicated
        mongodb server participating in the replica set identified by `rs` and
        whose participating hosts are members of the ansible group given by
        `group`.

  - `state` can be any one of "absent", "present", "stopped", "started",
    "reloaded", or "restarted".

  - For more details on mongodb configuration, see the
    [mongdb documentation](https://docs.mongodb.org/manual/reference/configuration-options).

#### mongodb-replica-set
Intializes and manages a mongodb replica set configuration

For initializing a replica set over multiple provisioned mongodb instances.

#### Variables

|Name               |Default          |Description                             |
|:------------------|:---------------:|:---------------------------------------|
|mongodb_replica_set|""               |name of the replica set to manage       |
|state              |present          |state of the service                    |

#### Notes

  - `state` can be either "absent" or "present".

#### mongodb-shard-cluster
Intializes and manages a mongodb shard cluster configuration

For initializing a shard cluster over multiple provisioned mongodb instances.

#### Variables

|Name               |Default          |Description                             |
|:------------------|:---------------:|:---------------------------------------|
|shards             |(required)       |list of shard entries                   |
|state              |present          |state of the service                    |

#### Notes

  - Each entry in `shards` represents a subset of the shards participating in
    the cluster, the unions of which serve as the total set of all shards.
      - If an entry is a string, its value must be that of an ansible group in
        the current playbook.  It is then taken to represent a set of hosts,
        which are the members of the given group, each running a non-replicated
        mongodb service to be used as a shard.  Note that the semantics for the
        shard entry's value in this case differ from that of the
        `mongodb_sharding_config` variable in that each host in the given
        ansible group is added to the cluster's shards, as opposed to only the
        first host being used for the sharding cluster's config database.
      - If an entry is a mapping, it must map values to the `rs` and `group`
        keys.  It is then taken to represent a replicated mongodb server
        participating in the replica set identified by `rs` and whose
        participating hosts are members of the ansible group given by `group`.
        The replica set are added to the cluster as a single shard.  The names
        of all replica sets in a cluster's set of shards must be unique.

  - `state` can be either "absent" or "present".


#### Examples

##### Simple Standalone Server

Install/Configure/Start
```YAML
  - hosts: mongodb
    roles:
      - role: mongodb
        state: started
```

Stop/Remove
```YAML
  - hosts: mongodb
    roles:
      - role: mongodb
        state: absent
```

##### Replication

Install/Configure/Start
```YAML
  - hosts: mongodb
    roles:
      - role: mongodb
        mongodb_replica_set: myReplicaSet
        state: started

      - role: mongodb-replica-set
        mongodb_replica_set: myReplicaSet
        state: present
```

Stop/Remove
```YAML
  - hosts: mongodb
    roles:
      - role: mongodb-replica-set
        mongodb_replica_set: myReplicaSet
        state: absent

      - role: mongodb
        state: absent
```

##### Sharding

Install/Configure/Start
```YAML
  - hosts: mongodb-config
    roles:
      - role: mongodb
        mongodb_mode: cluster-config
        state: started

  - hosts: mongodb-shards
      - role: mongodb
        mongodb_mode: shard
        state: started

  - hosts: mongodb-master
      - role: mongodb
        mongodb_mode: router
        mongodb_sharding_config: mongodb-config
        state: started

      - role: mongodb-shard-cluster
        shards:
          - mongodb-shards
        state: present
```

Stop/Remove
```YAML
  - hosts: mongodb-master
    roles:
      - role: mongodb-shard-cluster
        state: absent

      - role: mongodb
        state: absent

  - hosts: mongodb-shards
    roles:
      - role: mongodb
        state: absent

  - hosts: mongodb-config
    roles:
      - role: mongodb
        state: absent
```

