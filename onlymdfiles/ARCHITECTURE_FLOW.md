# Architecture & Data Flow - Quick Reference

## 🏗️ System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    USER BROWSER                              │
│              (HTML/CSS/JavaScript)                           │
└───────────────────────┬─────────────────────────────────────┘
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              AWS ELASTIC BEANSTALK                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         EC2 Instance (Docker Container)              │  │
│  │  ┌────────────────────────────────────────────────┐ │  │
│  │  │         Flask Application (app.py)              │ │  │
│  │  │  ┌──────────────┐  ┌──────────────────────┐  │ │  │
│  │  │  │   Routes     │  │   Custom Libraries    │  │ │  │
│  │  │  │  (app.py)    │  │  (lib/)               │  │ │  │
│  │  │  └──────┬───────┘  └──────────┬─────────────┘  │ │  │
│  │  │         │                      │                │ │  │
│  │  │         └──────────┬───────────┘                │ │  │
│  │  │                    │                            │ │  │
│  │  │         ┌──────────▼──────────┐                 │ │  │
│  │  │         │  AWS Service Clients│                 │ │  │
│  │  │         │  (aws_config/)       │                 │ │  │
│  │  │         └──────────┬──────────┘                 │ │  │
│  │  └────────────────────┼────────────────────────────┘ │  │
│  └────────────────────────┼──────────────────────────────┘  │
└────────────────────────────┼─────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   DynamoDB    │   │      S3       │   │     SNS      │
│  (Database)   │   │  (Storage)    │   │ (Notifications)│
│               │   │               │   │               │
│ Users         │   │ Receipts      │   │ Email Topic   │
│ Expenses      │   │ Reports       │   │ Subscribers   │
│ Budgets       │   │               │   │               │
│ Notifications │   │               │   │               │
└───────┬───────┘   └───────────────┘   └───────┬───────┘
        │                                        │
        │                                        │
        ▼                                        ▼
┌───────────────┐                      ┌───────────────┐
│    Lambda     │                      │  CloudWatch   │
│  Functions    │                      │    Events     │
│               │                      │               │
│ Budget Alert  │◄────────────────────│  (Scheduler) │
│ Report Gen    │                      │               │
└───────────────┘                      └───────────────┘
```

---

## 🔄 Complete Data Flows

### **Flow 1: User Registration**
```
Browser → POST /register
    ↓
app.py: register() route
    ↓
db.create_user() → DynamoDB (Users table)
    ↓
Password hashed with Werkzeug
    ↓
Session created
    ↓
Redirect to /dashboard
```

### **Flow 2: User Login**
```
Browser → POST /login
    ↓
app.py: login() route
    ↓
db.get_user_by_username() → DynamoDB
    ↓
check_password_hash() → Verify password
    ↓
Session created (user_id stored)
    ↓
Redirect to /dashboard
```

### **Flow 3: Adding Expense**
```
Browser → POST /api/expenses
    ↓
app.py: add_expense() route
    ↓
expense_processor.add_expense()
    ├─→ Validates input
    └─→ db.add_expense() → DynamoDB (Expenses table)
    ↓
Returns JSON response
    ↓
Frontend updates expense list
```

### **Flow 4: Setting Budget**
```
Browser → POST /api/budget
    ↓
app.py: set_budget() route
    ↓
db.add_budget() → DynamoDB (Budgets table)
    ↓
Returns JSON response
    ↓
Frontend updates budget list
```

### **Flow 5: Dashboard Summary**
```
Browser → GET /api/summary
    ↓
app.py: get_summary() route
    ↓
budget_calculator.get_budget_summary()
    ├─→ db.get_user_budgets() → DynamoDB
    ├─→ db.get_user_expenses() → DynamoDB
    └─→ Calculates totals, percentages, remaining
    ↓
Returns JSON with summary data
    ↓
Frontend displays charts and progress bars
```

### **Flow 6: Budget Alert (Automatic - Daily)**
```
CloudWatch Events → Triggers Lambda (8 AM daily)
    ↓
lambda_functions/budget_alert/lambda_function.py
    ├─→ db.get_all_users() → DynamoDB
    ├─→ db.get_user_budgets() → DynamoDB (for each user)
    ├─→ db.get_user_expenses() → DynamoDB (for each user)
    ├─→ Calculates spending vs budget
    └─→ If exceeded → sns.publish_message() → SNS Topic
    ↓
SNS Topic → Sends email to subscribed users
    ↓
db.add_notification() → DynamoDB (Notifications table)
```

### **Flow 7: Email Subscription**
```
Browser → POST /api/notifications/subscribe
    ↓
app.py: subscribe_notifications() route
    ↓
notification_manager.subscribe_user()
    └─→ sns.subscribe_email() → SNS Topic
    ↓
AWS SNS → Sends confirmation email to user
    ↓
User clicks confirmation link
    ↓
