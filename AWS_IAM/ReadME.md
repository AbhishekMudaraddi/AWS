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

## 📚 References
- [AWS IAM Documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html)  
- [IAM Policy Reference](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies.html)  
- [IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)  
- [AWS Security Blog](https://aws.amazon.com/blogs/security/)

---

### 🧭 Summary
IAM is the **backbone of AWS security**, providing fine-grained access control, auditability, and scalability across the entire cloud environment. Mastering IAM is essential for any cloud or DevOps engineer aiming to build secure, compliant, and automated AWS environments.

---

**Author:** *Abhishek B Mudaraddi*  
**MSc in Cloud Computing, National College of Ireland* 🇮🇪  
**#AWS #CloudSecurity #IAM #DevOps**
