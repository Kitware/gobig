
### ssh-known-hosts
Generates a list of known ssh hosts.

The `ssh-known-hosts` role generates a list of ssh host keys on each host in a
play.  Each host in the list recognizes each other host and thus do not need to
prompt for host key verification when establishing an ssh connection.

The combination of this role and the [ssh-key-exchange](ssh-key-exchange.md)
role allows for prompt-free, password-less login among participating hosts.

#### Variables

|Name                         |Default   |Description                                    |
|:----------------------------|:--------:|:----------------------------------------------|
|ssh_known_hosts_ansible_group|(required)|ansible group name for the participating hosts |
|ssh_known_hosts_net_interface|eth0      |interface whose ip is used as the hostname     |
|user                         |(system)  |user whose known hosts file is to be generated |

#### Notes

  - By default, the system-wide known hosts file is generated.

#### Examples

Populate the system-wide known hosts file with the public keys of every host in
the inventory.
```YAML
  - hosts: all
    roles:
      - role: ssh-known-hosts
        ssh_known_hosts_ansible_group: all
```

Populate the known hosts file for the "ssh" user.  Only the hosts in the
`ssh-hosts` ansible group will be featured in the generated file.  Note that the
hosts in the play can be a superset of the hosts in the target group, like in
this example.  All hosts will recognize those in the `ssh-hosts` group, but only
those in the `ssh-hosts` group will recognize each other.
```YAML
  - hosts: all
    roles:
      - role: ssh-known-hosts
        user: ssh
        ssh_known_hosts_ansible_group: ssh-hosts
```

