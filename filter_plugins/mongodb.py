
def mongodb_url(host_list, host_vars, net_interface, client_port, replica_set):
    """computes the mongodb url for the database corresponding to the given
       replica set

    If replica_set is empty, computes the url for the non-replicated database
    backed by the first host in host_list.

    :param host_list: the list of ansible hosts to include in the result
    :param host_vars: ansible host_vars object
    :param net_interface: the net interface from which to sample IP addresses
    :param client_port: port on which each host is listening for mongodb
                        connections
    :param replica_set: the name of the replica set

    :returns: the mongodb url for the database corresponding to the given
              replica set
    """

    net_interface_key = "ansible_{}".format(net_interface)
    if replica_set == "":
        return "{}:{}".format(host_vars[host_list[0]]
                                       [net_interface_key]
                                       ["ipv4"]
                                       ["address"],
                              str(client_port))
    else:
        return "".join((
            "{}/".format(replica_set),
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
        return {"mongodb_url": mongodb_url}

