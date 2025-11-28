"""
AWS Lambda Demonstration Application
This Flask app simulates AWS Lambda behavior for educational purposes.
"""

from flask import Flask, request, jsonify
import json
import time
import logging
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LambdaContext:
    """Simulates AWS Lambda Context object"""
    def __init__(self, function_name, memory_limit_mb=128, timeout=30):
        self.function_name = function_name
        self.memory_limit_mb = memory_limit_mb
        self.timeout = timeout
        self.start_time = time.time()
        self.request_id = f"sim-{int(time.time() * 1000)}"
    
    def get_remaining_time_in_millis(self):
        """Returns remaining execution time"""
        elapsed = (time.time() - self.start_time) * 1000
        remaining = (self.timeout * 1000) - elapsed
        return max(0, remaining)


def lambda_handler_wrapper(handler_func):
    """Decorator to wrap Lambda handlers with context and error handling"""
    def wrapper(*args, **kwargs):
        try:
            # Simulate Lambda event and context
            event = request.get_json() if request.is_json else request.form.to_dict()
            context = LambdaContext(function_name=handler_func.__name__)
            
            logger.info(f"Invoking Lambda function: {handler_func.__name__}")
            logger.info(f"Request ID: {context.request_id}")
            
            # Execute handler
            result = handler_func(event, context)
            
            return jsonify({
                'statusCode': 200,
                'body': result,
                'requestId': context.request_id,
                'executionTime': f"{(time.time() - context.start_time) * 1000:.2f}ms"
            })
        except Exception as e:
            logger.error(f"Error in Lambda function: {str(e)}")
            return jsonify({
                'statusCode': 500,
                'error': str(e),
                'requestId': context.request_id if 'context' in locals() else 'unknown'
            }), 500
    wrapper.__name__ = handler_func.__name__
    return wrapper


# Example Lambda Handler 1: Simple Hello World
@lambda_handler_wrapper
def hello_world_handler(event, context):
    """
    Simple Lambda handler that returns a greeting message.
    Demonstrates basic Lambda function structure.
    """
    name = event.get('name', 'World')
    return {
        'message': f'Hello, {name}!',
        'functionName': context.function_name,
        'timestamp': datetime.now().isoformat()
    }


# Example Lambda Handler 2: Data Processing
@lambda_handler_wrapper
def data_processor_handler(event, context):
    """
    Lambda handler that processes data (simulates data transformation).
    Demonstrates Lambda for ETL operations.
    """
    data = event.get('data', [])
    
    if not isinstance(data, list):
        raise ValueError("Data must be a list")
    
    # Process data: square each number
    processed = [item ** 2 if isinstance(item, (int, float)) else item for item in data]
    
    return {
        'original': data,
        'processed': processed,
        'count': len(processed),
        'memoryLimit': f"{context.memory_limit_mb}MB",
        'remainingTime': f"{context.get_remaining_time_in_millis():.2f}ms"
    }


# Example Lambda Handler 3: API Gateway Integration
@lambda_handler_wrapper
def api_gateway_handler(event, context):
    """
    Lambda handler simulating API Gateway integration.
    Demonstrates how Lambda works with API Gateway.
    """
    # Simulate API Gateway event structure
    http_method = event.get('httpMethod', request.method)
    path = event.get('path', request.path)
    query_params = event.get('queryStringParameters', {}) or {}
    body = event.get('body', '{}')
    
    # Parse body if it's a string
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except:
            body = {}
    
    return {
        'message': 'API Gateway Lambda Integration',
        'method': http_method,
        'path': path,
        'queryParameters': query_params,
        'body': body,
        'headers': dict(request.headers),
        'requestId': context.request_id
    }


# Example Lambda Handler 4: Scheduled Event (Cron)
@lambda_handler_wrapper
def scheduled_event_handler(event, context):
    """
    Lambda handler simulating CloudWatch Events/EventBridge trigger.
    Demonstrates scheduled Lambda functions.
    """
    # Simulate CloudWatch Events structure
    source = event.get('source', 'aws.events')
    detail_type = event.get('detail-type', 'Scheduled Event')
    
    return {
        'message': 'Scheduled Lambda execution',
        'source': source,
        'detailType': detail_type,
        'executionTime': datetime.now().isoformat(),
        'functionName': context.function_name,
        'status': 'success'
    }


# Example Lambda Handler 5: Error Handling
@lambda_handler_wrapper
def error_handler_demo(event, context):
    """
    Lambda handler demonstrating error handling.
    """
    should_fail = event.get('shouldFail', False)
    
    if should_fail:
        raise ValueError("This is a simulated error for demonstration purposes")
    
    return {
        'message': 'Error handling demonstration',
        'status': 'success',
        'note': 'Set shouldFail=true to see error handling'
    }


# Flask Routes
@app.route('/')
def index():
    """Home page with Lambda function list"""
    return jsonify({
        'message': 'AWS Lambda Demonstration Application',
        'availableFunctions': [
            {
                'name': 'hello_world_handler',
                'endpoint': '/lambda/hello',
                'method': 'POST',
                'description': 'Simple greeting Lambda function',
                'example': {'name': 'John'}
            },
            {
                'name': 'data_processor_handler',
                'endpoint': '/lambda/process',
                'method': 'POST',
                'description': 'Data processing Lambda function',
                'example': {'data': [1, 2, 3, 4, 5]}
            },
            {
                'name': 'api_gateway_handler',
                'endpoint': '/lambda/api',
                'method': 'POST',
                'description': 'API Gateway integration example',
                'example': {'httpMethod': 'GET', 'path': '/users', 'queryStringParameters': {'id': '123'}}
            },
            {
                'name': 'scheduled_event_handler',
                'endpoint': '/lambda/scheduled',
                'method': 'POST',
                'description': 'Scheduled event handler (CloudWatch Events)',
                'example': {'source': 'aws.events', 'detail-type': 'Scheduled Event'}
            },
            {
                'name': 'error_handler_demo',
                'endpoint': '/lambda/error',
                'method': 'POST',
                'description': 'Error handling demonstration',
                'example': {'shouldFail': False}
            }
        ],
        'usage': 'POST to any endpoint with JSON body matching the example'
    })


@app.route('/lambda/hello', methods=['POST'])
def hello_route():
    return hello_world_handler()


@app.route('/lambda/process', methods=['POST'])
def process_route():
    return data_processor_handler()


@app.route('/lambda/api', methods=['POST'])
def api_route():
    return api_gateway_handler()


@app.route('/lambda/scheduled', methods=['POST'])
def scheduled_route():
    return scheduled_event_handler()


@app.route('/lambda/error', methods=['POST'])
def error_route():
    return error_handler_demo()


if __name__ == '__main__':
    print("=" * 60)
    print("AWS Lambda Demonstration Application")
    print("=" * 60)
    print("\nAvailable endpoints:")
    print("  GET  / - List all Lambda functions")
    print("  POST /lambda/hello - Hello World handler")
    print("  POST /lambda/process - Data processor handler")
    print("  POST /lambda/api - API Gateway handler")
    print("  POST /lambda/scheduled - Scheduled event handler")
    print("  POST /lambda/error - Error handler demo")
    print("\nStarting Flask server on http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)

