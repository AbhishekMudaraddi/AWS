# AWS DynamoDB - Database Service

## What is DynamoDB?

DynamoDB is AWS's fully managed NoSQL database service. It provides fast, flexible, and scalable database storage without the need to manage servers or infrastructure.

## Why DynamoDB in This Project?

1. **Fully Managed**: No server management required
2. **Scalable**: Automatically scales based on demand
3. **Fast**: Low latency, high performance
4. **Cost-Effective**: Pay-per-request pricing model
5. **NoSQL**: Flexible schema for user data, expenses, budgets

## How DynamoDB is Used in This Project

DynamoDB stores all application data:
- **Users Table**: User accounts, credentials, contact information
- **Expenses Table**: All expense transactions
- **Budgets Table**: User budget settings by category
- **Notifications Table**: Notification history

## Implementation Files

### Primary Files:
1. **`aws_config/setup_dynamodb.py`** - Main DynamoDB client class (SDK wrapper)
2. **`aws_config/resource_manager.py`** - Creates DynamoDB tables
3. **`scripts/setup_aws_resources.py`** - Setup script that creates tables

### Usage in Application:
- **`app.py`** - Uses `DynamoDBClient` for all database operations
- **`lib/expense_processor.py`** - Uses DynamoDB to store expenses
- **`lib/budget_calculator.py`** - Queries budgets from DynamoDB
- **`lib/notification_manager.py`** - Stores notifications in DynamoDB

## Code Structure

### 1. Configuration (`aws_config/config.py`)

```python
DYNAMODB_TABLES = {
    'users': 'smart-budget-users',
    'expenses': 'smart-budget-expenses',
    'budgets': 'smart-budget-budgets',
    'notifications': 'smart-budget-notifications'
}
```

**Explanation**: Defines table names used throughout the application.

### 2. DynamoDB Client (`aws_config/dynamodb_client.py`)

**Key Methods:**

#### Creating a User
```python
def create_user(self, username, email, password_hash, phone_number=None):
    user_id = str(uuid.uuid4())
    user_data = {
        'user_id': user_id,
        'username': username,
        'email': email,
        'password_hash': password_hash,
        'created_at': datetime.utcnow().isoformat()
    }
    if phone_number:
        user_data['phone_number'] = phone_number
    
    self.users_table.put_item(Item=user_data)
    return user_data
```

**What it does**: Creates a new user record in DynamoDB with unique ID.

**Used in**: `app.py` - `/register` route

#### Getting User by Username
```python
def get_user_by_username(self, username):
    response = self.users_table.query(
        IndexName='username-index',
        KeyConditionExpression='username = :username',
        ExpressionAttributeValues={':username': username}
    )
    items = response.get('Items', [])
    return items[0] if items else None
```

**What it does**: Queries DynamoDB using Global Secondary Index (GSI) to find user by username.

**Used in**: `app.py` - `/login` route

#### Adding Expense
```python
def add_expense(self, user_id, amount, category, description, expense_date, receipt_url=None):
    expense_id = str(uuid.uuid4())
    item = {
        'expense_id': expense_id,
        'user_id': user_id,
        'amount': Decimal(str(amount)),
        'category': category,
        'description': description,
        'date': expense_date,
        'created_at': datetime.utcnow().isoformat()
    }
    if receipt_url:
        item['receipt_url'] = receipt_url
    self.expenses_table.put_item(Item=item)
    return item
```

**What it does**: Stores expense transaction in DynamoDB.

**Used in**: `app.py` - `/api/expenses` POST route

#### Querying Expenses by User
```python
def get_expenses_by_user(self, user_id, start_date=None, end_date=None, category=None):
    key_condition_expression = 'user_id = :user_id'
    expression_attribute_values = {':user_id': user_id}
    
    query_params = {
        'IndexName': 'user_id-date-index',
        'KeyConditionExpression': key_condition_expression,
        'ExpressionAttributeValues': expression_attribute_values,
        'ScanIndexForward': False  # Most recent first
    }
    
    response = self.expenses_table.query(**query_params)
    return response.get('Items', [])
```

