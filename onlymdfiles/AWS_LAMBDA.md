# AWS Lambda - Serverless Functions

## What is Lambda?

AWS Lambda is a serverless compute service that runs code in response to events without managing servers. You pay only for compute time used.

## Why Lambda in This Project?

1. **Budget Alerts**: Scheduled checks for budget thresholds
2. **Report Generation**: Generates PDF reports without blocking the main application
3. **Cost-Effective**: Pay only when functions run
4. **Scalable**: Automatically handles concurrent requests
5. **Serverless**: No server management required

## How Lambda is Used in This Project

Three Lambda functions:
1. **Budget Alert**: Scheduled daily check for budget thresholds
2. **Report Generator**: Generates PDF reports on-demand
3. **Notification Processor**: Processes SQS messages and sends email notifications via SNS

## Implementation Files

### Lambda Function Code:
1. **`lambda_functions/budget_alert/lambda_function.py`** - Checks budgets and sends alerts
2. **`lambda_functions/report_generator/lambda_function.py`** - Generates PDF reports
3. **`lambda_functions/notification_processor/lambda_function.py`** - Processes SQS messages and sends emails

### Integration Files:
1. **`aws_config/setup_lambda.py`** - Invokes Lambda functions from Flask app (SDK wrapper)
2. **`scripts/deploy_lambda_functions.py`** - Deploys Lambda functions to AWS

### Usage in Application:
- **`app.py`** - Invokes report generator Lambda
- **CloudWatch Events** - Triggers budget alert Lambda on schedule
- **SQS Queue** - Triggers notification processor Lambda when messages arrive

## Code Structure

### 1. Lambda Client (`aws_config/setup_lambda.py`)

**Purpose**: Provides interface to invoke Lambda functions from Flask application.

#### Invoking Report Generator
```python
def invoke_report_generator(self, user_id, report_type='monthly', start_date=None, end_date=None, year=None, month=None):
    function_name = self.function_names['report_generator']
    payload = {
        'user_id': user_id,
        'report_type': report_type,
        'start_date': start_date,
        'end_date': end_date
    }
    
    response = self.lambda_client.invoke(
        FunctionName=function_name,
        InvocationType='RequestResponse',  # Synchronous
        Payload=json.dumps(payload)
    )
    
    response_payload = json.loads(response['Payload'].read())
    return response_payload
```

**What it does**: Invokes report generator Lambda synchronously and waits for PDF generation.

**InvocationType**: `RequestResponse` = synchronous (waits for result)

**Used in**: `app.py` - `/api/reports` POST route

### 2. Budget Alert Lambda (`lambda_functions/budget_alert/lambda_function.py`)

**Trigger**: CloudWatch Events (scheduled daily)

**Purpose**: Checks all user budgets and sends alerts if threshold exceeded.

```python
def lambda_handler(event, context):
    budgets_response = budgets_table.scan()
    budgets = budgets_response.get('Items', [])
    
    for budget in budgets:
        user_id = budget.get('user_id')
        category = budget.get('category')
        budget_amount = Decimal(str(budget.get('amount', 0)))
        alert_threshold = Decimal(str(budget.get('alert_threshold', 80)))
        
        expenses = expenses_table.query(
            IndexName='user_id-index',
            KeyConditionExpression='user_id = :uid',
            FilterExpression='category = :cat',
            ExpressionAttributeValues={':uid': user_id, ':cat': category}
        )
        total_spent = sum(Decimal(str(e.get('amount', 0))) for e in expenses)
        
        percentage = (total_spent / budget_amount) * 100
        
        if percentage >= alert_threshold:
            user = users_table.get_item(Key={'user_id': user_id})
            user_email = user.get('Item', {}).get('email')
            
            if user_email:
                topic_arn = get_sns_topic_arn()
                if topic_arn and check_email_subscription(topic_arn, user_email):
                    remaining = budget_amount - total_spent
                    message = f"Budget Alert: You've spent {percentage:.1f}% of your {category} budget. Budget: ${budget_amount:.2f}, Spent: ${total_spent:.2f}, Remaining: ${remaining:.2f}"
                    subject = f"Budget Alert - {category}"
                    
                    if send_email_notification(topic_arn, user_email, subject, message):
                        notifications_table.put_item(Item={
                            'notification_id': str(uuid.uuid4()),
                            'user_id': user_id,
                            'type': 'budget_alert',
                            'message': message,
                            'status': 'sent',
                            'delivery_method': 'email',
                            'created_at': datetime.utcnow().isoformat()
                        })
```

