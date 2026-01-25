# Security Checklist

**Apply these to EVERY project. Non-negotiable.**

---

## Core Principles

### 1. Gatekeep Every Single Action
Just because a user is logged in doesn't mean they can do everything. Check authorization on EVERY endpoint, not just authentication.

```python
# BAD - only checks if logged in
@app.get("/api/projects/{project_id}")
async def get_project(project_id: str, user: User = Depends(get_current_user)):
    return db.get_project(project_id)  # Anyone can access any project!

# GOOD - checks if user OWNS this resource
@app.get("/api/projects/{project_id}")
async def get_project(project_id: str, user: User = Depends(get_current_user)):
    project = db.get_project(project_id)
    if project.organization_id != user.organization_id:
        raise HTTPException(403, "Not authorized")
    return project
```

Think of it like checking an ID badge at every high-security door, not just the building entrance.

---

### 2. Don't Hide, Withhold
If you have premium features, don't ask the backend "is this user premium?" and then trust the frontend to hide the button if the answer is "no." Tech-savvy users can easily change that "no" to a "yes" in browser devtools.

```javascript
// BAD - frontend decides access
if (user.isPremium) {
  showPremiumContent();
}

// GOOD - backend withholds data entirely
// Frontend just renders what it receives
const data = await fetch('/api/premium-content');
// Backend returns 403 if not premium, or the actual content if they are
```

**Rule:** Premium features should not exist in the client bundle at all for free users. The server should never send premium data to non-premium users.

---

### 3. Keep Secrets Off the Browser
Never put API keys (OpenAI, Stripe, Anthropic, etc.) in code that runs on the user's screen. If it's on their screen, it's in their pocket.

```javascript
// BAD - exposed in client code
const response = await fetch('https://api.openai.com/v1/chat', {
  headers: { 'Authorization': `Bearer ${process.env.NEXT_PUBLIC_OPENAI_KEY}` }
});

// GOOD - call your own backend, which has the key
const response = await fetch('/api/generate', {
  method: 'POST',
  body: JSON.stringify({ prompt })
});
// Your backend calls OpenAI with the secret key
```

**Remember:** `NEXT_PUBLIC_` prefix in Next.js means it's exposed to the browser!

---

### 4. Using .env Doesn't Mean You're Safe
`.env` just prevents pushing secrets to git. But if you reference those keys in client code, they still get bundled and shipped to users.

```bash
# .env
OPENAI_KEY=sk-xxx           # Server-only (safe)
NEXT_PUBLIC_API_URL=https:// # Client-exposed (intentional)
NEXT_PUBLIC_OPENAI_KEY=sk-xxx # DANGER - exposed to everyone!
```

**Audit:** Search your codebase for `NEXT_PUBLIC_` or `VITE_` prefixed secrets. They should NEVER be API keys.

---

### 5. Don't Do Math on the Phone
Avoid calculating prices, scores, or sensitive logic on the user's device. If the logic lives on their phone/browser, they can change the math.

```javascript
// BAD - client calculates price
const price = items.reduce((sum, item) => sum + item.price, 0);
const discount = user.isPremium ? 0.2 : 0;
const total = price * (1 - discount);
await charge(total);  // User can modify 'total' in devtools

// GOOD - server calculates everything
const { total } = await fetch('/api/calculate-price', {
  method: 'POST',
  body: JSON.stringify({ itemIds: items.map(i => i.id) })
});
// Server looks up real prices, applies real discounts, returns final number
```

---

### 6. Sanitize Everything
If a user types weird code into a comment box, it could break your database or execute in other users' browsers (XSS).

```python
# SQL Injection - BAD
query = f"SELECT * FROM users WHERE email = '{email}'"

# SQL Injection - GOOD (parameterized)
query = "SELECT * FROM users WHERE email = :email"
db.execute(query, {"email": email})

# XSS - BAD
<div dangerouslySetInnerHTML={{ __html: userComment }} />

# XSS - GOOD
<div>{userComment}</div>  # React auto-escapes
```

