#!/usr/bin/python

import os
import traceback as tb

from ConfigParser import ConfigParser

def main():
    arg_spec = {
        "profile"  : { "type": "str" , "required": False, },
        "path"     : { "type": "str" , "required": False, },
        "set_facts": { "type": "bool", "default" : True , },
    }

    module = AnsibleModule(argument_spec=arg_spec)
    get = module.params.get
    exit = module.exit_json
    fail = module.fail_json

    profile   = get("profile")
    path      = get("path")
    set_facts = get("set_facts")

    if path is None:
        path = os.path.join(os.environ.get("HOME", "~"), ".aws", "credentials")

    key_id = os.environ.get("AWS_ACCESS_KEY_ID")
    secret = os.environ.get("AWS_SECRET_ACCESS_KEY")

    try:
        if not (key_id and secret):
            parser = ConfigParser()
            parser.read([os.path.expanduser(path)])
            key_id = parser.get(profile, "aws_access_key_id")
            secret = parser.get(profile, "aws_secret_access_key")
    except:
        fail(
            msg="unknown error occured",
            error=tb.format_exc(),
        )
        raise

    result = {
        "msg": "AWS credentials successfully set",
        "changed": False,
        "access_key_id": key_id,
        "secret_key": secret,
    }

    if set_facts:
        result["ansible_facts"] = {
            "aws_access_key_id": result["access_key_id"],
            "aws_secret_key": result["secret_key"],
        }

    exit(**result)


from ansible.module_utils.basic import *

main()
