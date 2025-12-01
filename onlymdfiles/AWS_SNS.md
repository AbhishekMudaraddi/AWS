# AWS SNS - Notification Service

## What is SNS?

Amazon SNS (Simple Notification Service) is a fully managed messaging service for sending notifications to multiple subscribers via email, SMS, or other protocols.

## Why SNS in This Project?

1. **Email Notifications**: Send budget alerts and summaries via email
2. **Scalable**: Handles unlimited subscribers
3. **Reliable**: Managed service with high availability
4. **Cost-Effective**: Pay only for messages sent
5. **Easy Integration**: Simple API for publishing messages

## How SNS is Used in This Project

SNS sends email notifications for:
- **Budget Exceeded Alerts**: When user exceeds budget threshold (100%)
- **Budget Threshold Warnings**: When user reaches 80% of budget
- **Large Expense Alerts**: When expense exceeds $100 or 10% of category budget
- **Weekly Summaries**: Weekly expense summaries (methods implemented, require scheduled triggers)
- **Monthly Summaries**: Monthly expense summaries (methods implemented, require scheduled triggers)

## Implementation Files

### Primary Files:
1. **`aws_config/setup_sns.py`** - Main SNS client class (SDK wrapper)
2. **`lib/notification_manager.py`** - Business logic for notifications
3. **`lambda_functions/budget_alert/lambda_function.py`** - Scheduled budget alerts via SNS
4. **`aws_config/resource_manager.py`** - Creates SNS topic

### Usage in Application:
- **`app.py`** - Subscribes users to SNS topic
- **`lib/notification_manager.py`** - Sends notifications via SNS
- **Lambda Function** - Publishes budget alerts to SNS

## Code Structure

### 1. Configuration (`aws_config/config.py`)

```python
SNS_TOPIC = 'budget-alerts-topic'
```

**Explanation**: SNS topic name used for all notifications.

### 2. SNS Client (`aws_config/setup_sns.py`)

**Key Methods:**

#### Subscribing Email
```python
def subscribe_email(self, email):
    if not self.topic_arn:
        self._initialize_topic_arn()
    
    existing_subs = self.list_subscriptions()
    for sub in existing_subs:
        if sub.get('Protocol') == 'email' and sub.get('Endpoint').lower() == email.lower():
            if sub.get('SubscriptionArn') not in ['PendingConfirmation', 'Pending', '']:
                return sub.get('SubscriptionArn')
    
    response = self.sns.subscribe(
        TopicArn=self.topic_arn,
        Protocol='email',
        Endpoint=email
    )
    
    subscription_arn = response.get('SubscriptionArn', '')
    if subscription_arn == 'PendingConfirmation':
        return "Subscription created. Check your email for confirmation."
    return subscription_arn
```

**What it does**: 
- Subscribes email address to SNS topic
- AWS SNS sends confirmation email to user
- User must click confirmation link to activate subscription
- Returns subscription ARN or pending confirmation message

**Used in**: `app.py` - `/api/notifications/subscribe` route

#### Publishing Message
```python
def publish_message(self, subject, message, attributes=None):
    if not self.topic_arn:
        self._initialize_topic_arn()
    
    message_attributes = {}
    if attributes:
        for key, value in attributes.items():
            message_attributes[key] = {
                'DataType': 'String',
                'StringValue': str(value)
            }
    
    response = self.sns.publish(
        TopicArn=self.topic_arn,
        Subject=subject,
        Message=message,
        MessageAttributes=message_attributes
    )
    return response['MessageId']
```

**What it does**: Publishes message to SNS topic with optional MessageAttributes for filtering.

**MessageAttributes**: Used for subscription filter policies to enable user-specific delivery.

**Used in**: 
- `lib/notification_manager.py` - Direct publishing for subscription confirmations
- `lambda_functions/notification_processor/lambda_function.py` - Publishes notifications with user_email attribute
- `lambda_functions/budget_alert/lambda_function.py` - Publishes budget alerts with user_email attribute

**Note**: The `send_budget_alert` method in SNSClient is not directly used. Budget alerts are sent via the notification_processor Lambda function which handles user-specific filtering.

### 3. Notification Manager (`lib/notification_manager.py`)

**Purpose**: Business logic for when and how to send notifications.

#### Sending Budget Exceeded Alert
```python
def send_budget_exceeded_alert(self, user_id, user_email, category, budget_amount, spent_amount):
    overspend = spent_amount - budget_amount
    message = f"⚠️ Budget Exceeded: You've overspent your {category} budget by ${overspend:.2f}."
    subject = f"Budget Exceeded - {category}"
    return self._send_notification(user_id, user_email, message, subject, 'budget_exceeded')
```

