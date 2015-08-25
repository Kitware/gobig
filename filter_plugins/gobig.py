
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
                       domain,
                       host_vars,
                       extra_entries,
                       local_entries,
                       hostname,
                       nodename,
                       fqdn):
    import itertools as it

    net_interface_key = "ansible_{}".format(net_interface)

    loopback_keys = ["127.0.0.1", "::1"]
    loopback_entries = [( set(["localhost",
                               "localhost.localdomain",
                               "localhost4",
                               "localhost4.localdomain4"
                              ] + ([hostname,
                                    nodename,
                                    fqdn] + ([hostname+"."+domain,
                                              nodename+"."+domain]
                                             if domain else [])
                                   if local_entries else []))

                        | set(extra_entries.get("127.0.0.1", [])) ),

                        ( set(["localhost",
                             "localhost.localdomain",
                             "localhost6",
                             "localhost6.localdomain6"

                              ] + ([hostname,
                                    nodename,
                                    fqdn] + ([hostname+"."+domain,
                                              nodename+"."+domain]
                                             if domain else [])
                                   if local_entries else []))

                        | set(extra_entries.get("::1", [])) )]

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
                         host_vars[host]["ansible_nodename"],
                         host_vars[host]["ansible_fqdn"]
                        ] + ([host_vars[host]["ansible_hostname"]+"."+domain,
                              host_vars[host]["ansible_nodename"]+"."+domain]
                             if domain else [])
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
                 map(lambda x: sorted(list(x)),
                     loopback_entries + host_entries + remaining_entries))

    return result

class HostsFileFilterFunction(object):
    def __init__(self):
        import re
        self.RE_ENTRY = re.compile(r'''^[0-9\.\:/]+[ \t][^ \t]+''')

    def __call__(self,
                 hosts_file_contents,
                 host_list,
                 domain,
                 host_vars,
                 extra_entries,
                 hostname,
                 nodename,
                 fqdn):

        from cStringIO import StringIO

        hosts = ( set([hostname, nodename, fqdn])
                | set([hostname+"."+domain, nodename+"."+domain]
                      if domain else [])
                | set.union(*[
                    set([host_vars[host]["ansible_hostname"],
                         host_vars[host]["ansible_nodename"],
                         host_vars[host]["ansible_fqdn"]])
                    for host in host_list])
                | (
                    set.union(*[
                        set([host_vars[host]["ansible_hostname"]+"."+domain,
                             host_vars[host]["ansible_nodename"]+"."+domain])
                        for host in host_list])
                    if domain else set([]))
                | (
                    set.union(*[set(extra_aliases)
                                for extra_aliases in extra_entries])
                    if extra_entries else set([])))

        result = StringIO()
        for line in hosts_file_contents.split('\n'):
            m = self.RE_ENTRY.match(line)

            if m is not None:
                tokens = filter(lambda x: x not in hosts, line.split())

                if len(tokens) < 2: continue
                line = " ".join(tokens)

            result.write(line)
            result.write('\n')

        return result.getvalue()

def zk_url(list, hostvars, net_interface, client_port):
    net_interface_key = "ansible_{}".format(net_interface)
    return "".join((
        "zk://",
        ":{},".format(str(client_port)).join(
            hostvars[host]
                    [net_interface_key]
                    ["ipv4"]
                    ["address"]
            for host in list),
        ":",
        str(client_port),
    ))

class FilterModule(object):
    def filters(self):
        return {"hosts_file_entries": hosts_file_entries,
                "hosts_file_filter": HostsFileFilterFunction(),
                "zk_url": zk_url}

