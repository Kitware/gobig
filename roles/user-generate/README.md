
### user-generate
Creates a new user, and more

The `user-generate` role works like the `user` ansible module, except that it
will also create a new group for the user if the desired group is not present,
and add the new user's ssh key to its own list of authorized keys.

#### Variables

|Name        |Default    |Description                                |
|:-----------|:---------:|:------------------------------------------|
|name        |(required) |name of the new user                       |
|crypt_pass  |(generated)|hash of the password to use for the user   |
|state       |present    |state of the user                          |
|group       |`name`     |name of the new user's group               |
|system      |false      |whether to create a system user            |
|system_group|`system`   |whether to create a system group           |

#### Notes

  - By default, the hash for a blank password is used when creating
    a new user, disabling password login.

  - `state` can be "absent", or "present".

#### Examples

Create a new non-system user, "bob".  It will be placed in a non-system group
also named "bob".  The user will not be able to log in using a password.  The
user will have a generated ssh-key that will also be added to its own list of
authorized keys.
```YAML
  - hosts: all
    roles:
      - role: user-generate
        name: bob
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

