
### spark
Provisions and manages a spark node running over mesos

#### Variables

|Name                                 |Default       |Description                                                                  |
|:------------------------------------|:------------:|:----------------------------------------------------------------------------|
|hdfs_namenode_ansible_group          |(required)    |ansible group name for the hdfs name nodes                                   |
|mesos_group                          |mesos         |group to run the spark cluster dispatcher service as                         |
|mesos_master_ansible_group           |(required)    |ansible group name for the mesos master nodes                                |
|mesos_user                           |mesos         |user to run the spark cluster dispatcher service as                          |
|spark_broadcast_compress             |(sparkdefault)|whether to compress broadcast variables before sending them                  |
|spark_cores_max                      |(sparkdefault)|maximum limit of total CPU cores to request for an application               |
|spark_crypt_pass                     |(generated)   |hash of the password to use for the user                                     |
|spark_data_root                      |(generated)   |root directory for the spark data files                                      |
|spark_dispatcher_port                |7077          |port on which the spark cluster dispatcher service should listen             |
|spark_driver_cores                   |(sparkdefault)|number of cores to use for the driver process                                |
|spark_driver_memory                  |(sparkdefault)|amount of memory to use for the driver process                               |
|spark_executor_memory                |(sparkdefault)|amount of memory to use per executor process                                 |
|spark_group                          |spark         |group to install spark as                                                    |
|spark_install_root                   |(generated)   |root directory to install spark under                                        |
|spark_local_dir                      |(sparkdefault)|directory to use for "scratch" space in spark                                |
|spark_log_conf                       |(sparkdefault)|logs the effective SparkConf as INFO when started                            |
|spark_mesos_executor_cores           |(sparkdefault)|number of CPU cores to give each mesos executor                              |
|spark_mesos_executor_docker_image    |(sparkdefault)|name of the docker image that the spark executors will run in                |
|spark_mesos_executor_docker_portmaps |(sparkdefault)|list of port mappings of ports exposed by the docker image to the host       |
|spark_mesos_executor_docker_volumes  |(sparkdefault)|list of volumes to mount into the docker image                               |
|spark_mesos_executor_home            |(sparkdefault)|directory in which spark is installed                                        |
|spark_mesos_extra_cores              |(sparkdefault)|extra number of CPU cores to request per task in addition to those offered   |
|spark_mesos_mode                     |(sparkdefault)|whether to run in coarse-grained ("coarse"), or fine-grained ("fine") mode   |
|spark_net_interface                  |eth0          |interface on which to bind                                                   |
|spark_rdd_compress                   |(sparkdefault)|whether to compress serialized RDD partitions                                |
|spark_user                           |spark         |user to install spark as                                                     |
|spark_version                        |1.4.1         |version of spark to deploy                                                   |
|spark_webui_port                     |(sparkdefault)|port for the spark application's dashboard                                   |
|state                                |started       |state of the service                                                         |
|zookeeper_ansible_group              |(required)    |ansible group name for the zookeeper nodes                                   |

#### Notes

  - `state` can be any one of "absent", "present", "stopped", "started",
    "reloaded", or "restarted".

  - The spark cluster dispatcher service should be ran as the same user/group
    that installs and runs mesos (`mesos_user`/`mesos_group`).

  - By default, the hash for a blank password is used when creating
    a new spark user, disabling password login.

  - By default, spark is installed under /opt/spark/`spark-version`.

  - By default, spark's data is stored under /data/spark/`spark-version`.

  - The `hdfs_namenode_ansible_group`, `zookeeper_ansible_group`, and
    `mesos_master_ansible_group` variables provide spark nodes with the
    information necessary from each group of nodes for proper configuration and
    management.

  - All the options that control containerization and use docker are not
    currently supported by these roles.

  - See the
    [spark.apache.org/docs/latest/configuration.html#available_properties](spark configuration)
    and
    [spark.apache.org/docs/latest/running-on-mesos.html#configuration](spark mesos)
    documentation pages for more information about the various spark-dictated
    defaults.

#### Examples

Install/Configure/Start
```YAML
  - hosts: spark-nodes
    roles:
      - role: spark
        hdfs_namenode_ansible_group: namenodes
        zookeeper_ansible_group: zookeepers
        mesos_master_ansible_group: masters
        state: started
```

Stop/Remove
```
  - hosts: spark-nodes
    roles:
      - role: spark
        hdfs_namenode_ansible_group: namenodes
        zookeeper_ansible_group: zookeepers
        mesos_master_ansible_group: masters
        state: absent
```

