# Complete Code Explanation Guide

## 📋 Table of Contents
1. [Overall Architecture](#overall-architecture)
2. [AWS Services Used](#aws-services-used)
3. [Main Application Flow](#main-application-flow)
4. [Function Call Flows](#function-call-flows)
5. [AWS Service Integration Details](#aws-service-integration-details)
6. [Lambda Functions](#lambda-functions)
7. [Common Questions & Answers](#common-questions--answers)

---

## 🏗️ Overall Architecture

Your application is a **Smart Budget Planner** built with:
- **Frontend**: Flask web application (app.py)
- **Backend**: Python with AWS services
- **Database**: DynamoDB (NoSQL)
- **Storage**: S3 (for receipts and reports)
- **Notifications**: SNS + SQS (for email alerts)
- **Serverless**: Lambda functions (for background processing)

### Architecture Flow:
```
User → Flask App (app.py) → AWS Services → Response to User
                ↓
         Lambda Functions (background tasks)
```

---

## ☁️ AWS Services Used

### 1. **DynamoDB** (Database)
**Purpose**: Store all application data
**Tables**:
- `smart-budget-users` - User accounts
- `smart-budget-expenses` - Expense records
- `smart-budget-budgets` - Budget limits per category
- `smart-budget-notifications` - Notification history

**Where it's used**:
- `aws_config/setup_dynamodb.py` - DynamoDBClient class
- Called from: `app.py` (line 47: `db = DynamoDBClient()`)
- Used in: All routes that need to read/write data

### 2. **S3** (File Storage)
**Purpose**: Store receipt images and PDF reports
**Bucket**: `smart-budget-receipts`

**Where it's used**:
- `aws_config/setup_s3.py` - S3Client class
- Called from: `app.py` (line 49: `s3_client = S3Client()`)
- Used in:
  - `/api/receipts/upload` (line 612) - Upload receipts
  - `/api/reports/generate` (line 791) - Generate PDF reports
  - `lib/receipt_handler.py` - Wrapper for S3 operations

### 3. **SNS** (Simple Notification Service)
**Purpose**: Send email notifications to users
**Topic**: `budget-alerts-topic`

**Where it's used**:
- `aws_config/setup_sns.py` - SNSClient class
- Called from: `lib/notification_manager.py` (line 22: `self.sns = SNSClient()`)
- Used in:
  - User subscription (app.py line 708)
  - Sending alerts (notification_manager.py)
  - Lambda functions (budget_alert, notification_processor)

### 4. **SQS** (Simple Queue Service)
**Purpose**: Queue notification messages for processing
**Queue**: `notification-queue`

**Where it's used**:
- `aws_config/setup_sqs.py` - SQSClient class
- Called from: `lib/notification_manager.py` (line 24: `self.sqs = SQSClient()`)
- Used in: `notification_manager._send_notification()` (line 152)
- Trigger: SQS triggers `notification-processor` Lambda function

### 5. **Lambda** (Serverless Functions)
**Purpose**: Run background tasks without managing servers
**Functions**:
1. `budget-alert-function` - Daily budget check
2. `report-generator-function` - Generate PDF reports
3. `notification-processor-function` - Process queued notifications

**Where it's used**:
- `aws_config/setup_lambda.py` - LambdaClient class
- Called from: `app.py` (line 48: `lambda_client = LambdaClient()`)
- Used in: `/api/reports/generate` (line 791)

### 6. **CloudWatch** (Logging)
**Purpose**: Monitor and log application events
**Where it's used**: `app.py` (lines 34-45) - Automatic logging setup

---

## 🔄 Main Application Flow

### 1. **User Registration Flow**
```
User fills form → /register (app.py line 149)
    ↓
db.create_user() → DynamoDB (setup_dynamodb.py line 17)
    ↓
notification_manager.subscribe_user() → SNS (setup_sns.py line 66)
    ↓
User receives confirmation email from AWS SNS
```

### 2. **Adding Expense Flow**
```
User adds expense → /api/expenses POST (app.py line 371)
    ↓
expense_processor.add_expense() → DynamoDB (expense_processor.py line 25)
    ↓
budget_calculator.check_budget_exceeded() → Check if over budget (budget_calculator.py line 80)
    ↓
notification_manager.send_budget_exceeded_alert() → Queue notification (notification_manager.py line 56)
    ↓
SQS receives message → Triggers notification-processor Lambda
    ↓
Lambda sends email via SNS
```

### 3. **Receipt Upload Flow**
```
User uploads file → /api/receipts/upload (app.py line 591)
    ↓
receipt_handler.upload_receipt() → Validates file (receipt_handler.py line 32)
    ↓
s3.upload_receipt() → Uploads to S3 (setup_s3.py line 12)
    ↓
db.update_expense() → Updates DynamoDB with receipt URL (app.py line 620)
```

### 4. **Report Generation Flow**
```
User requests report → /api/reports/generate (app.py line 771)
    ↓
lambda_client.invoke_report_generator() → Calls Lambda (setup_lambda.py line 25)
    ↓
report-generator Lambda → Reads from DynamoDB, generates PDF
    ↓
PDF uploaded to S3 → Returns presigned URL
    ↓
User downloads report
```

---

## 🔗 Function Call Flows

### **DynamoDB Operations**

#### Where `db.get_user_by_id()` is called:
- `app.py` line 72 - Login check
- `app.py` line 95 - Get current user
- `app.py` line 207 - Session validation
- `app.py` line 265 - Check session API

#### Where `db.add_expense()` is called:
- `lib/expense_processor.py` line 31 - Called by `add_expense()`
- `app.py` line 387 - Called from `/api/expenses` POST route

#### Where `db.get_user_budgets()` is called:
- `lib/budget_calculator.py` line 10 - Calculate totals
- `lib/budget_calculator.py` line 47 - Check threshold
- `lib/budget_calculator.py` line 82 - Check exceeded
- `lib/budget_calculator.py` line 115 - Get category budget
- `lib/budget_calculator.py` line 125 - Get summary
- `app.py` line 490 - Get budgets API

### **S3 Operations**

#### Where `s3.upload_receipt()` is called:
- `lib/receipt_handler.py` line 44 - Called by `upload_receipt()`
- `app.py` line 612 - Called from `/api/receipts/upload` route

#### Where `s3.list_user_reports()` is called:
- `app.py` line 839 - Called from `/api/reports` GET route

### **SNS Operations**

#### Where `sns.subscribe_email()` is called:
- `lib/notification_manager.py` line 31 - Called by `subscribe_user()`
- `app.py` line 708 - Called from `/api/notifications/subscribe` route

#### Where `sns.publish_message()` is called:
- `lib/notification_manager.py` line 180 - Called by `publish_notification()`
- `lambda_functions/budget_alert/lambda_function.py` line 66 - Direct SNS publish
- `lambda_functions/notification_processor/lambda_function.py` line 47 - Direct SNS publish

### **SQS Operations**

#### Where `sqs.send_notification_message()` is called:
- `lib/notification_manager.py` line 152 - Called by `_send_notification()`
- This queues messages that trigger the notification-processor Lambda

### **Lambda Operations**

#### Where `lambda_client.invoke_report_generator()` is called:
- `app.py` line 791 - Called from `/api/reports/generate` route

---

## 🔧 AWS Service Integration Details

### **DynamoDB Integration**

**File**: `aws_config/setup_dynamodb.py`

**Key Functions**:
- `create_user()` - Creates new user (line 17)
- `get_user_by_id()` - Gets user by ID (line 36)
- `add_expense()` - Adds expense record (line 105)
- `get_user_expenses()` - Gets all expenses for user (line 131)
- `add_budget()` - Creates budget (line 177)
- `get_user_budgets()` - Gets all budgets for user (line 200)
- `add_notification()` - Records notification (line 262)

**How it's initialized**:
```python
# In app.py line 47
db = DynamoDBClient()
# This creates boto3 DynamoDB resource and connects to tables
```

**Where tables are defined**: `aws_config/config.py` lines 16-21

### **S3 Integration**

**File**: `aws_config/setup_s3.py`

**Key Functions**:
- `upload_receipt()` - Upload receipt file (line 12)
- `get_receipt_url()` - Get presigned URL (line 26)
- `upload_report()` - Upload PDF report (line 38)
- `list_user_reports()` - List user's reports (line 73)

**Bucket name**: Defined in `aws_config/config.py` line 23

**How files are stored**:
- Receipts: `receipts/{user_id}/{expense_id}.{extension}`
- Reports: `reports/{user_id}/{filename}.pdf`

### **SNS Integration**

**File**: `aws_config/setup_sns.py`

**Key Functions**:
- `subscribe_email()` - Subscribe email to topic (line 66)
- `publish_message()` - Send notification (line 40)
- `list_subscriptions()` - List all subscriptions (line 164)

**Topic ARN**: Auto-discovered or created in `_initialize_topic_arn()` (line 17)

**Filter Policy**: Used to send notifications only to specific email (line 96-103)

### **SQS Integration**

**File**: `aws_config/setup_sqs.py`

**Key Functions**:
- `send_notification_message()` - Queue notification (line 33)
- `receive_messages()` - Receive from queue (line 56)
- `delete_message()` - Delete after processing (line 88)

**Queue URL**: Auto-discovered in `_initialize_queue_urls()` (line 17)

**How it works**:
1. App sends message to SQS queue
2. SQS triggers notification-processor Lambda
3. Lambda processes message and sends email via SNS

### **Lambda Integration**

**File**: `aws_config/setup_lambda.py`

**Key Functions**:
- `invoke_report_generator()` - Call report Lambda (line 25)
- `invoke_budget_alert()` - Call budget alert Lambda (line 12)

**Function names**: Defined in `aws_config/config.py` lines 31-35

---

## ⚡ Lambda Functions

### 1. **Budget Alert Lambda** (`budget-alert-function`)

**File**: `lambda_functions/budget_alert/lambda_function.py`

**Purpose**: Check all budgets daily and send alerts if threshold exceeded

**How it's triggered**: 
- Scheduled via CloudWatch Events (daily)
- Can be manually invoked

**What it does**:
1. Scans all budgets from DynamoDB (line 88)
2. For each budget, calculates total expenses (line 106)
3. Checks if percentage >= alert_threshold (line 111)
4. Gets user email from DynamoDB (line 112)
5. Sends email via SNS (line 131)
6. Records notification in DynamoDB (line 132)

**Key Functions**:
- `get_sns_topic_arn()` - Find SNS topic (line 16)
- `check_email_subscription()` - Verify email subscribed (line 40)
- `send_email_notification()` - Send email (line 57)
- `lambda_handler()` - Main entry point (line 82)

### 2. **Notification Processor Lambda** (`notification-processor-function`)

**File**: `lambda_functions/notification_processor/lambda_function.py`

**Purpose**: Process queued notifications from SQS

**How it's triggered**: 
- Automatically by SQS when message arrives
- Event contains SQS records

**What it does**:
1. Receives SQS message (line 166)
2. Parses notification data (line 181)
3. Checks if email is subscribed (line 107)
4. Sends email via SNS (line 114)
5. Updates notification status in DynamoDB (line 117)

**Key Functions**:
- `process_notification()` - Process single notification (line 82)
- `send_email()` - Send via SNS (line 31)
- `lambda_handler()` - Main entry point (line 160)

### 3. **Report Generator Lambda** (`report-generator-function`)

**File**: `lambda_functions/report_generator/lambda_function.py`

**Purpose**: Generate PDF reports from expense data

**How it's triggered**: 
- Invoked from Flask app via LambdaClient (app.py line 791)

**What it does**:
1. Receives user_id and report_type (line 26)
2. Queries expenses from DynamoDB (line 111)
3. Generates PDF using ReportLab (line 376)
4. Uploads PDF to S3 (line 83)
5. Returns presigned URL (line 90)

**Key Functions**:
- `generate_monthly_report()` - Monthly report data (line 110)
- `generate_weekly_report()` - Weekly report data (line 201)
- `generate_custom_date_report()` - Custom date range (line 289)
- `generate_pdf_report()` - Create PDF (line 376)
- `lambda_handler()` - Main entry point (line 21)

---

## ❓ Common Questions & Answers

### Q: Where is DynamoDB initialized?
**A**: In `app.py` line 47: `db = DynamoDBClient()`
The DynamoDBClient class is in `aws_config/setup_dynamodb.py` and connects to tables defined in `aws_config/config.py`.

### Q: How does user authentication work?
**A**: 
- Login route: `app.py` line 200
- Uses Flask sessions to store `user_id`
- `login_required` decorator (line 55) checks session before allowing access
- Passwords hashed with `werkzeug.security.generate_password_hash()`

### Q: Where are expenses stored?
**A**: 
- DynamoDB table: `smart-budget-expenses`
- Added via: `db.add_expense()` called from `expense_processor.add_expense()`
- Route: `/api/expenses` POST (app.py line 371)

### Q: How do notifications work?
**A**: 
1. User subscribes: `/api/notifications/subscribe` (app.py line 678)
2. Email subscribed to SNS topic
3. When alert needed: `notification_manager._send_notification()` (notification_manager.py line 120)
4. Message queued to SQS (line 152)
5. SQS triggers notification-processor Lambda
6. Lambda sends email via SNS

### Q: Where are receipts stored?
**A**: 
- S3 bucket: `smart-budget-receipts`
- Path: `receipts/{user_id}/{expense_id}.{extension}`
- Upload route: `/api/receipts/upload` (app.py line 591)
- Uses `receipt_handler.upload_receipt()` which calls `s3.upload_receipt()`

### Q: How are reports generated?
**A**: 
1. User requests: `/api/reports/generate` (app.py line 771)
2. Flask calls: `lambda_client.invoke_report_generator()` (line 791)
3. Lambda function reads expenses from DynamoDB
4. Generates PDF using ReportLab
5. Uploads PDF to S3
6. Returns presigned URL to user

### Q: What triggers the budget alert Lambda?
**A**: 
- Scheduled via CloudWatch Events (daily schedule)
- Can also be manually invoked
- Scans all budgets and checks if spending exceeds threshold

### Q: How does SQS trigger the notification processor?
**A**: 
- SQS queue is configured as event source for Lambda
- When message arrives in queue, AWS automatically invokes Lambda
- Lambda receives event with `Records` array containing SQS messages

### Q: Where is the SNS topic created?
**A**: 
- Auto-created in `SNSClient._initialize_topic_arn()` (setup_sns.py line 17)
- If topic doesn't exist, it creates one (line 26)
- Topic name: `budget-alerts-topic` (config.py line 29)

### Q: How are budgets checked when expense is added?
**A**: 
- In `app.py` line 416: `budget_calculator.check_budget_exceeded()`
- This queries DynamoDB for user's budgets and expenses
- Compares spent amount vs budget amount
- If exceeded, calls `notification_manager.send_budget_exceeded_alert()` (line 422)

### Q: What is the filter policy in SNS?
**A**: 
- Used to send notifications only to specific email addresses
- Set in `setup_sns.py` line 96-103
- Ensures each user only receives their own notifications
- Uses `user_email` attribute in message

---

## 📝 Key File Locations

| Component | File | Purpose |
|-----------|------|---------|
| Main App | `app.py` | Flask routes and API endpoints |
| DynamoDB | `aws_config/setup_dynamodb.py` | Database operations |
| S3 | `aws_config/setup_s3.py` | File storage operations |
| SNS | `aws_config/setup_sns.py` | Email notifications |
| SQS | `aws_config/setup_sqs.py` | Message queue |
| Lambda | `aws_config/setup_lambda.py` | Lambda invocation |
| Config | `aws_config/config.py` | AWS resource names |
| Budget Logic | `lib/budget_calculator.py` | Budget calculations |
| Expense Logic | `lib/expense_processor.py` | Expense operations |
| Notifications | `lib/notification_manager.py` | Notification handling |
| Receipts | `lib/receipt_handler.py` | Receipt file handling |
| Budget Alert | `lambda_functions/budget_alert/` | Daily budget check |
| Notification Proc | `lambda_functions/notification_processor/` | Process notifications |
| Report Gen | `lambda_functions/report_generator/` | Generate PDF reports |

---

## 🎯 Quick Reference: Function Call Chain Examples

### Example 1: User Adds Expense
```
User → POST /api/expenses
  → expense_processor.add_expense()
    → db.add_expense() → DynamoDB
  → budget_calculator.check_budget_exceeded()
    → db.get_user_budgets() → DynamoDB
    → db.get_user_expenses() → DynamoDB
  → notification_manager.send_budget_exceeded_alert()
    → db.add_notification() → DynamoDB
    → sqs.send_notification_message() → SQS
      → Triggers notification-processor Lambda
        → Sends email via SNS
```

### Example 2: User Uploads Receipt
```
User → POST /api/receipts/upload
  → receipt_handler.upload_receipt()
    → Validates file type and size
    → s3.upload_receipt() → S3
  → db.update_expense() → DynamoDB (updates receipt_url)
```

### Example 3: Generate Report
```
User → POST /api/reports/generate
  → lambda_client.invoke_report_generator()
    → AWS Lambda: report-generator-function
      → Queries DynamoDB for expenses
      → Generates PDF
      → Uploads to S3
      → Returns presigned URL
```

---

**Remember**: All AWS operations use boto3 library, initialized through `get_boto3_session()` in `aws_config/config.py` line 5.

