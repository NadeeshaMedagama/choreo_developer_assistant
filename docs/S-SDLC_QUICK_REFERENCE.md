# S-SDLC Quick Reference Guide

Quick reference for using the AI agent throughout the Secure Software Development Life Cycle.

## 🔐 Security-First Development with AI Agent

### Quick Access
- **Local UI**: http://localhost:5173
- **API Endpoint**: http://localhost:8000/api/ask
- **API Docs**: http://localhost:8000/docs

## 📋 Phase-by-Phase Quick Reference

### 1️⃣ Planning & Requirements
**When to use AI:**
- Before starting any new feature
- When defining security requirements
- During threat modeling sessions

**Example Queries:**
```
❓ "What are the security requirements for Choreo API deployment?"
❓ "What compliance standards apply to Choreo applications?"
❓ "How should I handle sensitive data in Choreo?"
❓ "What authentication methods does Choreo support?"
```

### 2️⃣ Design Phase
**When to use AI:**
- Creating architecture diagrams
- Reviewing security patterns
- Validating design decisions

**Example Queries:**
```
❓ "Show me the secure authentication flow for Choreo"
❓ "Diagram the deployment architecture with security components"
❓ "What are secure patterns for API design?"
❓ "How should I design OAuth2 integration?"
```

**Diagram Generation:**
- Ask for diagrams: "Show me..." or "Diagram..."
- Supported types: flowchart, sequenceDiagram, stateDiagram
- Interactive zoom and fullscreen available

### 3️⃣ Development Phase
**When to use AI:**
- While writing code
- When implementing security features
- During code review preparation

**Example Queries:**
```
❓ "How do I securely store API keys in Choreo?"
❓ "Show me secure input validation patterns"
❓ "How to implement rate limiting?"
❓ "What's the best way to handle error messages securely?"
```

**API Usage During Development:**
```bash
# Quick query from terminal
curl -X POST "http://localhost:8000/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "How to secure environment variables?"}'

# Streaming response
curl -X POST "http://localhost:8000/api/ask/stream" \
  -H "Content-Type: application/json" \
  -d '{"question": "Show me secure configuration patterns"}'
```

### 4️⃣ Testing Phase
**When to use AI:**
- Writing security tests
- Understanding test requirements
- Creating test scenarios

**Example Queries:**
```
❓ "What security tests should I write for API endpoints?"
❓ "How to test authentication flows?"
❓ "What are common security test cases for Choreo?"
❓ "How to validate input sanitization?"
```

### 5️⃣ Security Testing & Validation
**When to use AI:**
- Interpreting security scan results
- Understanding vulnerabilities
- Getting remediation guidance

**Example Queries:**
```
❓ "Explain this CodeQL finding: [paste finding]"
❓ "How to fix SQL injection vulnerability?"
❓ "What does this OWASP dependency warning mean?"
❓ "How severe is this security alert?"
```

**CI/CD Integration:**
Our pipeline runs these security scans automatically:
- ✅ CodeQL Analysis (Python, JavaScript)
- ✅ Secret Scanning (Gitleaks, TruffleHog)
- ✅ Dependency Check (Safety, pip-audit)
- ✅ Container Scanning (Trivy)

Use AI to understand results:
```
❓ "What is CodeQL analyzing in my Python code?"
❓ "How do I fix dependencies with security vulnerabilities?"
❓ "Explain container security best practices"
```

### 6️⃣ Deployment Phase
**When to use AI:**
- Configuring production environment
- Setting up monitoring
- Validating deployment security

**Example Queries:**
```
❓ "How to securely deploy to Choreo?"
❓ "What environment variables need to be configured?"
❓ "How to enable security monitoring?"
❓ "What are the security hardening steps?"
```

### 7️⃣ Operations & Maintenance
**When to use AI:**
- During security incidents
- Interpreting alerts
- Planning updates

**Example Queries:**
```
❓ "How to respond to authentication failures?"
❓ "Explain this security alert: [paste alert]"
❓ "How to update dependencies safely?"
❓ "What's the impact of this security patch?"
```

## 🎯 Common Security Scenarios

### Scenario: New API Endpoint
```
1. Planning: "What security requirements for Choreo API endpoints?"
2. Design: "Show me secure API architecture diagram"
3. Development: "How to implement authentication for API?"
4. Testing: "What security tests for API endpoints?"
5. Deployment: "How to secure API in production?"
```

### Scenario: Handling User Data
```
1. Planning: "What are data protection requirements?"
2. Design: "Show me secure data flow diagram"
3. Development: "How to encrypt sensitive data?"
4. Testing: "How to test data protection?"
5. Operations: "How to monitor data access?"
```

### Scenario: Security Alert Response
```
1. Query: "Explain this security alert: [alert details]"
2. Query: "What's the severity and impact?"
3. Query: "How to remediate this vulnerability?"
4. Query: "What tests should I run after fixing?"
```

