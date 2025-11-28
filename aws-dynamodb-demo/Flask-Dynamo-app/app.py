from flask import Flask, render_template, request, jsonify
import boto3
import os
import time  # Added this import
import logging
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# AWS Configuration from environment variables
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'UserData')

# Check if required environment variables are set
if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
    logger.error("AWS credentials not found in environment variables")
    raise EnvironmentError("AWS credentials not found in environment variables")

logger.info(f"Using AWS region: {AWS_REGION}")
logger.info(f"Using DynamoDB table: {DYNAMODB_TABLE}")

# Initialize DynamoDB client
try:
    dynamodb = boto3.resource(
        'dynamodb',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    logger.info("DynamoDB client initialized successfully")
except Exception as e:
    logger.error(f"Error initializing DynamoDB client: {e}")
    raise

# Create DynamoDB table if not exists
def create_dynamodb_table():
    try:
        table = dynamodb.create_table(
            TableName=DYNAMODB_TABLE,
            KeySchema=[
                {'AttributeName': 'user_id', 'KeyType': 'HASH'}  # Partition key
            ],
            AttributeDefinitions=[
                {'AttributeName': 'user_id', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        table.wait_until_exists()
        logger.info(f"Table {DYNAMODB_TABLE} created successfully!")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            logger.info(f"Table {DYNAMODB_TABLE} already exists.")
        else:
            logger.error(f"Error creating table: {e}")
            raise

# Initialize table on startup
try:
    create_dynamodb_table()
    table = dynamodb.Table(DYNAMODB_TABLE)
    logger.info(f"Successfully connected to table {DYNAMODB_TABLE}")
except Exception as e:
    logger.error(f"Error setting up DynamoDB table: {e}")
    raise

@app.route('/')
def index():
    logger.info("Serving index page")
    return render_template('index.html')

@app.route('/test-db')
def test_db():
    try:
        # List tables to test connection
        tables = dynamodb.meta.client.list_tables()
        return f"Connection successful. Tables: {tables['TableNames']}"
    except Exception as e:
        logger.error(f"Database test failed: {e}")
        return f"Error: {str(e)}"

@app.route('/submit', methods=['POST'])
def submit():
    try:
        logger.info("Received form submission")
        
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        logger.info(f"Form data: name={name}, email={email}, message={message}")
        
        if not name or not email or not message:
            logger.warning("Missing form fields")
            return jsonify({'status': 'error', 'message': 'All fields are required'})
        
        # Generate unique ID (now using the imported time module)
        user_id = f"user_{int(time.time())}"
        
        # Store in DynamoDB
        table.put_item(
            Item={
                'user_id': user_id,
                'name': name,
                'email': email,
                'message': message
            }
        )
        logger.info(f"Successfully stored item with user_id: {user_id}")
        return jsonify({'status': 'success', 'message': 'Data saved successfully!'})
    except Exception as e:
        logger.error(f"Error in submit route: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)