**Rule:** Never trust user input. Validate, sanitize, escape.

---

### 7. Put a Speed Limit on Buttons (Rate Limiting)
Without rate limiting, a bot could click your "send email" or "generate image" button 1,000 times a second. This crashes your app and costs you a fortune.

```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/generate")
@limiter.limit("10/minute")  # Max 10 requests per minute per IP
async def generate(request: Request):
    ...
```

**Tiers:**
- Auth endpoints (login/register): 5/minute
- AI generation: 10-30/minute depending on tier
- Read endpoints: 100-500/minute
- Webhooks: Verify signature, no rate limit needed

---

### 8. Don't Log the Sensitive Stuff
When debugging, it's tempting to log everything. Make sure you aren't printing passwords, emails, API keys, or tokens where anyone can see them.

```python
# BAD
logger.info(f"User login: {email}, password: {password}")
logger.info(f"API call with key: {api_key}")

# GOOD
logger.info(f"User login attempt: {email}")
logger.info(f"API call with key: {api_key[:8]}...")  # Only first 8 chars

# BETTER - use structured logging with automatic redaction
logger.info("User login", extra={"email": email})  # Configure redaction rules
```

**Audit:** Search logs for `password`, `token`, `key`, `secret`, `bearer`.

---

### 9. Audit With a Rival AI
If you coded your app with Claude, ask Gemini or GPT-4 to audit it for security vulnerabilities. Using a second AI model catches blind spots.

```
Prompt for security audit:

"Audit this code for security vulnerabilities. Check for:
- SQL injection
- XSS (cross-site scripting)
- CSRF (cross-site request forgery)
- Authentication/authorization bypasses
- Exposed secrets or API keys
- Rate limiting gaps
- Input validation issues
- Sensitive data in logs
- Insecure dependencies

Be thorough and assume an attacker will try to exploit this."
```

---

### 10. Keep Dependencies Up to Date
Old versions have known bugs that hackers exploit. Regular updates patch those holes.

```bash
# Check for vulnerabilities
npm audit
pip-audit

# Update dependencies
npm update
pip install --upgrade -r requirements.txt

# Use automated tools
# - Dependabot (GitHub)
# - Snyk
# - Renovate
```

**Schedule:** Run vulnerability scans weekly. Update critical security patches immediately.

---

### 11. Error Handling Without Revealing Too Much
Don't let error messages spill secrets like database details, stack traces, or internal paths.

```python
# BAD - reveals internal structure
except Exception as e:
    return {"error": str(e)}
    # Could expose: "PostgreSQL error at /var/www/app/db.py line 47: column 'password' does not exist"

# GOOD - vague for users, detailed in logs
except Exception as e:
    logger.error(f"Database error: {e}", exc_info=True)  # Full details in private logs
    return {"error": "Something went wrong. Please try again."}  # Generic for users
```

**Production:** Never return stack traces to users. Log them privately.

---

## Implementation Checklist

### Authentication & Authorization
- [ ] Use Clerk/Auth0/NextAuth - never roll your own auth
- [ ] Check authorization on EVERY endpoint (not just authentication)
- [ ] API keys scoped per organization (not per user)
- [ ] JWT tokens with short expiry (15min access, 7d refresh)
- [ ] RBAC for team features (admin, member, viewer roles)
- [ ] Session invalidation on password change
- [ ] Rate limit auth endpoints (5/minute max)

### API Security
- [ ] All endpoints require auth (except public + signed webhooks)
- [ ] Input validation on all endpoints (Pydantic/Zod)
- [ ] No sensitive data in URL params (use POST body)
- [ ] CORS restricted to your domains only
- [ ] Request size limits (prevent payload bombs)
- [ ] Rate limiting on all endpoints (tier-based: 100/500/2000 req/min)

