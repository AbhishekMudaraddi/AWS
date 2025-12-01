# AWS Elastic Beanstalk - Application Hosting

## What is Elastic Beanstalk?

AWS Elastic Beanstalk is a Platform-as-a-Service (PaaS) that automatically handles deployment, capacity provisioning, load balancing, auto-scaling, and application health monitoring.

## Why Elastic Beanstalk in This Project?

1. **Easy Deployment**: Deploy Flask app without managing servers
2. **Automatic Scaling**: Scales based on traffic automatically
3. **Load Balancing**: Distributes traffic across multiple instances
4. **Health Monitoring**: Monitors application health automatically
5. **Docker Support**: Runs containerized Flask application

## How Elastic Beanstalk is Used in This Project

Elastic Beanstalk hosts the Flask application:
- **Platform**: Docker (Docker Compose)
- **Application**: Flask web application
- **Deployment**: Via GitHub Actions CI/CD pipeline
- **Scaling**: Auto-scales based on CPU/memory usage

## Implementation Files

### Primary Files:
1. **`Dockerfile`** - Builds Docker image for Flask app
2. **`docker-compose.yml`** - Defines container configuration for EB
3. **`scripts/setup_elastic_beanstalk.py`** - Creates EB application and environment
4. **`.github/workflows/deploy.yml`** - CI/CD pipeline for deployment

### Configuration:
- **`.ebextensions/`** - (Removed, not needed for Docker platform)
- **`application.py`** - (Optional, EB can use app.py directly)

## Code Structure

### 1. Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
```

**What it does**:
- Uses Python 3.9 slim base image
- Installs system dependencies (gcc for Python packages)
- Installs Python dependencies from requirements.txt
- Copies application code
- Exposes port 5000
- Runs Flask app using Gunicorn WSGI server

**Why Gunicorn**: Production-ready WSGI server (better than Flask's development server)

### 2. docker-compose.yml

```yaml
services:
  app:
    image: 503561414328.dkr.ecr.us-east-1.amazonaws.com/smart-budget-planner:latest
    ports:
      - "80:5000"
    environment:
      - AWS_REGION=us-east-1
      - SECRET_KEY=your-secret-key-change-this-in-production
      - S3_BUCKET_NAME=smart-budget-receipts
    restart: unless-stopped
```

**What it does**:
- Defines Docker Compose service
- Uses Docker image from ECR (Elastic Container Registry)
- Maps port 80 (HTTP) to container port 5000
- Sets environment variables
- Restarts container if it crashes

**Used by**: Elastic Beanstalk Docker Compose platform

### 3. GitHub Actions Deployment (`.github/workflows/deploy.yml`)

**Deployment Flow**:
1. **Build Docker Image** → Builds image from Dockerfile
2. **Push to ECR** → Pushes image to Elastic Container Registry
3. **Update docker-compose.yml** → Updates with new image tag
4. **Create Deployment Package** → Zips Dockerfile and docker-compose.yml
5. **Upload to S3** → Uploads package to S3
6. **Create EB Version** → Creates new application version in EB
7. **Wait for Processing** → Waits for version to be processed
8. **Update Environment** → Updates EB environment with new version

**Key Steps**:
```yaml
- Build Docker image
- Push to ECR
- Update docker-compose.yml with ECR image URI
- Create deployment package (zip)
- Upload to S3
- Create EB application version
- Update EB environment
```

### 4. EB Setup Script (`scripts/setup_elastic_beanstalk.py`)

**Purpose**: Programmatically creates EB application and environment.

**Key Functions**:
- Creates EB application
- Creates IAM roles for EB
- Gets ECR image URI
- Creates application version
- Creates/updates environment

**Used for**: Initial setup (one-time)

## Deployment Architecture

```
GitHub Repository
    ↓ (Push to main)
GitHub Actions
    ↓
Build Docker Image
    ↓
Push to ECR
    ↓
Create EB Application Version
    ↓
Update EB Environment
    ↓
EB Pulls Image from ECR
    ↓
EB Runs Container
    ↓