**What it does**: Queues budget exceeded alert to SQS for asynchronous processing.

**Flow**:
1. Records notification in DynamoDB (status: 'queued')
2. Queues message to SQS with notification data
3. SQS triggers notification_processor Lambda
4. Lambda sends email via SNS with user-specific filtering

**Triggered**: When user adds expense that exceeds budget

**Used in**: `app.py` - After expense is added

#### Sending Large Expense Alert
```python
def send_large_expense_alert(self, user_id, user_email, expense_data, category_budget=None):
    amount = float(expense_data.get('amount', 0))
    threshold_amount = 100
    threshold_percentage = 10
    
    should_alert = False
    if amount >= threshold_amount:
        should_alert = True
    
    if category_budget and float(category_budget) > 0:
        percentage = (amount / float(category_budget)) * 100
        if percentage >= threshold_percentage:
            should_alert = True
    
    if should_alert:
        message = f"Large Expense Alert: ${amount:.2f} expense recorded..."
        return self._send_notification(user_id, user_email, message, subject, 'large_expense')
    return False
```

**What it does**: Queues large expense alert if expense exceeds $100 or 10% of category budget.

**Flow**: Same as budget exceeded alert - queues to SQS, processed by Lambda, sent via SNS.

**Used in**: `app.py` - After expense is added

## Notification Flow

```
User Action (Add Expense, Budget Exceeded, etc.)
    ↓
NotificationManager.send_budget_exceeded_alert()
    ↓
NotificationManager._send_notification()
    ├─→ Records notification in DynamoDB (status: 'queued')
    └─→ Queues message to SQS (notification-queue)
        ↓
SQS Triggers Lambda (notification-processor-function)
    ↓
Lambda: process_notification()
    ├─→ get_sns_topic_arn()
    ├─→ check_email_subscription()
    ├─→ get_user_subscription_arn()
    ├─→ configure_subscription_filter() (user_email filter)
    ├─→ send_email_notification() (publishes with MessageAttributes)
    └─→ update_notification_status() (status: 'sent')
        ↓
SNS Topic (budget-alerts-topic)
    ↓
Subscription Filter Policy (evaluates user_email attribute)
    ↓
Email delivered only to matching user's subscription
```

## Subscription Flow

```
User Registers/Subscribes
    ↓
app.py → /api/notifications/subscribe
    ↓
SNSClient.subscribe_email()
    ↓
AWS SNS Creates Subscription
    ↓
AWS SNS Sends Confirmation Email
    ↓
User Clicks Confirmation Link
    ↓
Subscription Confirmed
    ↓
User Receives Notifications
```

## How to Explain in Class

### When Asked: "Why use SNS instead of sending emails directly?"

**Answer**:
- **Scalability**: Handles unlimited subscribers without managing email servers
- **Reliability**: AWS manages email delivery infrastructure
- **Compliance**: Handles email bounces, unsubscribes automatically
- **Cost**: Pay only for messages sent ($0.06 per 1000 emails)
- **No Server Management**: No need to manage SMTP servers or email infrastructure

### When Asked: "How does email subscription work?"

**Answer**:
1. **User subscribes** → Frontend calls `/api/notifications/subscribe` with email
2. **SNS subscribe** → `SNSClient.subscribe_email()` creates subscription
3. **Confirmation email** → AWS SNS automatically sends confirmation email
4. **User confirms** → User clicks link in email to confirm subscription
5. **Active subscription** → User now receives notifications

**Important**: User MUST confirm subscription via email link before receiving notifications.

**Code Flow**:
```
app.py (line 698)
  → notification_manager.sns.subscribe_email(email)
    → SNS API subscribe()
      → AWS SNS sends confirmation email
        → User clicks link
          → Subscription confirmed
```

### When Asked: "Show me how budget alerts are sent"

**Answer**:
1. **Expense added** → User adds expense that exceeds budget
2. **Check budget** → `budget_calculator.check_budget_exceeded()` checks if exceeded
3. **Send alert** → `notification_manager.send_budget_exceeded_alert()` called
4. **Queue to SQS** → Notification message queued to SQS for asynchronous processing
5. **Lambda triggered** → `notification-processor-function` Lambda processes message
6. **Verify subscription** → Lambda checks if user email is confirmed subscriber
7. **Publish to SNS** → Lambda publishes message to SNS topic
8. **Email delivered** → SNS delivers email to user

