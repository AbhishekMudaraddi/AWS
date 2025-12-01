# AWS Service Integration and Data Flow Documentation

This document explains how each AWS service is integrated into the Smart Budget Planner application and the complete data flow for each service.

---

## 1. Amazon DynamoDB Integration

### How DynamoDB is Integrated

DynamoDB is the primary NoSQL database used for storing all application data. It is integrated through the `DynamoDBClient` class in `aws_config/setup_dynamodb.py`.

**Integration Method:**
- Uses boto3 DynamoDB resource API
- Initialized with AWS session and region configuration
- Four tables are used: `users`, `expenses`, `budgets`, and `notifications`
- Global Secondary Indexes (GSIs) are used for efficient queries

**Tables and Their Structure:**

1. **Users Table**
   - Primary Key: `user_id` (String)
   - GSI: `username-index` (for login lookups)
   - GSI: `email-index` (for email lookups)
   - Attributes: username, email, password_hash, created_at, phone_number

2. **Expenses Table**
   - Primary Key: `expense_id` (String)
   - GSI: `user_id-index` (for querying user expenses)
   - Attributes: user_id, amount, category, description, date, receipt_url, status

3. **Budgets Table**
   - Primary Key: `budget_id` (String)
   - GSI: `user_id-index` (for querying user budgets)
   - Attributes: user_id, category, amount, alert_threshold, created_at

4. **Notifications Table**
   - Primary Key: `notification_id` (String)
   - GSI: `user_id-index` (for querying user notifications)
   - Attributes: user_id, type, message, status, delivery_method, created_at, updated_at

### Data Flow for DynamoDB

#### User Registration Flow:
```
1. User submits registration form (username, email, password)
2. Flask route `/register` receives POST request
3. Password is hashed using Werkzeug
4. DynamoDBClient.create_user() is called
5. UUID is generated for user_id
6. User record is inserted into users table via put_item()
7. User_id is returned and stored in session
```

#### User Login Flow:
```
1. User submits login form (username, password)
2. Flask route `/login` receives POST request
3. DynamoDBClient.get_user_by_username() queries username-index GSI
4. User record is retrieved from DynamoDB
5. Password hash is verified using Werkzeug
6. If valid, user_id is stored in Flask session
```

#### Expense Addition Flow:
```
1. User submits expense form (amount, category, description, receipt_url)
2. Flask route `/api/expenses` (POST) receives request
3. ExpenseProcessor.add_expense() is called
4. ExpenseProcessor validates data (amount > 0, category required)
5. DynamoDBClient.add_expense() is called
6. UUID is generated for expense_id
7. Expense record is inserted into expenses table via put_item()
8. Expense data is returned to Flask route
9. Notification checks are triggered (budget exceeded, large expense)
```

#### Budget Query Flow:
```
1. User requests budget summary
2. Flask route `/api/summary` receives GET request
3. BudgetCalculator.get_budget_summary() is called
4. DynamoDBClient.get_user_budgets() queries budgets table using user_id-index GSI
5. DynamoDBClient.get_user_expenses() queries expenses table using user_id-index GSI
6. Budget calculations are performed (totals, remaining, percentages)
7. Summary data is returned to user
```

#### Notification History Flow:
```
1. User requests notification history
2. Flask route `/api/notifications` receives GET request
3. NotificationManager.get_user_notifications() is called
4. DynamoDBClient.get_user_notifications() queries notifications table using user_id-index GSI
5. Notifications are sorted by created_at (descending)
6. Notification list is returned to user
```

---

## 2. Amazon S3 Integration

### How S3 is Integrated

S3 is used for storing receipt images and generated PDF reports. It is integrated through the `S3Client` class in `aws_config/setup_s3.py`.

**Integration Method:**
- Uses boto3 S3 client API
- Single bucket: `smart-budget-receipts`
- Presigned URLs are generated for secure, time-limited access
- Files are organized in folder structure: `receipts/{user_id}/{expense_id}.{ext}` and `reports/{user_id}/{filename}`

### Data Flow for S3

