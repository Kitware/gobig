
def zk_url(host_list, host_vars, net_interface, client_port):
    """computes the zookeeper url corresponding to the given list of hosts

    :param host_list: the list of ansible hosts to include in the result
    :param host_vars: ansible host_vars object
    :param net_interface: the net interface from which to sample IP addresses
    :param client_port: port on which each host is listening for zookeeper
                        connections

    :returns: the zookeeper url corresponding the given list of hosts
    """

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

