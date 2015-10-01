
### mongodb
Provisions and manages a mongodb node

#### Variables

|Name                 |Default|Description                                     |
|:--------------------|:-----:|:-----------------------------------------------|
|mongodb_net_interface|eth0   |interface on which to bind                      |
|mongodb_port         |27017  |port on which to listen for client connections  |
|state                |started|state of the service                            |

#### Notes

  - `state` can be any one of "absent", "present", "stopped", "started",
    "reloaded", or "restarted".

#### Examples

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

