# Code Understanding Guide - Smart Budget Planner
## Complete Learning Path for Presentation Preparation

**Note**: This guide reflects the cleaned codebase after removal of AI-generated comments and debug statements. All code is production-ready and professional.

---

## 📚 **STUDY ORDER: Start Here → End Here**

### **PHASE 1: Foundation & Configuration (30 minutes)**
*Understand the basic setup and AWS configuration*

#### 1.1 AWS Configuration
**File: `aws_config/config.py`** (5 min)
- What it does: Central configuration for all AWS services
- Key concepts: Region, table names, bucket names, queue names, Lambda function names
- Why important: Every other file references this for AWS resource names

**File: `aws_config/__init__.py`** (2 min)
- What it does: Package initialization
- Just exports config - quick read

#### 1.2 Database Client
**File: `aws_config/setup_dynamodb.py`** (15 min)
- What it does: All database operations (CRUD for Users, Expenses, Budgets, Notifications)
- Key methods to understand:
  - `create_user()` - User registration
  - `get_user_by_username()` - Login authentication
  - `add_expense()` - Save expense
  - `get_user_expenses()` - Fetch expenses
  - `add_budget()` - Save budget
  - `get_user_budgets()` - Fetch budgets
- Why important: This is where ALL data is stored/retrieved

#### 1.3 Other AWS Clients (Quick Overview - 8 min)
**Files:**
- `aws_config/setup_s3.py` - Receipt storage (upload, download, presigned URLs)
- `aws_config/setup_sns.py` - Email notifications (subscribe, publish)
- `aws_config/setup_lambda.py` - Invoke Lambda functions (budget alerts, reports)
- `aws_config/setup_sqs.py` - Message queuing (currently only for notifications)

**Focus:** Understand what each service does, not deep implementation details yet

---

### **PHASE 2: Business Logic Libraries (45 minutes)**
*Understand the core application logic*

#### 2.1 Expense Processing
**File: `lib/expense_processor.py`** (10 min)
- What it does: Validates and saves expenses
- Key flow:
  1. User submits expense → `add_expense()` called
  2. Validates amount, category, description
  3. Calls `db.add_expense()` to save to DynamoDB
  4. Returns expense data
- Key methods:
  - `validate_expense()` - Input validation
  - `add_expense()` - Main method (called from app.py)
  - `get_expenses_by_user()` - Fetch user expenses
  - `delete_expense()` - Remove expense

#### 2.2 Budget Calculations
**File: `lib/budget_calculator.py`** (15 min)
- What it does: Calculates budget vs spending, percentages, remaining amounts
- Key methods:
  - `calculate_totals()` - Total budgets and expenses
  - `calculate_remaining()` - Remaining budget amount
  - `calculate_percentage()` - Spending percentage
  - `check_budget_threshold()` - Check if budget exceeded
  - `get_budget_summary()` - Complete summary (used in dashboard)
- Why important: Dashboard and budget alerts depend on this

#### 2.3 Notification Management
**File: `lib/notification_manager.py`** (15 min)
- What it does: Handles all email notifications via SQS queuing
- Key flow:
  1. User subscribes → `subscribe_user()` → SNS subscription
  2. Budget alert needed → `send_budget_exceeded_alert()` → `_send_notification()` → SQS queue
  3. Notification saved to DynamoDB (status: 'queued')
  4. SQS triggers notification_processor Lambda
  5. Lambda processes message and sends via SNS
  6. Lambda updates notification status to 'sent' in DynamoDB
- Key methods:
  - `subscribe_user()` - Subscribe email to SNS
  - `send_budget_exceeded_alert()` - Queue budget exceeded alert
  - `send_large_expense_alert()` - Queue large expense alert
  - `_send_notification()` - Internal method that queues to SQS
  - `send_subscription_confirmation()` - Welcome email (direct SNS)
- Why important: All notifications go through this, uses SQS for async processing

#### 2.4 Receipt Handling
**File: `lib/receipt_handler.py`** (5 min)
- What it does: Uploads receipts to S3, generates presigned URLs
- Key methods:
  - `upload_receipt()` - Upload file to S3
  - `get_receipt_url()` - Get presigned URL for viewing
  - `validate_file_type()` - Check file format
- Why important: Receipt upload functionality

---

### **PHASE 3: Main Application (60 minutes)**
*Understand the Flask application and API routes*

