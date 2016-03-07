
### ec2-pod2
manages a self-contained collection of AWS EC2 resources

The `ec2-pod2` role can be used to manage a "pod", or a self-contained
collection of AWS EC2 resources organized under a single logical namespace.
These managed resources include EBS volumes, security groups, placement groups,
and elastic IPs -- as well as the EC2 instances and the key pairs used to
remotely access them.  Their specifications are given as part of the YAML
document where the role is used.  The role also dynamically adds managed
instances to the current inventory, allowing the instances to be provisioned
after management in one single playbook.  Combined with the aformentioned
resource specification, the `ec2-pod2` role may be used to add to- or in lieu
of- a play's initial inventory.

#### Variables

|Name                 |Default       |Description                                                                   |
|:--------------------|:------------:|:-----------------------------------------------------------------------------|
|aws_access_key_id    |(required)    |the ID of the AWS access key                                                  |
|aws_secret_key       |(required)    |the secret token for the AWS access key                                       |
|instances            |{}            |specification of the pod's instances                                          |
|name                 |default       |name of the pod to manage                                                     |
|options              |(see notes)   |additional options controlling the overall behavior of this role              |
|placement_groups     |{}            |specification of the pod's placement groups                                   |
|security_groups      |{}            |specification of the pod's security groups                                    |
|ssh_keys             |{}            |specification of the ssh key pairs used to remotely access the pod's instances|
|state                |running       |state of the pod's resources                                                  |
|templates            |{}            |specification templates for properties common across multiple resources       |

