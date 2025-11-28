# 🎯 AWS IAM Best Practices

This document outlines essential best practices for implementing and managing AWS IAM effectively.

---

## 🔐 Security Best Practices

### 1. **Never Use Root Account for Daily Operations**
- ✅ Create IAM users for daily tasks
- ✅ Enable MFA on root account
- ✅ Store root credentials securely (password manager, safe)
- ❌ Never share root credentials
- ❌ Never use root for API access

### 2. **Enable Multi-Factor Authentication (MFA)**
- ✅ Require MFA for all IAM users
- ✅ Use MFA for sensitive operations (delete, modify critical resources)
- ✅ Consider hardware MFA devices for high-privilege accounts
- ✅ Use virtual MFA devices for cost-effective implementation

### 3. **Use Strong Password Policies**
```json
{
  "MinimumPasswordLength": 14,
  "RequireUppercaseCharacters": true,
  "RequireLowercaseCharacters": true,
  "RequireNumbers": true,
  "RequireSymbols": true,
  "PasswordReusePrevention": 24,
  "MaxPasswordAge": 90
}
```

### 4. **Rotate Credentials Regularly**
- ✅ Rotate access keys every 90 days
- ✅ Use AWS Secrets Manager for automatic rotation
- ✅ Monitor unused access keys
- ✅ Remove unused credentials immediately

---

## 🎯 Principle of Least Privilege

### 1. **Grant Minimum Required Permissions**
- ✅ Start with no permissions, add only what's needed
- ✅ Use AWS managed policies as starting points
- ✅ Create custom policies for specific needs
- ❌ Avoid using `*` in Action or Resource fields unnecessarily

### 2. **Use Resource-Level Permissions**
```json
{
  "Effect": "Allow",
  "Action": "s3:GetObject",
  "Resource": "arn:aws:s3:::specific-bucket/*"
}
```
Instead of:
```json
{
  "Effect": "Allow",
  "Action": "s3:*",
  "Resource": "*"
}
```

### 3. **Use Conditions to Restrict Access**
- ✅ IP address restrictions
- ✅ Time-based access
- ✅ MFA requirements
- ✅ Source VPC restrictions
- ✅ Tag-based access control

---

## 👥 User and Group Management

### 1. **Organize Users into Groups**
- ✅ Create groups based on job functions (developers, admins, auditors)
- ✅ Attach policies to groups, not individual users
- ✅ Add/remove users from groups as roles change
- ✅ Use naming conventions: `Team-Function-Role`

### 2. **Use Roles Instead of Users When Possible**
- ✅ Use IAM roles for EC2 instances
- ✅ Use roles for Lambda functions
- ✅ Use roles for cross-account access
- ✅ Use roles for federated access
- ❌ Avoid long-lived access keys when roles can be used

### 3. **Regular Access Reviews**
- ✅ Review user access quarterly
- ✅ Remove unused accounts
- ✅ Audit group memberships
- ✅ Use AWS Access Analyzer for unused access

---

## 📋 Policy Management

### 1. **Prefer Managed Policies Over Inline**
- ✅ Use AWS managed policies when possible
- ✅ Create customer-managed policies for reusability
- ✅ Use inline policies only for unique, one-off cases
- ✅ Version control your custom policies

### 2. **Use Permissions Boundaries**
- ✅ Set permissions boundaries for users/roles
- ✅ Prevent privilege escalation
- ✅ Limit maximum permissions possible
- ✅ Use for delegated administration

### 3. **Policy Structure Best Practices**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DescriptiveStatementName",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::bucket-name",
        "arn:aws:s3:::bucket-name/*"
      ],
      "Condition": {
        "StringEquals": {
          "s3:ExistingObjectTag/Owner": "${aws:username}"
        }
      }
    }
  ]
}
```

---

## 🔄 Role-Based Access Patterns

### 1. **EC2 Instance Roles**
- ✅ Always use instance profiles for EC2
- ✅ Never store credentials in EC2 instances
- ✅ Rotate roles regularly
- ✅ Use least privilege for instance roles

### 2. **Lambda Execution Roles**
- ✅ Create dedicated roles per Lambda function
- ✅ Grant only required permissions
- ✅ Use resource-based policies when appropriate
- ✅ Monitor CloudWatch Logs for permission errors

### 3. **Cross-Account Access**
- ✅ Use external IDs for cross-account roles
- ✅ Implement least privilege in trust policies
- ✅ Use conditions in trust policies
- ✅ Document all cross-account relationships

---

## 📊 Monitoring and Auditing

### 1. **Enable CloudTrail**
- ✅ Enable CloudTrail in all regions
- ✅ Log all IAM API calls
- ✅ Store logs in separate S3 bucket
- ✅ Enable log file validation
- ✅ Set up CloudWatch alarms for suspicious activity

### 2. **Use AWS Config**
- ✅ Track IAM configuration changes
- ✅ Set up compliance rules
- ✅ Monitor policy changes
- ✅ Alert on unauthorized changes

### 3. **Regular Audits**
- ✅ Review access logs monthly
- ✅ Check for unused credentials
- ✅ Verify MFA compliance
- ✅ Audit policy changes
- ✅ Review cross-account access

---

## 🏢 Organizational Best Practices

### 1. **Use AWS Organizations**
- ✅ Centralize account management
- ✅ Use Service Control Policies (SCPs)
- ✅ Implement guardrails
- ✅ Enable consolidated billing

### 2. **Tagging Strategy**
- ✅ Tag IAM resources consistently
- ✅ Use tags for access control
- ✅ Document tagging standards
- ✅ Enforce tags via SCPs

### 3. **Documentation**
- ✅ Document all custom policies
- ✅ Maintain access matrix
- ✅ Document role purposes
- ✅ Keep runbooks updated

---

## 🚨 Common Mistakes to Avoid

### ❌ **Don't Do This:**
1. Sharing IAM credentials between users
2. Using wildcards (`*`) unnecessarily
3. Attaching policies directly to users instead of groups
4. Using root account for API access
5. Storing access keys in code repositories
6. Not enabling MFA
7. Creating overly permissive policies
8. Ignoring unused credentials
9. Not reviewing access regularly
10. Hardcoding credentials in applications

### ✅ **Do This Instead:**
1. Create individual IAM users
2. Use specific actions and resources
3. Organize users into groups
4. Use IAM users or roles
5. Use IAM roles or AWS Secrets Manager
6. Require MFA for all users
7. Follow least privilege principle
8. Automate credential rotation
9. Schedule quarterly access reviews
10. Use IAM roles or environment variables

---

## 📚 Additional Resources

- [AWS IAM Best Practices Guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [IAM Policy Simulator](https://policysim.aws.amazon.com/)
- [AWS Access Analyzer](https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html)
- [AWS Security Hub](https://aws.amazon.com/security-hub/)
- [IAM Policy Reference](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies.html)

---

## 🔍 Quick Checklist

- [ ] Root account has MFA enabled
- [ ] All IAM users have MFA enabled
- [ ] Strong password policy configured
- [ ] Users organized into groups
- [ ] Policies follow least privilege
- [ ] CloudTrail enabled and monitored
- [ ] Access keys rotated regularly
- [ ] Unused credentials removed
- [ ] Roles used for EC2/Lambda
- [ ] Permissions boundaries set
- [ ] Regular access reviews scheduled
- [ ] Documentation up to date

---

**Remember:** Security is an ongoing process, not a one-time setup. Regularly review and update your IAM configuration to maintain a secure AWS environment.

