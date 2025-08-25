# 🔒 Security Guidelines

## 🚨 **CRITICAL: API Key Security**

This repository handles EIA API keys and other sensitive configuration data. Follow these guidelines to prevent security breaches.

## ✅ **DO's**

1. **Use Environment Variables**: Always use `EIA_API_KEY` environment variable
2. **Use .env files**: Create a `.env` file from `env.example` template for local development
3. **Use GitHub Repository Secrets**: Store API keys as repository secrets for CI/CD
4. **Keep .env in .gitignore**: Never commit `.env` files to version control
5. **Use placeholder values**: Use `your_eia_api_key_here` in examples
6. **Validate API keys**: Check if API key exists before using it

## ❌ **DON'Ts**

1. **Never hardcode API keys** in source code
2. **Never commit .env files** to version control
3. **Never log API keys** in console output or logs
4. **Never share API keys** in public repositories
5. **Never use real API keys** in test files

## 🔧 **Proper API Key Usage**

### ✅ Correct Pattern:
```python
import os

api_key = os.getenv('EIA_API_KEY')
if not api_key:
    print("❌ EIA_API_KEY environment variable not set")
    print("   Please set EIA_API_KEY in your .env file or environment")
    return None

analyzer = EIAEnergyAnalyzer(api_key=api_key)
```

### ❌ Incorrect Pattern:
```python
# NEVER DO THIS!
api_key = "7Zh9UWfJ4WsW8vRXmO3NRVmwMPZuFudNeo44IcR2"
```

## 🛠️ **Setup Instructions**

### **Local Development:**
1. **Copy environment template**:
   ```bash
   cp env.example .env
   ```

2. **Edit .env file**:
   ```bash
   # Add your actual API key
   EIA_API_KEY=your_actual_api_key_here
   ```

3. **Verify .env is ignored**:
   ```bash
   git status
   # .env should NOT appear in tracked files
   ```

### **CI/CD (GitHub Actions):**
1. **Go to Repository Settings** → **Secrets and variables** → **Actions**
2. **Add Repository Secret**:
   - Name: `EIA_API_KEY`
   - Value: Your EIA API key
3. **GitHub Actions will automatically use the secret** in workflows

## 🔍 **Security Checklist**

Before committing code:

- [ ] No hardcoded API keys in source files
- [ ] `.env` file exists but is not tracked by git
- [ ] All API key references use `os.getenv('EIA_API_KEY')`
- [ ] Error handling for missing API keys
- [ ] No API keys in console output or logs
- [ ] Test files use environment variables, not hardcoded keys

## 🚨 **If API Key is Exposed**

1. **Generate a new API key** from EIA website (EIA doesn't support revocation)
2. **Update your .env file** with the new key (local development)
3. **Update GitHub Repository Secret** with the new key (CI/CD)
4. **Remove the exposed key** from all files
5. **Check git history** for any commits with the key
6. **Consider using git filter-branch** to remove from history if needed

## 📋 **Files to Monitor**

These files should NEVER contain hardcoded API keys:
- `*.py` files
- `*.ipynb` files
- `*.md` files
- `*.txt` files
- Configuration files

## 🔐 **Additional Security Measures**

1. **Use pre-commit hooks** to scan for secrets
2. **Enable GitGuardian** for automated secret detection
3. **Regular security audits** of the codebase
4. **Rotate API keys** periodically
5. **Use least privilege** principle for API access

## 📞 **Emergency Contacts**

If you discover a security breach:
1. Revoke exposed credentials immediately
2. Document the incident
3. Update this security guide if needed
4. Consider notifying relevant parties

---

**Remember**: Security is everyone's responsibility. When in doubt, ask before committing sensitive information.
