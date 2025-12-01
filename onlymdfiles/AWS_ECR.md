# AWS ECR - Container Registry

## What is ECR?

Amazon ECR (Elastic Container Registry) is a fully managed Docker container registry that makes it easy to store, manage, and deploy Docker container images.

## Why ECR in This Project?

1. **Docker Image Storage**: Stores Docker images for Flask application
2. **Integration**: Seamlessly integrates with Elastic Beanstalk
3. **Security**: Private registry with IAM-based access control
4. **Versioning**: Stores multiple versions of images (tags)
5. **Cost-Effective**: Pay only for storage used

## How ECR is Used in This Project

ECR stores Docker images:
- **Repository**: `smart-budget-planner`
- **Images**: Flask application Docker images
- **Tags**: `latest` and commit SHA (e.g., `abc123def456`)
- **Used by**: Elastic Beanstalk pulls images from ECR for deployment

## Implementation Files

### Primary Files:
1. **`scripts/setup_ecr.py`** - Creates ECR repository
2. **`.github/workflows/deploy.yml`** - Builds and pushes images to ECR
3. **`Dockerfile`** - Defines image build instructions

### Usage:
- **GitHub Actions** - Builds image and pushes to ECR
- **Elastic Beanstalk** - Pulls image from ECR to deploy

## Code Structure

### 1. ECR Setup (`scripts/setup_ecr.py`)

```python
def create_ecr_repository():
    ecr_client = session.client('ecr', region_name=AWSConfig.REGION)
    repository_name = AWSConfig.ECR_REPOSITORY
    
    try:
        response = ecr_client.create_repository(
            RepositoryName=repository_name,
            ImageTagMutability='MUTABLE',
            ImageScanningConfiguration={
                'ScanOnPush': True
            }
        )
        return response['Repository']['RepositoryUri']
    except ClientError as e:
        if e.response['Error']['Code'] == 'RepositoryAlreadyExistsException':
            # Repository exists, get URI
            response = ecr_client.describe_repositories(
                RepositoryNames=[repository_name]
            )
            return response['Repositories'][0]['RepositoryUri']
        raise
```

**What it does**: Creates ECR repository if it doesn't exist.

**Repository URI Format**: `{account_id}.dkr.ecr.{region}.amazonaws.com/{repository_name}`

**Example**: `503561414328.dkr.ecr.us-east-1.amazonaws.com/smart-budget-planner`

### 2. GitHub Actions - Build and Push (`.github/workflows/deploy.yml`)

#### Building Docker Image
```yaml
- name: Build Docker image
  run: |
    IMAGE_TAG=${{ github.sha }}
    ECR_URI=${{ env.AWS_ACCOUNT_ID }}.dkr.ecr.${{ env.AWS_REGION }}.amazonaws.com/${{ env.ECR_REPOSITORY }}
    
    docker build -t $ECR_URI:$IMAGE_TAG .
    docker tag $ECR_URI:$IMAGE_TAG $ECR_URI:latest
```

**What it does**:
- Builds Docker image from Dockerfile
- Tags image with commit SHA (unique version)
- Tags same image as `latest` (for easy reference)

#### Pushing to ECR
```yaml
- name: Push image to Amazon ECR
  run: |
    docker push $ECR_URI:$IMAGE_TAG
    docker push $ECR_URI:latest
```

**What it does**: Pushes both tagged images to ECR repository.

**Authentication**: GitHub Actions logs into ECR using AWS credentials before pushing.

### 3. Dockerfile

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

**What it does**: Defines how to build Docker image.

**Used by**: Docker build command in GitHub Actions

## Image Tagging Strategy

### Tags Used:
1. **Commit SHA**: `abc123def456...` (unique, immutable)
2. **Latest**: `latest` (always points to most recent build)

### Why Both Tags?
- **Commit SHA**: Specific version for deployment (traceable)
- **Latest**: Convenient reference for docker-compose.yml

## Image Lifecycle

```
Developer Pushes Code
    ↓
GitHub Actions Triggered
    ↓
Build Docker Image (from Dockerfile)
    ↓
Tag Image (commit SHA + latest)
    ↓
Push to ECR
    ↓
Image Stored in ECR
    ↓
EB Pulls Image from ECR
    ↓
EB Runs Container
```

## How to Explain in Class

### When Asked: "Why use ECR instead of Docker Hub?"