Email confirmed → Future alerts will be sent
```

### **Flow 8: Upload Receipt**
```
Browser → POST /api/receipts/upload
    ↓
app.py: upload_receipt() route
    ↓
receipt_handler.upload_receipt()
    ├─→ Validates file type/size
    └─→ s3_client.upload_file() → S3 Bucket
    ↓
S3 returns file key
    ↓
db.update_expense() → DynamoDB (add receipt_url)
    ↓
Returns JSON with receipt URL
```

### **Flow 9: View Receipt**
```
Browser → GET /api/receipts/<expense_id>
    ↓
app.py: get_receipt() route
    ↓
receipt_handler.get_receipt_url()
    └─→ s3_client.generate_presigned_url() → S3
    ↓
Returns presigned URL (expires in 1 hour)
    ↓
Frontend opens image in new tab
```

### **Flow 10: Generate Report**
```
Browser → POST /api/reports/generate
    ↓
app.py: generate_report() route
    ↓
lambda_client.invoke_report_generator()
    └─→ Invokes Lambda function (synchronous)
    ↓
lambda_functions/report_generator/lambda_function.py
    ├─→ db.get_user_expenses() → DynamoDB
    ├─→ Generates PDF using ReportLab
    └─→ s3_client.upload_file() → S3 Bucket
    ↓
Returns presigned URL
    ↓
Frontend downloads/opens PDF
```

---

## 📊 Component Interaction Diagram

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
       │ HTTP Requests
       ▼
┌─────────────────────────────────────┐
│         app.py (Flask)               │
│  ┌───────────────────────────────┐  │
│  │  Routes (API Endpoints)       │  │
│  └───────────┬───────────────────┘  │
│              │                       │
│  ┌───────────▼───────────────────┐  │
│  │  Custom Libraries (lib/)     │  │
│  │  - ExpenseProcessor          │  │
│  │  - BudgetCalculator          │  │
│  │  - NotificationManager       │  │
│  │  - ReceiptHandler            │  │
│  └───────────┬───────────────────┘  │
│              │                       │
│  ┌───────────▼───────────────────┐  │
│  │  AWS Clients (aws_config/)    │  │
│  │  - DynamoDBClient             │  │
│  │  - S3Client                   │  │
│  │  - SNSClient                  │  │
│  │  - LambdaClient               │  │
│  └───────────┬───────────────────┘  │
└──────────────┼───────────────────────┘
               │
    ┌──────────┼──────────┬──────────┬──────────┐
    │          │          │          │          │
    ▼          ▼          ▼          ▼          ▼
┌────────┐ ┌──────┐ ┌────────┐ ┌────────┐ ┌────────┐
│DynamoDB│ │  S3  │ │  SNS   │ │ Lambda │ │CloudWatch│
└────────┘ └──────┘ └────────┘ └────────┘ └────────┘
```

---

## 🔑 Key File Responsibilities

| Component | File(s) | Responsibility |
|-----------|---------|----------------|
| **Entry Point** | `app.py` | HTTP routes, request handling, session management |
| **Database** | `aws_config/setup_dynamodb.py` | All CRUD operations for Users, Expenses, Budgets, Notifications |
| **Expense Logic** | `lib/expense_processor.py` | Validate and process expenses |
| **Budget Logic** | `lib/budget_calculator.py` | Calculate totals, percentages, remaining amounts |
| **Notifications** | `lib/notification_manager.py` | Subscribe users, send email alerts |
| **Receipts** | `lib/receipt_handler.py` | Upload/download receipts from S3 |
| **Storage** | `aws_config/setup_s3.py` | S3 operations (upload, download, presigned URLs) |
| **Email** | `aws_config/setup_sns.py` | SNS operations (subscribe, publish) |
| **Serverless** | `aws_config/setup_lambda.py` | Invoke Lambda functions |
| **Budget Alerts** | `lambda_functions/budget_alert/` | Daily budget checking and alerting |
| **Reports** | `lambda_functions/report_generator/` | PDF report generation |
| **Config** | `aws_config/config.py` | Central configuration for all AWS resources |

---

## 🎯 Presentation Talking Points

### **1. Architecture Overview (2 min)**
- "The application follows a 3-tier architecture..."
- "We use 9 AWS services working together..."
- "The Flask app runs on Elastic Beanstalk..."

### **2. User Flow Example (3 min)**
- "Let me walk you through adding an expense..."
- "User submits form → Flask validates → Saves to DynamoDB → Returns response"
- "This demonstrates the separation of concerns..."

### **3. Serverless Components (2 min)**
- "Budget alerts run automatically via Lambda..."
- "CloudWatch Events triggers Lambda daily..."
- "Lambda queries DynamoDB, calculates spending, sends emails via SNS"

### **4. Scalability & Cost (1 min)**
- "DynamoDB auto-scales based on traffic..."
- "Lambda only charges when executing..."
- "Elastic Beanstalk auto-scales EC2 instances..."

---

**Use this as a quick reference during your presentation!**

