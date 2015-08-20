
### zookeeper
Provisions and manages a zookeeper node

#### Variables

|Name                            |Default        |Description                                                                  |
|:-------------------------------|:-------------:|:----------------------------------------------------------------------------|
|state                           |started        |state of the service                                                         |
|zookeeper_user                  |zookeeper      |user to run the zookeeper service as                                         |
|zookeeper_group                 |zookeeper      |group to run the zookeeper service as                                        |
|zookeeper_crypt_pass            |(generated)    |hash of the password to use for the user                                     |
|zookeeper_version               |3.4.6          |version of zookeeper to deploy                                               |
|zookeeper_install_root          |/opt/zookeeper |root directory to install zookeeper under                                    |
|zookeeper_data_root             |/data/zookeeper|root directory for the zookeeper data files                                  |
|zookeeper_ansible_group         |(required)     |ansible group name for the zookeeper nodes                                   |
|zookeeper_net_interface         |eth0           |interface on which to bind                                                   |
|zookeeper_tick_time             |2000           |duration of one "tick" (in milliseconds)                                     |
|zookeeper_init_limit            |10             |duration within which nodes in a quorum must connect to the leader (in ticks)|
|zookeeper_sync_limit            |5              |maximum duration by which nodes in a quorum may be out of date (in ticks)    |
|zookeeper_client_port           |2181           |port on which to listen to client connections                                |
|zookeeper_max_client_connections|128            |maximum number of simultaneous client connections                            |
|zookeeper_autopurge             |false          |whether to purge old snapshots and transaction logs                          |
|zookeeper_autopurge_retain      |3              |number of the most recent snapshots and transaction logs to retain           |
|zookeeper_autopurge_interval    |1              |autopurge interval (in ticks)                                                |
|recompile                       |false          |whether to force recompilation of zookeeper's C bindings                     |

#### Notes

  - `state` can be any one of "absent", "present", "stopped", "started",
    "reloaded", or "restarted".

  - By default, the hash for a blank password is used when creating
    a new zookeeper user, disabling password login.

  - zookeeper is installed under
    `zookeeper_install_root`/zookeeper-`zookeeper_version`.

  - The `zookeeper_ansible_group` variable provides zookeeper nodes with
    awareness of each other, which is necessary for configuration and
    management.

  - The zookeeper documentation suggests using an odd-number of zookeeper nodes
    in an ensemble.

#### Examples

Install/Configure/Start
```YAML
  - hosts: zookeepers
    roles:
      - role: zookeeper
        zookeeper_ansible_group: zookeepers
        state: started
```

Stop/Remove
```YAML
  - hosts: zookeepers
    roles:
      - role: zookeeper
        zookeeper_ansible_group: zookeepers
        state: absent
```