**What it does**: Queries expenses using GSI, filters by date/category, returns most recent first.

**Used in**: `app.py` - `/api/expenses` GET route

## Table Structure

### Users Table
- **Primary Key**: `user_id` (String)
- **GSI**: `username-index` (for login lookup)
- **GSI**: `email-index` (for email lookup)
- **Attributes**: username, email, password_hash, phone_number, created_at

### Expenses Table
- **Primary Key**: `expense_id` (String)
- **GSI**: `user_id-index` (to get all expenses for a user)
- **GSI**: `user_id-date-index` (for date range queries)
- **Attributes**: user_id, amount, category, description, date, receipt_url, created_at

### Budgets Table
- **Primary Key**: `budget_id` (String)
- **GSI**: `user_id-index` (to get all budgets for a user)
- **GSI**: `user_id-category-index` (to get budget for specific category)
- **Attributes**: user_id, category, amount, alert_threshold, created_at

### Notifications Table
- **Primary Key**: `notification_id` (String)
- **GSI**: `user_id-created_at-index` (to get notifications for a user)
- **Attributes**: user_id, type, message, delivery_method, created_at

## How to Explain in Class

### When Asked: "Why DynamoDB instead of SQL database?"

**Answer**: 
- This is a cloud-native application requiring automatic scaling
- DynamoDB handles scaling automatically without database administration
- Pay-per-request pricing is cost-effective for variable workloads
- NoSQL structure fits flexible expense data (different users have different categories)
- Low latency for real-time expense tracking

### When Asked: "How does DynamoDB work in your application?"

**Answer**:
1. **Setup**: Tables are created using `scripts/setup_aws_resources.py`
2. **Connection**: `DynamoDBClient` class connects to tables using boto3
3. **Operations**: All CRUD operations go through `dynamodb_client.py`
4. **Queries**: Uses Global Secondary Indexes (GSI) for efficient lookups
5. **Integration**: Flask app (`app.py`) uses the client for all database operations

### When Asked: "Show me where expenses are stored"

**Answer**:
- **File**: `aws_config/dynamodb_client.py`
- **Method**: `add_expense()` - Line 150-170
- **Table**: `smart-budget-expenses`
- **Called from**: `app.py` line 385 in `/api/expenses` POST route
- **Flow**: User submits expense → Flask route → DynamoDBClient.add_expense() → DynamoDB table

### When Asked: "How do you query expenses for a user?"

**Answer**:
- **File**: `aws_config/dynamodb_client.py`
- **Method**: `get_expenses_by_user()` - Line 172-210
- **Uses**: Global Secondary Index `user_id-index`
- **Why GSI**: Primary key is `expense_id`, but we need to query by `user_id`
- **Called from**: `app.py` line 347 in `/api/expenses` GET route

## Key Concepts to Remember

1. **Primary Key**: Unique identifier for each item (user_id, expense_id, etc.)
2. **Global Secondary Index (GSI)**: Allows querying by non-primary key attributes
3. **Query vs Scan**: Query is faster (uses index), Scan reads entire table
4. **ExpressionAttributeValues**: Used to prevent injection attacks
5. **Decimal Type**: DynamoDB uses Decimal for numbers to maintain precision

## Common Questions & Answers

**Q: Why use Decimal for amounts?**
A: To maintain precision for financial calculations. Float can have rounding errors.

**Q: How do you handle user authentication?**
A: User credentials stored in DynamoDB Users table. Password hashed with Werkzeug before storage.

**Q: What happens if DynamoDB is down?**
A: Application will fail gracefully with error messages. AWS manages DynamoDB availability (99.99% SLA).

**Q: How do you ensure data consistency?**
A: DynamoDB provides eventual consistency. For critical operations, we use conditional writes.
