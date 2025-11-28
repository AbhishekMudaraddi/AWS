#!/usr/bin/env python3
import boto3
from botocore.exceptions import ClientError
import json
from datetime import datetime, timedelta

s3_client = boto3.client('s3')

def enable_versioning(bucket_name):
    try:
        s3_client.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        print(f"Versioning enabled for bucket '{bucket_name}'")
        return True
    except ClientError as e:
        print(f"Error enabling versioning: {e}")
        return False

def enable_lifecycle_policy(bucket_name, transition_days=30, expiration_days=365):
    try:
        lifecycle_config = {
            'Rules': [
                {
                    'ID': 'TransitionToIA',
                    'Status': 'Enabled',
                    'Transitions': [
                        {
                            'Days': transition_days,
                            'StorageClass': 'STANDARD_IA'
                        }
                    ],
                    'Expiration': {
                        'Days': expiration_days
                    }
                }
            ]
        }
        s3_client.put_bucket_lifecycle_configuration(
            Bucket=bucket_name,
            LifecycleConfiguration=lifecycle_config
        )
        print(f"Lifecycle policy configured for bucket '{bucket_name}'")
        return True
    except ClientError as e:
        print(f"Error configuring lifecycle policy: {e}")
        return False

def enable_encryption(bucket_name, encryption_type='AES256'):
    try:
        if encryption_type == 'AES256':
            encryption_config = {
                'Rules': [{'ApplyServerSideEncryptionByDefault': {'SSEAlgorithm': 'AES256'}}]
            }
        else:
            encryption_config = {
                'Rules': [{'ApplyServerSideEncryptionByDefault': {'SSEAlgorithm': 'aws:kms'}}]
            }
        s3_client.put_bucket_encryption(
            Bucket=bucket_name,
            ServerSideEncryptionConfiguration=encryption_config
        )
        print(f"Encryption enabled for bucket '{bucket_name}'")
        return True
    except ClientError as e:
        print(f"Error enabling encryption: {e}")
        return False

def configure_cors(bucket_name, allowed_origins=['*'], allowed_methods=['GET', 'PUT', 'POST', 'DELETE']):
    try:
        cors_config = {
            'CORSRules': [
                {
                    'AllowedOrigins': allowed_origins,
                    'AllowedMethods': allowed_methods,
                    'AllowedHeaders': ['*'],
                    'ExposeHeaders': ['ETag'],
                    'MaxAgeSeconds': 3000
                }
            ]
        }
        s3_client.put_bucket_cors(Bucket=bucket_name, CORSConfiguration=cors_config)
        print(f"CORS configured for bucket '{bucket_name}'")
        return True
    except ClientError as e:
        print(f"Error configuring CORS: {e}")
        return False

def enable_static_website_hosting(bucket_name, index_document='index.html', error_document='error.html'):
    try:
        s3_client.put_bucket_website(
            Bucket=bucket_name,
            WebsiteConfiguration={
                'IndexDocument': {'Suffix': index_document},
                'ErrorDocument': {'Key': error_document}
            }
        )
        website_url = f"http://{bucket_name}.s3-website-{s3_client.meta.region_name}.amazonaws.com"
        print(f"Static website hosting enabled: {website_url}")
        return website_url
    except ClientError as e:
        print(f"Error enabling website hosting: {e}")
        return None

def set_bucket_policy(bucket_name, policy_json):
    try:
        s3_client.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(policy_json))
        print(f"Bucket policy set for '{bucket_name}'")
        return True
    except ClientError as e:
        print(f"Error setting bucket policy: {e}")
        return False

def enable_logging(source_bucket, target_bucket, target_prefix='logs/'):
    try:
        s3_client.put_bucket_logging(
            Bucket=source_bucket,
            BucketLoggingStatus={
                'LoggingEnabled': {
                    'TargetBucket': target_bucket,
                    'TargetPrefix': target_prefix
                }
            }
        )
        print(f"Logging enabled for '{source_bucket}' -> '{target_bucket}/{target_prefix}'")
        return True
    except ClientError as e:
        print(f"Error enabling logging: {e}")
        return False

