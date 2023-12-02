#!/bin/bash


PROFILE='038'
ACCOUNT_ID='700935310038'
REGION='us-east-1'

# Loop through the users file and create the users with the specified password
while read user; do
    aws cloud9 create-environment-ec2 --profile $PROFILE --name $user --instance-type t2.medium --automatic-stop-time-minutes 30 --owner-arn arn:aws:iam::$ACCOUNT_ID:user/$user --region $REGION --connection-type CONNECT_SSM --image-id ubuntu-22.04-x86_64
    sleep 60
done < users.txt