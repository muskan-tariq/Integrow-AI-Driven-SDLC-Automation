# API Setup Guide - Phase 1

**Purpose:** Step-by-step guide to get all required API keys for Phase 1 development

---

## 🎯 Overview

Phase 1 requires 4 APIs (2 required, 2 optional):

| API | Status | Free Tier | Purpose |
|-----|--------|-----------|---------|
| **Groq** | Required | 14,400 req/day | Fast LLM for ambiguity detection |
| **Gemini** | Required | 1,500 req/day | Free LLM for completeness checking |
| **HuggingFace** | Optional | Unlimited* | Advanced NER (Named Entity Recognition) |
| **OpenAI** | Optional | $5 credits | Backup LLM (fallback only) |

*Rate limited but sufficient for development

---

## 1️⃣ Groq API (Required - Primary LLM)

**Why:** Super-fast inference (500+ tokens/second), generous free tier

### Step-by-Step:

1. **Go to:** https://console.groq.com/
2. **Sign up:**
   - Click "Sign Up"
   - Use Google or GitHub account
   - Complete registration
3. **Get API Key:**
   - Click on your profile (top right)
   - Select "API Keys"
   - Click "Create API Key"
   - Give it a name: "InteGrow Development"
   - Copy the key (starts with `gsk_`)
4. **Add to .env:**
   ```bash
   GROQ_API_KEY=gsk_your_key_here
   ```

### Test Connection:
```bash
cd backend
.\integrow_env\Scripts\Activate.ps1
python tests/test_apis.py
```

You should see: `✅ Groq API: Connected`

---

## 2️⃣ Google Gemini API (Required - Secondary LLM)

**Why:** Free, fast, and reliable for completeness checking

### Step-by-Step:

1. **Go to:** https://makersuite.google.com/
2. **Sign in:**
   - Use your Google account
   - Accept terms and conditions
3. **Get API Key:**
   - Click "Get API Key" in the top right
   - If you have an existing project, select it
   - Otherwise, click "Create API key in new project"
   - Copy the key (starts with `AIzaSy`)
4. **Add to .env:**
   ```bash
   GEMINI_API_KEY=AIzaSy_your_key_here
   ```

### Alternative Method:
1. Go to: https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Select or create a Google Cloud project
4. Copy the generated key

### Test Connection:
```bash
python tests/test_apis.py
```

You should see: `✅ Gemini API: Connected`

---

## 3️⃣ HuggingFace API (Optional - NER)

**Why:** Advanced Named Entity Recognition, completely free

### Step-by-Step:

1. **Go to:** https://huggingface.co/
2. **Sign up:**
   - Click "Sign Up"
   - Use email, Google, or GitHub
3. **Get API Token:**
   - Click on your profile picture (top right)
   - Select "Settings"
   - Navigate to "Access Tokens"
   - Click "New token"
   - Name: "InteGrow Development"
   - Role: Select "Read"
   - Click "Generate token"
   - Copy the token (starts with `hf_`)
4. **Add to .env:**
   ```bash
   HUGGINGFACE_API_KEY=hf_your_key_here
   ```

### Note:
- This is optional for Phase 1
- Local spaCy will be used as primary NER
- HuggingFace adds advanced entity recognition capabilities

---

## 4️⃣ OpenAI API (Optional - Fallback)

**Why:** Backup LLM when Groq/Gemini are unavailable (rare)

### Step-by-Step:

1. **Go to:** https://platform.openai.com/
2. **Sign up:**
   - Create an account
   - Verify email
3. **Add Payment Method:**
   - Go to "Settings" → "Billing"
   - Add a payment method (required even for free credits)
   - You get $5 free credits (expires after 3 months)
4. **Get API Key:**
   - Navigate to "API Keys"
   - Click "Create new secret key"
   - Name: "InteGrow Development"
   - Copy the key (starts with `sk-`)
5. **Add to .env:**
   ```bash
   OPENAI_API_KEY=sk_your_key_here
   ```

### Note:
- Only used as fallback when Groq and Gemini fail
- $5 credits cover ~33,000 requests with GPT-4o-mini
- Not required for development, but good to have

---

## 🔧 Additional Setup

### Redis Installation (Required)

**Option 1: Windows Installer**
1. Download from: https://github.com/microsoftarchive/redis/releases
2. Download: `Redis-x64-3.0.504.msi`
3. Run installer
4. Keep default settings
5. Redis will run as Windows service