**What it does**:
1. Scans all budgets in DynamoDB
2. Calculates spending percentage for each budget
3. If >= threshold (default 80%), sends email alert via SNS
4. Runs daily via CloudWatch Events schedule

**Used by**: CloudWatch Events triggers daily at scheduled time

### 3. Report Generator Lambda (`lambda_functions/report_generator/lambda_function.py`)

**Trigger**: Direct invocation from Flask app

**Purpose**: Generates comprehensive PDF reports with expense analysis.

```python
def lambda_handler(event, context):
    user_id = event['user_id']
    report_type = event.get('report_type', 'monthly')
    
    # Query expenses from DynamoDB
    expenses = expenses_table.query(...)
    budgets = budgets_table.query(...)
    
    # Generate PDF using ReportLab
    pdf_buffer = generate_pdf_report(expenses, budgets, report_type)
    
    # Upload PDF to S3
    report_key = f"reports/{user_id}/{report_name}.pdf"
    s3_client.put_object(
        Bucket=bucket_name,
        Key=report_key,
        Body=pdf_buffer.getvalue(),
        ContentType='application/pdf'
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'report_key': report_key,
            'report_url': presigned_url
        })
    }
```

**What it does**:
1. Receives report request (monthly/weekly/custom date range)
2. Queries expenses and budgets from DynamoDB
3. Generates PDF report with charts, statistics, insights
4. Uploads PDF to S3
5. Returns S3 key and presigned URL

**Used by**: `app.py` - `/api/reports` POST route

### 4. Notification Processor Lambda (`lambda_functions/notification_processor/lambda_function.py`)

**Trigger**: SQS Queue (when notification message arrives)

**Purpose**: Processes notification messages from SQS and sends emails via SNS.

```python
def lambda_handler(event, context):
    processed = 0
    failed = 0
    errors = []
    
    try:
        for record in event.get('Records', []):
            try:
                if 'body' in record:
                    body = json.loads(record['body'])
                else:
                    body = record
                
                result = process_notification(body)
                
                if result.get('success'):
                    processed += 1
                else:
                    failed += 1
                    errors.append({
                        'user_id': body.get('user_id'),
                        'reason': result.get('reason', 'unknown')
                    })
            except Exception as e:
                print(f"Error processing record: {str(e)}")
                failed += 1
                errors.append({'error': str(e)})
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'processed': processed,
                'failed': failed,
                'errors': errors
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

**What it does**:
1. Receives notification message from SQS queue
2. Extracts user email, message, and subject
3. Checks if email is subscribed and confirmed
4. Configures subscription filter for user-specific delivery
5. Publishes message to SNS topic with user_email attribute
6. Updates notification status in DynamoDB

**Used by**: SQS queue triggers this Lambda when notification is queued

## Lambda Function Details

### Budget Alert
- **Runtime**: Python 3.9
- **Trigger**: CloudWatch Events (daily schedule)
- **Timeout**: 60 seconds
- **Memory**: 256 MB
- **IAM Role**: `smart-budget-lambda-role`
- **Permissions**: DynamoDB read, SNS publish

### Report Generator
- **Runtime**: Python 3.9
- **Trigger**: Direct invocation (synchronous)
- **Timeout**: 300 seconds (5 minutes)
- **Memory**: 512 MB
- **IAM Role**: `smart-budget-lambda-role`
- **Permissions**: DynamoDB read, S3 write, S3 read

### Notification Processor
- **Runtime**: Python 3.9
- **Trigger**: SQS Queue (notification-queue)
- **Timeout**: 60 seconds
- **Memory**: 256 MB
- **IAM Role**: `smart-budget-lambda-role`
- **Permissions**: DynamoDB read/write, SNS publish, SQS receive/delete

## How to Explain in Class

### When Asked: "Why use Lambda instead of running code in Flask?"

**Answer**:
- **Separation of Concerns**: Heavy processing (PDF generation) doesn't block Flask app
- **Scalability**: Lambda scales automatically for concurrent report requests
- **Cost**: Pay only when generating reports, not for idle server time
- **Performance**: PDF generation in Lambda doesn't slow down main application
- **Reliability**: If Lambda fails, Flask app continues working

### When Asked: "How does notification processing work?"

**Answer**:
1. **Notification triggered** → Budget exceeded, large expense, etc.
2. **Message queued** → Notification details sent to SQS queue
3. **Lambda triggered** → SQS triggers notification processor Lambda
4. **Check subscription** → Lambda verifies email is subscribed and confirmed
5. **Configure filter** → Sets subscription filter for user-specific delivery
6. **Publish to SNS** → Lambda publishes message to SNS topic
7. **Email delivered** → SNS delivers email to user
8. **Update status** → Notification status updated in DynamoDB

**Code Flow**:
```
app.py → notification_manager._send_notification()
  → SQS Queue (notification-queue)
    → Lambda Trigger
      → lambda_functions/notification_processor/lambda_function.py
        → Check subscription
        → Publish to SNS
        → Update DynamoDB
