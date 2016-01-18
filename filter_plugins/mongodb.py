
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

def mongodb_config(config, host_vars, net_interface):
    """compute the yaml representation for the mongodb configuration object that
    corresponds to the provided config mapping (because templating YAML with
    Jinja is cruel and unusual punishment).

    :param config: config mapping
    :param host_vars: ansible host_vars object
    :param net_interface: the net interface from which to sample IP addresses

    :returns: the yaml representation for the computed mongodb configuration
    """

    import yaml

    configdb_url                 = config["configdb_url"]
    db                           = config["db"]
    index_build_retry            = config["index_build_retry"]
    inventory_hostname           = config["inventory_hostname"]
    ipv6                         = config["ipv6"]
    is_replica_set               = config["is_replica_set"]
    is_shard_config              = config["is_shard_config"]
    is_shard_data                = config["is_shard_data"]
    is_shard_router              = config["is_shard_router"]
    journal_commit_interval      = config["journal_commit_interval"]
    journal_enabled              = config["journal_enabled"]
    max_connections              = int(config["max_connections"])
    port                         = int(config["port"])
    replica_enable_majority_read = config["replica_enable_majority_read"]
    replica_oplog_size           = int(config["replica_oplog_size"])
    replica_set                  = config["replica_set"]
    sharding_cluster_role        = config["sharding_cluster_role"]
    storage_engine               = config["storage_engine"]
    sync_period                  = int(config["sync_period"])
    verbosity                    = int(config["verbosity"])
    wire_object_check            = config["wire_object_check"]

    result = dict(
        net = dict(
            bindIp = host_vars[inventory_hostname]
                            ["ansible_" + net_interface]
                            ["ipv4"]
                            ["address"],
            ipv6 = ipv6,
            maxIncomingConnections = max_connections,
            port = port,
            wireObjectCheck = wire_object_check
        ),

        processManagement = dict(fork=False),

        systemLog = dict(verbosity=verbosity)
    )

    if is_replica_set:
        replication = dict(replSetName=replica_set)

        if replica_enable_majority_read != 0:
            replication["enableMajorityReadConcern"] = (
                mongodb_replica_enable_majority_read)

        if replica_oplog_size != 0:
            replication["oplogSizeMB"] = replica_oplog_size

        result["replication"] = replication

    if is_shard_config or is_shard_data or is_shard_router:
        sharding = dict()

        if is_shard_router:
            sharding["configDB"] = configdb_url
        else:
            sharding["clusterRole"] = sharding_cluster_role

        result["sharding"] = sharding

    if not is_shard_config:
        storage = dict(
            dbPath = db,
            directoryPerDB = True,
            indexBuildRetry = index_build_retry,
            journal = dict(
                commitIntervalMs = journal_commit_interval,
                enabled = journal_enabled
            )
        )

        if storage_engine != 0:
            storage["engine"] = storage_engine

        if sync_period != 0:
            storage["syncPeriodSecs"] = sync_period

        result["storage"] = storage

    return yaml.safe_dump(result, default_flow_style=False, indent=4)

class FilterModule(object):
    def filters(self):
        return {"mongodb_url": mongodb_url,
                "mongodb_config": mongodb_config}

