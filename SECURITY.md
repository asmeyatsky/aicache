# Security Policy

## Supported Versions

We provide security updates for the following versions of aicache:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in aicache, please follow these steps:

1. **Do not open a public issue** - this could expose the vulnerability to others
2. **Email us directly** at [your-email@example.com](mailto:your-email@example.com) with a detailed description of:
   - The vulnerability and its impact
   - Steps to reproduce the issue
   - Any potential fixes you've identified
   - Your GitHub username for credit if applicable

## Response Timeline

We will:
- Acknowledge your report within 48 hours
- Provide regular updates every 2-3 days after the initial response
- Work to fix the issue as quickly as possible, typically within 30 days
- Credit you for the discovery when the fix is released (unless you prefer to remain anonymous)

## Security Best Practices for Users

When using aicache, please follow these security best practices:

- Keep your installation up to date with the latest security patches
- Review the code and configurations before using aicache with sensitive data
- Be aware that aicache caches responses locally which may contain sensitive information
- Configure any network or API key access appropriately
- Regularly review and clean your cache to remove potentially sensitive cached data

## Scope

We consider the following to be in scope for security vulnerabilities:
- Authentication bypasses
- Authorization issues that allow unauthorized access
- Data exposure or leakage
- Command injection vulnerabilities
- Denial of service issues

The following are out of scope:
- Issues caused by misconfigurations in user code or environments
- Attacks requiring physical access to user's device
- Issues in dependencies that are not specific to aicache's usage