### Data Protection
- [ ] Encrypt API keys/tokens at rest in database
- [ ] Never log passwords, tokens, API keys, or PII
- [ ] GDPR compliant (delete user data on request)
- [ ] Database connections over SSL
- [ ] Secrets in env vars, never in code
- [ ] No secrets in client-side code (audit for NEXT_PUBLIC_, VITE_ prefixes)
- [ ] Search codebase for hardcoded secrets before deploy

### Business Logic
- [ ] All pricing/discounts/calculations on server only
- [ ] Premium features withheld by server, not hidden by client
- [ ] No trust of client-side data for critical operations
- [ ] Validate all business logic server-side (don't trust frontend)

### Third-Party API Keys (User's Keys)
- [ ] User OAuth tokens encrypted in DB
- [ ] Tokens refreshed automatically before expiry
- [ ] Tokens revoked on account deletion
- [ ] Request minimal OAuth scopes only

### Webhooks (Incoming)
- [ ] Signature verification on ALL webhooks (Stripe, etc.)
- [ ] Webhook secret rotation support
- [ ] Idempotency keys to prevent duplicate processing
- [ ] Timeout handling (don't hang on slow webhooks)

### Tracking & Links (if applicable)
- [ ] Short links validated before redirect
- [ ] No open redirects (whitelist destination domains)
- [ ] Tracking pixel uses CSP-safe approach
- [ ] Click fraud detection (rate limit per IP)

### Infrastructure
- [ ] HTTPS everywhere (no HTTP, ever)
- [ ] Security headers (HSTS, CSP, X-Frame-Options, X-Content-Type-Options)
- [ ] Database backups encrypted
- [ ] Separate staging/production environments
- [ ] Audit logs for admin actions
- [ ] No debug mode in production

### Monitoring & Maintenance
- [ ] Failed login attempt alerts (detect brute force)
- [ ] Unusual API usage alerts (detect abuse)
- [ ] Error tracking (Sentry) with PII sanitization
- [ ] Dependency vulnerability scanning weekly (npm audit, pip-audit)
- [ ] Dependabot/Snyk/Renovate enabled
- [ ] Security audit with rival AI before launch
- [ ] Incident response plan documented

---

## Security Audit Prompt

Use this prompt with a different AI than you used to build:

```
You are a security auditor. Analyze this codebase for vulnerabilities.

Check for:
1. SQL injection and NoSQL injection
2. XSS (cross-site scripting) - stored, reflected, DOM-based
3. CSRF (cross-site request forgery)
4. Broken authentication (weak passwords, session issues)
5. Broken authorization (IDOR, privilege escalation)
6. Sensitive data exposure (logs, error messages, client code)
7. Security misconfiguration (CORS, headers, debug mode)
8. Insecure deserialization
9. Using components with known vulnerabilities
10. Insufficient logging and monitoring
11. Rate limiting gaps
12. Business logic flaws (price manipulation, feature bypass)
13. API key exposure in client bundles
14. Improper input validation

For each issue found:
- Severity (Critical/High/Medium/Low)
- Location (file and line)
- Description of the vulnerability
- Proof of concept (how to exploit)
- Recommended fix with code example

Be thorough. Assume an attacker with full knowledge of the codebase.
```

---

## Quick Security Test

Before deploying, manually test:

1. **Auth bypass:** Try accessing /api/projects/123 without logging in
2. **IDOR:** Log in as User A, try to access User B's resources by changing IDs
3. **Premium bypass:** Open devtools, try to enable premium features client-side
4. **Rate limit:** Hit an endpoint 100 times rapidly, should get blocked
5. **XSS:** Enter `<script>alert('xss')</script>` in every input field
6. **SQL injection:** Enter `'; DROP TABLE users; --` in search fields
7. **Price manipulation:** Intercept checkout request, try changing the price
8. **Secret exposure:** View page source, check for API keys in JS bundles
