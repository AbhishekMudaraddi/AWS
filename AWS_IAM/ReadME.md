# 🛡️ AWS Identity and Access Management (IAM)

**AWS Identity and Access Management (IAM)** is a web service that helps you securely control access to AWS resources. It enables you to:

- 👥 Manage identities (users, groups, and roles)  
- 🔐 Control permissions through policies  
- ⏱️ Provide temporary access for federated users  
- 🧩 Enforce least privilege access  

> IAM is a **global service**, meaning it’s not bound to any specific AWS Region — though some IAM resources may be region-specific.

---

## 🌍 Why IAM?

### 🧱 Security Foundation
- Prevent unauthorized access to AWS resources  
- Implement **least privilege** by granting only required permissions  
- Audit access using **AWS CloudTrail** integration  

### ⚖️ Compliance Requirements
- Meet standards like **HIPAA**, **PCI DSS**, and **GDPR**  
- Maintain centralized governance and access control  
- Ensure accountability and ownership  

### ⚙️ Operational Excellence
- Manage access across AWS from a single console  
- Define granular, resource-level permissions  
- Automate IAM configuration via **DevOps** and **IaC (Infrastructure as Code)** tools  

---

## 🔑 Core IAM Concepts

| Concept | Description | Example / Notes |
|----------|--------------|----------------|
| **Root User** | Complete access to all AWS resources | Use only for setup or emergencies |
| **IAM Users** | Individual identities for team members | Access via console, CLI, or SDK |
| **IAM Groups** | Collections of users with shared permissions | Apply common policies easily |
| **IAM Roles** | Identities with permissions that can be assumed temporarily | Used by services or federated users |
| **Policies** | JSON documents defining permissions | `AmazonS3ReadOnlyAccess`, custom inline policies |
| **Managed Policies** | AWS-managed or customer-managed reusable policies | Easier to maintain and reuse |
| **Inline Policies** | Embedded directly into a user, group, or role | Use for specific, one-off cases |
| **Service Control Policies (SCPs)** | Org-level restrictions applied via AWS Organizations | Restrict even admin permissions |
| **MFA (Multi-Factor Authentication)** | Adds extra security to credentials | Recommended for all IAM users |
| **Temporary Security Credentials** | Short-lived tokens for federated or role-based access | Generated via **AWS STS** |

---

## 🧠 How AWS Implements IAM

### 1. ⚙️ Distributed Policy Engine
- **Component:** IAM Policy Evaluation Service  
- **Technology:** Distributed, low-latency system  
- **Process:**  
  - Policies parsed into Abstract Syntax Trees (ASTs)  
  - Evaluated on each request for `allow` / `deny` decisions  
  - Uses caching for efficiency  

---

### 2. 🌐 Global Replicated Database
- **Component:** IAM Database  
- **Technology:** Multi-region replication  
- **Features:**  
  - High availability and durability  
  - Eventual consistency model  
  - Conflict resolution for concurrent updates  

---

### 3. 🔏 Credential Management System
- **Component:** AWS STS (Security Token Service)  
- **Technology:** Cryptographic token generation  
- **Features:**  
  - Issues temporary credentials  
  - Integrates with identity providers (SSO, federated login)  
  - Supports role assumption and delegation  

---

### 4. 🧾 Access Logging & Auditing
- **Component:** AWS CloudTrail  
- **Technology:** Distributed, encrypted logging  
- **Features:**  
  - Captures all IAM API calls  
  - Logs stored securely in **Amazon S3**  
  - Enables historical tracking, compliance & forensic analysis  

---

## 🔐 IAM Security Model

### Policy Evaluation Logic
1. **Default Deny** – All requests are denied unless explicitly allowed  
2. **Explicit Allow** – Overrides default deny  
3. **Explicit Deny** – Always overrides allow  
4. **Permissions Boundaries** – Cap maximum permissions possible  

### Evaluation Order
1. **Organizations SCPs** (if applicable)  
2. **Resource-based policies**  
3. **Identity-based policies**  
4. **Session policies** (for temporary credentials)  

### Context-Based Evaluation
IAM considers:
- **Principal** – Who made the request  
- **Action** – What operation they’re performing  
- **Resource** – Which resource they’re accessing  
- **Condition** – Optional constraints (IP range, MFA status, time, etc.)  