#### Receipt Upload Flow:
```
1. User uploads receipt file via `/api/receipts/upload` endpoint
2. Flask receives multipart/form-data with file
3. ReceiptHandler.upload_receipt() is called
4. ReceiptHandler validates file type (jpg, jpeg, png, pdf, gif)
5. ReceiptHandler validates file size (max 10MB)
6. S3Client.upload_receipt() is called
7. S3 key is generated: receipts/{user_id}/{expense_id}.{extension}
8. File content is uploaded to S3 using put_object()
9. S3 key is returned and stored in expense record in DynamoDB
```

#### Receipt Retrieval Flow:
```
1. User requests receipt view via `/api/receipts/<expense_id>` endpoint
2. Flask route retrieves expense from DynamoDB
3. ReceiptHandler.get_receipt_url() is called
4. S3Client.get_receipt_url() generates presigned URL
5. Presigned URL is generated using generate_presigned_url() with 1-hour expiration
6. URL is returned to user for viewing receipt in browser
```

#### Presigned URL Generation Flow:
```
1. User requests presigned URL for direct upload via `/api/receipts/presigned-url`
2. ReceiptHandler.generate_presigned_url() is called
3. S3 key is generated: receipts/{user_id}/{uuid}.{extension}
4. S3Client.generate_presigned_url() creates PUT presigned URL
5. Presigned URL (valid for 1 hour) is returned to frontend
6. Frontend uploads file directly to S3 using presigned URL
7. S3 key is returned to backend and stored in expense record
```

#### Report Storage Flow:
```
1. User requests report generation via `/api/reports/generate`
2. Flask route invokes Lambda function (report_generator)
3. Lambda function generates PDF report using ReportLab
4. PDF content is stored in memory buffer
5. Lambda function uploads PDF to S3 using put_object()
6. S3 key: reports/{user_id}/{report_type}_report_{timestamp}.pdf
7. Lambda generates presigned URL (valid for 24 hours)
8. Presigned URL is returned to Flask route
9. URL is sent to user for downloading report
```

---

## 3. AWS Lambda Integration

### How Lambda is Integrated

Lambda functions are used for asynchronous processing tasks. Three Lambda functions are deployed:
1. **budget_alert**: Scheduled daily budget checks
2. **notification_processor**: Processes SQS messages for email delivery
3. **report_generator**: Generates PDF reports on-demand

**Integration Method:**
- Lambda functions are invoked via boto3 Lambda client
- Functions are triggered by CloudWatch Events (scheduled), SQS (event-driven), or direct invocation
- IAM roles provide permissions for Lambda to access DynamoDB, S3, SNS

### Data Flow for Lambda Functions

#### Budget Alert Lambda Flow:
```
1. CloudWatch Events triggers budget_alert Lambda daily (scheduled rule)
2. Lambda function receives event from CloudWatch
3. Lambda queries DynamoDB budgets table (scan operation)
4. For each budget:
   a. Lambda queries expenses table using user_id-index GSI filtered by category
   b. Calculates total spent for that category
   c. Calculates percentage: (spent / budget_amount) * 100
   d. If percentage >= alert_threshold:
      - Retrieves user record from users table
      - Gets user email
      - Checks if email is subscribed to SNS topic (check_email_subscription)
      - Gets user's subscription ARN (get_user_subscription_arn)
      - Configures SNS subscription filter for user_email (configure_subscription_filter)
      - Publishes message to SNS topic with MessageAttributes (user_email) via send_email_notification
      - Records notification in DynamoDB notifications table (status: sent)
5. Lambda returns summary: alerts_sent count and any errors
```

