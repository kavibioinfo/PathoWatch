# 🚀 PathoWatch Quick Start Guide

## For Your System (Intel i3-2310M, 9GB RAM, Windows)

### Step 1: Open VS Code
1. Open VS Code
2. File → Open Folder → Select `PathoWatch/`
3. Open Terminal: `Ctrl + ~`

### Step 2: Create Virtual Environment (Recommended)
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Run Setup
```bash
python scripts/setup.py
```
This will:
- Install all dependencies
- Create data folders
- Fetch initial data from APIs
- Process data for the dashboard

**Expected time:** 5-10 minutes on your i3

### Step 4: Start Dashboard
```bash
streamlit run dashboard/app.py
```

**Expected time:** 10-20 seconds to load on your i3

Open browser: `http://localhost:8501`

### Step 5: Verify All 5 Pages Work
1. **Global Overview** — Map, charts, metrics
2. **Phylogenetic Tree** — Embedded Nextstrain viewer
3. **Mutation Tracker** — Heatmap + mutation table
4. **Variant Alerts** — Alert cards + variant table
5. **Download Center** — Export buttons + API docs

---

## Deployment Options

### Option A: Streamlit Cloud (FREE — Recommended)

1. **Push to GitHub:**
```bash
git init
git add .
git commit -m "Initial PathoWatch commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/pathowatch.git
git push -u origin main
```

2. **Connect to Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app" → Select your repo
   - Main file path: `dashboard/app.py`
   - Click "Deploy"

3. **Custom Domain:**
   - In Streamlit Cloud settings, add custom domain
   - Enter: `hub.ayushnexa.com`
   - Add DNS CNAME record pointing to Streamlit's URL

**Cost:** $0/month
**Uptime:** 24/7
**Auto-updates:** Yes (via GitHub Actions)

---

### Option B: Self-Hosted on VPS

If you have a VPS (DigitalOcean, Linode, etc.):

```bash
# On your VPS
git clone https://github.com/YOUR_USERNAME/pathowatch.git
cd pathowatch
docker-compose up -d
```

Then point `hub.ayushnexa.com` to your VPS IP.

---

### Option C: Static Site on hub.ayushnexa (Limited)

If your current hosting only supports static HTML:
- You CANNOT run Streamlit there
- Alternative: Export dashboard as static HTML (limited interactivity)
- Better: Use Streamlit Cloud + CNAME to `hub.ayushnexa.com`

---

## Weekly Auto-Update (GitHub Actions)

Already configured in `.github/workflows/update_data.yml`

**What it does:**
- Every Sunday at 2 AM UTC
- Runs in GitHub's cloud (NOT on your laptop)
- Fetches fresh data from all APIs
- Processes and commits to repo
- Dashboard auto-refreshes on next visit

**To enable:**
1. Push repo to GitHub
2. Go to repo → Actions → Enable workflows
3. That's it — fully automated

---

## Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### Dashboard loads slowly
- Normal on i3-2310M. First load takes ~20s.
- Subsequent loads are faster (cached).
- Close other apps to free RAM.

### API fetch fails
- Check internet connection
- Some APIs may be temporarily down
- Re-run: `python scripts/fetch_data.py`

### Streamlit port already in use
```bash
streamlit run dashboard/app.py --server.port 8502
```

---

## File Structure

```
PathoWatch/
├── dashboard/
│   └── app.py              ← Main Streamlit app (START HERE)
├── scripts/
│   ├── fetch_data.py       ← Fetches data from APIs
│   ├── process_data.py     ← Processes raw → dashboard JSON
│   └── setup.py            ← One-time setup script
├── src/
│   └── utils.py            ← Helper functions
├── data/
│   ├── raw/                ← Fetched API data
│   └── processed/          ← Dashboard-ready JSON
├── .github/workflows/
│   └── update_data.yml     ← Weekly auto-update
├── .streamlit/
│   └── config.toml         ← Dark theme config
├── Dockerfile              ← Container config
├── docker-compose.yml      ← Docker deployment
├── requirements.txt        ← Python dependencies
└── README.md               ← Project documentation
```

---

## Your Recruiter Hook

Once live, add this to your LinkedIn/GitHub:

> **"Architected PathoWatch — a real-time SARS-CoV-2 genomic surveillance system 
> processing thousands of sequences with automated phylogenetic analysis, 
> interactive mutation tracking, and variant alert systems. Built with Python, 
> Streamlit, and Plotly, deployed on Streamlit Cloud with automated GitHub Actions 
> data pipelines."**

---

## Next: Project 5?

After PathoWatch is live, we can revisit errors in:
- SeqLens
- OmniGen
- CellScribe

Or start Project 5. Your call.
