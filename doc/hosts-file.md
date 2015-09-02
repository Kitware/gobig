
### hosts-file
Populates the `/etc/hosts` file with entires for multiple hosts

The `hosts-file` role populates the `/etc/hosts` file of each host with entries
that allow for each host to refer to each other by their host names and, if
present, their fully qualified domain names.

#### Variables

|Name                          |Default   |Description                                                          |
|:-----------------------------|:--------:|:--------------------------------------------------------------------|
|domain                        |""        |domain name                                                          |
|extra_clear_entries           |`[]`      |list of host aliases to remove                                       |
|extra_entries                 |`{}`      |mapping of IP addresses to host aliases                              |
|local_entries                 |false     |whether to include aliase entries for the local loopback interface   |
|hosts_file_ansible_group      |(required)|ansible group name for the nodes to be included                      |
|hosts_file_clear_ansible_group|""        |ansible group name for the nodes whose host aliases are to be removed|
|hosts_file_net_interface      |eth0      |network interface from which to sample IP addresses                  |
|state                         |present   |state of the specified entries                                       |

#### Notes

  - If set, `domain` adds additional entries such as
    `{{ hostname }}.{{ domain }}`.

  - The `extra_clear_entries` and `hosts_file_clear_ansible_group` options
    define the set of host aliases that should be removed from the hosts file
    prior to populating it with new entries.  For example, if the hostname of
    one of the hosts is `myhost` or `myhost` features in `extra_clear_entries`
    any existing entry in the hosts file that can be used to resolve `myhost`
    will have the `myhost` host aliase removed before new entries are added.

  - If `local_entries` is set, the same aliases used in the entries for the
    `hosts_file_net_interface` will also be included in those for the local
    loopback interface, so that names like `{{ hostname }}` and
    `{{ hostname }}.{{ domain }}` would resolve to `127.0.0.1` on that host.

  - `state` can be "absent", or "present".

  - This role does not overwrite a system's `/etc/hosts` file, but amends it
    in-place.  Therefore, any preexisting entires in a hosts file should be
    accounted for since they may cause name resolution behavior to differ from
    the behavior expected given only the entries created by this role.  Use the
    `extra_clear_entries` and `hosts_file_clear_ansible_group` options to ensure
    that any such entries are removed.

#### Examples

Populate the hosts file on every host in the inventory with entries referring to
each other by host name and by fully qualified domain name with "example.com" as
the domain.  Also add an extra entry for a fake host.
```YAML
  - hosts: all
    roles:
      - role: hosts-file
        hosts_file_ansible_group: all
        domain: example.com
        extra_entries:
            "1.2.3.4":
              - bogus.host.com
```

Same as above, but ensure that any preexisting entries are removed.
```YAML
  - hosts: all
    roles:
      - role: hosts-file
        hosts_file_ansible_group: all
        hosts_file_clear_ansible_group: all
        domain: example.com
        extra_entries:
            "1.2.3.4":
              - bogus.host.com
        extra_clear_entries:
          - bogus.host.com
```