#### Notification Processor Lambda Flow:
```
1. SQS queue receives notification message (triggered by Flask app)
2. SQS event triggers notification_processor Lambda
3. Lambda receives event with Records array (SQS messages)
4. For each message:
   a. Lambda parses JSON message body (handles both 'body' key and direct record)
   b. Extracts: user_id, user_email, message, subject, notification_type, notification_id
   c. Calls process_notification() function
   d. process_notification() gets SNS topic ARN (get_sns_topic_arn)
   e. Checks if user_email is subscribed and confirmed (check_email_subscription)
   f. Gets user's subscription ARN (get_user_subscription_arn)
   g. Configures subscription filter policy (configure_subscription_filter)
   h. Publishes message to SNS topic with MessageAttributes via send_email_notification
   i. Updates notification status in DynamoDB (queued → sent) via update_notification_status
   j. If failed, updates status to 'failed' with error message
5. Lambda returns summary: processed count, failed count, errors
```

#### Report Generator Lambda Flow:
```
1. User requests report via Flask route `/api/reports/generate`
2. Flask route calls LambdaClient.invoke_report_generator()
3. Lambda function is invoked synchronously (RequestResponse)
4. Lambda receives event payload: user_id, report_type, start_date, end_date, year, month
5. Lambda queries DynamoDB:
   a. Queries expenses table using user_id-index GSI
   b. Queries budgets table using user_id-index GSI
   c. Filters expenses by date range (monthly/weekly/custom)
6. Lambda generates report data:
   - Calculates totals, category breakdowns, statistics
   - Compares expenses vs budgets
   - Generates insights
7. Lambda generates PDF using ReportLab library
8. Lambda uploads PDF to S3: reports/{user_id}/{filename}.pdf
9. Lambda generates presigned URL (24-hour expiration)
10. Lambda returns JSON response: report_url, report_key, file_name
11. Flask route receives response and sends to user
```

---

## 4. Amazon SQS Integration

### How SQS is Integrated

SQS is used for asynchronous notification processing. It decouples the Flask application from email delivery.

**Integration Method:**
- Uses boto3 SQS client API
- Single queue: `notification-queue`
- Messages are sent from Flask app and consumed by Lambda function
- Queue URL is retrieved dynamically using get_queue_url()

### Data Flow for SQS

#### Notification Queuing Flow:
```
1. User action triggers notification (e.g., expense added, budget exceeded)
2. Flask route calls NotificationManager method (e.g., send_budget_exceeded_alert())
3. NotificationManager._send_notification() is called
4. Notification record is created in DynamoDB (status: 'queued')
5. Notification data is prepared:
   {
     'user_id': user_id,
     'user_email': user_email,
     'message': message,
     'subject': subject,
     'notification_type': type,
     'notification_id': notification_id,
     'timestamp': ISO timestamp
   }
6. SQSClient.send_notification_message() is called
7. Message is serialized to JSON string
8. Message is sent to SQS queue using send_message()
9. SQS returns MessageId
10. Flask route continues (non-blocking)
```

#### Notification Processing Flow (SQS → Lambda):
```
1. SQS queue receives notification message
2. SQS triggers notification_processor Lambda function
3. Lambda receives event with Records array
4. For each record:
   a. Lambda extracts message body (JSON string)
   b. Parses JSON to get notification data
   c. Processes notification (sends via SNS)
   d. Updates DynamoDB notification status
   e. Message is automatically deleted from queue after successful processing
5. If processing fails, message remains in queue for retry
6. After max retries, message moves to Dead Letter Queue (if configured)
```

---

## 5. Amazon SNS Integration

### How SNS is Integrated

SNS is used for email notification delivery. It provides pub/sub messaging with email subscriptions.

**Integration Method:**
- Uses boto3 SNS client API
- Single topic: `budget-alerts-topic`
- Email subscriptions are managed per user
- Subscription filter policies ensure user-specific delivery
- Messages are published with MessageAttributes for filtering

### Data Flow for SNS

#### Email Subscription Flow:
```
1. User subscribes to notifications via `/api/notifications/subscribe`
2. Flask route calls NotificationManager.subscribe_user()
3. SNSClient.subscribe_email() is called
4. SNSClient checks if email already subscribed (list_subscriptions_by_topic)
5. If not subscribed:
   a. SNSClient calls sns.subscribe() with topic ARN, protocol='email', endpoint=email
   b. SNS sends confirmation email to user
   c. Subscription ARN is returned (status: 'PendingConfirmation')
6. If already subscribed:
   a. Existing subscription ARN is retrieved
   b. Filter policy is configured: {'user_email': [email]}
7. User must click confirmation link in email to activate subscription
8. Once confirmed, subscription ARN changes from 'PendingConfirmation' to actual ARN
```