Application Live on EB URL
```

## How to Explain in Class

### When Asked: "Why use Elastic Beanstalk instead of EC2?"

**Answer**:
- **No Server Management**: EB handles EC2 instances, load balancers, auto-scaling automatically
- **Easy Deployment**: Just upload code, EB handles the rest
- **Automatic Scaling**: Scales up/down based on traffic automatically
- **Health Monitoring**: Monitors application and replaces unhealthy instances
- **Cost**: Pay only for underlying EC2 instances (same as EC2), but no management overhead

### When Asked: "How does deployment work?"

**Answer**:
1. **Code Push** → Developer pushes code to GitHub
2. **CI/CD Trigger** → GitHub Actions workflow starts
3. **Build Image** → Docker image built from Dockerfile
4. **Push to ECR** → Image pushed to Elastic Container Registry
5. **Create Version** → EB application version created with docker-compose.yml
6. **Update Environment** → EB environment updated with new version
7. **Deploy** → EB pulls image from ECR and runs container
8. **Health Check** → EB monitors application health
9. **Live** → Application available on EB URL

**Code Flow**:
```
.github/workflows/deploy.yml
  → Build Docker image
  → Push to ECR
  → Create deployment package
  → Upload to S3
  → Create EB version
  → Update EB environment
```

### When Asked: "Show me the Dockerfile"

**Answer**:
- **File**: `Dockerfile`
- **Base Image**: `python:3.9-slim` (lightweight Python image)
- **Dependencies**: Installs gcc (needed for some Python packages)
- **Application**: Copies requirements.txt, installs dependencies, copies code
- **Port**: Exposes port 5000 (Flask app)
- **Command**: Runs Gunicorn WSGI server with 4 workers

**Why Gunicorn**: 
- Production-ready server (Flask's built-in server is for development only)
- Handles multiple requests concurrently
- Better performance and stability

### When Asked: "What is docker-compose.yml used for?"

**Answer**:
- **Purpose**: Tells Elastic Beanstalk how to run the container
- **Image**: Specifies ECR image to use
- **Ports**: Maps port 80 (HTTP) to container port 5000
- **Environment**: Sets environment variables for application
- **Restart**: Automatically restarts container if it crashes

**Why Docker Compose**: 
- EB Docker Compose platform for multi-container deployments
- Allows defining service configuration
- EB reads this file to know how to run the application

### When Asked: "How does auto-scaling work?"

**Answer**:
- **EB Configuration**: Auto-scaling configured in EB environment settings
- **Triggers**: Based on CPU utilization, memory usage, or request count
- **Scale Up**: Creates new EC2 instances when threshold exceeded
- **Scale Down**: Terminates instances when load decreases
- **Load Balancer**: Distributes traffic across all instances automatically

**Example**: If CPU > 70%, EB creates new instance. If CPU < 25%, terminates instance.

## Environment Configuration

### Application Details
- **Application Name**: `smart-budget-planner`
- **Environment Name**: `smart-budget-planner-env`
- **Platform**: Docker running on 64bit Amazon Linux 2
- **Solution Stack**: Docker Compose platform

### Instance Configuration
- **Instance Type**: t3.small (default, can be changed)
- **Auto Scaling**: Enabled
- **Load Balancer**: Application Load Balancer (ALB)
- **Health Check**: HTTP GET on `/` endpoint

### Environment Variables
- `AWS_REGION`: us-east-1
- `SECRET_KEY`: Flask secret key
- `S3_BUCKET_NAME`: smart-budget-receipts
- AWS credentials via IAM instance role

## Key Concepts to Remember

1. **Application**: Container for environments (e.g., dev, staging, prod)
2. **Environment**: Running instance of application (e.g., smart-budget-planner-env)
3. **Application Version**: Specific deployment (code + configuration)
4. **Platform**: Runtime environment (Docker, Python, Node.js, etc.)
5. **Solution Stack**: Specific platform version
6. **Health Check**: EB monitors application health endpoint
7. **Auto Scaling**: Automatically adds/removes instances based on load

## Common Questions & Answers

**Q: Why use Docker instead of Python platform?**
A: Docker provides more control over dependencies and environment. Can package everything needed in container.

**Q: How does EB know which image to use?**
A: docker-compose.yml specifies ECR image URI. EB pulls image from ECR when deploying.

**Q: What happens if application crashes?**
A: EB health check detects failure and replaces instance automatically. Container restart policy also restarts container.

**Q: How do you update the application?**
A: Push code to GitHub → GitHub Actions builds new image → Pushes to ECR → Creates new EB version → Updates environment.

**Q: How much does EB cost?**
A: EB itself is free. You pay for underlying EC2 instances, load balancer, and other AWS resources used.

**Q: Can you SSH into EB instances?**
A: Yes, EB provides SSH access to instances for debugging. Use `eb ssh` command or AWS Console.

**Q: How does EB handle HTTPS?**
A: Application Load Balancer (ALB) can terminate HTTPS. Need SSL certificate from ACM (AWS Certificate Manager).