#### Notes

  - For seamless handling of aws credentials, including profile support, see the
    [`aws-credentials`](aws-credentials.md) role.

  - Details on the format of the `instances` specification variable is provided
    under [Instance Specification](#instance-specification).

  - For entries recognized in the `options` variable, see
    [Overall Options](#overall-options).

  - Details on the format of the `placement_groups` specification variable is
    provided under
    [Placement Group Specification](#placement-group-specification).

  - Details on the format of the `security_groups` specification variable is
    provided under
    [Security Group Specification](#security-group-specification).

  - Details on the format of the `ssh_keys` specification variable is
    provided under
    [Keypair Specification](#keypair-specification).

  - `state` can be "absent", "stopped", or "running".

  - As a special case, setting `state` to "absent" will terminate every instance
    that had once been part of a pod by the same name (given in `pod`), even if
    such instances have no matching entry in the `instances` specification.

  - See [Templating](#templating) for details on `ec2-pod2`'s templating
    features and how to to take advantage of them.

##### Instance Specification

The `instances` specification variable is a key-value mapping of instance names
to instance options.

**Note**: Take advantage of `ec2-pod2`'s templating features.  See
          [Templating](#templating) for more details.

|Name                 |Default   |Description                                                                     |
|:--------------------|:--------:|:---------------------------------------------                                  |
|ansible_groups       |[]        |ansible groups to add this instance to                                          |
|count                |1         |number of instances to manage                                                   |
|extends              |""        |template from which this instance derives                                       |
|extra_ansible_groups |[]        |additional ansible groups to add this instance to                               |
|extra_security_groups|[]        |additional security groups to add this instance to                              |
|image                |(required)|ami image to use for this instance                                              |
|ip                   |""        |IP address of the elastic ip to associate with this instance                    |
|placement_group      |""        |placement group to assign this instance to                                      |
|security_groups      |[]        |security groups to add this instance to                                         |
|ssh_key              |""        |name of the keypair entry to use for this instance                              |
|type                 |(required)|type of this instance                                                           |
|volumes              |[]        |volumes specification                                                           |
|wait                 |true      |whether to wait for this instance to become accessible over ssh before returning|

###### Notes
  - The ansible groups that each instance is added to is the union of its
    `ansible_groups` and `extra_ansible_groups` values.  The
    `extra_ansible_groups` variable is provided as a convenience for specifying
    a base set of ansible groups via templating.

  - The security groups that each instance is added to is the union of its
    `security_groups` and `extra_security_groups` values.  The
    `extra_security_groups` variable is provided as a convenience for specifying
    a base set of security groups via templating.  All referenced security
    groups must have matching entries in this pod's `security_groups`
    specification.

  - A valid instance specification cannot simultaneously provide a static
    elastic `ip` and a `count` greater than one.

  - The optional `volumes` specification variable for a given instance
    specification is a list of volume sizes in GiB.  The block device nodes
    assigned to each instance's volumes are: `/dev/xvdb` for the first,
    `/dev/xvdc` for the second, and so on.  Modification of the instance's root
    volume (`/dev/xvda`) prior to launch is not supported.

  - Set `wait` to `false` where waiting for ssh access to an instance is
    unnecessary or detrimental.  An example of such a scenario involves managing
    an instance in a security group that blocks ssh.  Care must be taken when
    adding such instances to ansible groups -- to avoid connection errors when
    targetting those groups in subsequent plays.

##### Placement Group Specification

The `placement_groups` specification variable is a key-value mapping of
placement group names to placement group options.

**Note**: Take advantage of `ec2-pod2`'s templating features.  See
          [Templating](#templating) for more details.

|Name    |Default      |Description                                     |
|:-------|:-----------:|:-----------------------------------------------|
|extends |""           |template from which this placement group derives|
|strategy|"cluster"    |strategy used for placing member instances      |

###### Notes
  - As of this writing, `strategy` is the only configurable option supported on
    AWS for placement groups, and "cluster" the only supported value.  Placement
    group specifications set to an empty object (`{}`) will automatically use
    these defaults.

##### Security Group Specification

The `security_groups` specification variable is a key-value mapping of security
group names to the list of rules that restrict traffic involving member
instances.  Note that the syntax for specifying security group rules is an
extension of that used for the `rules` and `rules_egress` settings in Ansible's
[ec2_group](http://docs.ansible.com/ansible/ec2_group_module.html) module.  In
general, there is a one-to-many mapping between rules in this specification and
the actual rules created for the security group.  Below are the options
available for each rule.

**Note**: Take advantage of `ec2-pod2`'s templating features.  See
          [Templating](#templating) for more details.

|Name   |Default      |Description                                                                                                             |
|:------|:-----------:|:-----------------------------------------------------------------------------------------------------------------------|
|cidr_ip|""           |only allow traffic with peers whose ip address lie within the given block                                               |
|extends|""           |template from which this rule derives                                                                                   |
|flow   |"in"         |only allow traffic with the given orientation                                                                           |
|groups |[]           |only allow traffic that peers with an instance whose security group membership includes any of the given security groups|
|port   |(any port/NA)|only allow traffic via the given ports                                                                                  |
|protos |"all"        |only allow traffic that follows the given protocols                                                                     |

###### Notes
  - Valid values for `flow` include "in", where only rules allowing inbound
    traffic are created, "out", where only rules allowing outbound traffic are
    created, and "sym", where both sets of rules are created.

  - All referenced security groups in `groups` must refer to another
    `security_groups` entry in this pod's specification.

  - The `port` value can take on several forms.  If a scalar, rules are created
    that restrict traffic to the given port.  If a list, each item in the list
    is considered in turn.  If an item is a scalar, rules are created as in the
    singular scalar case.  If an item in the list is, itself, another list, it
    must have at least two scalar elements and rules are created that restrict
    traffic to the range of ports between the first and second element,
    inclusive.

  - Valid values for `protos` include "tcp", "udp", "icmp", "all", and any other
    values supported by Ansible's
    [ec2_group](http://docs.ansible.com/ansible/ec2_group_module.html) module.

##### Keypair Specification

The `ssh_keys` specification variable is a key-value mapping of keypair names to
the local file path<sup>1</sup> of the public key.  Instances using a given
`ssh_key` entry will be accessible through ssh only with the matching private
key.

<sup>1</sup>The host or hosts to which the given path is local is determined by
the connection specification for the play containing the current invocation of
this role, which may not be `localhost`.  See Ansible's documentation on
[delegation and local actions](http://docs.ansible.com/ansible/playbooks_delegation.html)
for more information.

##### Overall Options

|Name                     |Default|Description                                                                   |
|:------------------------|:-----:|:-----------------------------------------------------------------------------|
|ansible_groups_amend     |true   |whether to add managed instances to groups with the current playbook inventory|
|ansible_groups_amend_mode|"ip"   |format in which the instances' addresses are to be added                      |

###### Notes

  - Valid values for `ansible_groups_amend_mode` include "ip" and "hostname".


##### Templating

The `ec2-pod2` role provides templating features through the `templates` option
in the pod configuration.  Using templates is an effective and flexible way to
detail a pod's specification while cutting down on redundant boilerplate.  Via
templates, configuration options common across multiple entries of a given
resource can be specified in one place, and then reused or extended where
particular resources differ.  The entries for the `templates` option mirror the
prominent features of the rest of the pod configuration.

|Name            |Description              |
|:---------------|:------------------------|
|instances       |instance templates       |
|placement_groups|placement group templates|
|rules           |rule templates           |

Each entry of a particular class of template is a key-value mapping from the
template name to the new default options provided by it.  Each template can
provide options that feature in the configuration of the same resource class as
that of the template.  For example, an instance template can specify values for
`image` and `type` (as well as all the other instance options).  Instances that
inherit from such a template need not specify their `image` or `type`, but
inherit them from the template.  In this manner, templates can be used to
provide configurable defaults.

```YAML
  - hosts: localhost
    roles:
      - role: ec2-pod2
        name: my-pod
        state: running

        templates:
            instances:
                common: { "image": "ami-fce3c696", "type": "t2.medium" }

        instances:
            web-medium: { "extends": "common" }
            web-large: { "extends": "common", "type": "t2.large" }
```

#### Examples

Create a new ec2 pod called "gobig".  Ssh to the managed instances will be done
using the "gobig" ssh key pair.  The pod's security group will allow inbound tcp
traffic over the ssh port.  Outbound, the security group allows all traffic.
The instances consist of a single `t2.medium` instance called "girder" with an
additional 20 GiB volume available under `/dev/xvdb` -- and
three `m3.large` instances called "spark", each with an additional 100 GiB
volume available under `/dev/xvdb`.

The `ec2-pod2` role tries to be idempotent in all cases, so if, for example,
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
targetting the groups given under each instances' `ansible_hosts` specification,
or by targetting the common group, "gobig".

```YAML
  - hosts: localhost
    connection: local
    gather_facts: false
    become: false
    roles:
      - role: ec2-pod2
        name: gobig

        ssh_keys:
            main: "~/.ssh/id_rsa.pub"

        security_groups:
            main:
              - { "flow": "in" , "proto": "tcp", "port": 22 }
              - { "flow": "out", "proto": "all" }

        instances:
            girder:
                ssh_key: main
                ansible_groups: ["girder", "gobig"]
                security_groups: ["main"]
                type: t2.medium
                image: ami-xyz
                volumes: [20]
            spark:
                count: 3
                ssh_key: main
                ansible_groups: ["spark", "gobig"]
                security_groups: ["main"]
                type: m3.large
                image: ami-xyz
                volumes: [100]

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

  - hosts: spark
    etc...
```

Same as above, but using instance templates.

```YAML
  - hosts: localhost
    connection: local
    gather_facts: false
    become: false
    roles:
      - role: ec2-pod2
        name: gobig

        ssh_keys:
            main: "~/.ssh/id_rsa.pub"

        security_groups:
            main:
              - { "flow": "in" , "proto": "tcp", "port": 22 }
              - { "flow": "out", "proto": "all" }

        instances:
            girder:
                extends: common-instance
                extra_ansible_groups: ["girder"]
            spark:
                extends: common-instance
                count: 3
                extra_ansible_groups: ["spark"]
                type: m3.large
                volumes: [100]

        templates:
            instances:
                common-instance:
                    ssh_key: main
                    ansible_groups: ["gobig"]
                    security_groups: ["main"]
                    type: t2.medium
                    image: ami-xyz
                    volumes: [20]
```

