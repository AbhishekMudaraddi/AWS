# Complete Library Functions Explanation Guide

## 📋 Table of Contents
1. [Overview](#overview)
2. [BudgetCalculator Class](#budgetcalculator-class)
3. [ExpenseProcessor Class](#expenseprocessor-class)
4. [NotificationManager Class](#notificationmanager-class)
5. [ReceiptHandler Class](#receipthandler-class)
6. [Function Call Summary](#function-call-summary)

---

## 🎯 Overview

The `lib/` directory contains **4 custom classes** that handle core business logic for the Smart Budget Planner application. These classes act as a **middle layer** between the Flask routes (`app.py`) and AWS services, providing:

- **Validation** - Data validation before saving
- **Business Logic** - Calculations and processing
- **Abstraction** - Clean interface to AWS services
- **Error Handling** - Consistent error management

**All classes are initialized in `app.py` (lines 50-53):**
```python
expense_processor = ExpenseProcessor()
budget_calculator = BudgetCalculator()
notification_manager = NotificationManager()
receipt_handler = ReceiptHandler()
```

---

## 💰 BudgetCalculator Class

**File**: `lib/budget_calculator.py`  
**Purpose**: Handles all budget-related calculations and checks

### Class Initialization
```python
def __init__(self):
    self.db = DynamoDBClient()
```
- Creates a DynamoDB client to access budget and expense data
- Used throughout all methods to query database

---

### 1. `calculate_totals(user_id)`

**Purpose**: Calculate total budget, total expenses, and remaining amount for a user

**What it does**:
- Fetches all budgets for the user from DynamoDB
- Fetches all expenses for the user from DynamoDB
- Sums up all budget amounts
- Sums up all expense amounts
- Calculates remaining = total_budget - total_expenses
- Returns dictionary with all three values

**Parameters**:
- `user_id` (str): The user's unique identifier

**Returns**:
```python
{
    'total_budget': float,
    'total_expenses': float,
    'remaining': float
}
```

**Where it's called**: 
- Currently **NOT directly called** in app.py, but available for future use
- Could be used in dashboard summary or reports

**Why it's used**:
- Provides quick overview of user's financial status
- Used for displaying summary information
- Helps users understand their overall budget situation

---

### 2. `calculate_remaining(budget_amount, expenses_amount)`

**Purpose**: Calculate remaining budget for a specific category

**What it does**:
- Takes budget amount and expenses amount as input
- Converts both to Decimal for precision
- Calculates: remaining = budget_amount - expenses_amount
- Returns as float

**Parameters**:
- `budget_amount` (float/Decimal): The budget limit
- `expenses_amount` (float/Decimal): Total expenses

**Returns**: `float` - Remaining budget amount

**Where it's called**: 
- Currently **NOT directly called** in app.py
- Available as utility function for calculations

**Why it's used**:
- Simple utility function for budget calculations
- Ensures consistent decimal handling
- Can be reused across different parts of the application

---

### 3. `calculate_percentage(spent, budget)`

**Purpose**: Calculate what percentage of budget has been spent

**What it does**:
- Takes spent amount and budget amount
- Handles division by zero (returns 0.0 if budget is 0)
- Calculates: (spent / budget) * 100
- Returns percentage as float

**Parameters**:
- `spent` (float/Decimal): Amount already spent
- `budget` (float/Decimal): Total budget amount

**Returns**: `float` - Percentage (0-100+)

**Where it's called**: 
- Used internally in `check_budget_threshold()` (line 63)
- Used internally in `get_budget_summary()` (line 140)
- Not directly called from app.py

**Why it's used**:
- Essential for determining if user is approaching budget limit
- Used to trigger alerts when percentage exceeds threshold
- Provides percentage display in UI

---

### 4. `check_budget_threshold(user_id, threshold_percentage=80)`

**Purpose**: Check if any budgets have exceeded the alert threshold percentage

**What it does**:
1. Fetches all budgets and expenses for user
2. Groups expenses by category
3. For each budget category:
   - Calculates total spent in that category
   - Calculates percentage spent
   - Compares against alert_threshold (default 80%)
4. Returns list of budgets that exceeded threshold

**Parameters**:
- `user_id` (str): User identifier
- `threshold_percentage` (int, optional): Default 80%

**Returns**: 
```python
[
    {
        'budget_id': str,
        'category': str,
        'budget_amount': float,
        'spent': float,
        'remaining': float,
        'percentage': float,
        'alert_threshold': float
    },
    ...
]
```

**Where it's called**: 
- Currently **NOT directly called** in app.py
- Available for scheduled checks or manual triggers
- Could be used by budget alert Lambda function

**Why it's used**:
- Proactive alerting before budget is fully exceeded
- Allows users to adjust spending before going over budget
- Can be scheduled to run daily/weekly

---

### 5. `check_budget_exceeded(user_id, category=None)`

**Purpose**: Check if user has exceeded any budget limits

**What it does**:
1. Fetches all budgets and expenses for user
2. Groups expenses by category
3. For each budget:
   - If `category` parameter provided, only checks that category
   - Compares spent amount vs budget amount
   - If spent > budget, adds to exceeded list
4. Returns list of exceeded budgets with overspend amount

**Parameters**:
- `user_id` (str): User identifier
- `category` (str, optional): Specific category to check, or None for all

**Returns**:
```python
[
    {
        'budget_id': str,
        'category': str,
        'budget_amount': float,
        'spent': float,
        'overspend': float  # How much over budget
    },
    ...
]
```

**Where it's called**: 
- **`app.py` line 416** - When user adds a new expense
```python
exceeded_budgets = budget_calculator.check_budget_exceeded(user['user_id'], category)
```

**Why it's used**:
- **Immediate alerting** when expense causes budget to be exceeded
- Called right after adding expense to check if budget is now over
- Triggers notification to user about overspending
- Critical for real-time budget monitoring

**Flow**:
```
User adds expense → Expense saved to DB → check_budget_exceeded() called
→ If exceeded → Notification sent to user
```

---

### 6. `get_category_budget(user_id, category)`

**Purpose**: Get the budget amount for a specific category

**What it does**:
1. Fetches all budgets for user
2. Searches for budget matching the category
3. Returns budget amount as float
4. Returns 0.0 if no budget found for category

**Parameters**:
- `user_id` (str): User identifier
- `category` (str): Category name to look up

**Returns**: `float` - Budget amount (0.0 if not found)

**Where it's called**: 
- **`app.py` line 436** - When checking for large expense alerts
```python
category_budget = budget_calculator.get_category_budget(user['user_id'], category)
```

**Why it's used**:
- Needed to determine if an expense is "large" relative to budget
- Used in large expense alert logic
- Provides context for expense notifications
- Helps determine if expense is significant percentage of budget

**Flow**:
```
User adds expense → get_category_budget() called → Compare expense to budget
→ If expense is large percentage → Send alert
```

---

### 7. `get_budget_summary(user_id)`

**Purpose**: Get complete budget summary with spending details for all categories

**What it does**:
1. Fetches all budgets and expenses for user
2. Groups expenses by category
3. For each budget category:
   - Calculates total spent
   - Calculates remaining budget
   - Calculates percentage used
4. Returns comprehensive summary list

**Parameters**:
- `user_id` (str): User identifier

**Returns**:
```python
[
    {
        'budget_id': str,
        'category': str,
        'budget': float,
        'spent': float,
        'remaining': float,
        'percentage': float
    },
    ...
]
```

**Where it's called**: 
- **`app.py` line 585** - In `/api/summary` GET endpoint
```python
summary = budget_calculator.get_budget_summary(user['user_id'])
```

**Why it's used**:
- **Dashboard display** - Shows user their budget status
- Provides complete overview of all categories
- Used by frontend to display charts and progress bars
- Essential for budget management UI

**Flow**:
```
User views dashboard → Frontend calls /api/summary → get_budget_summary() called
→ Returns all budget data → Displayed in UI
```

---

## 📝 ExpenseProcessor Class

**File**: `lib/expense_processor.py`  
**Purpose**: Handles all expense-related operations including validation and database operations

### Class Initialization
```python
def __init__(self):
    self.db = DynamoDBClient()
```
- Creates DynamoDB client for expense operations
- Provides logging capability

---

### 1. `validate_expense(amount, category, description='')`

**Purpose**: Validate expense data before saving to database

**What it does**:
- Checks if amount is provided and greater than 0
- Checks if category is provided and not empty
- Checks if description is within 500 character limit
- Returns validation result and list of errors

**Parameters**:
- `amount` (float): Expense amount
- `category` (str): Expense category
- `description` (str, optional): Expense description

**Returns**: 
```python
(is_valid: bool, errors: list)
```

**Where it's called**: 
- **Internally** in `add_expense()` method (line 27)
- Not called directly from app.py

**Why it's used**:
- **Data integrity** - Ensures only valid expenses are saved
- Prevents invalid data from reaching database
- Provides clear error messages to users
- First line of defense against bad data

**Validation Rules**:
1. Amount must be > 0
2. Category is required (non-empty)
3. Description max 500 characters

---

### 2. `add_expense(user_id, amount, category, description='', receipt_url='')`

**Purpose**: Add a new expense record to the database

**What it does**:
1. Validates expense data using `validate_expense()`
2. If validation fails, raises ValueError with error messages
3. If valid, calls `db.add_expense()` to save to DynamoDB
4. Returns the created expense data

**Parameters**:
- `user_id` (str): User who owns the expense
- `amount` (float): Expense amount
- `category` (str): Expense category
- `description` (str, optional): Expense description
- `receipt_url` (str, optional): S3 key for receipt image

**Returns**: `dict` - Created expense record with all fields

**Where it's called**: 
- **`app.py` line 387** - In `/api/expenses` POST endpoint
```python
expense_data = expense_processor.add_expense(
    user_id=user['user_id'],
    amount=amount,
    category=category,
    description=description,
    receipt_url=receipt_url
)
```

**Why it's used**:
- **Centralized expense creation** - All expenses go through this method
- Ensures validation before saving
- Provides consistent interface to database
- Called every time user adds an expense

**Flow**:
```
User submits expense form → POST /api/expenses → add_expense() called
→ Validates data → Saves to DynamoDB → Returns expense data
→ Triggers budget checks and notifications
```

---

### 3. `get_expenses_by_user(user_id)`

**Purpose**: Retrieve all expenses for a specific user

**What it does**:
1. Calls `db.get_user_expenses()` to query DynamoDB
2. Returns list of all expense records for user
3. Handles errors and provides meaningful messages

**Parameters**:
- `user_id` (str): User identifier

**Returns**: `list` - List of expense dictionaries

**Where it's called**: 
- **`app.py` line 348** - In `/api/expenses` GET endpoint
```python
expenses = expense_processor.get_expenses_by_user(user['user_id'])
```

**Why it's used**:
- **Display expenses** - Fetches all user expenses for display
- Used by frontend to show expense list
- Called when user views expenses page
- Essential for expense management UI

**Flow**:
```
User views expenses page → GET /api/expenses → get_expenses_by_user() called
→ Returns all expenses → Displayed in UI table/list
```

---

### 4. `update_expense_status(expense_id, status, category=None)`

**Purpose**: Update the status or category of an expense

**What it does**:
1. Builds update data dictionary
2. Optionally updates category if provided
3. Calls `db.update_expense()` to update DynamoDB record
4. Returns True on success

**Parameters**:
- `expense_id` (str): Expense identifier
- `status` (str): New status (e.g., 'pending', 'approved', 'rejected')
- `category` (str, optional): New category if changing

**Returns**: `bool` - True if successful

**Where it's called**: 
- Currently **NOT directly called** in app.py
- Available for future features like expense approval workflow
- Could be used for expense categorization changes

**Why it's used**:
- **Status management** - Track expense approval status
- Allows changing expense category
- Useful for expense review workflows
- Enables expense editing functionality

---

### 5. `delete_expense(expense_id, user_id)`

**Purpose**: Delete an expense record (with user verification)

**What it does**:
1. Calls `db.delete_expense()` which:
   - Verifies expense belongs to user
   - Deletes expense from DynamoDB
2. Returns True if deleted, False if not found

**Parameters**:
- `expense_id` (str): Expense identifier
- `user_id` (str): User identifier (for security verification)

**Returns**: `bool` - True if deleted, False if not found

**Where it's called**: 
- **`app.py` line 470** - In `/api/expenses/<expense_id>` DELETE endpoint
```python
success = expense_processor.delete_expense(expense_id, user['user_id'])
```

**Why it's used**:
- **Expense deletion** - Allows users to remove expenses
- Includes security check (user_id verification)
- Prevents users from deleting other users' expenses
- Called when user clicks delete button

**Flow**:
```
User clicks delete → DELETE /api/expenses/<id> → delete_expense() called
→ Verifies ownership → Deletes from DynamoDB → Returns success
```

---

## 🔔 NotificationManager Class

**File**: `lib/notification_manager.py`  
**Purpose**: Handles all notification operations including email subscriptions and alert sending

### Class Initialization
```python
def __init__(self):
    self.sns = SNSClient()      # For sending emails
    self.db = DynamoDBClient()  # For storing notification records
    self.sqs = SQSClient()      # For queueing notifications
```
- Integrates SNS, DynamoDB, and SQS
- Central point for all notification operations

### Configuration
```python
NOTIFICATION_CONFIG = {
    'send_expense_confirmation': False,
    'send_budget_exceeded': True,
    'send_budget_threshold': True,
    'send_large_expense': True,
    'large_expense_threshold': 100,
    'large_expense_percentage': 10,
    ...
}
```
- Controls which notifications are enabled
- Sets thresholds for alerts

---

### 1. `subscribe_user(user_email)`

**Purpose**: Subscribe a user's email to SNS topic for notifications

**What it does**:
1. Calls `sns.subscribe_email()` to subscribe email to SNS topic
2. Returns list of subscription ARNs
3. Handles errors and logs failures

**Parameters**:
- `user_email` (str): User's email address

**Returns**: 
```python
[
    {'type': 'email', 'arn': subscription_arn},
    ...
]
```

**Where it's called**: 
- **`app.py` line 181** - During user registration
```python
subscriptions = notification_manager.subscribe_user(user_email=email)
```

**Why it's used**:
- **Auto-subscription** - Automatically subscribes users during registration
- Sets up email notifications for new users
- User receives AWS SNS confirmation email
- Must be confirmed before receiving alerts

**Flow**:
```
User registers → subscribe_user() called → Email subscribed to SNS
→ AWS sends confirmation email → User confirms → Ready for notifications
```

---

### 2. `send_budget_alert(user_id, user_email, message, subject="Budget Alert")`

**Purpose**: Send a generic budget alert notification

**What it does**:
1. Calls internal `_send_notification()` method
2. Queues notification to SQS
3. Returns True if queued successfully

**Parameters**:
- `user_id` (str): User identifier
- `user_email` (str): User's email
- `message` (str): Alert message
- `subject` (str, optional): Email subject (default "Budget Alert")

**Returns**: `bool` - True if queued successfully

**Where it's called**: 
- Currently **NOT directly called** in app.py
- Available for generic budget alerts
- Could be used by scheduled checks

**Why it's used**:
- Generic alert mechanism
- Can be used for various budget-related alerts
- Provides flexible notification sending

---

### 3. `send_expense_confirmation(user_id, user_email, expense_data)`

**Purpose**: Send confirmation email when expense is recorded

**What it does**:
1. Checks if expense confirmations are enabled in config
2. Formats message with expense details
3. Calls `_send_notification()` to queue email
4. Returns False if disabled, True if queued

**Parameters**:
- `user_id` (str): User identifier
- `user_email` (str): User's email
- `expense_data` (dict): Expense information

**Returns**: `bool` - True if sent, False if disabled/failed

**Where it's called**: 
- Currently **NOT directly called** in app.py
- **Disabled by default** (NOTIFICATION_CONFIG['send_expense_confirmation'] = False)
- Available for future use if enabled

**Why it's used**:
- **Optional feature** - Can send confirmation for each expense
- Currently disabled to avoid email spam
- Could be enabled for important expenses
- Provides expense tracking confirmation

---

### 4. `send_budget_exceeded_alert(user_id, user_email, category, budget_amount, spent_amount)`

**Purpose**: Send alert when user exceeds a budget

**What it does**:
1. Checks if budget exceeded alerts are enabled
2. Calculates overspend amount
3. Formats alert message with details
4. Calls `_send_notification()` to queue email
5. Logs the alert action

**Parameters**:
- `user_id` (str): User identifier
- `user_email` (str): User's email
- `category` (str): Budget category that was exceeded
- `budget_amount` (float): Budget limit
- `spent_amount` (float): Total amount spent

**Returns**: `bool` - True if queued successfully

**Where it's called**: 
- **`app.py` line 422** - After checking if budget exceeded
```python
result = notification_manager.send_budget_exceeded_alert(
    user_id=user['user_id'],
    user_email=user_email,
    category=exceeded['category'],
    budget_amount=exceeded['budget_amount'],
    spent_amount=exceeded['spent']
)
```

**Why it's used**:
- **Critical alert** - Notifies user immediately when budget exceeded
- Called right after expense is added if it causes overspending
- Helps users stay aware of their spending
- Essential for budget management

**Flow**:
```
User adds expense → Budget check → If exceeded → send_budget_exceeded_alert() called
→ Queued to SQS → Lambda processes → Email sent via SNS
```

**Message Format**:
```
⚠️ Budget Exceeded: You've overspent your {category} budget by ${overspend}.
Budget: ${budget_amount}, Spent: ${spent_amount}
```

---

### 5. `send_large_expense_alert(user_id, user_email, expense_data, category_budget=None)`

**Purpose**: Send alert when user records a large expense

**What it does**:
1. Checks if large expense alerts are enabled
2. Gets expense amount and category
3. Checks two conditions:
   - **Amount threshold**: If expense >= $100 (configurable)
   - **Percentage threshold**: If expense >= 10% of category budget
4. If either condition met, sends alert
5. Logs detailed information about the check

**Parameters**:
- `user_id` (str): User identifier
- `user_email` (str): User's email
- `expense_data` (dict): Expense information (amount, category, etc.)
- `category_budget` (float, optional): Budget for the category

**Returns**: `bool` - True if alert sent, False if not needed

**Where it's called**: 
- **`app.py` line 438** - After adding expense
```python
result = notification_manager.send_large_expense_alert(
    user_id=user['user_id'],
    user_email=user_email,
    expense_data=expense_dict,
    category_budget=category_budget if category_budget > 0 else None
)
```

**Why it's used**:
- **Spending awareness** - Alerts user about significant expenses
- Helps identify unusual spending patterns
- Can catch fraudulent or mistaken charges
- Provides spending insights

**Flow**:
```
User adds expense → send_large_expense_alert() called
→ Checks if amount >= $100 OR >= 10% of budget
→ If yes → Queues alert → Email sent
```

**Alert Conditions**:
1. Expense amount >= $100 (absolute threshold)
2. Expense >= 10% of category budget (relative threshold)

---

### 6. `_send_notification(user_id, user_email, message, subject, notification_type)`

**Purpose**: **PRIVATE METHOD** - Internal method to queue notifications

**What it does**:
1. Validates user has email address
2. Creates notification record in DynamoDB (status: 'queued')
3. Builds notification data dictionary
4. Sends message to SQS queue
5. Updates notification status if queueing fails
6. Returns True if successfully queued

**Parameters**:
- `user_id` (str): User identifier
- `user_email` (str): User's email
- `message` (str): Notification message
- `subject` (str): Email subject
- `notification_type` (str): Type of notification (e.g., 'budget_exceeded')

**Returns**: `bool` - True if queued successfully

**Where it's called**: 
- **Internally** by other notification methods:
  - `send_budget_alert()` (line 41)
  - `send_expense_confirmation()` (line 52)
  - `send_budget_exceeded_alert()` (line 66)
  - `send_large_expense_alert()` (line 108)
  - `send_weekly_summary()` (line 173)

**Why it's used**:
- **Centralized notification queueing** - All notifications go through this
- Ensures notifications are recorded in database
- Uses SQS for reliable message delivery
- Provides consistent notification handling

**Flow**:
```
Any notification method → _send_notification() called
→ Save to DynamoDB → Queue to SQS → Lambda processes → Email sent
```

---

### 7. `send_weekly_summary(user_id, user_email, summary_data)`

**Purpose**: Send weekly budget summary email

**What it does**:
1. Formats summary message with totals
2. Calls `_send_notification()` to queue email
3. Returns True if queued successfully

**Parameters**:
- `user_id` (str): User identifier
- `user_email` (str): User's email
- `summary_data` (dict): Summary data with totals

**Returns**: `bool` - True if queued successfully

**Where it's called**: 
- Currently **NOT directly called** in app.py
- Available for scheduled weekly summaries
- Could be triggered by scheduled Lambda function

**Why it's used**:
- **Periodic updates** - Weekly spending summary
- Helps users track their progress
- Can be scheduled to run automatically
- Provides regular budget insights

---

### 8. `publish_notification(subject, message, attributes=None)`

**Purpose**: Directly publish notification to SNS (bypasses queue)

**What it does**:
1. Calls `sns.publish_message()` directly
2. Sends immediately without queuing
3. Returns message ID from SNS

**Parameters**:
- `subject` (str): Email subject
- `message` (str): Notification message
- `attributes` (dict, optional): Message attributes

**Returns**: `str` - SNS message ID

**Where it's called**: 
- Currently **NOT directly called** in app.py
- Available for immediate notifications
- Used in `send_subscription_confirmation()` (line 209)

**Why it's used**:
- **Immediate sending** - Bypasses queue for urgent notifications
- Used for welcome/confirmation messages
- Provides direct SNS access when needed

---

### 9. `send_subscription_confirmation(user_id, user_email, email_subscribed)`

**Purpose**: Send welcome email when user subscribes to notifications

**What it does**:
1. Checks if email is subscribed and confirmed
2. Formats welcome message with subscription info
3. Checks if email is already confirmed in SNS
4. If confirmed, sends welcome email via SNS
5. Provides instructions about confirmation

**Parameters**:
- `user_id` (str): User identifier
- `user_email` (str): User's email
- `email_subscribed` (bool): Whether email subscription succeeded

**Returns**: `bool` - True if sent

**Where it's called**: 
- **`app.py` line 182** - During registration
- **`app.py` line 717** - When user subscribes manually
```python
notification_manager.send_subscription_confirmation(
    user_id=user['user_id'],
    user_email=email,
    email_subscribed=True
)
```

**Why it's used**:
- **User onboarding** - Welcomes new users
- Explains notification system
- Reminds users to confirm SNS subscription
- Provides helpful information

**Flow**:
```
User subscribes → send_subscription_confirmation() called
→ Checks if confirmed → Sends welcome email → User receives instructions
```

---

### 10. `get_user_notifications(user_id, limit=50)`

**Purpose**: Retrieve notification history for a user

**What it does**:
1. Calls `db.get_user_notifications()` to query DynamoDB
2. Returns list of notifications sorted by date (newest first)
3. Limits results to specified number (default 50)

**Parameters**:
- `user_id` (str): User identifier
- `limit` (int, optional): Maximum number of notifications (default 50)

**Returns**: `list` - List of notification dictionaries

**Where it's called**: 
- **`app.py` line 753** - In `/api/notifications` GET endpoint
```python
notifications = notification_manager.get_user_notifications(user['user_id'], limit)
```

**Why it's used**:
- **Notification history** - Shows user their past notifications
- Used by frontend to display notification list
- Helps users track what alerts they received
- Essential for notification management UI

**Flow**:
```
User views notifications → GET /api/notifications → get_user_notifications() called
→ Returns notification history → Displayed in UI
```

---

## 📄 ReceiptHandler Class

**File**: `lib/receipt_handler.py`  
**Purpose**: Handles receipt file operations including validation and S3 uploads

### Class Initialization
```python
def __init__(self):
    self.s3 = S3Client()
    self.allowed_extensions = ['jpg', 'jpeg', 'png', 'pdf', 'gif']
    self.max_file_size = 10 * 1024 * 1024  # 10MB
```
- Creates S3 client for file operations
- Defines allowed file types and size limits

---

### 1. `validate_file_type(filename)`

**Purpose**: Validate that file extension is allowed

**What it does**:
1. Extracts file extension from filename
2. Converts to lowercase
3. Checks if extension is in allowed list
4. Returns validation result and extension or error message

**Parameters**:
- `filename` (str): Name of the file

**Returns**: 
```python
(is_valid: bool, file_extension_or_error: str)
```

**Where it's called**: 
- **Internally** in `upload_receipt()` method (line 33)
- Not called directly from app.py

**Why it's used**:
- **Security** - Prevents uploading dangerous file types
- Ensures only image/PDF files are accepted
- First validation step before upload
- Protects against malicious files

**Allowed Types**: jpg, jpeg, png, pdf, gif

---

### 2. `validate_file_size(file_content)`

**Purpose**: Validate that file size is within limits

**What it does**:
1. Gets file size from content length
2. Checks if size exceeds 10MB limit
3. Checks if file is empty (size = 0)
4. Returns validation result and error message if invalid

**Parameters**:
- `file_content` (bytes): File content as bytes

**Returns**: 
```python
(is_valid: bool, error_message: str or None)
```

**Where it's called**: 
- **Internally** in `upload_receipt()` method (line 38)
- Not called directly from app.py

**Why it's used**:
- **Storage management** - Prevents huge files
- Protects against storage abuse
- Ensures reasonable file sizes
- Prevents empty file uploads

**Size Limit**: 10MB maximum

---

### 3. `upload_receipt(file_content, filename, user_id, expense_id=None)`

**Purpose**: Upload receipt file to S3 after validation

**What it does**:
1. Validates file type using `validate_file_type()`
2. Validates file size using `validate_file_size()`
3. If validation fails, raises ValueError
4. If valid, calls `s3.upload_receipt()` to upload to S3
5. Returns S3 key (path) for the uploaded file

**Parameters**:
- `file_content` (bytes): File content as bytes
- `filename` (str): Original filename
- `user_id` (str): User identifier
- `expense_id` (str, optional): Associated expense ID

**Returns**: `str` - S3 key (path) of uploaded file

**Where it's called**: 
- **`app.py` line 612** - In `/api/receipts/upload` POST endpoint
```python
receipt_key = receipt_handler.upload_receipt(
    file_content=file_content,
    filename=file.filename,
    user_id=user['user_id'],
    expense_id=expense_id if expense_id else None
)
```

**Why it's used**:
- **Receipt storage** - Main method for uploading receipts
- Ensures files are validated before upload
- Called when user uploads receipt image
- Essential for expense documentation

**Flow**:
```
User uploads file → POST /api/receipts/upload → upload_receipt() called
→ Validates type & size → Uploads to S3 → Returns S3 key
→ S3 key saved to expense record in DynamoDB
```

**S3 Path Format**:
- With expense_id: `receipts/{user_id}/{expense_id}.{extension}`
- Without expense_id: `receipts/{user_id}/{uuid}.{extension}`

---

### 4. `get_receipt_url(receipt_key, expiration=3600)`

**Purpose**: Generate presigned URL to access receipt from S3

**What it does**:
1. Validates receipt_key is provided
2. Calls `s3.get_receipt_url()` to generate presigned URL
3. Returns URL that expires after specified time

**Parameters**:
- `receipt_key` (str): S3 key (path) of the receipt
- `expiration` (int, optional): URL expiration in seconds (default 3600 = 1 hour)

**Returns**: `str` - Presigned URL or None if key is invalid

**Where it's called**: 
- **`app.py` line 622** - After uploading receipt
- **`app.py` line 653** - When retrieving receipt
- **`app.py` line 880** - For report downloads
```python
receipt_url = receipt_handler.get_receipt_url(receipt_key)
```

**Why it's used**:
- **Secure access** - Provides temporary access to S3 files
- URLs expire after 1 hour (default)
- Allows frontend to display receipt images
- Prevents direct S3 bucket access

**Flow**:
```
User views receipt → get_receipt_url() called → Presigned URL generated
→ Frontend uses URL to display image → URL expires after 1 hour
```

---

### 5. `generate_presigned_url(user_id, expense_id=None, expiration=3600)`

**Purpose**: Generate presigned URL for uploading receipt (client-side upload)

**What it does**:
1. Constructs S3 key based on user_id and expense_id
2. Generates presigned URL for PUT operation
3. Returns both key and URL

**Parameters**:
- `user_id` (str): User identifier
- `expense_id` (str, optional): Associated expense ID
- `expiration` (int, optional): URL expiration (default 3600 seconds)

**Returns**: 
```python
{
    'key': str,  # S3 key
    'url': str   # Presigned URL
}
```

**Where it's called**: 
- **`app.py` line 669** - In `/api/receipts/presigned-url` POST endpoint
```python
result = receipt_handler.generate_presigned_url(
    user_id=user['user_id'],
    expense_id=expense_id
)
```

**Why it's used**:
- **Client-side upload** - Allows frontend to upload directly to S3
- Reduces server load
- Provides secure upload URL
- Used for direct browser-to-S3 uploads

**Flow**:
```
User wants to upload → POST /api/receipts/presigned-url → generate_presigned_url() called
→ Returns presigned URL → Frontend uploads directly to S3 → File stored
```

---

### 6. `delete_receipt(receipt_key)`

**Purpose**: Delete receipt file from S3

**What it does**:
1. Validates receipt_key is provided
2. Calls `s3.delete_receipt()` to delete from S3
3. Returns True if deleted successfully

**Parameters**:
- `receipt_key` (str): S3 key (path) of the receipt

**Returns**: `bool` - True if deleted, False if key is invalid

**Where it's called**: 
- Currently **NOT directly called** in app.py
- Available for receipt deletion feature
- Could be used when expense is deleted

**Why it's used**:
- **Cleanup** - Removes receipt files when no longer needed
- Prevents S3 storage bloat
- Can be called when expense is deleted
- Useful for storage management

---

### 7. `receipt_exists(receipt_key)`

**Purpose**: Check if receipt file exists in S3

**What it does**:
1. Validates receipt_key is provided
2. Calls `s3.file_exists()` to check S3
3. Returns True if exists, False otherwise

**Parameters**:
- `receipt_key` (str): S3 key (path) of the receipt

**Returns**: `bool` - True if exists, False otherwise

**Where it's called**: 
- Currently **NOT directly called** in app.py
- Available for validation checks
- Could be used to verify receipt before displaying

**Why it's used**:
- **Validation** - Verify receipt exists before operations
- Prevents errors from missing files
- Useful for error handling
- Can check file status

---

## 📊 Function Call Summary

### Most Frequently Called Functions

| Function | Times Called | Primary Use Case |
|----------|--------------|------------------|
| `budget_calculator.check_budget_exceeded()` | 1 | Check if budget exceeded when adding expense |
| `budget_calculator.get_category_budget()` | 1 | Get budget for large expense check |
| `budget_calculator.get_budget_summary()` | 1 | Dashboard summary display |
| `expense_processor.add_expense()` | 1 | Add new expense |
| `expense_processor.get_expenses_by_user()` | 1 | Display expense list |
| `expense_processor.delete_expense()` | 1 | Delete expense |
| `notification_manager.send_budget_exceeded_alert()` | 1 | Alert when budget exceeded |
| `notification_manager.send_large_expense_alert()` | 1 | Alert for large expenses |
| `notification_manager.subscribe_user()` | 1 | Subscribe during registration |
| `notification_manager.get_user_notifications()` | 1 | Display notification history |
| `receipt_handler.upload_receipt()` | 1 | Upload receipt file |
| `receipt_handler.get_receipt_url()` | 3 | Get receipt URL for display |

### Functions Available But Not Currently Used

These functions are implemented and ready to use but not currently called in app.py:

**BudgetCalculator**:
- `calculate_totals()` - For overall budget summary
- `calculate_remaining()` - Utility calculation
- `calculate_percentage()` - Used internally
- `check_budget_threshold()` - For proactive alerts

**ExpenseProcessor**:
- `update_expense_status()` - For expense approval workflow

**NotificationManager**:
- `send_budget_alert()` - Generic budget alerts
- `send_expense_confirmation()` - Expense confirmations (disabled)
- `send_weekly_summary()` - Weekly summaries

**ReceiptHandler**:
- `delete_receipt()` - Receipt deletion
- `receipt_exists()` - File existence check

---

## 🎯 Key Design Patterns

### 1. **Separation of Concerns**
- Business logic separated from routes
- Database operations abstracted
- AWS services wrapped in classes

### 2. **Validation Before Action**
- All data validated before database operations
- File validation before S3 upload
- Prevents invalid data from being stored

### 3. **Error Handling**
- Consistent exception handling
- Meaningful error messages
- Logging for debugging

### 4. **Reusability**
- Functions can be called from multiple places
- Utility functions available for various use cases
- Consistent interfaces across classes

### 5. **Configuration-Driven**
- Notification settings in NOTIFICATION_CONFIG
- File limits configurable
- Easy to enable/disable features

---

## 🔄 Complete Data Flow Examples

### Example 1: User Adds Expense with Receipt

```
1. User submits expense form
   ↓
2. POST /api/expenses (app.py:371)
   ↓
3. expense_processor.add_expense() (expense_processor.py:26)
   → validate_expense() checks data
   → db.add_expense() saves to DynamoDB
   ↓
4. budget_calculator.check_budget_exceeded() (budget_calculator.py:80)
   → Checks if budget exceeded
   ↓
5. If exceeded:
   → notification_manager.send_budget_exceeded_alert() (notification_manager.py:56)
   → _send_notification() queues to SQS
   ↓
6. budget_calculator.get_category_budget() (budget_calculator.py:113)
   → Gets budget for category
   ↓
7. notification_manager.send_large_expense_alert() (notification_manager.py:73)
   → Checks if expense is large
   → _send_notification() queues to SQS
   ↓
8. User uploads receipt
   → POST /api/receipts/upload (app.py:591)
   ↓
9. receipt_handler.upload_receipt() (receipt_handler.py:32)
   → validate_file_type() checks extension
   → validate_file_size() checks size
   → s3.upload_receipt() uploads to S3
   ↓
10. receipt_handler.get_receipt_url() (receipt_handler.py:54)
    → Generates presigned URL
    ↓
11. db.update_expense() updates expense with receipt URL
```

### Example 2: User Views Dashboard

```
1. User opens dashboard
   ↓
2. Frontend calls GET /api/summary (app.py:576)
   ↓
3. budget_calculator.get_budget_summary() (budget_calculator.py:123)
   → db.get_user_budgets() gets all budgets
   → db.get_user_expenses() gets all expenses
   → Groups expenses by category
   → Calculates spent, remaining, percentage for each
   ↓
4. Returns summary data
   ↓
5. Frontend displays charts and progress bars
```

---

## 📝 Summary

The `lib/` directory provides a **clean, organized layer** between your Flask routes and AWS services. Each class has a specific responsibility:

- **BudgetCalculator**: All budget calculations and checks
- **ExpenseProcessor**: Expense validation and database operations
- **NotificationManager**: Email notifications and subscriptions
- **ReceiptHandler**: File validation and S3 operations

This architecture makes your code:
- ✅ **Maintainable** - Easy to update and modify
- ✅ **Testable** - Functions can be tested independently
- ✅ **Reusable** - Functions can be called from multiple places
- ✅ **Readable** - Clear separation of concerns
- ✅ **Scalable** - Easy to add new features

All functions are well-documented and follow consistent patterns, making the codebase professional and easy to understand.

