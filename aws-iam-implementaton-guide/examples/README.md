# 💻 AWS IAM Practical Examples

This directory contains practical code examples demonstrating AWS IAM operations using Python (boto3) and AWS CLI.

## 📁 Files Overview

### Python Scripts

#### `iam_user_management.py`
Demonstrates IAM user management operations:
- Creating IAM users
- Creating and managing access keys
- Attaching policies to users
- Creating and managing IAM groups
- Adding users to groups
- Listing users and their policies

**Usage:**
```bash
python iam_user_management.py
```

#### `iam_role_management.py`
Demonstrates IAM role management:
- Creating roles for EC2, Lambda, and cross-account access
- Creating instance profiles
- Attaching policies to roles
- Assuming roles using AWS STS
- Trust policy examples

**Usage:**
```bash
python iam_role_management.py
```

#### `iam_policy_examples.py`
Collection of IAM policy examples:
- S3 read-only access
- IP-restricted access
- MFA-required policies
- Tag-based access control
- Least privilege patterns
- Permissions boundaries
- Service Control Policies (SCPs)
- Self-management policies

**Usage:**
```bash
python iam_policy_examples.py
```

### Shell Scripts

#### `aws_cli_examples.sh`
Comprehensive AWS CLI examples for IAM operations:
- User creation and management
- Policy creation and attachment
- Group management
- Role creation for EC2
- Instance profile setup
- MFA device creation
- Role assumption
- Listing and querying IAM resources

**Usage:**
```bash
chmod +x aws_cli_examples.sh
./aws_cli_examples.sh
```

## 🚀 Prerequisites

### For Python Scripts:
1. Python 3.7 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### For AWS CLI Scripts:
1. AWS CLI installed and configured
2. Appropriate IAM permissions

## ⚙️ Configuration

Before running any examples, ensure you have:

1. **AWS Credentials Configured:**
   ```bash
   aws configure
   ```
   Or set environment variables:
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_DEFAULT_REGION=us-east-1
   ```

2. **Required IAM Permissions:**
   - `iam:CreateUser`
   - `iam:CreateRole`
   - `iam:CreatePolicy`
   - `iam:AttachUserPolicy`
   - `iam:AttachRolePolicy`
   - `iam:ListUsers`
   - `iam:ListRoles`
   - And other IAM permissions as needed

## ⚠️ Important Notes

1. **These are demonstration scripts** - Review and modify before using in production
2. **Follow least privilege** - Only grant necessary permissions
3. **Test in a development account first** - Never test IAM changes in production
4. **Clean up resources** - Remove test users, roles, and policies after testing
5. **Never commit credentials** - Keep AWS credentials secure and out of version control

## 🔒 Security Best Practices

- Always use IAM roles instead of access keys when possible
- Enable MFA for all IAM users
- Rotate access keys regularly
- Use least privilege principle
- Review and audit IAM policies regularly
- Use CloudTrail to monitor IAM API calls

## 📚 Additional Resources

- [AWS IAM Documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html)
- [boto3 IAM Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html)
- [AWS CLI IAM Commands](https://docs.aws.amazon.com/cli/latest/reference/iam/)
- [IAM Policy Simulator](https://policysim.aws.amazon.com/)

## 🐛 Troubleshooting

### Common Issues:

1. **Access Denied Errors:**
   - Verify your AWS credentials have sufficient permissions
   - Check if your account has IAM service enabled

2. **EntityAlreadyExists Errors:**
   - The resource already exists - modify the script to use different names or handle existing resources

3. **Invalid Policy Document:**
   - Validate your JSON policy documents using the IAM Policy Simulator
   - Ensure proper JSON formatting

4. **Region Issues:**
   - IAM is a global service, but some operations may require region configuration
   - Set AWS_DEFAULT_REGION environment variable

## 📝 Example Workflow

1. **Review the scripts** to understand what they do
2. **Modify resource names** to avoid conflicts
3. **Run in a test/development account** first
4. **Monitor CloudTrail** for API calls
5. **Clean up resources** after testing

---

**Remember:** Security is paramount. Always review and test IAM changes carefully before applying them to production environments.

