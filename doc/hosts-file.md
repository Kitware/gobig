
### hosts-file
Populates the `/etc/hosts` file with entires for multiple hosts

The `hosts-file` role populates the `/etc/hosts` file of each host with entries
that allow for each host to refer to each other by their host names and, if
present, their fully qualified domain name.

#### Variables

|Name                    |Default   |Description                                        |
|:-----------------------|:--------:|:--------------------------------------------------|
|extra_entries           |`{}`      |mapping of IP addresses to host aliases            |
|hosts_file_ansible_group|(required)|ansible group name for the nodes to be included    |
|hosts_file_net_interface|eth0      |network interface from which to sample IP addresses|
|state                   |present   |state of the specified entries                     |

#### Notes

  - `state` can be "absent", or "present".

#### Examples

Populate the hosts file on every host in the inventory with entries referring to
each other by host name and, if present, fully qualified domain name.  Also add
an extra entry for a fake host.
```YAML
  - hosts: all
    roles:
      - role: hosts-file
        hosts_file_ansible_group: all
        extra_entries:
            "1.2.3.4":
                - bogus.website.com
```

