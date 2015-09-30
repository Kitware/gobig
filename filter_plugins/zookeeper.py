
def zk_url(host_list, host_vars, net_interface, client_port):
    net_interface_key = "ansible_{}".format(net_interface)
    return "".join((
        "zk://",
        ":{},".format(str(client_port)).join(
            host_vars[host]
                     [net_interface_key]
                     ["ipv4"]
                     ["address"]
            for host in host_list),
        ":",
        str(client_port),
    ))

class FilterModule(object):
    def filters(self):
        return {"zk_url": zk_url}