#### 3.1 Application Entry Point
**File: `app.py`** (60 min) - **MOST IMPORTANT FILE**
- What it does: Main Flask application with all routes

**Study order within app.py:**

1. **Imports & Setup (lines 1-53)** (5 min)
   - Understand what libraries are imported
   - See how AWS clients and custom libraries are initialized

2. **Authentication Routes (lines 55-268)** (15 min)
   - `@app.route('/register')` - User registration
   - `@app.route('/login')` - User login
   - `@app.route('/logout')` - Logout
   - `@app.route('/api/check-session')` - Session validation
   - **Key concept:** Session management, password hashing

3. **Page Routes (lines 270-298)** (5 min)
   - `@app.route('/dashboard')` - Dashboard page
   - `@app.route('/expenses')` - Expenses page
   - `@app.route('/budget')` - Budget page
   - Just render templates - simple

4. **Expense API Routes (lines 300-450)** (15 min)
   - `GET /api/expenses` - Fetch user expenses
   - `POST /api/expenses` - Add new expense
   - `DELETE /api/expenses/<id>` - Delete expense
   - **Flow:** Request → Validate → Process → Return JSON

5. **Budget API Routes (lines 452-550)** (10 min)
   - `GET /api/budget` - Fetch user budgets
   - `POST /api/budget` - Create/update budget
   - `DELETE /api/budget/<id>` - Delete budget
   - **Flow:** Similar to expenses

6. **Receipt Routes (lines 552-650)** (5 min)
   - `POST /api/receipts/upload` - Upload receipt
   - `GET /api/receipts/<expense_id>` - Get receipt URL
   - Uses `receipt_handler` library

7. **Notification Routes (lines 652-750)** (5 min)
   - `POST /api/notifications/subscribe` - Subscribe to email
   - `GET /api/user/contact-info` - Get user email/subscription status
   - Uses `notification_manager` library

8. **Report Routes (lines 752-850)** (5 min)
   - `POST /api/reports/generate` - Generate PDF report
   - Invokes Lambda function
   - Returns report URL

9. **Summary Route (lines 852-900)** (5 min)
   - `GET /api/summary` - Dashboard summary data
   - Uses `budget_calculator` library
   - Returns JSON for frontend

---

### **PHASE 4: Lambda Functions (30 minutes)**
*Understand serverless functions*

#### 4.1 Budget Alert Lambda
**File: `lambda_functions/budget_alert/lambda_function.py`** (20 min)
- What it does: Runs daily, checks all budgets, sends email alerts
- Trigger: CloudWatch Events (scheduled daily)
- Flow:
  1. Lambda triggered by schedule
  2. Query all users and budgets from DynamoDB
  3. Calculate spending vs budget for each
  4. If threshold exceeded → Publish to SNS
  5. SNS sends email to subscribed users
- Key functions:
  - `lambda_handler()` - Entry point
  - `get_sns_topic_arn()` - Get SNS topic
  - Budget calculation logic

#### 4.2 Report Generator Lambda
**File: `lambda_functions/report_generator/lambda_function.py`** (10 min)
- What it does: Generates PDF reports from expense data
- Trigger: Invoked from Flask app (synchronous)
- Flow:
  1. Flask calls Lambda with user_id and date range
  2. Lambda queries DynamoDB for expenses
  3. Generates PDF using ReportLab
  4. Uploads PDF to S3
  5. Returns presigned URL
- Key functions:
  - `lambda_handler()` - Entry point
  - `generate_pdf()` - PDF generation logic

---

### **PHASE 5: Frontend (30 minutes)**
*Understand user interface*

#### 5.1 HTML Templates
**Files:**
- `templates/base.html` - Base template (navigation, layout)
- `templates/index.html` - Dashboard (summary, charts)
- `templates/expenses.html` - Expense management (add, list, delete)
- `templates/budget.html` - Budget management (set budgets, subscribe notifications)
- `templates/login.html` - Login page
- `templates/register.html` - Registration page

**Focus:** Understand the structure, not every line. See how JavaScript interacts with API.

#### 5.2 JavaScript (in templates)
**Key JavaScript sections:**
- Expense form submission → POST `/api/expenses`
- Budget form submission → POST `/api/budget`
- Notification subscription → POST `/api/notifications/subscribe`
- Dashboard data loading → GET `/api/summary`

**Pattern:** All frontend uses `fetch()` API to call backend routes

---

### **PHASE 6: Deployment & Infrastructure (20 minutes)**
*Understand how it's deployed*