---

## 💻 Practical Examples & Code

This repository includes practical examples demonstrating IAM implementation:

### 📁 Project Structure
```
AWS_IAM/
├── ReadME.md                    # This comprehensive guide
├── BEST_PRACTICES.md            # IAM best practices and guidelines
├── examples/
│   ├── iam_user_management.py   # Python examples for user management
│   ├── iam_role_management.py   # Python examples for role management
│   ├── iam_policy_examples.py   # Various IAM policy patterns
│   ├── aws_cli_examples.sh      # AWS CLI command examples
│   └── requirements.txt         # Python dependencies
└── [PDF Documentation Files]
```

### 🐍 Python Examples (boto3)

#### User Management
- Create IAM users
- Manage access keys
- Attach policies to users
- Create and manage groups
- List users and their permissions

**File:** `examples/iam_user_management.py`

#### Role Management
- Create IAM roles for EC2, Lambda, and cross-account access
- Create instance profiles
- Assume roles using STS
- Attach policies to roles

**File:** `examples/iam_role_management.py`

#### Policy Examples
- S3 read-only access policies
- IP-restricted access
- MFA-required policies
- Tag-based access control
- Least privilege patterns
- Permissions boundaries
- Service Control Policies (SCPs)

**File:** `examples/iam_policy_examples.py`

### 🔧 AWS CLI Examples

Comprehensive shell script demonstrating:
- User creation and management
- Policy creation and attachment
- Group management
- Role creation for EC2
- Instance profile setup
- MFA device creation
- Role assumption

**File:** `examples/aws_cli_examples.sh`

### 🚀 Getting Started

1. **Install Dependencies:**
   ```bash
   pip install -r examples/requirements.txt
   ```

2. **Configure AWS Credentials:**
   ```bash
   aws configure
   ```

3. **Run Python Examples:**
   ```bash
   python examples/iam_user_management.py
   python examples/iam_role_management.py
   python examples/iam_policy_examples.py
   ```

4. **Run CLI Examples:**
   ```bash
   chmod +x examples/aws_cli_examples.sh
   ./examples/aws_cli_examples.sh
   ```

> ⚠️ **Important:** These are demonstration scripts. Review and modify them before running in production environments. Always follow the principle of least privilege.

---

## 🎯 Common Use Cases

### 1. **EC2 Instance Access to S3**
Create a role that allows EC2 instances to read from S3 buckets without storing credentials.

### 2. **Lambda Function Permissions**
Grant Lambda functions specific permissions to access DynamoDB, S3, or other AWS services.

### 3. **Cross-Account Access**
Enable secure access between AWS accounts using IAM roles with external IDs.

### 4. **Developer Access Control**
Organize developers into groups with appropriate permissions based on their roles.

### 5. **Temporary Access**
Provide time-limited access to resources using role assumption and session policies.

### 6. **MFA-Protected Operations**
Require MFA for sensitive operations like deleting resources or modifying security settings.

---

## 📚 References
- [AWS IAM Documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html)  
- [IAM Policy Reference](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies.html)  
- [IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)  
- [AWS Security Blog](https://aws.amazon.com/blogs/security/)
- [IAM Policy Simulator](https://policysim.aws.amazon.com/)
- [AWS Access Analyzer](https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html)

---

## 📖 Additional Documentation

- **[BEST_PRACTICES.md](./BEST_PRACTICES.md)** - Comprehensive guide to IAM best practices, security guidelines, and common mistakes to avoid.

---

### 🧭 Summary
IAM is the **backbone of AWS security**, providing fine-grained access control, auditability, and scalability across the entire cloud environment. Mastering IAM is essential for any cloud or DevOps engineer aiming to build secure, compliant, and automated AWS environments.

This repository serves as both a **learning resource** and a **practical reference** for implementing IAM in real-world scenarios. The included examples demonstrate common patterns and best practices that can be adapted for your specific use cases.

---

**Author:** *Abhishek B Mudaraddi*  
**MSc in Cloud Computing, National College of Ireland* 🇮🇪  
**#AWS #CloudSecurity #IAM #DevOps**
