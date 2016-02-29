
def process_aws_credentials(config_path, profile, key_id, key):
    """parses the given AWS credentials file and returns the referenced set of
    AWS credentials.

    The return value is a dictionary with the keys ``key_id`` and ``key``
    containing the access key id and the secret access key, respectively.
    If either ``key_id` or ``key`` are provided, the provided credentials are
    returned without parsing any files.

    :param config_path: path to credentials file to parse
    :param profile: AWS profile from which to extract credentials while parsing
    :param key_id: AWS access key id to use (disables parsing)
    :param key: AWS secret access key to use (disables parsing)

    :returns: the AWS credentials from the given profile, or the directly passed
              credentials
    """

    from os.path import expanduser
    from ConfigParser import ConfigParser

    if not (key_id or key):
        parser = ConfigParser()
        parser.read([expanduser(config_path)])
        key_id = parser.get(profile, "aws_access_key_id")
        key    = parser.get(profile, "aws_secret_access_key")

    return { "key_id": key_id, "key": key }

class FilterModule(object):
    def filters(self):
        return {"process_aws_credentials": process_aws_credentials,}