#### Email Notification Publishing Flow:
```
1. Notification Processor Lambda processes SQS message
2. Lambda gets SNS topic ARN
3. Lambda gets user's subscription ARN for their email
4. Lambda configures subscription filter policy:
   {
     'user_email': [user_email]
   }
5. Lambda publishes message to SNS topic:
   - TopicArn: budget-alerts-topic ARN
   - Subject: notification subject
   - Message: notification message
   - MessageAttributes: {'user_email': {'DataType': 'String', 'StringValue': user_email}}
6. SNS evaluates filter policy for each subscription
7. Only subscription matching user_email receives the message
8. SNS delivers email to user's email address
9. Notification status in DynamoDB is updated to 'sent'
```

#### Budget Alert Lambda → SNS Flow:
```
1. Budget Alert Lambda runs daily (CloudWatch Events trigger)
2. Lambda checks all budgets and calculates spending percentages
3. For budgets exceeding threshold:
   a. Lambda gets user email from users table
   b. Lambda checks if email is subscribed (get_user_subscription_arn)
   c. Lambda configures subscription filter for that email
   d. Lambda publishes to SNS topic with user_email MessageAttribute
   e. SNS filter policy ensures only that user's subscription receives email
   f. Email is delivered to user
```

---

## 6. AWS Elastic Beanstalk Integration

### How Elastic Beanstalk is Integrated

Elastic Beanstalk hosts the Flask application and manages the infrastructure automatically.

**Integration Method:**
- Application is containerized using Docker
- Docker image is pushed to ECR
- Elastic Beanstalk pulls image from ECR
- Environment variables are configured for AWS credentials and service names
- Health checks are configured on `/health` endpoint

### Data Flow for Elastic Beanstalk

#### Application Deployment Flow:
```
1. Developer commits code to GitHub
2. GitHub Actions CI/CD pipeline triggers
3. Pipeline builds Docker image
4. Image is tagged and pushed to ECR
5. Pipeline creates new Elastic Beanstalk application version
6. Pipeline updates Elastic Beanstalk environment with new version
7. Elastic Beanstalk:
   a. Pulls Docker image from ECR
   b. Deploys to EC2 instances
   c. Configures load balancer
   d. Runs health checks
   e. Switches traffic to new version (zero-downtime deployment)
8. Application is accessible via Elastic Beanstalk URL
```

#### Request Handling Flow:
```
1. User makes HTTP request to Elastic Beanstalk URL
2. Elastic Beanstalk load balancer receives request
3. Load balancer routes request to healthy EC2 instance
4. EC2 instance runs Flask application in Docker container
5. Flask application processes request:
   a. Routes to appropriate endpoint
   b. Authenticates user (checks session)
   c. Calls custom libraries
   d. Interacts with AWS services (DynamoDB, S3, Lambda, SQS, SNS)
   e. Returns response
6. Response is sent back through load balancer to user
```

#### Health Check Flow:
```
1. Elastic Beanstalk periodically calls `/health` endpoint
2. Flask route returns 200 OK if application is healthy
3. If health check fails, Elastic Beanstalk:
   a. Marks instance as unhealthy
   b. Routes traffic away from unhealthy instance
   c. Launches new instance if needed
   d. Terminates unhealthy instance
```

---

## 7. Amazon ECR Integration

### How ECR is Integrated

ECR stores Docker container images for the application.

**Integration Method:**
- ECR repository is created via setup script
- Docker images are built locally
- Images are pushed to ECR using docker push
- Elastic Beanstalk pulls images from ECR during deployment

### Data Flow for ECR