#### 6.1 Docker
**File: `Dockerfile`** (5 min)
- What it does: Containerizes the Flask app
- Key steps: Install dependencies, copy code, run with Gunicorn

#### 6.2 CI/CD
**File: `.github/workflows/deploy.yml`** (10 min)
- What it does: Automated deployment pipeline
- Flow: Push to GitHub → Build Docker → Push to ECR → Deploy to EB

#### 6.3 Setup Scripts (Quick overview - 5 min)
- `scripts/setup_aws_resources.py` - Creates AWS resources
- `scripts/deploy_lambda_functions.py` - Deploys Lambda functions
- `scripts/setup_elastic_beanstalk.py` - Sets up EB environment

---

## 🔄 **COMPLETE TASK FLOWS**

### **Flow 1: User Registration & Login**
```
1. User visits /register
2. Fills form → POST /register
3. app.py: register() route
   - Validates input
   - Calls db.create_user() → DynamoDB
   - Hashes password
   - Creates session
4. Redirects to dashboard
```

### **Flow 2: Adding an Expense**
```
1. User on /expenses page
2. Fills expense form → JavaScript POST /api/expenses
3. app.py: add_expense() route
   - Gets user from session
   - Calls expense_processor.add_expense()
     - Validates expense
     - Calls db.add_expense() → DynamoDB
   - Returns JSON
4. Frontend updates expense list
```

### **Flow 3: Setting a Budget**
```
1. User on /budget page
2. Fills budget form → JavaScript POST /api/budget
3. app.py: set_budget() route
   - Gets user from session
   - Calls db.add_budget() → DynamoDB
   - Returns JSON
4. Frontend updates budget list
```

### **Flow 4: Budget Alert (Automatic)**
```
1. CloudWatch Events triggers Lambda daily (8 AM)
2. budget_alert/lambda_function.py runs
   - Queries all users and budgets from DynamoDB
   - For each budget:
     - Calculates spending vs budget
     - If exceeded → Publishes to SNS topic
3. SNS sends email to subscribed users
4. Notification saved to DynamoDB
```

### **Flow 5: Subscribing to Notifications**
```
1. User on /budget page
2. Enters email → JavaScript POST /api/notifications/subscribe
3. app.py: subscribe_notifications() route
   - Gets user from session
   - Calls notification_manager.subscribe_user()
     - Calls sns.subscribe_email() → SNS subscription
   - Returns success message
4. User receives AWS SNS confirmation email
5. User clicks confirmation link
6. Email confirmed → Future alerts will be sent
```

### **Flow 6: Generating a Report**
```
1. User clicks "Generate Report" → JavaScript POST /api/reports/generate
2. app.py: generate_report() route
   - Gets user from session
   - Calls lambda_client.invoke_report_generator()
     - Invokes Lambda function synchronously
3. Lambda function:
   - Queries DynamoDB for expenses
   - Generates PDF
   - Uploads to S3
   - Returns presigned URL
4. Flask returns URL to frontend
5. Frontend opens/downloads report
```

### **Flow 7: Uploading a Receipt**
```
1. User selects file → JavaScript POST /api/receipts/upload
2. app.py: upload_receipt() route
   - Gets user from session
   - Calls receipt_handler.upload_receipt()
     - Validates file
     - Calls s3_client.upload_file() → S3
     - Returns S3 key
   - Updates expense with receipt URL
3. Frontend shows receipt link
```

---

## 📋 **FILES TO MEMORIZE FOR PRESENTATION**

### **Must Know (Core Files)**
1. **`app.py`** - Main application, all routes
2. **`aws_config/setup_dynamodb.py`** - Database operations
3. **`lib/expense_processor.py`** - Expense logic
4. **`lib/budget_calculator.py`** - Budget calculations
5. **`lib/notification_manager.py`** - Notification logic
6. **`lambda_functions/budget_alert/lambda_function.py`** - Budget alerts

### **Should Know (Important)**
7. **`aws_config/setup_s3.py`** - Receipt storage
8. **`aws_config/setup_sns.py`** - Email notifications
9. **`lib/receipt_handler.py`** - Receipt handling
10. **`lambda_functions/report_generator/lambda_function.py`** - Report generation

### **Good to Know (Supporting)**
11. **`aws_config/config.py`** - Configuration
12. **`aws_config/setup_lambda.py`** - Lambda invocations
13. **`Dockerfile`** - Containerization
14. **`.github/workflows/deploy.yml`** - CI/CD

