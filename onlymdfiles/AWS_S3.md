# AWS S3 - Storage Service

## What is S3?

Amazon S3 (Simple Storage Service) is an object storage service that provides scalable storage for files, images, documents, and any type of data.

## Why S3 in This Project?

1. **Receipt Storage**: Store user-uploaded receipt images/PDFs
2. **Report Storage**: Store generated PDF reports
3. **Scalable**: Handles unlimited file storage
4. **Secure**: Private bucket with presigned URLs for access
5. **Cost-Effective**: Pay only for storage used

## How S3 is Used in This Project

S3 stores two types of files:
- **Receipts**: User-uploaded receipt images/PDFs (`receipts/{user_id}/{expense_id}.{ext}`)
- **Reports**: Generated PDF reports (`reports/{user_id}/{report_name}.pdf`)

## Implementation Files

### Primary Files:
1. **`aws_config/setup_s3.py`** - Main S3 client class (SDK wrapper)
2. **`lib/receipt_handler.py`** - Handles receipt upload/download logic
3. **`aws_config/resource_manager.py`** - Creates S3 bucket

### Usage in Application:
- **`app.py`** - Uses S3Client for receipt uploads and report downloads
- **`lib/receipt_handler.py`** - Wraps S3Client with validation logic
- **Lambda Functions** - Upload generated reports to S3

## Code Structure

### 1. Configuration (`aws_config/config.py`)

```python
S3_BUCKET = os.getenv('S3_BUCKET_NAME', 'smart-budget-receipts')
```

**Explanation**: S3 bucket name used for all file storage.

### 2. S3 Client (`aws_config/setup_s3.py`)

**Key Methods:**

#### Uploading Receipt
```python
def upload_receipt(self, file_content, file_extension, user_id, expense_id=None):
    if expense_id:
        key = f"receipts/{user_id}/{expense_id}.{file_extension}"
    else:
        key = f"receipts/{user_id}/{uuid.uuid4()}.{file_extension}"
    
    self.s3_client.put_object(
        Bucket=self.bucket_name,
        Key=key,
        Body=file_content,
        ContentType=self._get_content_type(file_extension)
    )
    return key
```

**What it does**: Uploads receipt file to S3 with organized folder structure.

**File Path Structure**: `receipts/{user_id}/{expense_id}.jpg`

**Used in**: `lib/receipt_handler.py` → `app.py` - `/api/receipts/upload` route

#### Generating Presigned URL
```python
def generate_presigned_url(self, object_name, expiration=3600):
    url = self.s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': self.bucket_name, 'Key': object_name},
        ExpiresIn=expiration
    )
    return url
```

**What it does**: Creates temporary URL (valid for 1 hour) to access private S3 file.

**Why Presigned URLs**: S3 bucket is private. Presigned URLs allow temporary access without exposing bucket publicly.

**Used in**: `app.py` - `/api/receipts/view/<object_name>` route

#### Uploading Report
```python
def upload_report(self, file_content, file_name, user_id):
    key = f"reports/{user_id}/{file_name}"
    self.s3_client.put_object(
        Bucket=self.bucket_name,
        Key=key,
        Body=file_content,
        ContentType='application/pdf'
    )
    return key
```

**What it does**: Uploads generated PDF report to S3.

**File Path Structure**: `reports/{user_id}/monthly-report-2024-01.pdf`

**Used in**: Lambda report generator function

#### Listing User Reports
```python
def list_user_reports(self, user_id):
    prefix = f"reports/{user_id}/"
    response = self.s3_client.list_objects_v2(
        Bucket=self.bucket_name,
        Prefix=prefix
    )
    
    reports = []
    for obj in response.get('Contents', []):
        reports.append({
            'key': obj['Key'],
            'name': obj['Key'].split('/')[-1],
            'size': obj['Size'],
            'last_modified': obj['LastModified'].isoformat()
        })
    return reports
```

**What it does**: Lists all reports for a specific user.

**Used in**: `app.py` - `/api/reports` GET route

### 3. Receipt Handler (`lib/receipt_handler.py`)

**Purpose**: Wraps S3Client with validation and business logic.

#### File Validation
```python
def validate_file_type(self, filename):
    file_extension = filename.rsplit('.', 1)[-1].lower()
    if file_extension not in self.allowed_extensions:
        return False, f"File type not allowed"
    return True, file_extension

def validate_file_size(self, file_content):
    if len(file_content) > self.max_file_size:  # 10MB
        return False, "File size exceeds maximum"
    return True, None
```

