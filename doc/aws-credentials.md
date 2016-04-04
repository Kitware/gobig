
### aws-credentials
Load a set of AWS credentials as Ansible facts

The `aws-credentials` role sets facts that later roles and tasks can use to
interract with Amazon's AWS service.  It supports aws profiles, environment
variables, and setting credentials explicitly in a playbook.

#### Variables

|Name           |Default                 |Description                           |
|:--------------|:----------------------:|:-------------------------------------|
|access_key     |(see notes)             |access key ID                         |
|path           |"$HOME/.aws/credentials"|file path to the aws credentials file |
|profile        |"default"               |aws credentials profile               |
|secret_key     |(see notes)             |secret key                            |

#### Notes

  - If provided, the `access_key` given will be passed through as-is.
    Otherwise, the `AWS_ACCESS_KEY_ID` environment variable is used.  If the
    environment variable is not set, `access_key` is taken from the given
    `profile` in the aws credentials file given by `path`.

  - If provided, the `secret_key` given will be passed through as-is.
    Otherwise, the `AWS_SECRET_ACCESS_KEY` environment variable is used.  If the
    environment variable is not set, `secret_key` is taken from the given
    `profile` in the aws credentials file given by `path`.

#### Examples

Parse the default aws credentials file and return the credentials for the
`gobig` profile.

```YAML
  - hosts: localhost
    connection: local
    roles:
      - role: aws-credentials
        profile: gobig
```

