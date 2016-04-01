#!/usr/bin/python

import os
import traceback as tb

try:
    from configparser import SafeConfigParser as ConfigParser,
                             NoSectionError, NoOptionError
except ImportError:
    from ConfigParser import SafeConfigParser as ConfigParser,
                             NoSectionError, NoOptionError

def get_profile_value(parser, profile, key, default=None):
    result = default
    try:
        result = parser.get(profile, key)
    except (NoSectionError, NoOptionError):
        pass

    return result

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

    default_key_id = None
    default_secret = None

    if path is None:
        path = os.path.join(os.environ.get("HOME", "~"), ".aws", "credentials")

    try:
        parser = ConfigParser()
        parser.read([os.path.expanduser(path)])

        if profile is not None:
            key_id = get_profile_value(parser, profile, "aws_access_key_id")
            secret = get_profile_value(parser, profile, "aws_secret_access_key")

        default_key_id = get_profile_value(
            parser, "default", "aws_access_key_id")
        default_secret = get_profile_value(
            parser, "default", "aws_secret_access_key")
    except:
        fail(
            msg="unknown error occured",
            error=tb.format_exc(),
        )
        raise

    if key_id is None or secret is None:
        key_id = os.environ.get("AWS_ACCESS_KEY_ID")
        secret = os.environ.get("AWS_SECRET_ACCESS_KEY")

    if key_id is None or secret is None:
        key_id = default_key_id
        secret = default_secret

    if key_id is None or secret is None:
        result = fail
        result_data = {
            "msg": "failed to acquire a suitable set of AWS credentials",
            "changed": False,
            "aws_access_key_id": key_id,
            "aws_secret_key": secret,
        }
    else:
        result = exit
        result_data = {
            "msg": "AWS credentials successfully set",
            "changed": False,
            "access_key_id": key_id,
            "secret_key": secret,
        }

    if set_facts:
        result_data["ansible_facts"] = {
            "aws_access_key_id": result_data["access_key_id"],
            "aws_secret_key": result_data["secret_key"],
        }

    result(**result_data)


from ansible.module_utils.basic import *

main()