#### Image Push Flow:
```
1. Developer runs build script or CI/CD pipeline
2. Docker image is built from Dockerfile
3. Image is tagged with ECR repository URL
4. AWS credentials are configured for ECR
5. Docker login to ECR: aws ecr get-login-password | docker login
6. Docker image is pushed to ECR: docker push <ecr-url>/<image>:<tag>
7. Image is stored in ECR repository
8. Multiple tags can be used (latest, commit SHA, version number)
```

#### Image Pull Flow (by Elastic Beanstalk):
```
1. Elastic Beanstalk deployment is triggered
2. Elastic Beanstalk uses IAM role to authenticate with ECR
3. Elastic Beanstalk pulls Docker image from ECR repository
4. Image is cached on EC2 instance
5. Container is started from image
6. Application runs in container
```

---

## 8. Amazon CloudWatch Integration

### How CloudWatch is Integrated

CloudWatch is used for logging, monitoring, and scheduled events.

**Integration Method:**
- CloudWatch Logs: Application logs are automatically sent
- CloudWatch Events: Scheduled rules trigger Lambda functions
- CloudWatch Metrics: Automatic metrics collection from AWS services

### Data Flow for CloudWatch

#### Logging Flow:
```
1. Flask application writes logs using Python logging module
2. Logs are written to stdout/stderr
3. Elastic Beanstalk captures stdout/stderr
4. Logs are automatically sent to CloudWatch Logs
5. Log group: /aws/elasticbeanstalk/smart-budget-planner-env/var/log/web.stdout.log
6. Logs can be viewed in CloudWatch Logs console
7. Logs are searchable and filterable
```

#### Scheduled Event Flow (Budget Alerts):
```
1. CloudWatch Events rule is created (cron expression: daily at specific time)
2. Rule is configured to trigger budget_alert Lambda function
3. At scheduled time, CloudWatch Events invokes Lambda
4. Lambda function receives event from CloudWatch
5. Lambda processes budgets and sends alerts
6. CloudWatch records invocation metrics
```

#### Metrics Collection Flow:
```
1. AWS services automatically send metrics to CloudWatch:
   - DynamoDB: Read/Write capacity, throttling events
   - Lambda: Invocations, duration, errors
   - SQS: Queue depth, message age
   - S3: Request counts, data transfer
   - Elastic Beanstalk: Request count, latency, HTTP errors
2. Metrics are available in CloudWatch Metrics console
3. Alarms can be configured based on metrics
4. Dashboards can be created to visualize metrics
```

---

## 9. AWS IAM Integration

### How IAM is Integrated

IAM provides security and access control for all AWS services.

**Integration Method:**
- IAM roles are created for Lambda functions
- IAM instance profiles are used for Elastic Beanstalk EC2 instances
- IAM policies define permissions for each service
- No hardcoded credentials are used

### Data Flow for IAM

#### Lambda Function Permissions Flow:
```
1. IAM role is created for Lambda functions
2. Role has policies attached:
   - DynamoDB: Read/Write access to tables
   - S3: Read/Write access to bucket
   - SNS: Publish messages to topic
   - SQS: Receive/Delete messages from queue
   - CloudWatch Logs: Write logs
3. Lambda function is configured with this IAM role
4. When Lambda executes, it uses role credentials automatically
5. AWS services verify IAM permissions before allowing operations
```

#### Elastic Beanstalk Instance Permissions Flow:
```
1. IAM instance profile is created
2. Instance profile has policies attached:
   - DynamoDB: Read/Write access to tables
   - S3: Read/Write access to bucket
   - Lambda: Invoke functions
   - SQS: Send messages to queue
   - SNS: Subscribe and publish
   - CloudWatch Logs: Write logs
3. EC2 instance is launched with this instance profile
4. Flask application uses instance profile credentials (via boto3)
5. No AWS access keys are stored in code or environment variables
```

#### Service-to-Service Authentication Flow:
```
1. Flask application needs to call DynamoDB
2. boto3 uses IAM instance profile credentials
3. Request is signed with IAM credentials
4. DynamoDB verifies IAM permissions
5. If authorized, request is processed
6. If not authorized, access denied error is returned
```

---

## Complete End-to-End Data Flow Examples