def create_multipart_upload(bucket_name, object_name):
    try:
        response = s3_client.create_multipart_upload(Bucket=bucket_name, Key=object_name)
        upload_id = response['UploadId']
        print(f"Multipart upload initiated: {upload_id}")
        return upload_id
    except ClientError as e:
        print(f"Error creating multipart upload: {e}")
        return None

def upload_part(bucket_name, object_name, upload_id, part_number, data):
    try:
        response = s3_client.upload_part(
            Bucket=bucket_name,
            Key=object_name,
            PartNumber=part_number,
            UploadId=upload_id,
            Body=data
        )
        etag = response['ETag']
        print(f"Part {part_number} uploaded, ETag: {etag}")
        return {'PartNumber': part_number, 'ETag': etag}
    except ClientError as e:
        print(f"Error uploading part: {e}")
        return None

def complete_multipart_upload(bucket_name, object_name, upload_id, parts):
    try:
        s3_client.complete_multipart_upload(
            Bucket=bucket_name,
            Key=object_name,
            UploadId=upload_id,
            MultipartUpload={'Parts': parts}
        )
        print(f"Multipart upload completed for '{object_name}'")
        return True
    except ClientError as e:
        print(f"Error completing multipart upload: {e}")
        return False

def get_bucket_notification_config(bucket_name):
    try:
        response = s3_client.get_bucket_notification_configuration(Bucket=bucket_name)
        print(f"Notification configuration: {json.dumps(response, indent=2, default=str)}")
        return response
    except ClientError as e:
        print(f"Error getting notification config: {e}")
        return None

def configure_event_notifications(bucket_name, lambda_function_arn=None, sns_topic_arn=None, sqs_queue_arn=None):
    try:
        notification_config = {}
        if lambda_function_arn:
            notification_config['LambdaFunctionConfigurations'] = [{
                'LambdaFunctionArn': lambda_function_arn,
                'Events': ['s3:ObjectCreated:*'],
                'Filter': {'Key': {'FilterRules': [{'Name': 'prefix', 'Value': 'uploads/'}]}}
            }]
        if sns_topic_arn:
            notification_config['TopicConfigurations'] = [{
                'TopicArn': sns_topic_arn,
                'Events': ['s3:ObjectCreated:*']
            }]
        if sqs_queue_arn:
            notification_config['QueueConfigurations'] = [{
                'QueueArn': sqs_queue_arn,
                'Events': ['s3:ObjectCreated:*']
            }]
        s3_client.put_bucket_notification_configuration(
            Bucket=bucket_name,
            NotificationConfiguration=notification_config
        )
        print(f"Event notifications configured for '{bucket_name}'")
        return True
    except ClientError as e:
        print(f"Error configuring notifications: {e}")
        return False

def generate_presigned_post(bucket_name, object_name, expiration=3600, max_size=10485760):
    try:
        response = s3_client.generate_presigned_post(
            Bucket=bucket_name,
            Key=object_name,
            Fields={'acl': 'private'},
            Conditions=[
                {'acl': 'private'},
                ['content-length-range', 1, max_size]
            ],
            ExpiresIn=expiration
        )
        print(f"Presigned POST URL generated for '{object_name}'")
        return response
    except ClientError as e:
        print(f"Error generating presigned POST: {e}")
        return None

def list_object_versions(bucket_name, prefix=''):
    try:
        response = s3_client.list_object_versions(Bucket=bucket_name, Prefix=prefix)
        versions = []
        if 'Versions' in response:
            for version in response['Versions']:
                versions.append({
                    'Key': version['Key'],
                    'VersionId': version['VersionId'],
                    'IsLatest': version['IsLatest'],
                    'LastModified': version['LastModified']
                })
        print(f"Found {len(versions)} versions for prefix '{prefix}'")
        return versions
    except ClientError as e:
        print(f"Error listing versions: {e}")
        return []

if __name__ == "__main__":
    print("=" * 60)
    print("AWS S3 Advanced Features - Template Code")
    print("=" * 60)
    print("\nThis template demonstrates advanced S3 features.")
    print("Configure AWS credentials before running.")
    print("=" * 60)

