# Smart Budget Planner - AWS Cloud Application

A cloud-native personal finance management application built with Flask, AWS services, Docker, and CI/CD pipeline. Track expenses, set budgets, upload receipts, and receive notifications via Email.

## Features

- **User Authentication**: Secure registration and login with DynamoDB
- **Expense Tracking**: Record expenses with receipt uploads to S3
- **Budget Management**: Set budgets and track spending by category
- **Receipt Management**: Upload and view receipts stored in S3
- **Notifications**: Email alerts via SNS when budgets are exceeded
- **Report Generation**: Generate monthly/yearly expense reports via Lambda
- **Cloud Deployment**: Deployed on Elastic Beanstalk with Docker

## AWS Services Used

1. **DynamoDB**: Primary database (Users, Expenses, Budgets, Notifications tables)
2. **S3**: Receipt and report storage
3. **Lambda**: Budget alerts, report generation, notification processing
4. **SQS**: Notification queue for asynchronous email delivery
5. **SNS**: Budget alert notifications (Email)
6. **Elastic Beanstalk**: Application hosting
7. **ECR**: Docker image registry
8. **CloudWatch**: Logging and monitoring
9. **IAM**: Service roles and permissions

## Prerequisites

- Python 3.9+
- AWS Account with appropriate permissions
- AWS CLI configured with credentials
- Docker installed
- Jenkins installed (for CI/CD)

## Installation

### 1. Clone and Setup

```bash
git clone <repository-url>
cd CloudPlatformProj
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure AWS Credentials

Ensure AWS credentials are configured:
```bash
aws configure
```

Or set environment variables:
```bash
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_REGION=us-east-1
```

### 3. Create AWS Resources

Run the setup script to create all AWS resources:
```bash
python scripts/setup_aws_resources.py
```

This will create:
- DynamoDB tables (Users, Expenses, Budgets, Notifications)
- S3 bucket for receipts
- SQS queues
- SNS topic
- IAM roles for Lambda

### 4. Deploy Lambda Functions

Deploy Lambda functions using the provided script:
```bash
python3 scripts/deploy_lambda_functions.py
```

This will deploy:
- Budget Alert Lambda (scheduled daily via CloudWatch Events)
- Report Generator Lambda (on-demand invocation)
- Notification Processor Lambda (triggered by SQS queue)

### 5. Run Locally

```bash
python app.py
```

Or with Docker:
```bash
docker-compose up
```

## Docker Deployment

### Build Docker Image

```bash
docker build -t smart-budget-planner .
```

### Run Container

```bash
docker run -p 5000:5000 \
  -e AWS_ACCESS_KEY_ID=your-key \
  -e AWS_SECRET_ACCESS_KEY=your-secret \
  -e AWS_REGION=us-east-1 \
  smart-budget-planner