**Answer**:
- **Integration**: Seamless integration with other AWS services (EB, ECS)
- **Security**: Private registry, IAM-based access control
- **Performance**: Faster image pulls (same AWS network)
- **Cost**: First 500MB free per month, then $0.10 per GB/month
- **Compliance**: Images stored in your AWS account, better for compliance

### When Asked: "How does image building and pushing work?"

**Answer**:
1. **GitHub Actions** → Workflow triggered on code push
2. **Login to ECR** → Authenticates Docker client with ECR
3. **Build Image** → `docker build` creates image from Dockerfile
4. **Tag Image** → Tags with commit SHA and `latest`
5. **Push to ECR** → `docker push` uploads image to ECR repository
6. **Image Stored** → Image available in ECR for EB to pull

**Code Flow**:
```
.github/workflows/deploy.yml
  → Login to ECR
  → docker build -t $ECR_URI:$IMAGE_TAG .
  → docker push $ECR_URI:$IMAGE_TAG
  → docker push $ECR_URI:latest
```

### When Asked: "Show me how EB uses ECR images"

**Answer**:
- **docker-compose.yml** → Specifies ECR image URI
- **EB Deployment** → EB reads docker-compose.yml
- **Image Pull** → EB pulls image from ECR
- **Container Run** → EB runs container from pulled image

**Code**:
```yaml
# docker-compose.yml
services:
  app:
    image: 503561414328.dkr.ecr.us-east-1.amazonaws.com/smart-budget-planner:latest
```

**EB Process**:
1. Reads docker-compose.yml
2. Authenticates with ECR (using instance role)
3. Pulls image: `docker pull {ECR_URI}:latest`
4. Runs container: `docker-compose up`

### When Asked: "What happens if you push a new image?"

**Answer**:
- **New Image Created** → New image pushed to ECR with new tag
- **docker-compose.yml Updated** → GitHub Actions updates docker-compose.yml with new image tag
- **EB Version Created** → New EB application version created
- **Environment Updated** → EB environment updated with new version
- **Image Pulled** → EB pulls new image from ECR
- **Container Restarted** → New container runs with new image
- **Zero Downtime** → EB uses rolling deployment (new instances before terminating old)

### When Asked: "How do you version images?"

**Answer**:
- **Commit SHA Tag**: Each build tagged with Git commit SHA (e.g., `abc123def`)
- **Latest Tag**: Always points to most recent build
- **Benefits**: 
  - Can rollback to specific commit
  - Can track which code version is deployed
  - Immutable tags (commit SHA doesn't change)

**Example**:
```
Image: 503561414328.dkr.ecr.us-east-1.amazonaws.com/smart-budget-planner:abc123def
Image: 503561414328.dkr.ecr.us-east-1.amazonaws.com/smart-budget-planner:latest
```

## Repository Configuration

### Repository Details
- **Name**: `smart-budget-planner`
- **Region**: us-east-1
- **URI**: `503561414328.dkr.ecr.us-east-1.amazonaws.com/smart-budget-planner`
- **Tag Mutability**: MUTABLE (tags can be overwritten)
- **Image Scanning**: Enabled (scans for vulnerabilities on push)

### Access Control
- **IAM Roles**: EB instance role has `ecr:GetAuthorizationToken`, `ecr:BatchGetImage` permissions
- **GitHub Actions**: Uses AWS credentials to push images
- **Private**: Repository is private (only accessible with AWS credentials)

## Key Concepts to Remember

1. **Repository**: Container for Docker images (like a folder)
2. **Image**: Built Docker container image
3. **Tag**: Label for image version (commit SHA, latest, etc.)
4. **Push**: Upload image to ECR
5. **Pull**: Download image from ECR
6. **Image URI**: Full path to image (account.dkr.ecr.region.amazonaws.com/repo:tag)

## Common Questions & Answers

**Q: Why not use Docker Hub?**
A: ECR provides better integration with AWS services, private registry by default, and faster pulls within AWS network.

**Q: How much does ECR cost?**
A: First 500MB free per month, then $0.10 per GB/month. Very cost-effective for this project.

**Q: What happens to old images?**
A: Images remain in ECR unless manually deleted. Can set lifecycle policy to auto-delete old images.

**Q: How do you pull images locally?**
A: `aws ecr get-login-password | docker login --username AWS --password-stdin {ECR_URI}` then `docker pull {image}`

**Q: Can multiple environments use same image?**
A: Yes, multiple EB environments can pull same image from ECR. Each environment can use different tags.

**Q: How do you rollback to previous version?**
A: Update docker-compose.yml with previous commit SHA tag, create new EB version, update environment.

