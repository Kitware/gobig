
### girder
Provisions and manages a girder node

#### Variables

|Name                       |Default         |Description                                                    |
|:--------------------------|:--------------:|:--------------------------------------------------------------|
|climos_test_install_root   |(generated)     |root directory to install the climos test plugin               |
|climos_test_version        |master          |version of the climos test plugin to install                   |
|girder_admin_user          |(required)      |login name of the first girder admin user                      |
|girder_admin_password      |(required)      |login password of the first girder admin user                  |
|girder_api_root            |api/v1          |root on which to mount girder's web api                        |
|girder_api_static_root     |../static       |root on which to mount girder's static web api assets          |
|girder_bcrypt_rounds       |12              |how many rounds of bcrypt to use (if using bcrypt)             |
|girder_crypt_pass          |(generated)     |hash of the password to use for the user                       |
|girder_data_root           |(generated)     |root directory for the girder data files                       |
|girder_email_regex         |(girder default)|regex to use when checking for a valid email address           |
|girder_group               |romanesco       |group to run the girder service as                             |
|girder_hash_algorithm      |bcrypt          |hashing algorithm to use                                       |
|girder_install_root        |(generated)     |root directory to install girder under                         |
|girder_login_description   |(girder default)|error message to show users when entering an invalid login name|
|girder_login_regex         |(girder default)|regex to use when checking for a valid login name              |
|girder_mode                |development     |mode in which to run girder                                    |
|girder_net_interface       |eth0            |interface on which to bind                                     |
|girder_password_description|(girder default)|error message to show users when entering an invalid password  |
|girder_password_regex      |(girder default)|regex to use when checking for a valid password                |
|girder_port                |9080            |port on which to listen for client connections                 |
|girder_replica_set         |(empty)         |TODO                                                           |
|girder_static_root         |static          |root on which to mount girder's static assets                  |
|girder_thread_pool         |100             |size of the girder thread pool                                 |
|girder_user                |girder          |user to run the girder service as                              |
|girder_version             |master          |version of girder to deploy                                    |
|hdfs_namenode_ansible_group|(required)      |ansible group name for the hdfs name nodes                     |
|mongodb_ansible_group      |(required)      |ansible group name for the mongodb nodes                       |
|rabbitmq_ansible_group     |(required)      |ansible group name for the rabbitmq nodes                      |
|romanesco_version          |master          |version of romanesco to install                                |
|sparktest_install_root     |(generated)     |root directory to install the spark test plugin                |
|sparktest_version          |master          |version of the spark test plugin to install                    |
|state                      |started         |state of the service                                           |

#### Notes

  - By default, the climos test plugin is installed under
    /opt/climos_test/`climos_test-version`.

  - By default, girder is installed under /opt/girder/`girder-version`.

  - By default, girder's data is stored under /data/girder/`girder-version`.

  - `girder_mode` can be either "development" or "production".

  - By default, the hash for a blank password is used when creating
    a new girder user, disabling password login.

  - The `hdfs_namenode_ansible_group`, `mongodb_ansible_group`, and
    `rabbitmq_ansible_group` variables provide the girder serivce with the
    information it needs to provide various services.

  - By default, the romanesco dependency is installed under
    /opt/romanesco/`romanesco-version`.

  - `state` can be any one of "absent", "present", "stopped", "started",
    "reloaded", or "restarted".

  - By default, the sparktest plugin is installed under
    /opt/sparktest/`sparktest-version`.

#### Examples

Install/Configure/Start
```YAML
  - hosts: girder
    roles:
      - role: girder
        mongodb_ansible_group: mongodb
        rabbitmq_ansible_group: rabbitmq
        hdfs_namenode_ansible_group: namenodes
        girder_admin_user: girder
        girder_admin_password: girder
        state: started
```

Stop/Remove
```YAML
  - hosts: girder
    roles:
      - role: girder
        mongodb_ansible_group: mongodb
        rabbitmq_ansible_group: rabbitmq
        hdfs_namenode_ansible_group: namenodes
        girder_admin_user: girder
        girder_admin_password: girder
        state: absent
```

