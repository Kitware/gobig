#!/usr/bin/python

from itertools import chain, product

def reg_get(x, *items):
    try:
        for item in items:
            if item not in x:
                return None
            x = x[item]
        return x
    except TypeError:
        return None

def detect_cycles(template_namespace):
    result = False

    for object in template_namespace.values():
        iter_flag = False

        tracer_a = reg_get(object, "extends")
        if tracer_a is None: break

        tracer_b = reg_get(reg_get(template_namespace, tracer_a), "extends")

        result = (tracer_a == tracer_b)
        while not result and tracer_b is not None:
            if iter_flag:
                tracer_a = reg_get(
                    reg_get(template_namespace, tracer_a), "extends")

            tracer_b = reg_get(reg_get(template_namespace, tracer_b), "extends")

            iter_flag = not iter_flag
            result = (tracer_a == tracer_b)

        if result: break

    return result

def render_helper(target, ns, result=None):
    if result is None: result = {}
    if target is None: return result

    render_helper(ns.get(target.get("extends")), ns, result)
    result.update(target)

    return result

def render(target, ns):
    result = render_helper(target, ns)
    result.pop("extends", None)
    return result

def process_rule(pod_name, rule, egress=False):
    base = {}
    base.update(rule)

    flow = base.pop("flow", "in")
    skip_rule = (     flow != "sym"
                 and (flow != "out" or not egress)
                 and (flow != "in"  or     egress))

    if skip_rule: return

    ports = []
    port = base.pop("port", None)
    if port is not None:
        try:
            for port_entry in port:
                try:              from_port, to_port = tuple(port_entry)
                except TypeError: from_port, to_port = (port_entry, port_entry)
                ports.append((from_port, to_port))
        except TypeError:
            ports.append((port, port))

    if not ports:
        ports.append(None)

    groups = base.pop("group", None)
    if isinstance(groups, basestring) or groups is None: groups = [groups]

    protos = base.pop("proto", "all")
    if isinstance(protos, basestring): protos = [protos]

    for (port_entry, group, proto) in product(ports, groups, protos):
        result = {}
        result.update(base)

        from_port, to_port = (
            2*("all",) if proto == "all" else
            2*(-1,) if proto == "icmp" else
            (1, (1 << 16) - 1)
        )

        if port_entry is not None:
            from_port, to_port = port_entry

        result["from_port"] = from_port
        result["to_port"] = to_port

        if group is not None:
            result["group_name"] = "_".join((pod_name, "sg", group))
            result["group_desc"] =  "".join((
                "ec2 pod security group: ", pod_name, "/", group))

        if proto is not None:
            result["proto"] = proto

        yield result

def process_instance(pod_name, instance_name, instance):
    result = {}
    result.update(instance)

    volumes = result.pop("volumes", [])
    if volumes:
        volumes = [
            {
                "device_name": "/dev/xvd" + chr(ord("b") + index),
                "volume_size": size,
                "delete_on_termination": True
            }
            for index, size in enumerate(volumes)
        ]

    result["volumes"] = volumes

    placement_group = result.pop("placement_group", None)
    if placement_group is not None:
        placement_group = "_".join((pod_name, "pg", placement_group))
        result["placement_group"] = placement_group

    security_groups = result.pop("security_groups", [])
    extra_security_groups = result.pop("extra_security_groups", [])
    security_groups = set(security_groups) | set(extra_security_groups)
    if security_groups:
        security_groups = [
            "_".join((pod_name, "sg", security_group))
            for security_group in security_groups
        ]
        result["group"] = security_groups

    ansible_groups = result.pop("ansible_groups", [])
    extra_ansible_groups = result.pop("extra_ansible_groups", [])
    ansible_groups = set(ansible_groups) | set(extra_ansible_groups)
    if ansible_groups:
        result["ansible_groups"] = list(ansible_groups)

    result["count"] = result.pop("count", 1)

    result["count_tag"] = {
        "Name": "_".join((pod_name, "in", instance_name)),
        "ec2_pod": pod_name,
        "ec2_pod_instance_name": instance_name
    }

    ssh_key = result.pop("ssh_key")
    ssh_key = "_".join((pod_name, "key", ssh_key))
    result["ssh_key"] = ssh_key

    eip = result.pop("ip", None)
    if eip is not None:
        if result["count"] > 1:
            raise ValueError(
                "Cannot associate an elastic IP when count > 1")

    result["ip"] = eip

    result["wait"] = result.pop("wait", True)

    return result

def main():
    states = ["present", "running", "stopped", "absent"]

    arg_spec = {
        "instances"       : { "type": "dict" },
        "name"            : { "type": "str"  },
        "options"         : { "type": "dict" },
        "placement_groups": { "type": "dict" },
        "security_groups" : { "type": "dict" },
        "ssh_keys"        : { "type": "dict" },
        "state"           : { "type": "str", "choices": states },
        "region"          : { "type": "str"  },
        "templates"       : { "type": "dict" },
    }

    module = AnsibleModule(argument_spec=arg_spec)
    get = module.params.get
    exit = module.exit_json
    fail = module.fail_json

    instances        = get("instances"       )
    pod_name         = get("name"            )
    options          = get("options"         )
    placement_groups = get("placement_groups")
    security_groups  = get("security_groups" )
    ssh_keys         = get("ssh_keys"        )
    state            = get("state"           )
    region           = get("region"          )
    templates        = get("templates"       )

    ssh_keys = {
        "_".join((pod_name, "key", key_name)): key_path
        for key_name, key_path in ssh_keys.items()
    }

    instance_templates = reg_get(templates, "instances") or {}
    if detect_cycles(instance_templates):
        fail(msg="cycle detected among instance templates",
             templates=instance_templates,
             changed=False)
        return

    placment_group_templates = reg_get(templates, "placment_groups") or {}
    if detect_cycles(placment_group_templates):
        fail(msg="cycle detected among placement group templates",
             templates=placment_group_templates,
             changed=False)
        return

    rule_templates = reg_get(templates, "rules") or {}
    if detect_cycles(rule_templates):
        fail(msg="cycle detected among rule templates",
             templates=rule_templates,
             changed=False)
        return

    instances = {
        "_".join((pod_name, "in", instance_name)):
            process_instance(
                pod_name,
                instance_name,
                render(instance, instance_templates))
        for instance_name, instance in instances.items()
    }

    placment_groups = {
        "_".join((pod_name, "pg", group_name)):
            render(placment_group, placment_group_templates)
        for group_name, placment_group in placement_groups.items()
    }

    security_groups = {
        "_".join((pod_name, "sg", group_name)): {
            "rules": list(chain.from_iterable(
                process_rule(pod_name, rendered_rule, False)
                for rendered_rule in rendered_rules
            )),

            "rules_egress": list(chain.from_iterable(
                process_rule(pod_name, rendered_rule, True)
                for rendered_rule in rendered_rules
            )),

            "description": "".join((
                "ec2 pod security group: ", pod_name, "/", group_name))
        }

        for group_name, rendered_rules in (
            (
                name, tuple(render(rule, rule_templates)
                            for rule in rules)
            )
            for name, rules in security_groups.items()
        )
    }

    exit(msg="pod processed successfully",
         instances=instances,
         name=pod_name,
         options=options,
         placement_groups=placement_groups,
         security_groups=security_groups,
         region=region,
         ssh_keys=ssh_keys,
         state=state,
         changed=True)

from ansible.module_utils.basic import *

main()

