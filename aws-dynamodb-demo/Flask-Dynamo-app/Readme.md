# Flask-Dynamo-app

## Overview
This sample app demonstrates building a lightweight REST API using Flask with DynamoDB as the datastore. It focuses on practical CRUD operations, data modeling with composite keys, and local development using DynamoDB Local.

## Why This Was Made
- Learn how to integrate Flask (Python) with DynamoDB using `boto3`
- Practice DynamoDB data modeling and access patterns
- Understand request flow, error handling, and environment configuration
- Provide a starting point for serverless/API projects backed by DynamoDB

## What You Learn
- Designing keys and items for scalable access patterns
- Using `Query` versus `Scan` and why it matters
- Performing CRUD operations with conditional writes
- Running locally against DynamoDB Local or against AWS
- Structuring a small Flask app with clean routes and service layer

## Architecture
- `Flask` provides HTTP endpoints
- `boto3` interacts with `DynamoDB`
- Table schema uses composite primary key: `PK` and `SK`
- Items organized by entity type and timestamp for efficient queries

Example table design:
- Partition key `PK`: `USER#<userId>`
- Sort key `SK`: `NOTE#<epoch>`

## Endpoints (Example: Notes API)
- `GET /health` — health check
- `POST /notes` — create a note
- `GET /notes` — list notes for a user
- `GET /notes/<id>` — get a single note
- `DELETE /notes/<id>` — delete a note

Example request/response flow:
1. Client sends HTTP request to Flask endpoint
2. Route handler validates input and calls a `notes_service`
3. Service composes keys (`PK`, `SK`), executes DynamoDB operation via `boto3`
4. Response serializes result or returns appropriate error

## Local Setup
- Python 3.10+
- Create virtual environment and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate
pip install flask boto3 python-dotenv
```

- Optional: run DynamoDB Local in Docker
```bash
docker run -p 8000:8000 amazon/dynamodb-local
```

- Create a table locally (composite keys):
```bash
aws dynamodb create-table \
  --endpoint-url http://localhost:8000 \
  --table-name DemoTable \
  --attribute-definitions AttributeName=PK,AttributeType=S AttributeName=SK,AttributeType=S \
  --key-schema AttributeName=PK,KeyType=HASH AttributeName=SK,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST
```

- Environment configuration:
  - `AWS_REGION` (e.g., `us-east-1`)
  - For AWS: use your default profile or set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
  - For local: set DynamoDB endpoint: `endpoint_url="http://localhost:8000"`

## Minimal Code Sketch (for reference)
```python
# app.py
import os
import time
import boto3
from flask import Flask, request, jsonify
from boto3.dynamodb.conditions import Key

DYNAMO_ENDPOINT = os.getenv("DYNAMO_ENDPOINT")  # e.g., http://localhost:8000
TABLE_NAME = os.getenv("TABLE_NAME", "DemoTable")
USER_ID = os.getenv("USER_ID", "USER#demo")  # demo user

dynamodb = boto3.resource("dynamodb", endpoint_url=DYNAMO_ENDPOINT) if DYNAMO_ENDPOINT else boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)

app = Flask(__name__)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/notes")
def create_note():
    data = request.get_json(force=True)
    note_id = str(int(time.time() * 1000))
    item = {
        "PK": USER_ID,
        "SK": f"NOTE#{note_id}",
        "title": data.get("title", ""),
        "content": data.get("content", "")
    }
    table.put_item(Item=item)
    return jsonify({"id": note_id}), 201

@app.get("/notes")
def list_notes():
    resp = table.query(
        KeyConditionExpression=Key("PK").eq(USER_ID) & Key("SK").begins_with("NOTE#")
    )
    return jsonify(resp.get("Items", []))

@app.get("/notes/<note_id>")
def get_note(note_id):
    resp = table.get_item(Key={"PK": USER_ID, "SK": f"NOTE#{note_id}"})
    item = resp.get("Item")
    if not item:
        return {"error": "Not found"}, 404
    return jsonify(item)

@app.delete("/notes/<note_id>")
def delete_note(note_id):
    table.delete_item(Key={"PK": USER_ID, "SK": f"NOTE#{note_id}"})
    return {}, 204

if __name__ == "__main__":
    app.run(debug=True)
```

## Run the App
- Set env vars (examples):
```bash
export AWS_REGION=us-east-1
export TABLE_NAME=DemoTable
export USER_ID=USER#demo
# For local DynamoDB
export DYNAMO_ENDPOINT=http://localhost:8000
```
- Start Flask:
```bash
FLASK_APP=app.py flask run
# or
python app.py
```

## Test with curl
```bash
curl http://127.0.0.1:5000/health
curl -X POST http://127.0.0.1:5000/notes -H 'Content-Type: application/json' -d '{"title":"Hello","content":"World"}'
curl http://127.0.0.1:5000/notes
curl http://127.0.0.1:5000/notes/<note_id>
curl -X DELETE http://127.0.0.1:5000/notes/<note_id>
```

## Production Options
- Wrap Flask in AWS Lambda (AWS SAM, Lambda Web Adapter, or Zappa)
- Use API Gateway + Lambda for serverless, or ECS/Elastic Beanstalk for containers
- Enable CloudWatch logging, X-Ray tracing, and IAM least-privilege policies

## Best Practices
- Prefer `Query` over `Scan` by designing good keys
- Use conditional expressions for safe updates/deletes
- TTL for ephemeral items and Streams for event-driven integrations
- Backups and point-in-time recovery for resilience

## Next Steps
- Add authentication (Cognito or JWT)
- Pagination and filtering
- GSI for alternative queries (e.g., by title or created date)
- Unit tests for service layer

## Summary
This app is built to learn and demonstrate a practical integration between Flask and DynamoDB. You saw how to model data, connect using `boto3`, implement CRUD endpoints, and run locally or in AWS. It’s a foundation for building scalable, serverless-friendly APIs on AWS.