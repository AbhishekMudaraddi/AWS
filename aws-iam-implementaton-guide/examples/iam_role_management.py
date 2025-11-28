#!/usr/bin/env python3
"""
AWS IAM Role Management Examples
Demonstrates IAM role creation and management using boto3
"""

import boto3
import json
from botocore.exceptions import ClientError

# Initialize IAM client
iam_client = boto3.client('iam')


def create_iam_role(role_name, trust_policy, description=""):
    """Create an IAM role with a trust policy"""
    try:
        response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description=description
        )
        print(f"✅ Created IAM role: {role_name}")
        print(f"   Role ARN: {response['Role']['Arn']}")
        return response['Role']
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print(f"⚠️  Role {role_name} already exists")
        else:
            print(f"❌ Error creating role: {e}")
        return None


def attach_policy_to_role(role_name, policy_arn):
    """Attach a managed policy to a role"""
    try:
        iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_arn
        )
        print(f"✅ Attached policy {policy_arn} to role {role_name}")
    except ClientError as e:
        print(f"❌ Error attaching policy: {e}")


def create_instance_profile(profile_name):
    """Create an instance profile for EC2"""
    try:
        response = iam_client.create_instance_profile(
            InstanceProfileName=profile_name
        )
        print(f"✅ Created instance profile: {profile_name}")
        return response['InstanceProfile']
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print(f"⚠️  Instance profile {profile_name} already exists")
        else:
            print(f"❌ Error creating instance profile: {e}")
        return None


def add_role_to_instance_profile(role_name, profile_name):
    """Add a role to an instance profile"""
    try:
        iam_client.add_role_to_instance_profile(
            InstanceProfileName=profile_name,
            RoleName=role_name
        )
        print(f"✅ Added role {role_name} to instance profile {profile_name}")
    except ClientError as e:
        print(f"❌ Error adding role to instance profile: {e}")


def assume_role(role_arn, session_name):
    """Assume an IAM role and get temporary credentials"""
    sts_client = boto3.client('sts')
    try:
        response = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName=session_name
        )
        credentials = response['Credentials']
        print(f"✅ Assumed role: {role_arn}")
        print(f"   Access Key ID: {credentials['AccessKeyId']}")
        print(f"   Expires: {credentials['Expiration']}")
        return credentials
    except ClientError as e:
        print(f"❌ Error assuming role: {e}")
        return None


# Example trust policies
EC2_TRUST_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "ec2.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}

LAMBDA_TRUST_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}

CROSS_ACCOUNT_TRUST_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::123456789012:root"
            },
            "Action": "sts:AssumeRole",
            "Condition": {
                "StringEquals": {
                    "sts:ExternalId": "unique-external-id-12345"
                }
            }
        }
    ]
}


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("AWS IAM Role Management Examples")
    print("=" * 60)
    
    # Example 1: Create EC2 role
    ec2_role_name = "EC2-S3-Access-Role"
    create_iam_role(
        ec2_role_name,
        EC2_TRUST_POLICY,
        "Allows EC2 instances to access S3"
    )
    attach_policy_to_role(ec2_role_name, "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess")
    
    # Create instance profile for EC2
    profile_name = "EC2-S3-Access-Profile"
    create_instance_profile(profile_name)
    add_role_to_instance_profile(ec2_role_name, profile_name)
    
    # Example 2: Create Lambda role
    lambda_role_name = "Lambda-DynamoDB-Role"
    create_iam_role(
        lambda_role_name,
        LAMBDA_TRUST_POLICY,
        "Allows Lambda to access DynamoDB"
    )
    attach_policy_to_role(lambda_role_name, "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess")
    
    # Example 3: Cross-account role (commented - requires account ID)
    # cross_account_role = "CrossAccountAccessRole"
    # create_iam_role(cross_account_role, CROSS_ACCOUNT_TRUST_POLICY)
    
    print("\n" + "=" * 60)
    print("Note: This is a demonstration script.")
    print("Review and modify before running in production!")
    print("=" * 60)

