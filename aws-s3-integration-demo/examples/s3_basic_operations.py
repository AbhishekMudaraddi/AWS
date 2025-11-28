#!/usr/bin/env python3
import boto3
from botocore.exceptions import ClientError
import json

s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')

def create_bucket(bucket_name, region='us-east-1'):
    try:
        if region == 'us-east-1':
            response = s3_client.create_bucket(Bucket=bucket_name)
        else:
            response = s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        print(f"Bucket '{bucket_name}' created successfully")
        return response
    except ClientError as e:
        print(f"Error creating bucket: {e}")
        return None

def upload_file(file_path, bucket_name, object_name=None):
    if object_name is None:
        object_name = file_path
    try:
        s3_client.upload_file(file_path, bucket_name, object_name)
        print(f"File '{file_path}' uploaded to '{bucket_name}/{object_name}'")
        return True
    except ClientError as e:
        print(f"Error uploading file: {e}")
        return False

def upload_fileobj(file_obj, bucket_name, object_name):
    try:
        s3_client.upload_fileobj(file_obj, bucket_name, object_name)
        print(f"File object uploaded to '{bucket_name}/{object_name}'")
        return True
    except ClientError as e:
        print(f"Error uploading file object: {e}")
        return False

def download_file(bucket_name, object_name, local_file_path):
    try:
        s3_client.download_file(bucket_name, object_name, local_file_path)
        print(f"File '{object_name}' downloaded to '{local_file_path}'")
        return True
    except ClientError as e:
        print(f"Error downloading file: {e}")
        return False

def download_fileobj(bucket_name, object_name, file_obj):
    try:
        s3_resource.Bucket(bucket_name).Object(object_name).download_fileobj(file_obj)
        print(f"File '{object_name}' downloaded to file object")
        return True
    except ClientError as e:
        print(f"Error downloading file object: {e}")
        return False

def list_buckets():
    try:
        response = s3_client.list_buckets()
        buckets = [bucket['Name'] for bucket in response['Buckets']]
        print(f"Available buckets: {buckets}")
        return buckets
    except ClientError as e:
        print(f"Error listing buckets: {e}")
        return []

def list_objects(bucket_name, prefix=''):
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        if 'Contents' in response:
            objects = [obj['Key'] for obj in response['Contents']]
            print(f"Objects in '{bucket_name}': {objects}")
            return objects
        else:
            print(f"No objects found in '{bucket_name}'")
            return []
    except ClientError as e:
        print(f"Error listing objects: {e}")
        return []

def get_object(bucket_name, object_name):
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=object_name)
        content = response['Body'].read()
        print(f"Retrieved object '{object_name}' from '{bucket_name}'")
        return content
    except ClientError as e:
        print(f"Error getting object: {e}")
        return None

def delete_object(bucket_name, object_name):
    try:
        s3_client.delete_object(Bucket=bucket_name, Key=object_name)
        print(f"Object '{object_name}' deleted from '{bucket_name}'")
        return True
    except ClientError as e:
        print(f"Error deleting object: {e}")
        return False

def delete_bucket(bucket_name):
    try:
        s3_client.delete_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' deleted")
        return True
    except ClientError as e:
        print(f"Error deleting bucket: {e}")
        return False

def put_object(bucket_name, object_name, content):
    try:
        s3_client.put_object(Bucket=bucket_name, Key=object_name, Body=content)
        print(f"Object '{object_name}' created in '{bucket_name}'")
        return True
    except ClientError as e:
        print(f"Error putting object: {e}")
        return False

def copy_object(source_bucket, source_key, dest_bucket, dest_key):
    try:
        copy_source = {'Bucket': source_bucket, 'Key': source_key}
        s3_resource.meta.client.copy(copy_source, dest_bucket, dest_key)
        print(f"Object copied from '{source_bucket}/{source_key}' to '{dest_bucket}/{dest_key}'")
        return True
    except ClientError as e:
        print(f"Error copying object: {e}")
        return False

def get_object_metadata(bucket_name, object_name):
    try:
        response = s3_client.head_object(Bucket=bucket_name, Key=object_name)
        metadata = {
            'ContentType': response.get('ContentType'),
            'ContentLength': response.get('ContentLength'),
            'LastModified': response.get('LastModified'),
            'ETag': response.get('ETag'),
            'Metadata': response.get('Metadata', {})
        }
        print(f"Metadata for '{object_name}': {json.dumps(metadata, indent=2, default=str)}")
        return metadata
    except ClientError as e:
        print(f"Error getting metadata: {e}")
        return None

def set_object_acl(bucket_name, object_name, acl='private'):
    try:
        s3_client.put_object_acl(Bucket=bucket_name, Key=object_name, ACL=acl)
        print(f"ACL set to '{acl}' for '{object_name}'")
        return True
    except ClientError as e:
        print(f"Error setting ACL: {e}")
        return False

def generate_presigned_url(bucket_name, object_name, expiration=3600):
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': object_name},
            ExpiresIn=expiration
        )
        print(f"Presigned URL generated for '{object_name}' (expires in {expiration}s)")
        return url
    except ClientError as e:
        print(f"Error generating presigned URL: {e}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("AWS S3 Basic Operations - Template Code")
    print("=" * 60)
    print("\nThis is a template demonstrating S3 operations.")
    print("Configure AWS credentials before running:")
    print("  aws configure")
    print("  OR")
    print("  export AWS_ACCESS_KEY_ID=your_key")
    print("  export AWS_SECRET_ACCESS_KEY=your_secret")
    print("\nExample usage:")
    print("  list_buckets()")
    print("  create_bucket('my-bucket-name')")
    print("  upload_file('local_file.txt', 'my-bucket-name', 'remote_file.txt')")
    print("=" * 60)

