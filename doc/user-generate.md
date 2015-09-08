
### user-generate
Creates a new user, and more

The `user-generate` role works like the `user` ansible module, except that it
will also create a new group for the user if the desired group is not present,
and add the new user's ssh key to its own list of authorized keys.

#### Variables

|Name         |Default    |Description                                         |
|:------------|:---------:|:---------------------------------------------------|
|crypt_pass   |(generated)|SHA-512 hash of the user's password                 |
|force        |false      |whether to replace a preexisting user               |
|group        |`name`     |name of the new user's group                        |
|local_ssh_key|(optional) |local key to add to the user's authorized keys list |
|name         |(required) |name of the new user                                |
|state        |present    |state of the user                                   |
|system       |false      |whether to create a system user                     |
|system_group |`system`   |whether to create a system group                    |

#### Notes

  - By default, the hash for a blank password is used when creating
    a new user, disabling password login.

  - If provided, the ssh-key in `local_ssh_key` will be added to the user's list
    of authorized keys as well as its own generated key.

  - `state` can be "absent", or "present".

  - By default, a new user will not be created if one with the same name already
    exists.  Set `force` to "true" to replace a preexisting user of the same
    name.

#### Examples

Create a new non-system user, "bob".  It will be placed in a non-system group
also named "bob".  The user will not be able to log in using a password.  The
user will have a generated ssh-key whose public key will be added to its own
list of authorized keys.  The public key of the local user running ansible will
be added, as well.
```YAML
  - hosts: all
    roles:
      - role: user-generate
        name: bob
        local_ssh_key: "{{ lookup('file', '~/.ssh/id_rsa.pub') }}"
```

Remove "bob"
```YAML
  - hosts: all
    roles:
      - role: user-generate
        name: bob
        state: absent
```

Create a new system user, "custom-service-user".  It will be placed in a
*non-system* group named "all-users".  The given hash allows the system user to
login using the password "gobig".
```YAML
  - hosts: all
    roles:
      - role: user-generate
        name: custom-service-user
        group: all-users
        system: true
        system_group: false
        crypt_pass: "$6$x/XyhbGVzDN0WOf$EN\
                     h0Tcrqaiv5axQRgV8yP/.\
                     977ZhO9kLaQqXX4V8GFmU\
                     esIJ1N4XQQXJqLjEQ3Cos\
                     vBkoPsO/HXGhtmK3l9R6."
```

