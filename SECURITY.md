# 🔐 Security Guidelines for HealthLink Agent

## ⚠️ CRITICAL: API Keys & Secrets

### ✅ DO:
- Keep all API keys in `.env` file (which is gitignored)
- Use `.env.example` with **placeholder values only**
- Rotate keys immediately if accidentally committed
- Use environment variables in production
- Store private keys in secure vaults (AWS Secrets Manager, Azure Key Vault, etc.)

### ❌ DON'T:
- **NEVER** commit real API keys to git
- **NEVER** share `.env` file publicly
- **NEVER** hardcode secrets in source code
- **NEVER** commit private keys to version control

## 🔑 Keys to Protect

### High Priority (Immediate rotation if exposed):
- `PRIVATE_KEY` - Ethereum wallet private key (can drain funds)
- `SUPABASE_SERVICE_KEY` - Full database access
- `GOOGLE_API_KEY` - Can incur costs
- `OPENAI_API_KEY` - Can incur significant costs

### Medium Priority:
- `ENCRYPTION_KEY` - Used for data encryption
- `JWT_SECRET` - Authentication security
- `SUPABASE_KEY` - Limited database access

## 🚨 If You Accidentally Committed Secrets

### Immediate Actions:

1. **Rotate ALL exposed keys immediately:**
   - Google API: https://console.cloud.google.com/apis/credentials
   - Supabase: https://app.supabase.com/project/_/settings/api
   - Alchemy: https://dashboard.alchemy.com/
   - Transfer any funds from exposed Ethereum wallet

2. **Remove from Git history:**
   ```bash
   # Install BFG Repo-Cleaner
   brew install bfg  # macOS
   # or download from: https://rtyley.github.io/bfg-repo-cleaner/

   # Remove the sensitive file from history
   bfg --delete-files .env

   # Clean up
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   
   # Force push (⚠️ coordinate with team first!)
   git push --force
   ```

3. **Use git-secrets to prevent future leaks:**
   ```bash
   # Install git-secrets
   brew install git-secrets  # macOS
   # or: pip install git-secrets

   # Set up in repo
   cd /path/to/repo
   git secrets --install
   git secrets --register-aws
   
   # Add custom patterns
   git secrets --add 'AIza[0-9A-Za-z\\-_]{35}'  # Google API keys
   git secrets --add 'sb_secret_[a-zA-Z0-9_-]+'  # Supabase keys
   git secrets --add '0x[a-fA-F0-9]{64}'  # Private keys
   ```

## 📋 Security Checklist

Before committing code:
- [ ] Checked `.env` is not staged for commit
- [ ] Verified `.env.example` contains only placeholders
- [ ] No API keys in source code
- [ ] No private keys in source code
- [ ] All secrets in environment variables
- [ ] `.gitignore` is up to date

Before deploying:
- [ ] Environment variables set in hosting platform
- [ ] Production keys are different from development keys
- [ ] CORS origins properly configured
- [ ] Rate limiting enabled
- [ ] HTTPS enforced
- [ ] Database RLS policies enabled

## 🛡️ Best Practices

### 1. Environment Separation
```bash
# Development
.env.development

# Staging
.env.staging

# Production (use hosting platform's env vars)
# NEVER commit production secrets
```

### 2. Key Rotation Schedule
- **High-priority keys:** Rotate every 90 days
- **Medium-priority keys:** Rotate every 180 days
- **After any security incident:** Immediate rotation

### 3. Access Control
- Use principle of least privilege
- Separate read-only and write keys
- Use different keys for different environments
- Implement IP whitelisting where possible

### 4. Monitoring
- Set up alerts for unusual API usage
- Monitor blockchain transactions
- Track failed authentication attempts
- Review access logs regularly

## 🔗 Resources

- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)
- [Git-secrets](https://github.com/awslabs/git-secrets)
- [Supabase Security Best Practices](https://supabase.com/docs/guides/auth/auth-helpers/nextjs)

## 📞 Report Security Issues

If you discover a security vulnerability:
1. **DO NOT** open a public issue
2. Email: tiwaridewesh234@gmail.com
3. Include: detailed description, steps to reproduce
4. Allow 48 hours for response

---

**Remember: Security is everyone's responsibility! 🛡️**
