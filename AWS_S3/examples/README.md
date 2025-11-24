# AWS S3 Code Examples

This directory contains practical Python code examples demonstrating various AWS S3 operations.

## Files Overview

### `s3_basic_operations.py`
Core S3 operations including:
- Bucket creation and deletion
- File upload/download
- Object listing and retrieval
- Object deletion
- Copying objects
- Metadata operations
- ACL management
- Presigned URL generation

### `s3_advanced_features.py`
Advanced S3 features including:
- Versioning
- Lifecycle policies
- Encryption configuration
- CORS setup
- Static website hosting
- Bucket policies
- Logging configuration
- Multipart uploads
- Event notifications
- Presigned POST URLs

### `s3_file_manager.py`
File management utilities:
- Directory upload/download
- Directory synchronization
- Recursive file operations
- Batch operations

## Prerequisites

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure AWS credentials:**
   ```bash
   aws configure
   ```
   Or set environment variables:
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_DEFAULT_REGION=us-east-1
   ```

## Usage

### Basic Operations
```python
from s3_basic_operations import *

list_buckets()
create_bucket('my-bucket-name')
upload_file('local_file.txt', 'my-bucket-name', 'remote_file.txt')
download_file('my-bucket-name', 'remote_file.txt', 'downloaded_file.txt')
```

### Advanced Features
```python
from s3_advanced_features import *

enable_versioning('my-bucket-name')
enable_encryption('my-bucket-name')
enable_static_website_hosting('my-bucket-name')
```

### File Manager
```python
from s3_file_manager import S3FileManager

manager = S3FileManager('my-bucket-name')
manager.upload_directory('./local_folder', 'remote_folder')
manager.download_directory('remote_folder', './downloads')
manager.sync_directory('./local_folder', 'remote_folder')
```

## Important Notes

- These are template examples for demonstration purposes
- Review and modify code before using in production
- Always follow AWS security best practices
- Never commit AWS credentials to version control
- Test in a development environment first

## Error Handling

All functions include error handling using `ClientError` exceptions. Review error messages to troubleshoot issues.

## Security Considerations

- Use IAM roles instead of access keys when possible
- Enable encryption for sensitive data
- Set appropriate bucket policies
- Use presigned URLs for temporary access
- Regularly audit bucket permissions