---

## 🎯 **PRESENTATION PREPARATION CHECKLIST**

### **Before Presentation - Review These:**

- [ ] **Architecture Overview**
  - 3-tier architecture (Presentation → Application → Data)
  - AWS services used (9 services)
  - How components interact

- [ ] **Key Flows (Be able to explain verbally)**
  - User registration/login
  - Adding expense
  - Setting budget
  - Budget alert trigger
  - Email subscription
  - Report generation

- [ ] **Code Examples (Be ready to show)**
  - Show `app.py` route example
  - Show `lib/` library example
  - Show Lambda function example
  - Show DynamoDB operation example

- [ ] **AWS Services Integration**
  - How DynamoDB is used
  - How S3 is used
  - How SNS is used
  - How Lambda is used
  - How Elastic Beanstalk is used

- [ ] **Technical Decisions**
  - Why DynamoDB over RDS?
  - Why Lambda for alerts?
  - Why SNS for notifications?
  - Why Docker?
  - Why Elastic Beanstalk?

---

## 💡 **QUICK REFERENCE: File Purposes**

| File | Purpose | Key Function |
|------|---------|--------------|
| `app.py` | Main Flask app | All HTTP routes |
| `aws_config/setup_dynamodb.py` | Database | CRUD operations |
| `lib/expense_processor.py` | Expense logic | Validate & save expenses |
| `lib/budget_calculator.py` | Budget logic | Calculate totals, percentages |
| `lib/notification_manager.py` | Notifications | Send emails via SNS |
| `lib/receipt_handler.py` | Receipts | Upload to S3 |
| `lambda_functions/budget_alert/` | Daily alerts | Check budgets, send emails |
| `lambda_functions/report_generator/` | PDF reports | Generate reports |
| `aws_config/setup_s3.py` | File storage | Upload/download files |
| `aws_config/setup_sns.py` | Email service | Subscribe/publish |
| `aws_config/setup_lambda.py` | Lambda calls | Invoke functions |
| `Dockerfile` | Container | Package app |
| `.github/workflows/deploy.yml` | CI/CD | Auto deployment |

---

## ⏱️ **STUDY TIME ESTIMATE**

- **Phase 1 (Foundation):** 30 minutes
- **Phase 2 (Libraries):** 45 minutes
- **Phase 3 (Application):** 60 minutes
- **Phase 4 (Lambda):** 30 minutes
- **Phase 5 (Frontend):** 30 minutes
- **Phase 6 (Deployment):** 20 minutes
- **Review & Practice:** 30 minutes

**Total: ~4.5 hours** (adjust based on your pace)

---

## 🚀 **TIPS FOR PRESENTATION**

1. **Start with Architecture Diagram** - Show the big picture first
2. **Explain One Complete Flow** - Walk through adding an expense end-to-end
3. **Show Code Examples** - Have `app.py` and one library file ready
4. **Demonstrate Live** - If possible, show the app running
5. **Be Ready for Questions:**
   - "How does authentication work?" → Show session management in app.py
   - "How are budgets checked?" → Show budget_alert Lambda
   - "How are emails sent?" → Show notification_manager and SNS
   - "How is it deployed?" → Show Dockerfile and deploy.yml

---

## 📝 **COMMON QUESTIONS & ANSWERS**

**Q: How does user authentication work?**
A: User registers → Password hashed with Werkzeug → Stored in DynamoDB → Login validates password → Session created → Session checked on each request

**Q: How are budget alerts triggered?**
A: CloudWatch Events schedules Lambda daily → Lambda queries all budgets → Calculates spending → If exceeded → Publishes to SNS → SNS sends email

**Q: How are expenses stored?**
A: User submits expense → Validated by ExpenseProcessor → Saved to DynamoDB via DynamoDBClient → Retrieved by user_id index

**Q: How does receipt upload work?**
A: User selects file → Validated → Uploaded to S3 via S3Client → S3 key stored in expense record → Presigned URL generated for viewing

**Q: Why use Lambda for budget alerts?**
A: Serverless, pay-per-use, automatic scaling, no server management, scheduled execution

**Q: How is the app deployed?**
A: GitHub Actions → Builds Docker image → Pushes to ECR → Deploys to Elastic Beanstalk → Auto-scales based on traffic

---

**Good luck with your presentation! 🎉**