```

### When Asked: "Show me how report generation works"

**Answer**:
1. **User requests report** → Frontend calls `/api/reports` POST
2. **Flask invokes Lambda** → `lambda_client.invoke_report_generator()`
3. **Lambda generates PDF** → Queries DynamoDB, creates PDF with ReportLab
4. **Upload to S3** → PDF uploaded to S3 bucket
5. **Return URL** → Presigned URL returned to Flask
6. **Frontend downloads** → User downloads PDF via presigned URL

**Code Flow**:
```
app.py (line 760)
  → lambda_client.invoke_report_generator()
    → Lambda Function (lambda_functions/report_generator/)
      → Query DynamoDB
      → Generate PDF
      → Upload to S3
      → Return S3 key
```

### When Asked: "How are budget alerts sent?"

**Answer**:
1. **Scheduled Trigger** → CloudWatch Events triggers Lambda daily
2. **Scan Budgets** → Lambda scans all budgets from DynamoDB
3. **Calculate Spending** → Queries expenses, calculates percentage spent
4. **Check Threshold** → If >= 80% threshold, sends alert
5. **Send Email** → Publishes message to SNS topic
6. **SNS Delivers** → SNS sends email to subscribed users

**Code Flow**:
```
CloudWatch Events (daily schedule)
  → lambda_functions/budget_alert/lambda_function.py
    → Query DynamoDB (budgets + expenses)
    → Calculate percentages
    → Publish to SNS
      → Email sent to users
```

## Key Concepts to Remember

1. **Serverless**: No server management, AWS handles infrastructure
2. **Event-Driven**: Functions triggered by events (SQS, CloudWatch, HTTP)
3. **Invocation Types**: 
   - `RequestResponse` = Synchronous (wait for result)
   - `Event` = Asynchronous (fire and forget)
4. **Cold Start**: First invocation may be slower (container initialization)
5. **Timeout**: Maximum execution time (5 minutes for report generator)
6. **IAM Role**: Lambda needs permissions to access other AWS services

## Common Questions & Answers

**Q: Why not generate PDFs in Flask directly?**
A: PDF generation is CPU-intensive and can take 30+ seconds. Running in Lambda prevents blocking Flask app and allows concurrent report generation.

**Q: What happens if Lambda function fails?**
A: Error is returned to Flask app, which shows error message to user. Lambda retries automatically for SQS-triggered functions.

**Q: How much does Lambda cost?**
A: First 1 million requests free per month, then $0.20 per million requests. Very cost-effective for this application.

**Q: Can Lambda access DynamoDB directly?**
A: Yes, Lambda uses IAM role (`smart-budget-lambda-role`) with DynamoDB permissions to read/write data.

**Q: How do you deploy Lambda functions?**
A: Using `scripts/deploy_lambda_functions.py` which packages code and deploys via boto3 SDK.