### Example 1: User Adds Expense with Receipt

```
1. User submits expense form with receipt file
2. Flask route `/api/expenses` (POST) receives request
3. ReceiptHandler validates file (type, size)
4. ReceiptHandler uploads file to S3 → S3 stores file at receipts/{user_id}/{expense_id}.jpg
5. S3 returns key
6. ExpenseProcessor validates expense data
7. ExpenseProcessor calls DynamoDBClient.add_expense()
8. DynamoDB stores expense record with receipt_url (S3 key)
9. BudgetCalculator checks if budget exceeded
10. If exceeded, NotificationManager queues notification to SQS
11. SQS stores message in notification-queue
12. SQS triggers notification_processor Lambda
13. Lambda processes message, publishes to SNS
14. SNS delivers email to user
15. Flask returns expense data to user
```

### Example 2: Daily Budget Alert Check

```
1. CloudWatch Events triggers budget_alert Lambda (scheduled daily)
2. Lambda queries DynamoDB budgets table (scan)
3. For each budget:
   a. Lambda queries expenses table (user_id-index, filtered by category)
   b. Calculates spending percentage
   c. If >= threshold:
      - Gets user email from users table
      - Checks SNS subscription status
      - Configures subscription filter
      - Publishes to SNS topic with user_email attribute
      - Records notification in DynamoDB
4. SNS evaluates filter policy
5. SNS delivers email to subscribed user
6. Lambda returns summary of alerts sent
```

### Example 3: Report Generation

```
1. User requests report via `/api/reports/generate`
2. Flask route calls LambdaClient.invoke_report_generator()
3. Lambda function is invoked synchronously
4. Lambda queries DynamoDB:
   - Expenses table (user_id-index)
   - Budgets table (user_id-index)
5. Lambda filters expenses by date range
6. Lambda calculates report data (totals, categories, statistics)
7. Lambda generates PDF using ReportLab
8. Lambda uploads PDF to S3 → S3 stores at reports/{user_id}/monthly_report_20240115.pdf
9. Lambda generates presigned URL (24-hour expiration)
10. Lambda returns JSON with report_url
11. Flask route sends report_url to user
12. User downloads report using presigned URL
```

---

## Integration Summary

| Service | Integration Method | Primary Use Case | Trigger/Invocation |
|---------|-------------------|------------------|-------------------|
| DynamoDB | boto3 resource API | Data storage (users, expenses, budgets, notifications) | Direct calls from Flask app and Lambda |
| S3 | boto3 client API | File storage (receipts, reports) | Direct calls from Flask app and Lambda |
| Lambda | boto3 client API (invoke) | Asynchronous processing (alerts, reports, notifications) | CloudWatch Events, SQS, direct invocation |
| SQS | boto3 client API | Message queuing for notifications | Flask app sends, Lambda consumes |
| SNS | boto3 client API | Email delivery | Lambda publishes, SNS delivers |
| Elastic Beanstalk | AWS CLI/Console | Application hosting | CI/CD pipeline deploys |
| ECR | Docker CLI + AWS CLI | Container image storage | CI/CD pipeline pushes, EB pulls |
| CloudWatch | Automatic + boto3 | Logging, monitoring, scheduling | Automatic for logs, boto3 for events |
| IAM | AWS Console/CLI | Security and permissions | Configured once, used automatically |

---

## Key Integration Patterns

1. **Direct API Calls**: Flask app and Lambda functions use boto3 to directly call AWS service APIs
2. **Event-Driven**: SQS triggers Lambda, CloudWatch Events triggers Lambda
3. **Asynchronous Processing**: Notifications are queued in SQS, processed by Lambda asynchronously
4. **Presigned URLs**: S3 uses presigned URLs for secure, time-limited access without public buckets
5. **IAM Roles**: All services use IAM roles for authentication, no hardcoded credentials
6. **GSI Queries**: DynamoDB uses Global Secondary Indexes for efficient user-specific queries
7. **Filter Policies**: SNS uses subscription filter policies for user-specific email delivery

