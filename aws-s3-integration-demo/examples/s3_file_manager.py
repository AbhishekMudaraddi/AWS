#!/usr/bin/env python3
import boto3
import os
from pathlib import Path
from botocore.exceptions import ClientError

s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')

class S3FileManager:
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.bucket = s3_resource.Bucket(bucket_name)
    
    def upload_directory(self, local_dir, s3_prefix=''):
        uploaded_files = []
        local_path = Path(local_dir)
        
        for file_path in local_path.rglob('*'):
            if file_path.is_file():
                relative_path = file_path.relative_to(local_path)
                s3_key = f"{s3_prefix}/{relative_path}".replace('\\', '/').lstrip('/')
                
                try:
                    self.bucket.upload_file(str(file_path), s3_key)
                    uploaded_files.append(s3_key)
                    print(f"Uploaded: {file_path} -> s3://{self.bucket_name}/{s3_key}")
                except ClientError as e:
                    print(f"Error uploading {file_path}: {e}")
        
        return uploaded_files
    
    def download_directory(self, s3_prefix, local_dir):
        downloaded_files = []
        local_path = Path(local_dir)
        local_path.mkdir(parents=True, exist_ok=True)
        
        try:
            objects = self.bucket.objects.filter(Prefix=s3_prefix)
            for obj in objects:
                s3_key = obj.key
                relative_path = s3_key.replace(s3_prefix, '').lstrip('/')
                local_file_path = local_path / relative_path
                local_file_path.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    self.bucket.download_file(s3_key, str(local_file_path))
                    downloaded_files.append(str(local_file_path))
                    print(f"Downloaded: s3://{self.bucket_name}/{s3_key} -> {local_file_path}")
                except ClientError as e:
                    print(f"Error downloading {s3_key}: {e}")
        except ClientError as e:
            print(f"Error listing objects: {e}")
        
        return downloaded_files
    
    def sync_directory(self, local_dir, s3_prefix='', delete=False):
        local_path = Path(local_dir)
        local_files = {str(f.relative_to(local_path)): f.stat().st_mtime 
                      for f in local_path.rglob('*') if f.is_file()}
        
        try:
            s3_objects = {obj.key.replace(s3_prefix, '').lstrip('/'): obj.last_modified.timestamp()
                          for obj in self.bucket.objects.filter(Prefix=s3_prefix)}
            
            for local_file, local_mtime in local_files.items():
                s3_key = f"{s3_prefix}/{local_file}".replace('\\', '/').lstrip('/')
                if local_file not in s3_objects or local_mtime > s3_objects[local_file]:
                    try:
                        self.bucket.upload_file(str(local_path / local_file), s3_key)
                        print(f"Synced: {local_file} -> s3://{self.bucket_name}/{s3_key}")
                    except ClientError as e:
                        print(f"Error syncing {local_file}: {e}")
            
            if delete:
                for s3_file in s3_objects:
                    if s3_file not in local_files:
                        s3_key = f"{s3_prefix}/{s3_file}".replace('\\', '/').lstrip('/')
                        try:
                            self.bucket.Object(s3_key).delete()
                            print(f"Deleted: s3://{self.bucket_name}/{s3_key}")
                        except ClientError as e:
                            print(f"Error deleting {s3_key}: {e}")
        except ClientError as e:
            print(f"Error syncing: {e}")
    
    def get_file_size(self, s3_key):
        try:
            obj = self.bucket.Object(s3_key)
            return obj.content_length
        except ClientError as e:
            print(f"Error getting file size: {e}")
            return None
    
    def list_files_recursive(self, prefix=''):
        files = []
        try:
            for obj in self.bucket.objects.filter(Prefix=prefix):
                files.append({
                    'key': obj.key,
                    'size': obj.size,
                    'last_modified': obj.last_modified
                })
        except ClientError as e:
            print(f"Error listing files: {e}")
        return files
    
    def delete_files_by_prefix(self, prefix):
        deleted_count = 0
        try:
            objects = [{'Key': obj.key} for obj in self.bucket.objects.filter(Prefix=prefix)]
            if objects:
                response = self.bucket.delete_objects(
                    Delete={'Objects': objects}
                )
                deleted_count = len(response.get('Deleted', []))
                print(f"Deleted {deleted_count} files with prefix '{prefix}'")
        except ClientError as e:
            print(f"Error deleting files: {e}")
        return deleted_count

if __name__ == "__main__":
    print("=" * 60)
    print("AWS S3 File Manager - Template Code")
    print("=" * 60)
    print("\nExample usage:")
    print("  manager = S3FileManager('my-bucket')")
    print("  manager.upload_directory('./local_folder', 'remote_folder')")
    print("  manager.download_directory('remote_folder', './downloads')")
    print("  manager.sync_directory('./local_folder', 'remote_folder')")
    print("=" * 60)

