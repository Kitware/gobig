
def _get_items(x, *items):
    try:
        for item in items:
            if item not in x:
                return None
            x = x[item]
        return x
    except TypeError:
        return None

def hosts_file_entries(host_list,
                       net_interface,
                       host_vars,
                       extra_entries,
                       nodename,
                       hostname):
    import itertools as it

    net_interface_key = "ansible_{}".format(net_interface)

    loopback_keys = ["127.0.0.1", "::1"]
    loopback_entries = [( set(["localhost",
                               "localhost.localdomain",
                               "localhost4",
                               "localhost4.localdomain4",
                               nodename,
                               hostname])
                        | set(extra_entries.get("127.0.0.1", [])) ),

                        ( set(["localhost",
                             "localhost.localdomain",
                             "localhost6",
                             "localhost6.localdomain6",
                             nodename,
                             hostname])
                        | set(extra_entries.get("127.0.0.1", [])) )]

    address_to_host_list = dict(
        it.chain.from_iterable(
            filter(lambda x: (x[0] is not None and
                              x[0] not in loopback_keys),
                (
                    (
                        _get_items(host_vars[host],
                                   net_interface_key,
                                   protocol,
                                   "address"),

                        [host_vars[host]["ansible_hostname"],
                         host_vars[host]["ansible_nodename"]]
                    )
                    for host in host_list
                )
            )
            for protocol in ("ipv4", "ipv6")
        )
    )

    host_keys = list(address_to_host_list.keys())
    host_entries = [( set(address_to_host_list[ip])
                    | set(extra_entries.get(ip, [])))
                    for ip in host_keys]

    remaining_keys = list(set(extra_entries.keys()) - ( set(loopback_keys)
                                                      | set(host_keys)))
    remaining_entries = [extra_entries[ip] for ip in remaining_keys]

    result = zip(loopback_keys + host_keys + remaining_keys,
                 map(list, loopback_entries + host_entries + remaining_entries))

    return result

class FilterModule(object):
    def filters(self):
        return {"hosts_file_entries": hosts_file_entries}