**Option 2: Docker (Recommended)**
```bash
docker run -d -p 6379:6379 --name redis redis:7-alpine
```

**Test Redis:**
```bash
python tests/test_apis.py
```

You should see: `✅ Redis: Connected`

---

### spaCy Model Installation (Required)

```bash
cd backend
.\integrow_env\Scripts\Activate.ps1
python -m spacy download en_core_web_sm
```

**Test spaCy:**
```bash
python tests/test_apis.py
```

You should see: `✅ spaCy: Model 'en_core_web_sm' loaded`

---

## ✅ Verification Checklist

Run the complete API test:

```bash
cd "E:\Uni data\FYP\integrow\backend"
.\integrow_env\Scripts\Activate.ps1
python tests/test_apis.py
```

Expected output:
```
🔍 Testing API Connections for Phase 1
========================================

✅ Groq API: Connected
   Model: llama-3.1-70b-versatile
   Response: test successful

✅ Gemini API: Connected
   Model: gemini-1.5-flash
   Response: test successful

✅ HuggingFace: Package installed
   API key configured

⚠️  OpenAI API: Not configured (optional fallback)

✅ spaCy: Model 'en_core_web_sm' loaded

✅ Redis: Connected
   URL: redis://localhost:6379

📊 Test Results Summary
=======================
✅ PASS - Groq (Required)
✅ PASS - Gemini (Required)
✅ PASS - HuggingFace (Optional)
⚠️  PASS - OpenAI (Optional)
✅ PASS - spaCy (Required)
✅ PASS - Redis (Required)

✅ All required APIs are configured correctly!
🚀 You're ready to start Phase 1 development!
```

---

## 🔒 Security Best Practices

1. **Never commit .env file:**
   - Already in .gitignore
   - Contains sensitive API keys

2. **Use environment variables:**
   - API keys loaded from .env
   - No hardcoded keys in code

3. **Rotate keys if exposed:**
   - If you accidentally commit keys, revoke and create new ones
   - All platforms allow key rotation

4. **Monitor usage:**
   - Check API dashboards regularly
   - Set up alerts for high usage
   - Stay within free tiers during development

---

## 💰 Cost Tracking

### Free Tier Limits (Development):

| API | Daily Limit | Monthly Limit | Cost if Exceeded |
|-----|------------|---------------|------------------|
| Groq | 14,400 req | ~430K req | N/A (rate limited) |
| Gemini | 1,500 req | ~45K req | N/A (rate limited) |
| HuggingFace | Unlimited* | Unlimited* | Free |
| OpenAI | N/A | $5 credits | $0.15-0.60/1K req |

*Rate limited but sufficient

### Expected Usage (Development):
- **Testing:** ~50 requests/day
- **Development:** ~100 requests/day
- **Demo/Review:** ~20 requests/day
- **Total:** ~170 requests/day (well under limits)

---

## 🐛 Troubleshooting

### "Invalid API Key" Error:

**Groq:**
- Ensure key starts with `gsk_`
- Check for extra spaces in .env
- Regenerate key if needed

**Gemini:**
- Ensure key starts with `AIzaSy`
- Verify Google Cloud project is active
- Check API is enabled in Google Cloud Console

### "Rate Limit Exceeded":

**Solution:**
- Implement caching (already in roadmap)
- Reduce test frequency
- Use fallback API

### "Connection Refused" (Redis):

**Solution:**
- Check if Redis is running: `redis-cli ping`
- Windows: Check Windows Services for Redis
- Docker: `docker ps` to verify container is running

---

## 📚 Additional Resources

### API Documentation:
- **Groq:** https://console.groq.com/docs
- **Gemini:** https://ai.google.dev/docs
- **HuggingFace:** https://huggingface.co/docs/api-inference
- **OpenAI:** https://platform.openai.com/docs

### Support:
- **Groq Discord:** https://discord.gg/groq
- **Gemini Forum:** https://ai.google.dev/community
- **HuggingFace Forum:** https://discuss.huggingface.co/

---

## 🎉 Ready to Code!

Once all tests pass, you're ready to start implementing:

1. **Parser Agent** (uses spaCy + HuggingFace)
2. **Ambiguity Detector** (uses Groq)
3. **Completeness Checker** (uses Gemini)
4. **Ethics Auditor** (local patterns + AIF360)

Follow the roadmap in `PHASE1_DEVELOPMENT_ROADMAP.md`!

---

**Last Updated:** October 7, 2025  
**Next:** Install dependencies and start Parser Agent implementation
