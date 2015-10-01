
AWS_CREDENTIALS_FILE="$HOME/.aws/credentials"

if [ -f "$AWS_CREDENTIALS_FILE" ] ; then
    AWS_ACCESS_KEY_ID="$(
        awk '/aws_access_key/{print $3;}' < "$AWS_CREDENTIALS_FILE" )"
    AWS_SECRET_ACCESS_KEY="$(
        awk '/aws_secret_access_key/{print $3;}' < "$AWS_CREDENTIALS_FILE" )"
    export AWS_ACCESS_KEY_ID
    export AWS_SECRET_ACCESS_KEY
fi

