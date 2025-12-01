# AWS SQS - Message Queue Service

## What is SQS?

Amazon SQS (Simple Queue Service) is a fully managed message queuing service that enables decoupling and asynchronous processing of application components.

## Why SQS in This Project?

1. **Asynchronous Processing**: Decouples notification processing from main application
2. **Reliability**: Messages are stored durably until processed
3. **Scalability**: Handles variable workloads automatically
4. **Fault Tolerance**: If processing fails, message remains in queue for retry
5. **Decoupling**: Flask app doesn't wait for notification processing to complete

## How SQS is Used in This Project

SQS queues notification messages for asynchronous email delivery:
- **Notification Queue**: Receives notification data from the Flask application
- **Lambda Processing**: Notification Processor Lambda function processes messages from the queue
- **Email Delivery**: Lambda sends emails via SNS after processing queued messages

**Flow**: Flask App → SQS Queue → Lambda Function → SNS → Email

## Implementation Files

### Primary Files:
1. **`aws_config/setup_sqs.py`** - Main SQS client class (SDK wrapper)
2. **`lib/notification_manager.py`** - Queues notifications to SQS
3. **`lambda_functions/notification_processor/lambda_function.py`** - Processes SQS messages and sends emails
4. **`aws_config/resource_manager.py`** - Creates SQS queues

### Usage in Application:
- **`lib/notification_manager.py`** - Queues notification messages to SQS when sending alerts
- **`lambda_functions/notification_processor/`** - Lambda function triggered by SQS to process and send emails

## Code Structure

### 1. Configuration (`aws_config/config.py`)

```python
SQS_QUEUES = {
    'notification': 'notification-queue'
}
```

**Explanation**: Queue names used for message queuing.

### 2. SQS Client (`aws_config/setup_sqs.py`)

**Key Methods:**

#### Sending Notification Message
```python
def send_notification_message(self, notification_data):
    if not self.notification_queue_url:
        self._initialize_queue_urls()
    
    message_body = json.dumps(notification_data, default=str)
    response = self.sqs.send_message(
        QueueUrl=self.notification_queue_url,
        MessageBody=message_body
    )
    return response['MessageId']
```

**What it does**: Sends notification data as JSON message to SQS queue.

**Message Format**:
```json
{
    "user_id": "uuid",
    "user_email": "user@example.com",
    "notification_type": "budget_exceeded",
    "message": "Budget exceeded for Food category",
    "subject": "Budget Exceeded - Food",
    "notification_id": "uuid",
    "timestamp": "2024-01-15T10:30:00"
}
```

**Used in**: `lib/notification_manager.py` - Queues notification messages for asynchronous email delivery

#### Receiving Messages
```python
def receive_messages(self, queue_name='notification', max_messages=10, wait_time=20):
    queue_url = self.notification_queue_url
    
    response = self.sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=max_messages,
        WaitTimeSeconds=wait_time
    )
    
    messages = response.get('Messages', [])
    result = []
    for msg in messages:
        body = json.loads(msg['Body'])
        result.append({
            'ReceiptHandle': msg['ReceiptHandle'],
            'Body': body,
            'MessageId': msg['MessageId']
        })
    return result
```

**What it does**: Receives messages from notification queue.

**Parameters**:
- `max_messages`: Maximum messages to receive (1-10)
- `wait_time`: Long polling wait time (up to 20 seconds)

**Used in**: Lambda function receives messages automatically via SQS trigger

#### Deleting Message
```python
def delete_message(self, receipt_handle, queue_name='notification'):
    self.sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
    )
    return True
```

**What it does**: Deletes message from queue after successful processing.

**Why Important**: Prevents message from being processed again.

## Message Flow

```
User Action (Budget Exceeded, Large Expense, etc.)
    ↓
Flask App (app.py)
    ↓
NotificationManager._send_notification()
    ↓
SQS Queue (notification-queue)
    ↓
Lambda Trigger (automatic)
    ↓
Notification Processor Lambda
    ├─→ Check email subscription
    ├─→ Send email via SNS
    └─→ Update notification status in DynamoDB
    ↓
Email Delivered to User
```

## Queue Configuration

### Notification Queue
- **Name**: `notification-queue`
- **Type**: Standard Queue
- **Status**: Active and in use
- **Purpose**: Asynchronous notification processing for email delivery
- **Lambda Trigger**: Yes (notification-processor-function)
- **Batch Size**: 10 messages per Lambda invocation
- **Visibility Timeout**: 30 seconds

## Key Concepts to Remember

1. **Message**: Data sent to queue (JSON format)
2. **Visibility Timeout**: Time message is invisible after being received
3. **ReceiptHandle**: Token needed to delete message
4. **Long Polling**: Wait up to 20 seconds for messages (reduces API calls)
5. **Dead Letter Queue**: Queue for failed messages after max retries
6. **Event Source Mapping**: SQS → Lambda automatic trigger configuration

## Common Questions & Answers

**Q: How does SQS work with notifications?**
A: When the Flask application needs to send an email notification, it queues a message to SQS instead of sending directly. The Notification Processor Lambda function is automatically triggered by SQS, processes the message, and sends the email via SNS. This decouples notification queuing from email delivery, improving reliability and scalability.

**Q: What if the same message is processed twice?**
A: SQS provides at-least-once delivery. Application should be idempotent (safe to process same message multiple times).

**Q: How do you ensure messages aren't lost?**
A: SQS stores messages durably. Messages persist until explicitly deleted or retention period expires (14 days).

**Q: How much does SQS cost?**
A: First 1 million requests free per month, then $0.40 per million requests. Very cost-effective for this application.
