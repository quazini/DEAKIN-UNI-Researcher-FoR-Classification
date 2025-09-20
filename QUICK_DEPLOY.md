# 🚀 Quick Deploy Guide (No Domain Required)

Deploy your FoR Classification System to Digital Ocean App Platform using their provided URL (no custom domain needed).

## ⚡ Quick Setup (5 minutes)

### Step 1: Get Digital Ocean Ready

1. **Sign up for Digital Ocean**: https://cloud.digitalocean.com/
2. **Create API Token**:
   - Go to: API → Tokens → Generate New Token
   - Name: `for-classification`
   - Write access: ✅ Enabled
   - Copy the token

### Step 2: Setup Environment

**Your app supports multiple configuration methods:**

#### Option A: Environment Variables (Docker/Production)
- Digital Ocean App Platform automatically uses environment variables
- Set via GitHub Secrets (recommended) or DO dashboard

#### Option B: .env File (Local Development)
```bash
# Copy and edit the environment file
cp .env.example .env

# Edit .env with your values:
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
DEFAULT_WEBHOOK_URL=https://your-n8n-instance.com/webhook/your-id
ADMIN_EMAIL=admin@yourdomain.com
```

#### Option C: Streamlit Secrets (Legacy)
- Create `.streamlit/secrets.toml` (see `.streamlit/secrets.toml.example`)

**For deployment, we'll use Option A (GitHub Secrets → Environment Variables)**

### Step 3: Deploy via GitHub (Easiest)

1. **Fork this repository** to your GitHub account

2. **Add GitHub Secrets**:
   - Go to: Settings → Secrets and variables → Actions
   - Add these 4 secrets:

   | Secret Name | Value |
   |-------------|-------|
   | `DO_ACCESS_TOKEN` | Your DO API token |
   | `DO_APP_NAME` | `for-classification-app` |
   | `SUPABASE_URL` | Your Supabase URL |
   | `SUPABASE_KEY` | Your Supabase key |

3. **Update app.yaml**:
   ```yaml
   # Line 12-14: Update with your GitHub info
   github:
     repo: YOUR_GITHUB_USERNAME/YOUR_REPO_NAME
     branch: main

   # Line 58: Update with your webhook URL
   - key: DEFAULT_WEBHOOK_URL
     value: "YOUR_N8N_WEBHOOK_URL"
   ```

4. **Deploy**:
   ```bash
   git add .
   git commit -m "Configure for deployment"
   git push origin main
   ```

   ✅ GitHub Actions will automatically build and deploy!

### Step 4: Get Your App URL

1. **Install Digital Ocean CLI** (optional but helpful):
   ```bash
   # macOS
   brew install doctl

   # Or download from: https://github.com/digitalocean/doctl/releases
   ```

2. **Get your app URL**:
   ```bash
   # Login to DO CLI
   doctl auth init
   # Paste your API token

   # Get your app URL
   doctl apps list
   doctl apps get for-classification-app
   ```

   Or check the GitHub Actions deployment log for the URL.

---

## 🎯 Alternative: Manual Deploy

If you prefer manual deployment:

```bash
# Install DO CLI and authenticate
doctl auth init

# Deploy directly
doctl apps create --spec app.yaml --wait

# Get your app URL
doctl apps list
```

---

## 📱 Your App URL Format

Digital Ocean provides URLs like:
- `https://for-classification-app-xxxxx.ondigitalocean.app`
- `https://sample-app-xxxx.ondigitalocean.app`

**Features included FREE:**
- ✅ **HTTPS/SSL** - Secure by default
- ✅ **Global CDN** - Fast worldwide
- ✅ **Auto-scaling** - Handles traffic spikes
- ✅ **Monitoring** - Built-in health checks

---

## 💰 Cost

**Digital Ocean App Platform**: $12/month
- 512MB RAM, 1 vCPU
- Includes SSL, CDN, monitoring
- No domain costs needed!

**Optional Upgrades**:
- Professional tier ($25/month) for more resources
- Add custom domain later if needed

---

## 🔧 After Deployment

1. **Test your app** at the provided URL
2. **Create admin user** via the app interface
3. **Test webhook connection** using the debug tools
4. **Monitor** via Digital Ocean dashboard

---

## 🚨 Troubleshooting

**Deployment fails?**
```bash
# Check GitHub Actions logs
# Or check DO App Platform logs:
doctl apps logs for-classification-app --follow
```

**App won't start?**
- Verify all environment variables in GitHub secrets
- Check Supabase credentials are correct
- Ensure n8n webhook is active

**Need help?**
- Check the full `DEPLOYMENT.md` guide
- Digital Ocean has great documentation
- GitHub Actions logs show detailed error info

---

## 🎉 You're Done!

Your app will be live at: `https://your-app-name-xxxxx.ondigitalocean.app`

**Next steps:**
1. Bookmark your app URL
2. Share with your team
3. Consider adding a custom domain later if needed

The Digital Ocean provided URL is perfect for production use and includes all the enterprise features you need!