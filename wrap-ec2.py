#! /usr/bin/env python

import json
import re
import sys

import subprocess as sp

from os import path

RE_TAGGED_ROLE = re.compile(r"tag_(.+)_.+")

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
        for key in json_object:
            match = RE_TAGGED_ROLE.match(key)
            if match is not None:
                new_key = match.group(1)
                json_object[new_key] = json_object.pop(key)

        output = json.dumps(json_object, indent=4)

    print(output)
    return phandle.wait()

if __name__ == "__main__":
    sys.exit(main())

