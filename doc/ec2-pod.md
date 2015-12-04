
### ec2-pod
manages a self-contained collection of AWS EC2 instances

The `ec2-pod` role can be used to manage a "pod", or a self-contained collection
of AWS EC2 instances organized under a single security group.  The instances and
their properties are specified as part of the YAML document where the role is
used.  The role also dynamically adds managed instances to the current
inventory, allowing the instances to be provisioned after management in one
single playbook.  Combined with the aformentioned instance specification, the
`ec2-pod` role may be used to add to- or in lieu of- a play's initial
inventory.

#### Variables

|Name                 |Default       |Description                                         |
|:--------------------|:------------:|:---------------------------------------------------|
|add_by_hostname      |false         |add managed hosts by hostname instead of IP address |
|default_image        |ami-d05e75b8  |default ami image to use for instances              |
|default_instance_type|t2.medium     |default instance type                               |
|default_ssh_key      |ec2           |name of the default keypair to use                  |
|hosts                |(empty)       |hosts specification                                 |
|name                 |pod           |name of the pod to manage                           |
|region               |us-east-1     |region to use for the pod's instances               |
|rules                |(all open)    |firewall rules for the pod's security group         |
|rules_egress         |(all open)    |firewall egress rules for the pod's security group  |
|state                |running       |state of the pod's instances                        |

#### Notes

  - Proper operation of this role requires that the `AWS_ACCESS_KEY_ID` and
    `AWS_SECRET_ACCESS_KEY` environment variables be set to the credentials
    necessary to access the desired AWS account.

  - The `default_image`, `default_instance_type`, and `default_ssh_key`
    variables provide defaults for the instances' image, type, and key,
    respectively.

  - Details on the format of the `hosts` specification variable is provided
    under [Hosts Specification](#hosts-specification).

  - The format of the `rules` and `rules_egress` variables follow the same
    format as that documented in the Ansible
    [ec2_group](http://docs.ansible.com/ansible/ec2_group_module.html) module.

  - `state` can be "absent", "stopped", or "running".

  - As a special case, setting `state` to "absent" will terminate every instance
    that had once been part of a pod by the same name (given in `pod`),
    even if such instances have no matching entry in the `hosts` specification.

##### Hosts Specification

The `hosts` specification variable is a key-value mapping of instance names to
instance options.

|Name   |Default                |Description                                   |
|:------|:---------------------:|:---------------------------------------------|
|count  |1                      |number of instances to manage                 |
|groups |(empty)                |list of ansible groups to add this instance to|
|image  |(default image)        |ami image to use for this instance            |
|name   |(generated)            |name of the instance                          |
|ssh_key|(default ssh key)      |name of the keypair to use for this instance  |
|type   |(default instance type)|type of this instance                         |
|volumes|(empty)                |volumes specification                         |

##### Notes

  - In addition to any given `groups`, all managed instances are added to a
    catch-all ansible group with the same name as the pod.

  - By default, the name of the instance is a mangled name that includes the
    name of the pod followed by the key matching this entry in the `hosts`
    specification.  Set the `name` variable to override this generated name.

  - The optional `volumes` specification variable for a given hosts
    specification entry is a key-value mapping of volume device names to volume
    capacities (in GiB).  Volumes should be specified with names as in "sdb",
    "sdc", and so on (modification of the instance's root volume, "sda" is not
    supported).  Note that the volumes are mounted within the instances under
    mount points such as "xvdb", "xvdc", etc.

#### Examples

Create a new ec2 pod called "gobig".  Ssh to the managed instances will be done
using the "gobig" ssh key pair.  The pod's security group will allow inbound tcp
traffic over the ssh port.  Outbound, the security group allows all traffic (the
default).  The instances consist of a single `t2.medium` instance called
"girder" with an additional 20 GiB volume available under `/dev/xvdb` -- and
three `m3.large` instances called "spark", each with an additional 100 GiB
volume available under `/dev/xvdb`.

The `ec2-pod` role tries to be idempotent in all cases, so if, for example,
there already exists a pod called "gobig" with two matching and running "girder"
instances, and one matching and running "spark" instance, one of the spare
"girder" instances would be terminated, and two new "spark" instances would be
created.  As another example, if a preexisting matching pod had two "spark"
instances, one of which was stopped, The running instance would be reused, the
stopped instance restarted, and a new instance created.  In cases of excess
instances, stopped instances are preferentially chosen for termination before
terminating running instances, so for a pod with one running "girder" instance
and one stopped "girder" instance, this example would terminate the stopped
instance and leave the running instance as is.

The instances can then be further provisioned within the same playbook by
targetting the groups given under each instances' `hosts` specification, or by
targetting the pod-wide group, "gobig".

```YAML
  - hosts: localhost
    connection: local
    gather_facts: false
    become: false
    roles:
      - role: ec2-pod
        default_ssh_key: gobig
        name: gobig
        rules:
          - proto: tcp
            from_port: 22
            to_port: 22
            cidr_ip: 0.0.0.0/0

        hosts:
            girder:
                name: girder
                groups:
                  - girder
                  - resonant
                type: t2.medium
                volumes:
                    sdb: 20
            spark:
                name: spark
                count: 3
                groups:
                  - spark
                type: m3.large
                volumes:
                    sdb: 100

  - hosts: gobig
    tasks:
      - name: filesystems | create
        filesystem:
            fstype: ext4
            dev: /dev/xvdb

      - name: filesystems | mount
        mount:
            fstype: ext4
            name: /data
            src: /dev/xvdb
            state: mounted

      - etc...

  - hosts: girder
    etc...

  - hosts: resonant
    etc...

  - hosts: spark
    etc...
```

