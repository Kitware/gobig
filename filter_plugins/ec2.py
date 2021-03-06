
def flatten_ec2_result(ec2_result):
    result = []
    for entry in ec2_result["results"]:
        for instance in entry["tagged_instances"]:
            result.append({"hostname": instance["public_dns_name"],
                           "ip": instance["public_ip"],
                           "id": instance["id"],
                           "eip": entry["item"]["value"]["ip"],
                           "wait": entry["item"]["value"]["wait"],
                           "groups": entry["item"]["value"]["ansible_groups"]})

    return result

def compute_ec2_update_lists(pod_name, instances, state, region, key_id, key):
    from collections import defaultdict
    from itertools import chain
    from boto import ec2

    conn = ec2.connect_to_region(region,
                                 aws_access_key_id=key_id,
                                 aws_secret_access_key=key)

    if conn is None:
        raise Exception(" ".join((
            "region name:",
            region,
            "likely not supported, or AWS is down."
            "connection to region failed.")))

    reservations = conn.get_all_instances()

    # short-circuit the case where the pod should be terminated
    if state == "absent":
        return {"start": [], "terminate": list(set(
            chain.from_iterable(
                (instance.id for instance in reservation.instances
                 if instance.tags.get("ec2_pod") == pod_name)
                for reservation in reservations)
        ))}

    ec2_host_table = defaultdict(lambda: defaultdict(set))
    for reservation in reservations:
        for instance in reservation.instances:
            if instance.tags.get("ec2_pod") != pod_name:
                continue

            if instance.state not in ("running", "stopped"):
                continue

            instance_name = instance.tags.get("ec2_pod_instance_name")
            composite_key = (unicode(instance_name),
                             unicode(instance.key_name),
                             unicode(instance.image_id),
                             unicode(instance.instance_type))

            ec2_host_table[composite_key][instance.state].add(instance.id)

    host_counter_table = dict(
        (
            (
                unicode(instance["count_tag"]["ec2_pod_instance_name"]),
                unicode(instance["ssh_key"]),
                unicode(instance["image"]),
                unicode(instance["type"])
            ),
            instance.get("count", 1)
        )
        for instance in instances.values()
    )

    start_set = set()
    terminate_set = set()

    for composite_key, sets in ec2_host_table.items():
        running_list = list(sets["running"])
        stopped_list = list(sets["stopped"])

        num_running = len(running_list)
        num_stopped = len(stopped_list)

        num_wanted = host_counter_table.get(composite_key, 0)

        num_to_keep = min(num_running, num_wanted)
        num_to_start = num_wanted - num_to_keep

        start_set |= set(stopped_list[:num_to_start])

        terminate_set |= set(stopped_list[num_to_start:])
        terminate_set |= set(running_list[num_to_keep:])

    return {"start": list(start_set), "terminate": list(terminate_set)}

def compute_ec2_ein_mapping(ec2_result, region, key_id, key):
    from boto import ec2

    conn = ec2.connect_to_region(region,
                                 aws_access_key_id=key_id,
                                 aws_secret_access_key=key)

    if conn is None:
        raise Exception(" ".join((
            "region name:",
            region,
            "likely not supported, or AWS is down."
            "connection to region failed.")))

    reservations = conn.get_all_instances()

    security_group_mapping = {
        group.name: group.id
        for group in conn.get_all_security_groups()
    }

    eni_mapping = {
        eni.attachment.instance_id: eni.id
        for eni in conn.get_all_network_interfaces()
    }

    result = {}
    for entry in ec2_result["results"]:
        groups = [
            security_group_mapping.get(group, group)
            for group in entry["item"]["value"]["group"]]

        result.update({
            eni_mapping[instance["id"]]: groups
            for instance in entry["tagged_instances"]})

    # TODO(opadron): need to remove this once we switch to Ansible 2.0
    for eni_id, groups in result.items():
        conn.modify_network_interface_attribute(interface_id=eni_id,
                                                attr="groupSet",
                                                value=groups)

    return result

def get_ec2_hosts(instance_table):
    import operator as op
    return map(op.itemgetter("id"), instance_table)

def get_ec2_eips(instance_table):
    import operator as op
    return map(
        op.itemgetter("eip", "id"),
        filter(op.itemgetter("eip"), instance_table))

def get_ec2_wait_list(instance_table, host_key):
    import operator as op
    return map(
        op.itemgetter(host_key),
        filter(op.itemgetter("wait"), instance_table))

class FilterModule(object):
    def filters(self):
        return {"compute_ec2_update_lists": compute_ec2_update_lists,
                "flatten_ec2_result": flatten_ec2_result,
                "compute_ec2_ein_mapping": compute_ec2_ein_mapping,
                "get_ec2_wait_list": get_ec2_wait_list,
                "get_ec2_hosts": get_ec2_hosts,
                "get_ec2_eips": get_ec2_eips}

