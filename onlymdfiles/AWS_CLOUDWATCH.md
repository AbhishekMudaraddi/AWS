# AWS CloudWatch - Monitoring & Logging

## What is CloudWatch?

Amazon CloudWatch is a monitoring and observability service that collects metrics, logs, and events from AWS resources and applications.

## Why CloudWatch in This Project?

1. **Application Logs**: Collects logs from Flask application
2. **Lambda Logs**: Captures Lambda function execution logs
3. **Scheduled Events**: Triggers Lambda functions on schedule
4. **Monitoring**: Monitors application health and performance
5. **Alarms**: Can set up alerts for errors or performance issues

## How CloudWatch is Used in This Project

CloudWatch is used for:
- **Application Logging**: Flask app logs sent to CloudWatch Logs
- **Lambda Logging**: All Lambda functions log to CloudWatch
- **Scheduled Triggers**: CloudWatch Events triggers budget alert Lambda daily
- **EB Health Monitoring**: Elastic Beanstalk uses CloudWatch for health checks

## Implementation Files

### Primary Files:
1. **`app.py`** - Configures CloudWatch logging
2. **`lambda_functions/budget_alert/lambda_function.py`** - Triggered by CloudWatch Events
3. **`scripts/setup_cloudwatch_alarms.py`** - Sets up monitoring alarms (optional)

### Usage:
- **Application**: Logs sent automatically to CloudWatch Logs
- **Lambda**: Logs captured automatically
- **Scheduled Tasks**: CloudWatch Events triggers Lambda functions

## Code Structure

### 1. Application Logging (`app.py`)

```python
import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        RotatingFileHandler('app.log', maxBytes=10000000, backupCount=5),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

try:
    from aws_config.config import get_boto3_session
    boto3_session = get_boto3_session()
    logs_client = boto3_session.client('logs', region_name=os.getenv('AWS_REGION', 'us-east-1'))
    log_group_name = '/aws/elasticbeanstalk/smart-budget-planner-env/var/log/web.stdout.log'
    try:
        logs_client.create_log_group(logGroupName=log_group_name)
    except ClientError as e:
        if e.response['Error']['Code'] != 'ResourceAlreadyExistsException':
            logger.warning(f"Could not create CloudWatch log group: {str(e)}")
except Exception as e:
    logger.warning(f"CloudWatch logging not configured: {str(e)}")
```

**What it does**:
- Configures Python logging
- Logs to file (`app.log`) and console
- Attempts to create CloudWatch log group (EB handles this automatically)

**Log Levels**: INFO, WARNING, ERROR

**Used throughout**: All Python files use `logger.info()`, `logger.error()`, etc.

### 2. CloudWatch Events - Scheduled Trigger

**Purpose**: Triggers budget alert Lambda function daily.

**Configuration**: Set up in `scripts/deploy_lambda_functions.py`

```python
def setup_scheduled_trigger(function_name, schedule_expression='cron(0 2 * * ? *)'):
    events_client.put_rule(
        Name=f'{function_name}-schedule',
        ScheduleExpression=schedule_expression,
        State='ENABLED'
    )
    
    events_client.put_targets(
        Rule=f'{function_name}-schedule',
        Targets=[{
            'Id': '1',
            'Arn': function_arn
        }]
    )
```

**Schedule Expression**: `cron(0 2 * * ? *)` = Daily at 2:00 AM UTC

**What it does**: CloudWatch Events triggers Lambda function at scheduled time.

**Used for**: Budget alert Lambda function

### 3. Lambda Logging

**Automatic**: Lambda functions automatically log to CloudWatch Logs.

**Log Group**: `/aws/lambda/{function-name}`

**Example**:
```python
# In Lambda function
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info("Lambda function started")
    # ... processing ...
    logger.error("Error occurred: " + str(e))
```

**What it does**: All print statements and logger calls go to CloudWatch Logs.

**View Logs**: AWS Console → CloudWatch → Log Groups → `/aws/lambda/{function-name}`

## Log Groups

### Application Logs
- **Log Group**: `/aws/elasticbeanstalk/smart-budget-planner-env/var/log/web.stdout.log`
- **Source**: Flask application running on Elastic Beanstalk
- **Content**: Application logs, errors, warnings

