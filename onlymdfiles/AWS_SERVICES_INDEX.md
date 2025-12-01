# AWS Services Used in Smart Budget Planner - Index

This document provides an overview of all AWS services used in the project and links to detailed documentation for each service.

## Services Overview

This project uses **9 AWS services** to build a cloud-native budget planning application:

1. **[DynamoDB](AWS_DYNAMODB.md)** - Database for storing users, expenses, budgets, and notifications
2. **[S3](AWS_S3.md)** - Storage for receipts and PDF reports
3. **[Lambda](AWS_LAMBDA.md)** - Serverless functions for expense categorization, budget alerts, and report generation
4. **[SQS](AWS_SQS.md)** - Message queue for asynchronous expense processing
5. **[SNS](AWS_SNS.md)** - Notification service for email alerts
6. **[Elastic Beanstalk](AWS_ELASTIC_BEANSTALK.md)** - Application hosting platform
7. **[ECR](AWS_ECR.md)** - Docker container registry
8. **[CloudWatch](AWS_CLOUDWATCH.md)** - Logging and monitoring
9. **[IAM](AWS_IAM.md)** - Access control and permissions

## Quick Reference

### Data Storage
- **DynamoDB**: All application data (users, expenses, budgets, notifications)
- **S3**: Files (receipts, PDF reports)

### Compute & Processing
- **Lambda**: Serverless functions (categorization, alerts, reports)
- **Elastic Beanstalk**: Flask application hosting

### Messaging & Notifications
- **SQS**: Asynchronous expense processing queue
- **SNS**: Email notifications for budget alerts

### Infrastructure
- **ECR**: Docker image storage
- **CloudWatch**: Logging and scheduled events
- **IAM**: Security and access control

## Service Interaction Flow

```
User → Elastic Beanstalk (Flask App)
    ↓
DynamoDB (Store Data)
    ↓
S3 (Store Files)
    ↓
SQS (Queue Expenses)
    ↓
Lambda (Process Expenses)
    ↓
SNS (Send Notifications)
    ↓
CloudWatch (Monitor & Schedule)
```

## Detailed Documentation

Click on any service name above to view detailed documentation including:
- What the service is
- Why it's used in this project
- How it's implemented
- Code examples and file locations
- How to explain it in class
- Common questions and answers

## Study Guide for Class Presentation

### For Each Service, Be Ready to Explain:

1. **What it is**: Brief definition
2. **Why we use it**: Specific use case in project
3. **How it works**: Implementation details
4. **Code location**: Which files contain the code
5. **Integration**: How it connects with other services

### Key Points to Remember:

- **DynamoDB**: NoSQL database, stores all application data, uses Global Secondary Indexes for queries
- **S3**: Object storage, stores receipts and reports, uses presigned URLs for secure access
- **Lambda**: Serverless functions, triggered by SQS and CloudWatch Events, generates reports
- **SQS**: Message queue, decouples expense categorization from main app
- **SNS**: Email notifications, requires subscription confirmation
- **Elastic Beanstalk**: Hosts Flask app, auto-scales, manages infrastructure
- **ECR**: Stores Docker images, EB pulls images for deployment
- **CloudWatch**: Logs and monitoring, triggers scheduled Lambda functions
- **IAM**: Security, roles for Lambda and EB, no hardcoded credentials

## Common Questions You Might Get

1. **"Why use AWS instead of traditional servers?"**
   - Scalability, reliability, cost-effectiveness, managed services

2. **"How do services communicate?"**
   - Via AWS SDK (boto3), IAM roles for authentication, APIs for integration

3. **"What happens if a service fails?"**
   - AWS provides high availability (99.99%+), automatic failover, retry mechanisms

4. **"How do you ensure security?"**
   - IAM roles, private S3 buckets, encrypted data, VPC (if needed)

5. **"How much does it cost?"**
   - Pay-per-use model, very cost-effective for this scale, likely under $50/month

## Next Steps

1. Read each service documentation file
2. Review the code files mentioned in each document
3. Practice explaining each service
4. Prepare answers for common questions
5. Understand how services integrate together

---

**Note**: Each service documentation file contains detailed explanations, code examples, and answers to common questions. Use them as your reference guide for class presentations and demonstrations.