**What it does**: Validates file type (jpg, png, pdf) and size (max 10MB) before upload.

**Used in**: `app.py` - Before uploading receipt

## File Organization Structure

```
smart-budget-receipts/
├── receipts/
│   ├── {user_id_1}/
│   │   ├── {expense_id_1}.jpg
│   │   ├── {expense_id_2}.pdf
│   │   └── ...
│   ├── {user_id_2}/
│   │   └── ...
│   └── ...
└── reports/
    ├── {user_id_1}/
    │   ├── monthly-report-2024-01.pdf
    │   ├── weekly-report-2024-01-15.pdf
    │   └── ...
    └── ...
```

## How to Explain in Class

### When Asked: "Why use S3 for file storage?"

**Answer**:
- **Scalability**: Can store unlimited files without managing storage servers
- **Reliability**: 99.999999999% (11 9's) durability
- **Cost**: Pay only for storage used, cheaper than maintaining servers
- **Security**: Private bucket with controlled access via presigned URLs
- **Integration**: Easy integration with other AWS services (Lambda, EB)

### When Asked: "How does receipt upload work?"

**Answer**:
1. **User uploads file** → Flask receives file in `/api/receipts/upload` route
2. **Validation** → `ReceiptHandler` validates file type and size
3. **Upload to S3** → `S3Client.upload_receipt()` uploads file to S3
4. **Store key** → S3 key (path) stored in DynamoDB expense record
5. **Return key** → Key returned to frontend for later retrieval

**Code Flow**:
```
app.py (line 593) 
  → receipt_handler.upload_receipt() 
    → s3_client.upload_receipt() 
      → S3 Bucket
```

### When Asked: "How do users view their receipts?"

**Answer**:
1. **Request URL** → Frontend requests `/api/receipts/view/<object_name>`
2. **Generate Presigned URL** → `S3Client.generate_presigned_url()` creates temporary URL
3. **Return URL** → Presigned URL (valid 1 hour) returned to frontend
4. **Display** → Frontend displays image using presigned URL

**Why Presigned URLs**: 
- S3 bucket is private (secure)
- Presigned URLs provide temporary access without making bucket public
- URLs expire after 1 hour (configurable)

### When Asked: "Show me the code for uploading a receipt"

**Answer**:
- **File**: `aws_config/s3_client.py`
- **Method**: `upload_receipt()` - Line 12-24
- **Called from**: `lib/receipt_handler.py` line 44
- **Used in**: `app.py` line 593 in `/api/receipts/upload` route

**Code**:
```python
# In app.py
receipt_file = request.files.get('receipt')
if receipt_file:
    receipt_url = receipt_handler.upload_receipt(
        receipt_file.read(), 
        receipt_file.filename, 
        user['user_id']
    )
```

### When Asked: "How are reports stored in S3?"

**Answer**:
- **Generated by**: Lambda function (`lambda_functions/report_generator/`)
- **Uploaded to**: S3 via `s3_client.put_object()` in Lambda
- **Path**: `reports/{user_id}/{report_name}.pdf`
- **Listed by**: `S3Client.list_user_reports()` - queries S3 with prefix filter
- **Downloaded via**: Presigned URL generated by `S3Client.generate_presigned_url()`

## Key Concepts to Remember

1. **Bucket**: Container for all files (like a folder)
2. **Key**: File path/name in bucket (e.g., `receipts/user123/expense456.jpg`)
3. **Presigned URL**: Temporary URL for accessing private files
4. **Prefix**: Used for filtering files (e.g., `reports/user123/` lists all user's reports)
5. **ContentType**: MIME type (image/jpeg, application/pdf)

## Common Questions & Answers

**Q: Why not store files in the application server?**
A: Application servers are stateless and can be replaced. S3 provides persistent, scalable storage independent of servers.

**Q: What happens if S3 is down?**
A: AWS S3 has 99.99% availability SLA. If down, uploads/downloads will fail gracefully with error messages.

**Q: How do you ensure users can only access their own files?**
A: File paths include user_id. Backend validates user_id matches logged-in user before generating presigned URL.

**Q: Why use presigned URLs instead of making bucket public?**
A: Security - public bucket allows anyone to access files. Presigned URLs provide temporary, controlled access.

**Q: How much does S3 storage cost?**
A: Very cheap - approximately $0.023 per GB/month. For this project with receipts and reports, likely under $1/month.
