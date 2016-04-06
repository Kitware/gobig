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

        "version"  : { "type": "str" , "default" : "master" },
        "recursive": { "type": "bool", "default" : False    },
        "dest"     : { "type": "str" , "required": True     },
    }

    module = AnsibleModule(argument_spec=arg_spec)
    get = module.params.get
    exit = module.exit_json
    fail = module.fail_json

    key_file         = get("key_file")
    repo             = get("repo")
    version          = get("version")
    state            = get("state")
    recursive        = get("recursive")
    target_base_path = get("dest")

    try:
        sp.check_call(["which", "git"], stdout=DEVNULL, stderr=DEVNULL)
    except sp.CalledProcessError:
        fail(msg="git is not installed")
        return

    repo_hash = hashlib.sha1()
    repo_hash.update(repo)
    repo_hash = repo_hash.hexdigest()

    repo_base_path = path.join(
        "/repo",
        path.join(*tuple(
            tok for tok in
            (repo_hash[:2], repo_hash[2:4], repo_hash[4:])
            if tok
        ))
    )

    repo_path = path.join(repo_base_path, "git")
    work_path = path.join(repo_base_path, "work")

    if state == "present":
        try:
            try: os.makedirs(repo_base_path)
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

                sp.check_call(
                    ["git", "pull"],
                    stderr=DEVNULL,
                    cwd=work_path
                )

                if recursive:
                    sp.check_call(
                        ["git", "submodule", "update", "--init", "--recursive"],
                        stderr=DEVNULL,
                        cwd=work_path
                    )
            else:
                git_clone_command = ["git", "clone"]
                if recursive:
                    git_clone_command.append("--recursive")

                git_clone_command.extend([
                    "-b", version,
                    "=".join(("--separate-git-dir", repo_path)),
                    repo,
                    work_path
                ])

                sp.check_call(git_clone_command, stderr=DEVNULL)

            new_rev = sp.check_output(
                ["git", "rev-parse", "--no-flags", "HEAD"],
                stderr=DEVNULL,
                cwd=work_path
            )[:-1]

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

            target_path = path.join(target_base_path, tag_path)

            old_hash = None
            if path.exists(target_path):
                try:
                    old_hash = sp.check_output(
                        "find . -type f -exec sha1sum '{}' \\; | sha1sum",
                        stderr=DEVNULL,
                        shell=True,
                        cwd=target_path
                    ).split()[0]
                except CalledProcessError:
                    pass
            else:
                os.makedirs(target_path)

            sp.check_call(
                [
                    "rsync",
                    "-acvz",
                    "--exclude=.git/",
                    "--exclude=.git",
                    "--delete-after",
                    "--delete-excluded",
                    "./",
                    target_path
                ],
                stderr=DEVNULL,
                cwd=work_path
            )

            new_hash = sp.check_output(
                "find . -type f -exec sha1sum '{}' \\; | sha1sum",
                stderr=DEVNULL,
                shell=True,
                cwd=target_path
            ).split()[0]

            changed = (old_hash != new_hash)

            exit(
                msg=("repository fetched successfully" if changed else
                     "repository revision already present"),
                changed=changed,
                old_revision=old_rev,
                old_checksum=old_hash,
                revision=new_rev,
                tag=tag,
                revision_path=rev_path,
                tag_path=tag_path,
                repo_path=repo_path,
                work_path=work_path,
                checksum=new_hash,
                destination=target_path
            )
        except sp.CalledProcessError as e:
            fail(msg="command execution failed", error=tb.format_exc())
            raise
        except OSError as e:
            fail(msg="os error occurred", error=tb.format_exc())
            raise

    else: # state == "absent"
        changed = False
        try: shutil.rmtree(target_base_path)
        except OSError: pass
        else: changed = True

        try: shutil.rmtree(repo_path)
        except OSError: pass
        else: changed = True

        try: shutil.rmtree(work_path)
        except OSError: pass
        else: changed = True

        try: os.removedirs(repo_base_path)
        except OSError: pass

        exit(
            msg=("repository removed successfully" if changed else
                 "repository not present"),
            changed=changed,
        )

from ansible.module_utils.basic import *

with open(os.devnull, "wb") as DEVNULL:
    main(DEVNULL)

