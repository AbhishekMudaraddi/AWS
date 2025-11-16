#!/usr/bin/env python3
"""
AWS IAM Policy Examples
Demonstrates various IAM policy patterns and best practices
"""

import json


# Example 1: S3 Bucket Read-Only Access
S3_READ_ONLY_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::my-bucket",
                "arn:aws:s3:::my-bucket/*"
            ]
        }
    ]
}

# Example 2: S3 Bucket with Conditions (IP Restriction)
S3_IP_RESTRICTED_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": "arn:aws:s3:::my-bucket/*",
            "Condition": {
                "IpAddress": {
                    "aws:SourceIp": "203.0.113.0/24"
                }
            }
        }
    ]
}

# Example 3: Time-Based Access (MFA Required)
MFA_REQUIRED_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:StartInstances",
                "ec2:StopInstances"
            ],
            "Resource": "*",
            "Condition": {
                "BoolIfExists": {
                    "aws:MultiFactorAuthPresent": "true"
                }
            }
        }
    ]
}

# Example 4: Resource Tag-Based Access
TAG_BASED_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:StartInstances",
                "ec2:StopInstances",
                "ec2:TerminateInstances"
            ],
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                    "ec2:ResourceTag/Owner": "${aws:username}"
                }
            }
        }
    ]
}

# Example 5: Least Privilege - Specific Resource Access
LEAST_PRIVILEGE_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:Query"
            ],
            "Resource": "arn:aws:dynamodb:us-east-1:123456789012:table/Users"
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:PutItem"
            ],
            "Resource": "arn:aws:dynamodb:us-east-1:123456789012:table/Users",
            "Condition": {
                "StringEquals": {
                    "dynamodb:LeadingKeys": "${aws:username}"
                }
            }
        }
    ]
}

# Example 6: Cross-Service Access (Lambda to S3 and DynamoDB)
LAMBDA_CROSS_SERVICE_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": "arn:aws:s3:::my-lambda-bucket/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:PutItem",
                "dynamodb:GetItem",
                "dynamodb:UpdateItem"
            ],
            "Resource": "arn:aws:dynamodb:*:*:table/MyTable"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }
    ]
}

# Example 7: Deny Policy (Explicit Deny)
EXPLICIT_DENY_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "s3:*",
            "Resource": "*"
        },
        {
            "Effect": "Deny",
            "Action": "s3:DeleteBucket",
            "Resource": "*"
        }
    ]
}

# Example 8: Permissions Boundary (Limits Maximum Permissions)
PERMISSIONS_BOUNDARY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:*",
                "dynamodb:*"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Deny",
            "Action": [
                "iam:*",
                "ec2:DeleteVpc",
                "rds:DeleteDBInstance"
            ],
            "Resource": "*"
        }
    ]
}

# Example 9: Service Control Policy (SCP) Pattern
SCP_PATTERN = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Deny",
            "Action": [
                "ec2:RunInstances"
            ],
            "Resource": "*",
            "Condition": {
                "StringNotEquals": {
                    "ec2:InstanceType": [
                        "t2.micro",
                        "t2.small"
                    ]
                }
            }
        }
    ]
}

# Example 10: Self-Management Policy (Users can manage their own credentials)
SELF_MANAGEMENT_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "iam:ChangePassword",
                "iam:GetUser",
                "iam:CreateAccessKey",
                "iam:DeleteAccessKey",
                "iam:ListAccessKeys",
                "iam:UpdateAccessKey",
                "iam:ListAttachedUserPolicies",
                "iam:ListUserPolicies",
                "iam:GetUserPolicy"
            ],
            "Resource": "arn:aws:iam::*:user/${aws:username}"
        }
    ]
}


def print_policy(name, policy):
    """Pretty print a policy"""
    print(f"\n{'='*60}")
    print(f"Policy: {name}")
    print(f"{'='*60}")
    print(json.dumps(policy, indent=2))


if __name__ == "__main__":
    print("=" * 60)
    print("AWS IAM Policy Examples")
    print("=" * 60)
    
    policies = {
        "S3 Read-Only Access": S3_READ_ONLY_POLICY,
        "S3 IP Restricted": S3_IP_RESTRICTED_POLICY,
        "MFA Required": MFA_REQUIRED_POLICY,
        "Tag-Based Access": TAG_BASED_POLICY,
        "Least Privilege": LEAST_PRIVILEGE_POLICY,
        "Lambda Cross-Service": LAMBDA_CROSS_SERVICE_POLICY,
        "Explicit Deny": EXPLICIT_DENY_POLICY,
        "Permissions Boundary": PERMISSIONS_BOUNDARY,
        "SCP Pattern": SCP_PATTERN,
        "Self-Management": SELF_MANAGEMENT_POLICY
    }
    
    for name, policy in policies.items():
        print_policy(name, policy)
    
    print("\n" + "=" * 60)
    print("These are example policies for reference.")
    print("Modify resource ARNs and conditions as needed.")
    print("=" * 60)