```

### Push to ECR

```bash
python scripts/setup_ecr.py
./scripts/build_and_push.sh
```

## Jenkins CI/CD Setup

1. Install Jenkins plugins:
   - Docker Pipeline
   - AWS Steps
   - Pipeline

2. Configure AWS credentials in Jenkins:
   - Go to Jenkins > Credentials > System > Global credentials
   - Add AWS credentials with ID: `aws-credentials`

3. Create Jenkins pipeline:
   - New Item > Pipeline
   - Point to Jenkinsfile in repository
   - Run pipeline

## Elastic Beanstalk Deployment

### Create EB Application

```bash
eb init -p python-3.9 smart-budget-planner --region us-east-1
eb create smart-budget-planner-env
```

### Configure Environment Variables

Set in EB console or via CLI:
- AWS_REGION
- SECRET_KEY
- S3_BUCKET_NAME
- AWS credentials (via IAM instance profile)

### Deploy

```bash
eb deploy
```

Or use Jenkins pipeline for automated deployment.

## Project Structure

```
CloudPlatformProj/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker container definition
├── docker-compose.yml              # Local development
├── aws_config/                     # AWS service SDK clients
│   ├── __init__.py
│   ├── config.py                   # AWS configuration
│   ├── setup_dynamodb.py           # DynamoDB SDK wrapper
│   ├── setup_s3.py                 # S3 SDK wrapper
│   ├── setup_sqs.py                # SQS SDK wrapper
│   ├── setup_sns.py                # SNS SDK wrapper
│   ├── setup_lambda.py             # Lambda SDK wrapper
│   └── resource_manager.py         # AWS resource creation
├── lib/                            # Custom libraries
│   ├── __init__.py
│   ├── expense_processor.py        # Expense processing logic
│   ├── budget_calculator.py        # Budget calculations
│   ├── notification_manager.py     # Notification handling
│   └── receipt_handler.py          # Receipt operations
├── lambda_functions/               # Lambda function code
│   ├── budget_alert/               # Scheduled budget alerts
│   ├── notification_processor/     # SQS-triggered email processing
│   └── report_generator/            # On-demand PDF report generation
├── scripts/                        # Setup and deployment scripts
│   ├── setup_aws_resources.py      # Create AWS resources
│   ├── setup_ecr.py                # Create ECR repository
│   ├── deploy_lambda_functions.py  # Deploy Lambda functions
│   └── build_and_push.sh           # Docker build/push script
├── templates/                      # HTML templates
└── static/                         # CSS and JavaScript
```

## Custom Libraries

The application uses 4 custom libraries:

1. **ExpenseProcessor**: Validates and processes expenses, saves to DynamoDB
2. **BudgetCalculator**: Calculates totals, remaining amounts, percentages, checks thresholds
3. **NotificationManager**: Handles email notifications via SQS queuing and SNS delivery
4. **ReceiptHandler**: Manages receipt uploads to S3, generates presigned URLs

### Published Library

The custom libraries have been packaged and published to Test PyPI:

- **Package name**: `smart-budget-lib`
- **Installation**: 
  ```bash
  pip install --index-url https://test.pypi.org/simple/ smart-budget-lib
  ```
- **Usage**:
  ```python
  from smart_budget_lib.expense_processor import ExpenseProcessor
  from smart_budget_lib.budget_calculator import BudgetCalculator
  from smart_budget_lib.notification_manager import NotificationManager
  from smart_budget_lib.receipt_handler import ReceiptHandler
  ```

Note: The published library requires `aws_config` dependencies to be available in your project.

## API Endpoints

### Authentication
- `POST /register` - Register new user
- `POST /login` - Login user
- `GET /logout` - Logout user

### Expenses
- `GET /api/expenses` - Get user expenses
- `POST /api/expenses` - Add expense
- `DELETE /api/expenses/<id>` - Delete expense

### Budgets
- `GET /api/budget` - Get user budgets
- `POST /api/budget` - Set/update budget
- `DELETE /api/budget/<id>` - Delete budget

### Receipts
- `POST /api/receipts/upload` - Upload receipt
- `GET /api/receipts/<expense_id>` - Get receipt URL
- `POST /api/receipts/presigned-url` - Get presigned upload URL

### Notifications
- `POST /api/notifications/subscribe` - Subscribe to notifications
- `GET /api/notifications` - Get user notifications

### Reports
- `POST /api/reports/generate` - Generate expense report

### Summary
- `GET /api/summary` - Get budget summary

## Testing

Run tests:
```bash
pytest tests/
```

Tests use moto for AWS service mocking.

## Monitoring

- CloudWatch Logs: Application logs automatically sent to CloudWatch
- CloudWatch Metrics: Monitor Lambda invocations, SQS queue depth
- Health Check: `/health` endpoint for EB health checks

## Security

- Passwords hashed with Werkzeug
- User sessions managed securely
- IAM roles for service access
- S3 presigned URLs for secure receipt access
- Environment variables for sensitive data

## Troubleshooting

### AWS Credentials
Ensure AWS credentials are configured:
```bash
aws sts get-caller-identity
```

### DynamoDB Tables
Check if tables exist:
```bash
aws dynamodb list-tables
```

### S3 Bucket
Verify bucket exists:
```bash
aws s3 ls
```

### Lambda Functions
Check Lambda function status:
```bash
aws lambda list-functions
```

## License

MIT License
