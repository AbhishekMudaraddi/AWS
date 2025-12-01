# Quick Reference Cheat Sheet

## 🚀 AWS Services - One Line Explanation

| Service | Purpose | Key File |
|---------|---------|----------|
| **DynamoDB** | Store users, expenses, budgets, notifications | `aws_config/setup_dynamodb.py` |
| **S3** | Store receipt images and PDF reports | `aws_config/setup_s3.py` |
| **SNS** | Send email notifications to users | `aws_config/setup_sns.py` |
| **SQS** | Queue notification messages | `aws_config/setup_sqs.py` |
| **Lambda** | Run background tasks (reports, alerts) | `aws_config/setup_lambda.py` |

---

## 📍 Where Functions Are Called From

### DynamoDB Functions
- `db.get_user_by_id()` → Called in: `app.py` lines 72, 95, 207, 265
- `db.add_expense()` → Called in: `expense_processor.py` line 31
- `db.get_user_budgets()` → Called in: `budget_calculator.py` lines 10, 47, 82, 115, 125
- `db.add_budget()` → Called in: `app.py` line 539

### S3 Functions
- `s3.upload_receipt()` → Called in: `receipt_handler.py` line 44
- `s3.list_user_reports()` → Called in: `app.py` line 839

### SNS Functions
- `sns.subscribe_email()` → Called in: `app.py` line 708
- `sns.publish_message()` → Called in: `notification_manager.py` line 180

### SQS Functions
- `sqs.send_notification_message()` → Called in: `notification_manager.py` line 152

### Lambda Functions
- `lambda_client.invoke_report_generator()` → Called in: `app.py` line 791

---

## 🔄 Common Flows

### Adding Expense
```
POST /api/expenses
→ expense_processor.add_expense()
→ db.add_expense() [DynamoDB]
→ budget_calculator.check_budget_exceeded()
→ notification_manager.send_budget_exceeded_alert()
→ sqs.send_notification_message() [SQS]
→ Lambda processes → SNS sends email
```

### Upload Receipt
```
POST /api/receipts/upload
→ receipt_handler.upload_receipt()
→ s3.upload_receipt() [S3]
→ db.update_expense() [DynamoDB]
```

### Generate Report
```
POST /api/reports/generate
→ lambda_client.invoke_report_generator()
→ Lambda reads DynamoDB
→ Generates PDF
→ Uploads to S3
→ Returns URL
```

---

## 📂 File Structure

```
app.py                    → Main Flask application
aws_config/
  ├── config.py          → AWS resource names/config
  ├── setup_dynamodb.py  → DynamoDB operations
  ├── setup_s3.py        → S3 operations
  ├── setup_sns.py       → SNS operations
  ├── setup_sqs.py       → SQS operations
  └── setup_lambda.py    → Lambda invocation
lib/
  ├── budget_calculator.py      → Budget calculations
  ├── expense_processor.py      → Expense operations
  ├── notification_manager.py   → Notification logic
  └── receipt_handler.py        → Receipt file handling
lambda_functions/
  ├── budget_alert/              → Daily budget check
  ├── notification_processor/    → Process SQS messages
  └── report_generator/         → Generate PDF reports
```

---

## 🎯 Key Routes in app.py

| Route | Method | Purpose | Line |
|-------|--------|---------|------|
| `/api/expenses` | GET | Get user expenses | 338 |
| `/api/expenses` | POST | Add expense | 371 |
| `/api/budget` | GET | Get budgets | 481 |
| `/api/budget` | POST | Add budget | 508 |
| `/api/receipts/upload` | POST | Upload receipt | 591 |
| `/api/reports/generate` | POST | Generate report | 771 |
| `/api/notifications/subscribe` | POST | Subscribe to alerts | 678 |

---

## 💡 Quick Answers to Common Questions

**Q: Where is DynamoDB initialized?**
A: `app.py` line 47: `db = DynamoDBClient()`

**Q: How are notifications sent?**
A: App → SQS → Lambda → SNS → Email

**Q: Where are receipts stored?**
A: S3 bucket `smart-budget-receipts` at path `receipts/{user_id}/{expense_id}.{ext}`

**Q: What triggers budget alerts?**
A: Scheduled Lambda function (daily) checks all budgets

**Q: How does SQS trigger Lambda?**
A: SQS is configured as event source - automatically invokes Lambda when message arrives

**Q: Where is SNS topic created?**
A: Auto-created in `SNSClient._initialize_topic_arn()` if it doesn't exist

---

## 🔑 Important Classes

| Class | File | Purpose |
|-------|------|---------|
| `DynamoDBClient` | `setup_dynamodb.py` | All database operations |
| `S3Client` | `setup_s3.py` | File storage operations |
| `SNSClient` | `setup_sns.py` | Email notifications |
| `SQSClient` | `setup_sqs.py` | Message queue |
| `LambdaClient` | `setup_lambda.py` | Invoke Lambda functions |
| `BudgetCalculator` | `budget_calculator.py` | Budget calculations |
| `ExpenseProcessor` | `expense_processor.py` | Expense operations |
| `NotificationManager` | `notification_manager.py` | Notification handling |
| `ReceiptHandler` | `receipt_handler.py` | Receipt file handling |

---

## 📊 Data Flow Diagram

```
User Request
    ↓
Flask App (app.py)
    ↓
Business Logic (lib/)
    ↓
AWS Client (aws_config/)
    ↓
AWS Service (DynamoDB/S3/SNS/SQS/Lambda)
    ↓
Response to User
```

---

## 🎓 Study Tips

1. **Start with app.py** - This is where everything connects
2. **Follow the imports** - See where classes are imported from
3. **Trace function calls** - Use the call chains in the main guide
4. **Understand AWS services** - Know what each service does
5. **Practice explaining flows** - Be able to explain how data moves through the system

---

**Remember**: All AWS operations use boto3, initialized via `get_boto3_session()` in `config.py`