**Code Flow**:
```
app.py
  → budget_calculator.check_budget_exceeded()
  → notification_manager.send_budget_exceeded_alert()
    → notification_manager._send_notification()
      ├─→ db.add_notification() (status: 'queued')
      └─→ sqs_client.send_notification_message()
          → SQS Queue (notification-queue)
            → Lambda Trigger (notification-processor-function)
              → process_notification()
                ├─→ get_sns_topic_arn()
                ├─→ check_email_subscription()
                ├─→ get_user_subscription_arn()
                ├─→ configure_subscription_filter() (user_email)
                ├─→ send_email_notification() (publishes with MessageAttributes)
                └─→ update_notification_status() (status: 'sent')
                  → SNS Topic (with filter policy)
                    → Email delivered only to that user
```

### When Asked: "What happens if user doesn't confirm subscription?"

**Answer**:
- **Subscription Status**: Remains "PendingConfirmation"
- **Notifications**: Will NOT be sent to unconfirmed emails
- **Code Check**: `send_budget_alert()` checks if subscription is confirmed before sending
- **User Action**: User must check email and click confirmation link

**Code**:
```python
# In sns_client.py
email_confirmed = False
for sub in subscriptions:
    if sub.get('SubscriptionArn') not in ['PendingConfirmation', 'Pending', '']:
        email_confirmed = True  # Only send if confirmed
```

### When Asked: "How are scheduled budget alerts sent?"

**Answer**:
1. **CloudWatch Events** → Triggers budget alert Lambda daily
2. **Lambda scans budgets** → Queries all budgets from DynamoDB
3. **Calculate spending** → Calculates percentage spent for each budget
4. **Check threshold** → If >= 80%, gets user email and checks subscription
5. **User-specific delivery** → Configures subscription filter for that user's email
6. **Publish to SNS** → Publishes message with user_email MessageAttribute
7. **SNS filter policy** → Only that user's subscription receives the email

**Code Flow**:
```
CloudWatch Events (daily)
  → lambda_functions/budget_alert/lambda_function.py
    → budgets_table.scan()
    → For each budget:
      → expenses_table.query() (filtered by category)
      → Calculate percentage
      → If >= threshold:
        → users_table.get_item() (get user email)
        → get_sns_topic_arn()
        → check_email_subscription()
        → get_user_subscription_arn()
        → configure_subscription_filter() (user_email filter)
        → send_email_notification() (publishes with MessageAttributes)
          → SNS Topic (with filter policy)
            → Email delivered only to that user
```

## Topic Structure

### Budget Alerts Topic
- **Name**: `budget-alerts-topic`
- **Type**: Standard Topic
- **Subscribers**: Email addresses (confirmed)
- **Messages**: Budget alerts, large expense alerts, summaries

## Key Concepts to Remember

1. **Topic**: Central messaging channel for notifications
2. **Subscription**: User's email/phone subscribed to topic
3. **Confirmation**: Email subscriptions require confirmation via email link
4. **Publish**: Sending message to topic (delivers to all subscribers)
5. **Subscription ARN**: Unique identifier for subscription
6. **PendingConfirmation**: Status before user confirms subscription

## Common Questions & Answers

**Q: Why do users need to confirm email subscription?**
A: Prevents spam and ensures user actually wants notifications. AWS SNS requires confirmation for email subscriptions.

**Q: What happens if email bounces?**
A: AWS SNS handles bounces automatically. After multiple bounces, subscription may be disabled.

**Q: Can users unsubscribe?**
A: Yes, AWS SNS provides unsubscribe link in emails. Users can also unsubscribe via AWS Console.

**Q: How much does SNS cost?**
A: First 100,000 requests free per month, then $0.50 per 100,000 requests. Very cost-effective.

**Q: Why check if subscription is confirmed before sending?**
A: SNS won't deliver to unconfirmed subscriptions. Checking prevents unnecessary API calls and ensures users receive notifications.

**Q: How do you ensure user-specific notifications?**
A: Each notification is published with a `user_email` MessageAttribute. The subscription filter policy is configured per subscription to only receive messages matching that user's email. This ensures only the intended user receives the notification.

**Q: How does subscription filtering work?**
A: When a notification is sent, the Lambda function:
1. Gets the user's specific subscription ARN
2. Configures a filter policy: `{'user_email': [user_email]}`
3. Publishes message with `user_email` in MessageAttributes
4. SNS evaluates the filter and only delivers to matching subscriptions

