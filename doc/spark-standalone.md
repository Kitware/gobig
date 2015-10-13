
### spark
Provisions and manages a spark node running over mesos

#### Variables

|Name                                 |Default         |Description                                                                  |
|:------------------------------------|:--------------:|:----------------------------------------------------------------------------|
|hadoop_profile                       |(without-hadoop)|Hadoop profile (e.g.,  hadoop2.4, hadoop2.6, etc)                            |
|slave_group                          |(all)           |Hosts where executors will be launched                                       | 
|spark_broadcast_compress             |(sparkdefault)  |whether to compress broadcast variables before sending them                  |
|spark_cores_max                      |(sparkdefault)  |maximum limit of total CPU cores to request for an application               |
|spark_crypt_pass                     |(generated)     |hash of the password to use for the user                                     |
|spark_data_root                      |(generated)     |root directory for the spark data files                                      |
|spark_dispatcher_port                |7077            |port on which the spark cluster dispatcher service should listen             |
|spark_driver_cores                   |(sparkdefault)  |number of cores to use for the driver process                                |
|spark_driver_memory                  |(sparkdefault)  |amount of memory to use for the driver process                               |
|spark_executor_memory                |(sparkdefault)  |amount of memory to use per executor process                                 |
|spark_group                          |spark           |group to install spark as                                                    |
|spark_install_root                   |(generated)     |root directory to install spark under                                        |
|spark_local_dir                      |(sparkdefault)  |directory to use for "scratch" space in spark                                |
|spark_log_conf                       |(sparkdefault)  |logs the effective SparkConf as INFO when started                            |
|spark_net_interface                  |eth0            |interface on which to bind                                                   |
|spark_rdd_compress                   |(sparkdefault)  |whether to compress serialized RDD partitions                                |
|spark_user                           |spark           |user to install spark as                                                     |
|spark_version                        |1.5.1           |version of spark to deploy                                                   |
|spark_webui_port                     |(sparkdefault)  |port for the spark application's dashboard                                   |
|state                                |started         |state of the service                                                         |

#### Notes
  - The default hadoop_profile `without-hadoop` assumes that you have
    already installed hadoop using the hadoop-hdfs-* roles

  - `state` can be any one of "absent", "present", "stopped", "started",
    "reloaded", or "restarted".

  - By default, the hash for a blank password is used when creating
    a new spark user, disabling password login.

  - By default, spark is installed under /opt/spark/`spark-version`.

  - By default, spark's data is stored under /data/spark/`spark-version`.

  - All the options that control containerization and use docker are not
    currently supported by these roles.

  - See the
    [spark configuration](http://spark.apache.org/docs/latest/configuration.html#available-properties)
    documentation pages for more information about the various spark-dictated
    defaults.

#### Examples

Install/Configure/Start
```YAML
  - hosts: spark
    roles:
      - role: spark-standalone-install
    tags:
      - spark
  
  - hosts: head
    roles:
      - role: spark-standalone-service
        slave_group: spark-slaves
        state: started
```
In this example the ```spark``` group should contain all hosts that will
run spark code (e.g.,  masters and workers). The ```head``` group should
contain the head node which will run the spark standalone service. Finally
```spark-slaves``` is a group that contains all the nodes that should run
spark executors (Note this may be the same set as ```spark```). If not
specified ```slave_group``` defaults to ```all```.


Stop/Remove
```YAML
  - hosts: spark-nodes
    roles:
      - role: spark-standalone-install
        state: absent
```

