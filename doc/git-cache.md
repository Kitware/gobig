
### git-cache
Maintain a cache of cloned git repos

The `git-cache` role maintains a cache of cloned git repos that it populates
using the `git` ansible module.  It can be used most places where the `git`
ansible module would be used with the added benefit of having several additional
variables set that allow for easy inspection of the details of the repository.

#### Variables

|Name           |Default   |Description                                        |
|:--------------|:--------:|:--------------------------------------------------|
|key_file       |""        |ssh key file to use during checkout                |
|repo           |(required)|url to the git repository to clone                 |
|state          |present   |state of the repo cache entry                      |
|variable_prefix|""        |prefix to use for the output variables             |
|version        |master    |version of the repo to check out                   |

#### Notes

  - `state` can be "absent" or "present".
  - If defined, an underscore (`_`) is appended to `variable_prefix`.  This role
    sets the following variables after possibly adding the underscore:
      - `{{ variable_prefix }}git_hash`: SHA-1 hash of the provided url
      - `{{ variable_prefix }}git_repo_dir`: path to the `git` directory
        containing the repository files
      - `{{ variable_prefix }}git_work_dir`: path to the working copy
      - `{{ variable_prefix }}git_version`: repository version as reported by
        `git-describe`
  - `version` can refer to any branch name, tag name, or SHA-1 hash of any
    commit.

#### Examples

Clone the gobig repository and prepend the output variable names with "gobig_".
```YAML
  - hosts: all
    roles:
      - role: git-cache
        repo: git://github.com/kitware/gobig.git
        variable_prefix: gobig
```

