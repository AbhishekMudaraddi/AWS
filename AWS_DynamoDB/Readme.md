
# AWS DynamoDB

## Overview
DynamoDB is a fully managed, serverless NoSQL database for key-value and document data, designed for massive scale and single-digit millisecond performance. This README helps you learn core concepts, practice common operations, and build a small hands-on project.

## Key Features
- Serverless scaling with high availability and durability
- Consistent low-latency reads and writes
- On-demand or provisioned capacity (RCU/WCU) with auto scaling
- Global tables for multi-region replication
- Streams, TTL, point-in-time recovery, and encryption at rest

## Core Concepts
- Table: A collection of items
- Item: A row (JSON-like document)
- Attributes: Key-value pairs within an item
- Primary Key:
  - Partition key only (hash key)
  - Partition key + sort key (composite key)
- Secondary Indexes:
  - GSI (Global Secondary Index): new partition/sort keys; independent throughput
  - LSI (Local Secondary Index): same partition key, different sort key
- Capacity:
  - Read Capacity Units (RCU) and Write Capacity Units (WCU)
  - On-demand vs provisioned
- Consistency: Eventually consistent reads (default) or strongly consistent reads

## Data Modeling Best Practices
- Design around access patterns first (queries > scans)
- Prefer single-table design with composite keys
- Use GSIs for alternative access patterns
- Avoid hot partitions by distributing partition keys
- Use sparse indexes (only items with certain attributes appear)
- Store related entities together using sort key patterns (e.g., `USER#123`, `ORDER#456`)

## Common Operations
- PutItem: Create or replace an item
- GetItem: Fetch by primary key
- UpdateItem: Modify attributes atomically
- DeleteItem: Remove an item
- Query: Efficient lookup by partition key (with sort key conditions)
- Scan: Full table read (avoid in production when possible)
- BatchGet/BatchWrite: Bulk operations
- Transactions: All-or-nothing writes across multiple items

## Example: Create a Table (CLI)
```bash
aws dynamodb create-table \
  --table-name DemoTable \
  --attribute-definitions AttributeName=PK,AttributeType=S AttributeName=SK,AttributeType=S \
  --key-schema AttributeName=PK,KeyType=HASH AttributeName=SK,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST
```

Add a GSI (optional):
```bash
aws dynamodb update-table \
  --table-name DemoTable \
  --attribute-definitions AttributeName=GSI1PK,AttributeType=S AttributeName=GSI1SK,AttributeType=S \
  --global-secondary-index-updates '{
    "Create": {
      "IndexName": "GSI1",
      "KeySchema": [
        {"AttributeName": "GSI1PK", "KeyType": "HASH"},
        {"AttributeName": "GSI1SK", "KeyType": "RANGE"}
      ],
      "Projection": {"ProjectionType": "ALL"},
      "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
    }
  }'
```

## Example: Python (boto3)
```python
import boto3
from boto3.dynamodb.conditions import Key

# Local: set endpoint_url="http://localhost:8000" if using DynamoDB Local
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("DemoTable")

# Put item
table.put_item(Item={
    "PK": "USER#123",
    "SK": "PROFILE#2024-10-01",
    "name": "Abhishek",
    "email": "user@example.com"
})

# Query
resp = table.query(
    KeyConditionExpression=Key("PK").eq("USER#123") & Key("SK").begins_with("PROFILE#")
)
print(resp["Items"])
```

## Hands-On Project: Serverless Notes API
- Architecture: API Gateway + Lambda (Python) + DynamoDB
- Table keys: `PK` (e.g., `USER#<id>`), `SK` (e.g., `NOTE#<timestamp>`) 
- Endpoints: `POST /notes`, `GET /notes`, `GET /notes/{id}`, `DELETE /notes/{id}`
- Steps:
  - Create table (`DemoTable`) with composite keys
  - Create IAM role for Lambda with DynamoDB permissions
  - Implement Lambda handlers using boto3 for CRUD
  - Deploy via SAM/CDK or manual setup
  - Test with curl/Postman

## Local Development (DynamoDB Local)
Run with Docker:
```bash
docker run -p 8000:8000 amazon/dynamodb-local
```
Create a local table:
```bash
aws dynamodb create-table \
  --endpoint-url http://localhost:8000 \
  --table-name DemoTable \
  --attribute-definitions AttributeName=PK,AttributeType=S AttributeName=SK,AttributeType=S \
  --key-schema AttributeName=PK,KeyType=HASH AttributeName=SK,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST
```
Point SDK to local:
- Python: `boto3.resource("dynamodb", endpoint_url="http://localhost:8000")`
- CLI: add `--endpoint-url http://localhost:8000`

## Best Practices
- Prefer `Query` over `Scan`; design keys to avoid scans
- Use conditional expressions to prevent overwrites
- Enable TTL for ephemeral data and Streams for event-driven patterns
- Use on-demand for unknown traffic, provisioned for predictable workloads
- Monitor with CloudWatch; enable backups and point-in-time recovery

## Cost Optimization
- Keep items small; store large blobs in S3 with references
- Use on-demand for spiky/low traffic; provisioned for steady high traffic
- Right-size RCU/WCU and enable auto scaling

## Useful Links
- DynamoDB developer guide: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Welcome.html
- DynamoDB Local: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html
- AWS SDK for Python (boto3): https://boto3.amazonaws.com/v1/documentation/api/latest/index.html