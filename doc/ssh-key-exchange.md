
### ssh-key-exchange
Exchange a set of public ssh keys among several hosts

The `ssh-key-exchange` role exhanges a set of a user's public ssh keys among
several ansible hosts, populating the user's `authorized_keys` file on each.
This role assumes that the user's ssh key pairs have already been generated on
each participating host.

The combination of this role and the [ssh-known-hosts](ssh-known-hosts.md) role
allows for prompt-free, password-less login among participating hosts.

#### Variables

|Name                          |Default   |Description                                          |
|:-----------------------------|:--------:|:----------------------------------------------------|
|ssh_key_exchange_ansible_group|(required)|ansible group name for the participating hosts       |
|user                          |(required)|user whose authorized keys files are to be populated |

#### Examples

Populate the authorized keys files for the user `bob` with keys from each host
in the inventory.
```YAML
  - hosts: all
    roles:
      - role: ssh-key-exchange
        user: bob
        ssh_key_exchange_ansible_group: all
```

Populate the authorized keys files for the "ssh" user.  Only the hosts in the
`ssh-hosts` ansible group will be added to the `authorized_keys` file.  Note
that the hosts in the play can be a superset of the hosts in the target group,
like in this example.  All hosts will be able to log into those in the
`ssh-hosts` group without a password, but those in the `ssh-hosts` group will
only be able log into each other without a password.
```YAML
  - hosts: all
    roles:
      - role: ssh-key-exchange
        user: ssh
        ssh_key_exchange_ansible_group: ssh-hosts
```

