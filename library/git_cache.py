#!/usr/bin/python

import hashlib
import os
import shutil
import subprocess as sp
import traceback as tb

from os import path

def main(DEVNULL):
    states = ["present", "absent"]

    arg_spec = {
        "key_file": { "type": "str", "required": False,                     },
        "repo"    : { "type": "str", "required": True ,                     },
        "state"   : { "type": "str", "required": True , "choices": states   },
        "version" : { "type": "str",                    "default": "master" },
    }

    module = AnsibleModule(argument_spec=arg_spec)
    get = module.params.get
    exit = module.exit_json
    fail = module.fail_json

    key_file = get("key_file")
    repo     = get("repo")
    version  = get("version")
    state    = get("state")

    try:
        sp.check_call(["which", "git"], stdout=DEVNULL, stderr=DEVNULL)
    except sp.CalledProcessError:
        fail(msg="git is not installed")
        return

    repo_hash = hashlib.sha1()
    repo_hash.update(repo)
    repo_hash = "".join("%02x" % ord(char) for char in repo_hash.digest())

    base_dir = path.join(
        "/repo",
        path.join(*tuple(
            tok for tok in
            (repo_hash[:2], repo_hash[2:4], repo_hash[4:])
            if tok
        ))
    )

    repo_path = path.join(base_dir, "git")
    work_path = path.join(base_dir, "work")

    if state == "present":
        try:
            try: os.makedirs(base_dir)
            except OSError: pass

            old_rev = None
            if path.exists(work_path):
                old_rev = sp.check_output(
                    ["git", "rev-parse", "--no-flags", "HEAD"],
                    stderr=DEVNULL,
                    cwd=work_path
                )[:-1]

                sp.check_call(
                    ["git", "checkout", version],
                    stderr=DEVNULL,
                    cwd=work_path
                )
            else:
                sp.check_call(
                    [
                        "git",
                        "clone",
                        "-b", version,
                        "=".join(("--separate-git-dir", repo_path)),
                        repo,
                        work_path
                    ],
                    stderr=DEVNULL
                )

            new_rev = sp.check_output(
                ["git", "rev-parse", "--no-flags", "HEAD"],
                stderr=DEVNULL,
                cwd=work_path
            )[:-1]

            changed = (old_rev != new_rev)

            rev_path = path.join(*tuple(
                tok for tok in
                (new_rev[:2], new_rev[2:4], new_rev[4:])
                if tok
            ))

            try:
                tag = sp.check_output(
                    ["git", "describe", "--tags"],
                    stderr=DEVNULL,
                    cwd=work_path
                )[:-1]

                tag_path = tag
            except sp.CalledProcessError:
                tag = "-".join(("untagged", new_rev))
                tag_path = path.join("untagged", rev_path)

            exit(
                msg=("repository fetched successfully" if changed else
                     "repository revision already present"),
                changed=changed,
                old_revision=old_rev,
                revision=new_rev,
                tag=tag,
                revision_path=rev_path,
                tag_path=tag_path,
                repo_path=repo_path,
                work_path=work_path,
            )
        except sp.CalledProcessError as e:
            fail(msg="command execution failed", error=tb.format_exc())
            raise
        except OSError as e:
            fail(msg="os error occurred", error=tb.format_exc())
            raise

    else: # state == "absent"
        changed = False
        try: shutil.rmtree(repo_path)
        except OSError: pass
        else: changed = True

        try: shutil.rmtree(work_path)
        except OSError: pass
        else: changed = True

        try: os.removedirs(base_dir)
        except OSError: pass

        exit(
            msg=("repository removed successfully" if changed else
                 "repository not present"),
            changed=changed,
        )

from ansible.module_utils.basic import *

with open(os.devnull, "wb") as DEVNULL:
    main(DEVNULL)

