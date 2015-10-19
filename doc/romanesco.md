
### romanesco
Provisions and manages a romanesco node

#### Variables

|Name                      |Default    |Description                                                   |
|:-------------------------|:---------:|:-------------------------------------------------------------|
|rabbitmq_ansible_group    |(required) |ansible group name for the rabbitmq nodes                     |
|romanesco_crypt_pass      |(generated)|hash of the password to use for the user                      |
|romanesco_data_root       |(generated)|root directory for the romanesco data files                   |
|romanesco_group           |romanesco  |group to run the romanesco service as                         |
|romanesco_install_root    |(generated)|root directory to install romanesco under                     |
|romanesco_net_interface   |eth0       |interface on which to bind                                    |
|romanesco_version         |master     |version of romanesco to deploy                                |
|romanesco_user            |romanesco  |user to run the romanesco service as                          |
|romanesco_main_app_name   |romanesco  |name of the main application to report to celery              |
|romanesco_celery_broker   |(generated)|broker url for celery                                         |
|romanesco_tmp_root        |(generated)|root directory for temporary files                            |
|romanesco_plugin_load_path|(empty)    |list of directories to add to the romanesco plugin search path|
|state                     |started    |state of the service                                          |

#### Notes

  - `state` can be any one of "absent", "present", "stopped", "started",
    "reloaded", or "restarted".

  - By default, the hash for a blank password is used when creating
    a new romanesco user, disabling password login.

  - By default, romanesco is installed under /opt/romanesco/`romanesco-version`.

  - By default, romanesco's data is stored under
    /data/romanesco/`romanesco-version`.

  - The default celery broker uri is based on the `rabbitmq_ansible_group`
    value.

#### Examples

Install/Configure/Start
```YAML
  - hosts: romanesco
    roles:
      - role: romanesco
        rabbitmq_ansible_group: rabbitmq
        state: started
```

Stop/Remove
```YAML
  - hosts: romanesco
    roles:
      - role: romanesco
        rabbitmq_ansible_group: rabbitmq
        state: absent
```

