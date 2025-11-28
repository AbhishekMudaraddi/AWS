#!/usr/bin/env python3
"""
AWS IAM User Management Examples
Demonstrates common IAM user operations using boto3
"""

import boto3
import json
from botocore.exceptions import ClientError

# Initialize IAM client
iam_client = boto3.client('iam')


def create_iam_user(username):
    """Create a new IAM user"""
    try:
        response = iam_client.create_user(UserName=username)
        print(f"✅ Created IAM user: {username}")
        print(f"   User ARN: {response['User']['Arn']}")
        return response['User']
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print(f"⚠️  User {username} already exists")
        else:
            print(f"❌ Error creating user: {e}")
        return None


def create_access_key(username):
    """Create access keys for an IAM user"""
    try:
        response = iam_client.create_access_key(UserName=username)
        access_key = response['AccessKey']
        print(f"✅ Created access key for {username}")
        print(f"   Access Key ID: {access_key['AccessKeyId']}")
        print(f"   ⚠️  Secret Access Key: {access_key['SecretAccessKey']}")
        print(f"   ⚠️  Store this securely - it won't be shown again!")
        return access_key
    except ClientError as e:
        print(f"❌ Error creating access key: {e}")
        return None


def attach_policy_to_user(username, policy_arn):
    """Attach a managed policy to a user"""
    try:
        iam_client.attach_user_policy(
            UserName=username,
            PolicyArn=policy_arn
        )
        print(f"✅ Attached policy {policy_arn} to user {username}")
    except ClientError as e:
        print(f"❌ Error attaching policy: {e}")


def create_custom_policy(policy_name, policy_document):
    """Create a custom IAM policy"""
    try:
        response = iam_client.create_policy(
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_document)
        )
        print(f"✅ Created custom policy: {policy_name}")
        print(f"   Policy ARN: {response['Policy']['Arn']}")
        return response['Policy']
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print(f"⚠️  Policy {policy_name} already exists")
        else:
            print(f"❌ Error creating policy: {e}")
        return None


def create_iam_group(group_name):
    """Create an IAM group"""
    try:
        response = iam_client.create_group(GroupName=group_name)
        print(f"✅ Created IAM group: {group_name}")
        return response['Group']
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print(f"⚠️  Group {group_name} already exists")
        else:
            print(f"❌ Error creating group: {e}")
        return None


def add_user_to_group(username, group_name):
    """Add a user to an IAM group"""
    try:
        iam_client.add_user_to_group(
            GroupName=group_name,
            UserName=username
        )
        print(f"✅ Added user {username} to group {group_name}")
    except ClientError as e:
        print(f"❌ Error adding user to group: {e}")


def list_users():
    """List all IAM users"""
    try:
        response = iam_client.list_users()
        users = response['Users']
        print(f"\n📋 Found {len(users)} IAM users:")
        for user in users:
            print(f"   - {user['UserName']} (Created: {user['CreateDate']})")
        return users
    except ClientError as e:
        print(f"❌ Error listing users: {e}")
        return []


def get_user_policies(username):
    """Get all policies attached to a user"""
    try:
        # Get attached managed policies
        attached_policies = iam_client.list_attached_user_policies(UserName=username)
        
        # Get inline policies
        inline_policies = iam_client.list_user_policies(UserName=username)
        
        print(f"\n📋 Policies for user {username}:")
        print("   Managed Policies:")
        for policy in attached_policies['AttachedPolicies']:
            print(f"      - {policy['PolicyName']} ({policy['PolicyArn']})")
        
        print("   Inline Policies:")
        for policy_name in inline_policies['PolicyNames']:
            print(f"      - {policy_name}")
    except ClientError as e:
        print(f"❌ Error getting user policies: {e}")


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("AWS IAM User Management Examples")
    print("=" * 60)
    
    # Example: Create a user
    username = "demo-user"
    create_iam_user(username)
    
    # Example: Create access keys (commented out for security)
    # create_access_key(username)
    
    # Example: Attach AWS managed policy
    attach_policy_to_user(username, "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess")
    
    # Example: Create custom policy
    custom_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:ListBucket"
                ],
                "Resource": [
                    "arn:aws:s3:::my-bucket/*",
                    "arn:aws:s3:::my-bucket"
                ]
            }
        ]
    }
    create_custom_policy("MyCustomS3Policy", custom_policy)
    
    # Example: Create group and add user
    group_name = "developers"
    create_iam_group(group_name)
    add_user_to_group(username, group_name)
    
    # List all users
    list_users()
    
    # Get user policies
    get_user_policies(username)
    
    print("\n" + "=" * 60)
    print("Note: This is a demonstration script.")
    print("Review and modify before running in production!")
    print("=" * 60)

