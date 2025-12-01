# AWS IAM - Identity and Access Management

## What is IAM?

AWS IAM (Identity and Access Management) is a service that controls access to AWS resources by managing users, roles, and permissions.

## Why IAM in This Project?

1. **Security**: Controls who can access AWS resources
2. **Roles**: Allows services to access other services securely
3. **Permissions**: Grants minimum required permissions (principle of least privilege)
4. **Best Practice**: Essential for secure cloud applications

## How IAM is Used in This Project

IAM manages access for:
- **IAM User**: Developer/user deploying resources (`smartbudgetplanner`, `PassManagerIAM`)
- **Lambda Execution Role**: Allows Lambda functions to access DynamoDB, S3, SNS
- **EB Instance Role**: Allows Elastic Beanstalk instances to access AWS services
- **EC2 Instance Role**: Allows EC2 instances (EB) to pull images from ECR

## Implementation Files

### Primary Files:
1. **`scripts/create_lambda_role.py`** - Creates IAM role for Lambda functions
2. **`scripts/add_eb_dynamodb_permissions.py`** - Adds DynamoDB permissions to EB role
3. **`scripts/add_eb_sns_permissions.py`** - Adds SNS permissions to EB role
4. **`aws_config/config.py`** - Uses AWS profile for credentials

### Usage:
- **Local Development**: Uses AWS profile (`smart-budget-planner`)
- **Elastic Beanstalk**: Uses instance role (`aws-elasticbeanstalk-ec2-role`)
- **Lambda**: Uses execution role (`smart-budget-lambda-role`)

## Code Structure

### 1. AWS Profile Configuration (`aws_config/config.py`)

```python
def get_boto3_session():
    profile = os.getenv('AWS_PROFILE', 'smart-budget-planner')
    try:
        return boto3.Session(profile_name=profile)
    except ProfileNotFound:
        return boto3.Session()  # Uses default credentials (IAM role on EB)
```

**What it does**:
- **Local**: Uses named AWS profile (`smart-budget-planner`)
- **EB**: Falls back to default credentials (instance role)

**Why**: Allows same code to work locally (with profile) and on EB (with role)

### 2. Lambda Execution Role (`scripts/create_lambda_role.py`)

**Purpose**: Creates IAM role that Lambda functions use to access AWS services.

**Permissions Granted**:
- **DynamoDB**: Read/write access to all tables
- **S3**: Read/write access to bucket
- **SNS**: Publish messages to topic
- **CloudWatch Logs**: Write logs

**Role Name**: `smart-budget-lambda-role`

**Used by**: All Lambda functions (expense categorizer, budget alert, report generator)

### 3. EB Instance Role

**Purpose**: Allows Elastic Beanstalk instances to access AWS services.

**Default Role**: `aws-elasticbeanstalk-ec2-role`

**Additional Permissions Added**:
- **DynamoDB**: Read/write access (via `add_eb_dynamodb_permissions.py`)
- **S3**: Read/write access
- **SNS**: Publish/subscribe (via `add_eb_sns_permissions.py`)
- **ECR**: Pull images (for Docker deployment)

## IAM Roles and Permissions

### Lambda Execution Role (`smart-budget-lambda-role`)

**Permissions**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/smart-budget-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::smart-budget-receipts/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sns:Publish"
      ],
      "Resource": "arn:aws:sns:*:*:budget-alerts-topic"
    }
  ]
}
```

**Used by**: All Lambda functions

### EB Instance Role (`aws-elasticbeanstalk-ec2-role`)

**Permissions**:
- DynamoDB access (added via script)
- S3 access (default)
- SNS access (added via script)
- ECR access (for pulling Docker images)

**Used by**: Flask application running on Elastic Beanstalk

## How to Explain in Class

### When Asked: "Why use IAM roles instead of access keys?"

**Answer**:
- **Security**: Roles provide temporary credentials (rotated automatically)
- **No Hardcoding**: Don't need to store access keys in code
- **Principle of Least Privilege**: Roles have only necessary permissions
- **Best Practice**: AWS recommended approach for service-to-service access

### When Asked: "How does Lambda access DynamoDB?"

**Answer**:
1. **Lambda Execution Role**: Lambda function assumes `smart-budget-lambda-role`
2. **Temporary Credentials**: AWS provides temporary credentials to Lambda
3. **Permissions**: Role has DynamoDB read/write permissions
4. **Access**: Lambda uses boto3 with default credentials (from role)
5. **No Keys Needed**: No access keys required in code

**Code**:
```python
# In Lambda function
import boto3
dynamodb = boto3.resource('dynamodb')  # Uses execution role automatically
table = dynamodb.Table('smart-budget-expenses')
```

### When Asked: "Show me how permissions are granted"

**Answer**:
- **Lambda Role**: Created by `scripts/create_lambda_role.py`
- **Policy Attached**: Policy with DynamoDB, S3, SNS permissions
- **Role Assigned**: Lambda function configured to use this role
- **Automatic**: Lambda automatically uses role credentials

**Code Flow**:
```
scripts/create_lambda_role.py
  → Creates IAM role
  → Attaches policy with permissions
  → Lambda function uses role
    → Can access DynamoDB, S3, SNS
```

### When Asked: "How does EB access AWS services?"

**Answer**:
1. **Instance Role**: EB instances use `aws-elasticbeanstalk-ec2-role`
2. **Default Permissions**: Basic permissions for EB operations
3. **Additional Permissions**: Scripts add DynamoDB, SNS permissions
4. **Application Code**: Flask app uses boto3 with default credentials (from role)
5. **No Keys**: No access keys needed in application code

**Code**:
```python
# In app.py
from aws_config.config import get_boto3_session
session = get_boto3_session()  # Uses instance role on EB
dynamodb = session.resource('dynamodb')
```

## Key Concepts to Remember

1. **IAM User**: Human or application identity (for programmatic access)
2. **IAM Role**: Assumed by AWS services (Lambda, EC2, etc.)
3. **Policy**: Document defining permissions
4. **Principle of Least Privilege**: Grant minimum required permissions
5. **Temporary Credentials**: Roles provide temporary, rotating credentials
6. **Trust Policy**: Defines who can assume the role

## Common Questions & Answers

**Q: Why not use access keys in environment variables?**
A: Access keys are permanent and can be compromised. Roles provide temporary credentials that rotate automatically.

**Q: How do you grant permissions to Lambda?**
A: Create IAM role with required permissions, assign role to Lambda function. Lambda automatically uses role credentials.

**Q: What happens if Lambda doesn't have permission?**
A: AWS returns `AccessDeniedException`. Need to add permission to Lambda execution role.

**Q: Can you see who accessed what?**
A: Yes, CloudTrail logs all API calls including IAM actions. Can audit access.

**Q: How do you test permissions locally?**
A: Use AWS profile with same permissions as role. Code uses profile locally, role on AWS.

**Q: What is the difference between user and role?**
A: User is permanent identity (for humans/apps). Role is temporary identity assumed by AWS services.