### Lambda Logs
- **Expense Categorizer`: `/aws/lambda/expense-categorizer-function`
- **Budget Alert**: `/aws/lambda/budget-alert-function`
- **Report Generator**: `/aws/lambda/report-generator-function`

## How to Explain in Class

### When Asked: "Why use CloudWatch for logging?"

**Answer**:
- **Centralized**: All logs in one place (application, Lambda, EB)
- **Searchable**: Can search logs across all services
- **Retention**: Logs retained for configurable period (default 7 days)
- **Integration**: Works seamlessly with other AWS services
- **Monitoring**: Can set up alarms based on log patterns

### When Asked: "How does application logging work?"

**Answer**:
1. **Python Logging**: Application uses Python `logging` module
2. **Log Handlers**: Logs written to file and console
3. **EB Capture**: Elastic Beanstalk captures stdout/stderr
4. **CloudWatch**: EB automatically sends logs to CloudWatch Logs
5. **View Logs**: Can view in AWS Console or via AWS CLI

**Code Flow**:
```
app.py → logger.info("message")
  → stdout/stderr
    → Elastic Beanstalk captures
      → CloudWatch Logs
        → View in AWS Console
```

### When Asked: "How are scheduled tasks triggered?"

**Answer**:
1. **CloudWatch Events Rule** → Created with schedule expression
2. **Target**: Lambda function ARN
3. **Schedule**: Runs daily at specified time (e.g., 2 AM UTC)
4. **Trigger**: CloudWatch Events invokes Lambda function
5. **Execution**: Lambda function runs and processes budgets

**Code Flow**:
```
CloudWatch Events (scheduled)
  → Triggers Lambda function
    → lambda_functions/budget_alert/lambda_function.py
      → Processes budgets
        → Sends alerts via SNS
```

### When Asked: "Show me how to view logs"

**Answer**:
- **AWS Console**: CloudWatch → Log Groups → Select log group → View log streams
- **AWS CLI**: `aws logs tail /aws/lambda/expense-categorizer-function --follow`
- **EB Console**: Elastic Beanstalk → Environment → Logs → Request Logs

**Example Log Entry**:
```
2024-01-15 10:30:45 INFO app Expense added successfully: expense-123
```

### When Asked: "How do you debug Lambda function errors?"

**Answer**:
1. **View Logs**: CloudWatch Logs → Lambda function log group
2. **Check Errors**: Look for ERROR level logs
3. **Trace Execution**: Follow log entries to see execution flow
4. **Error Details**: Stack traces show exact error location

**Example**:
```
ERROR lambda_function Error processing expense: KeyError 'expense_id'
Traceback (most recent call last):
  File "/var/task/lambda_function.py", line 15, in lambda_handler
    expense_id = body.get('expense_id')
```

## Scheduled Events Configuration

### Budget Alert Schedule
- **Rule Name**: `budget-alert-function-schedule`
- **Schedule**: `cron(0 2 * * ? *)` (Daily at 2:00 AM UTC)
- **Target**: `budget-alert-function` Lambda
- **State**: ENABLED

### Schedule Expression Format
```
cron(minute hour day-of-month month day-of-week year)
```

**Examples**:
- `cron(0 2 * * ? *)` - Daily at 2 AM
- `cron(0 */6 * * ? *)` - Every 6 hours
- `cron(0 0 ? * MON *)` - Every Monday at midnight

## Key Concepts to Remember

1. **Log Group**: Container for log streams
2. **Log Stream**: Sequence of log events from same source
3. **CloudWatch Events**: Service for scheduling and event routing
4. **Rule**: Defines when and how to trigger targets
5. **Target**: Resource triggered by rule (Lambda function)
6. **Retention**: How long logs are kept (default 7 days, can extend)

## Common Questions & Answers

**Q: How much do CloudWatch Logs cost?**
A: First 5GB free per month, then $0.50 per GB ingested. Very cost-effective for this project.

**Q: How long are logs retained?**
A: Default 7 days. Can configure retention up to 10 years (costs more for longer retention).

**Q: Can you search logs?**
A: Yes, CloudWatch Logs Insights allows querying logs using SQL-like syntax.

**Q: How do you set up alerts based on logs?**
A: Create CloudWatch Alarm based on log metric filter. Can trigger SNS notification or other actions.

**Q: What happens if CloudWatch is down?**
A: Logs are buffered locally and sent when service is available. Very rare occurrence (99.99% availability).

**Q: How do you trigger Lambda on schedule?**
A: CloudWatch Events Rule with schedule expression. Rule targets Lambda function ARN.

