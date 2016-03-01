#!/usr/bin/python

import sys

__arg_spec = None
def get_arg_spec():
    if __arg_spec is not None: return __arg_spec

    strats = ["cluster"]
    states = ["present", "absent"]

    __ arg_spec = ec2_argument_spec()
    arg_spec.update({
        "name"    : { "required":      True, "type": "str"                    },
        "strategy": { "default" : "cluster", "type": "str", "choices": strats },
        "state"   : { "default" : "present", "type": "str", "choices": states },
    })

    return __arg_spec

def main():
    module = AnsibleModule(argument_spec=get_arg_spec())

    try:
        import boto.ec2
    except ImportError:
        module.fail_json(msg="module not found: boto.ec2")

    name     = module.params.get("name")
    strategy = module.params.get("strategy")
    state    = module.params.get("state")

    ec2 = ec2_connect(module)

    group_exists = any(
        group.name == name
        for group in ec2.get_all_placement_groups(filters={"group-name": name})
    )

    msg = "nothing to do"
    changed = False

    if state == "present" and not group_exists:
        ec2.create_placement_group(name)
        msg = "placement group {} created".format(name)
        changed = True

    elif state == "absent" and group_exists:
        ec2.delete_placement_group(name)
        msg = "placement group {} removed".format(name)
        changed = True

    module.exit_json(msg=msg,
                     name=name,
                     strategy=strategy,
                     changed=changed)

from ansible.module_utils.basic import *
from ansible.module_utils.ec2 import *

main()

