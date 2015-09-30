
### nodejs
Installs nodejs from source

#### Variables

|Name               |Default    |Description                                   |
|:------------------|:---------:|:---------------------------------------------|
|nodejs_install_root|(generated)|root directory to install nodejs under        |
|nodejs_version     |v4.0.0     |version of nodejs to install                  |
|recompile          |false      |whether to force recompilation of nodejs      |
|state              |present    |state of the software package                 |

#### Notes

  -  The `nodejs_version` value can be any tag, branch, or commit hash from the
     nodejs github repository.

  - `state` can be either "absent" or "present".

#### Examples

Install/Configure
```YAML
  - hosts: nodejs
    roles:
      - role: nodejs
        state: present
```

Uninstall
```YAML
  - hosts: nodejs
    roles:
      - role: nodejs
        state: absent
```

