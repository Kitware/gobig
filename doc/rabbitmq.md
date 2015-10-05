
### rabbitmq
Provisions and manages a rabbitmq node

#### Variables

|Name                 |Default|Description                                     |
|:--------------------|:-----:|:-----------------------------------------------|
|state                |started|state of the service                            |


#### Notes

  - `state` can be any one of "absent", "present", "stopped", "started",
    "reloaded", or "restarted".

#### Examples

Install/Configure/Start
```YAML
  - hosts: rabbitmq
    roles:
      - role: rabbitmq
        state: started
```

Stop/Remove
```YAML
  - hosts: rabbitmq
    roles:
      - role: rabbitmq
        state: absent
```

