#!/bin/bash

# Read the password from user input
PASSWORD=''
PROFILE='038'

# Loop through the users file and create the users with the specified password
while read user; do
    # Create the user with the specified password
    aws iam create-user --user-name "$user" --profile $PROFILE
    aws iam add-user-to-group --group-name students --user-name "$user" --profile $PROFILE
    aws iam create-login-profile --user-name "$user" --password "$PASSWORD" --password-reset-required --profile $PROFILE
    sleep 3
done < users.txt