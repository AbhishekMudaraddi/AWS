#!/bin/bash
# AWS CLI IAM Examples
# Demonstrates common IAM operations using AWS CLI

echo "=========================================="
echo "AWS CLI IAM Examples"
echo "=========================================="

# Example 1: Create an IAM user
echo ""
echo "1. Creating IAM User"
echo "----------------------------------------"
aws iam create-user --user-name demo-user
aws iam create-login-profile --user-name demo-user --password 'TempPassword123!' --password-reset-required

# Example 2: Create and attach a policy
echo ""
echo "2. Creating Custom Policy"
echo "----------------------------------------"
cat > /tmp/s3-read-policy.json <<EOF
{
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
EOF

aws iam create-policy \
    --policy-name S3ReadOnlyPolicy \
    --policy-document file:///tmp/s3-read-policy.json

# Example 3: Attach managed policy to user
echo ""
echo "3. Attaching Managed Policy"
echo "----------------------------------------"
aws iam attach-user-policy \
    --user-name demo-user \
    --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

# Example 4: Create IAM group
echo ""
echo "4. Creating IAM Group"
echo "----------------------------------------"
aws iam create-group --group-name developers

# Example 5: Add user to group
echo ""
echo "5. Adding User to Group"
echo "----------------------------------------"
aws iam add-user-to-group \
    --group-name developers \
    --user-name demo-user

# Example 6: Attach policy to group
echo ""
echo "6. Attaching Policy to Group"
echo "----------------------------------------"
aws iam attach-group-policy \
    --group-name developers \
    --policy-arn arn:aws:iam::aws:policy/PowerUserAccess

# Example 7: Create IAM role for EC2
echo ""
echo "7. Creating IAM Role for EC2"
echo "----------------------------------------"
cat > /tmp/ec2-trust-policy.json <<EOF
{
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
EOF

aws iam create-role \
    --role-name EC2-S3-Access-Role \
    --assume-role-policy-document file:///tmp/ec2-trust-policy.json

aws iam attach-role-policy \
    --role-name EC2-S3-Access-Role \
    --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

# Example 8: Create instance profile
echo ""
echo "8. Creating Instance Profile"
echo "----------------------------------------"
aws iam create-instance-profile --instance-profile-name EC2-S3-Profile
aws iam add-role-to-instance-profile \
    --instance-profile-name EC2-S3-Profile \
    --role-name EC2-S3-Access-Role

# Example 9: List all users
echo ""
echo "9. Listing All IAM Users"
echo "----------------------------------------"
aws iam list-users --output table

# Example 10: List policies attached to user
echo ""
echo "10. Listing User Policies"
echo "----------------------------------------"
aws iam list-attached-user-policies --user-name demo-user
aws iam list-user-policies --user-name demo-user

# Example 11: Get user details
echo ""
echo "11. Getting User Details"
echo "----------------------------------------"
aws iam get-user --user-name demo-user

# Example 12: Create access keys
echo ""
echo "12. Creating Access Keys"
echo "----------------------------------------"
aws iam create-access-key --user-name demo-user

# Example 13: Enable MFA for user
echo ""
echo "13. Creating Virtual MFA Device"
echo "----------------------------------------"
aws iam create-virtual-mfa-device \
    --virtual-mfa-device-name demo-user-mfa \
    --outfile QRCode.png \
    --bootstrap-method QRCodePNG

# Example 14: List all roles
echo ""
echo "14. Listing All IAM Roles"
echo "----------------------------------------"
aws iam list-roles --output table

# Example 15: Get role details
echo ""
echo "15. Getting Role Details"
echo "----------------------------------------"
aws iam get-role --role-name EC2-S3-Access-Role

# Example 16: Assume role (using STS)
echo ""
echo "16. Assuming Role"
echo "----------------------------------------"
ROLE_ARN=$(aws iam get-role --role-name EC2-S3-Access-Role --query 'Role.Arn' --output text)
aws sts assume-role \
    --role-arn "$ROLE_ARN" \
    --role-session-name "demo-session"

# Cleanup (commented out - uncomment to clean up resources)
# echo ""
# echo "Cleaning up resources..."
# aws iam remove-user-from-group --group-name developers --user-name demo-user
# aws iam detach-user-policy --user-name demo-user --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
# aws iam delete-user --user-name demo-user
# aws iam delete-group --group-name developers
# aws iam delete-role --role-name EC2-S3-Access-Role
# aws iam delete-instance-profile --instance-profile-name EC2-S3-Profile

echo ""
echo "=========================================="
echo "Examples completed!"
echo "=========================================="
echo ""
echo "Note: Review and modify these commands before running in production."
echo "Some commands may require specific permissions or account configurations."