## 🛠️ Pro Tips

### Effective Queries
✅ **DO:**
- Be specific: "How to implement JWT authentication in FastAPI?"
- Ask for diagrams: "Show me the OAuth flow"
- Request examples: "Show me secure error handling example"
- Use conversation history: Ask follow-up questions

❌ **DON'T:**
- Be too vague: "How to secure my app?"
- Mix multiple topics in one query
- Assume AI knows your specific code context

### Conversation Memory
The AI remembers your conversation:
- Ask follow-up questions naturally
- Build on previous answers
- Reference earlier topics: "Based on your earlier answer about auth..."

### Source Citations
Every answer includes sources:
- Click source links to verify information
- Check relevance scores (higher = more relevant)
- Use sources for documentation and audits

## 📊 Security Metrics to Monitor

Ask AI about these metrics:
```
❓ "What security metrics should I monitor?"
❓ "How to interpret authentication failure rates?"
❓ "What's a normal rate for 429 errors?"
```

**Key Metrics:**
- Failed authentication attempts
- Rate limit violations
- API error rates
- Response times
- Token usage

## 🔗 Quick Links

### Documentation
- [Full S-SDLC Integration Guide](./S-SDLC_INTEGRATION.md)
- [S-SDLC Diagrams](./S-SDLC_DIAGRAMS.md)
- [Security Audit Report](./implementation/SECURITY_AUDIT_REPORT.md)

### Workflows
- [CI/CD Pipeline](../.github/workflows/ci-cd.yml)
- [Security Scans](../.github/workflows/security.yml)
- [Dependency Checks](../.github/workflows/dependency-check.yml)

### Tools
- [Backend API](../backend/app.py)
- [Chat Service](../backend/services/chat_service.py)
- [Monitoring](../backend/monitoring/)

## 📝 Daily Security Checklist

### Before Coding
- [ ] Review security requirements with AI
- [ ] Understand security patterns needed
- [ ] Check for security updates

### During Development
- [ ] Query AI for secure implementation patterns
- [ ] Validate security assumptions
- [ ] Test security features locally

### Before Committing
- [ ] Review code for security issues
- [ ] Ensure no secrets in code
- [ ] Run local security checks

### After CI/CD
- [ ] Review security scan results
- [ ] Use AI to understand findings
- [ ] Fix critical issues immediately

### Before Deployment
- [ ] Verify secure configuration with AI
- [ ] Check environment variables
- [ ] Validate monitoring setup

### In Production
- [ ] Monitor security metrics
- [ ] Review alerts with AI assistance
- [ ] Keep conversation history for audits

## 🚨 Emergency Response

### Security Incident Response
```
1. Immediate: Stop deployment if in progress
2. Query AI: "How to respond to [incident type]?"
3. Investigate: Use AI to understand scope
4. Remediate: Get guidance on fixes
5. Document: Save conversation for audit
6. Prevent: Ask AI about prevention
```

### Quick Commands
```bash
# Check for secrets in code
git diff | grep -i "api.key\|token\|secret\|password"

# Review security scan results
gh workflow view security

# Get AI help via API
curl -X POST "http://localhost:8000/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "Security incident response for [type]"}'
```

## 📖 Learning Resources

### Security Topics to Explore
Ask AI about:
- OWASP Top 10
- Secure coding practices
- Authentication & authorization
- Data encryption
- Input validation
- Error handling
- API security
- Container security

### Example Learning Session
```
Session 1: "What are the OWASP Top 10 vulnerabilities?"
Session 2: "How to prevent SQL injection in Python?"
Session 3: "Show me secure authentication patterns"
Session 4: "How to implement rate limiting?"
```

## 🎓 Best Practices

1. **Query Early and Often**: Don't wait until you have problems
2. **Use Diagrams**: Visual understanding improves security design
3. **Save Conversations**: Export important security discussions
4. **Verify Sources**: Check cited documentation links
5. **Iterate**: Ask follow-up questions for clarity
6. **Share Knowledge**: Document AI-provided insights
7. **Stay Updated**: Ask about latest security practices

## 🔍 Troubleshooting

### AI Not Responding?
- Check backend is running: http://localhost:8000/health
- Verify API keys in `.env` file
- Check network connectivity

### Incorrect or Outdated Information?
- Check source citations
- Verify against official Choreo docs
- Ask for clarification or alternative sources

### Need Human Expert?
AI complements but doesn't replace security experts:
- Complex vulnerability analysis
- Critical security decisions
- Compliance certifications
- Security architecture review

---

**Quick Start**: Open http://localhost:5173 and start asking security questions!

**Remember**: The AI agent is your security companion throughout the entire SDLC. Use it proactively, not just reactively.

**Last Updated**: February 2026
