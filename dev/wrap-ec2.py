#! /usr/bin/env python

import json
import re
import sys

import subprocess as sp

from os import path

RE_TAGGED_ROLE = re.compile(r"tag_(.+)_.*")

def main():
    argv = [path.join(path.realpath(path.dirname(
        sys.argv[0])), "ec2.py")] + sys.argv[1:]

    phandle = sp.Popen(argv, stdout=sp.PIPE)
    output = phandle.stdout.read()

    try:
        json_object = json.loads(output)
    except ValueError:
        pass
    else:
        update_dict = {}
        update_keys = {}
        for key in json_object:
            match = RE_TAGGED_ROLE.match(key)
            if match is not None:
                new_key = match.group(1)
                update_set = update_dict.get(new_key, set([]))
                update_set |= set(json_object[key])
                update_dict[new_key] = update_set

                key_set = update_keys.get(new_key, set([]))
                key_set.add(key)
                update_keys[new_key] = key_set

        for key, val in update_dict.items():
            json_object[key] = list(val)

            for old_key in update_keys[key]:
                del json_object[old_key]

        output = json.dumps(json_object, indent=4)

    print(output)
    return phandle.wait()

if __name__ == "__main__":
    sys.exit(main())

