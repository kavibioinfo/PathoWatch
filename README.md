# 🌍 PathoWatch — Global SARS-CoV-2 Genomic Surveillance Dashboard

**Live at:** `https://hub.ayushnexa.com`

A real-time genomic surveillance dashboard tracking SARS-CoV-2 mutations, variants, and phylogenetic evolution using public data from Nextstrain, NCBI, and Outbreak.info.

## Architecture (Lite Version — Older-System Friendly)

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Data Sources   │────▶│  Python Scripts  │────▶│  Static JSON    │
│  (NCBI, Open)   │     │  (Run Weekly)    │     │  Data Files     │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                        │
┌─────────────────┐     ┌──────────────────┐           │
│  Streamlit      │◀────│  Pre-computed    │◀──────────┘
│  Dashboard      │     │  Analysis Results│
│  (Frontend)     │     │  (JSON/CSV)      │
└─────────────────┘     └──────────────────┘
        │
        ▼
┌─────────────────┐
│  hub.ayushnexa  │
│  (Streamlit     │
│   Cloud / Self) │
└─────────────────┘
```

## Why This Works on an i3-2310M

| Heavy Task | Our Solution |
|------------|-------------|
| Phylogenetic tree building (Augur/MAFFT) | Use Nextstrain's **pre-computed trees** |
| Sequence alignment | **Skip entirely** — use metadata only |
| Real-time data pipeline | **Weekly batch script** via GitHub Actions |
| Database server | **JSON files** — no PostgreSQL/MongoDB |
| Complex backend | **Streamlit** — pure Python, minimal resources |

## Data Sources

1. **Nextstrain Open Data** — Pre-built phylogenetic trees (`https://data.nextstrain.org/ncov_global.json`)
2. **NCBI Datasets CLI** — Genomic metadata (no API key needed)
3. **Outbreak.info API** — Mutation frequencies and variant data (open, no key)
4. **Pathoplexus** — Modern open genomic database (fallback)

## Pages

1. **Global Overview** — Geographic spread map, lineage distribution
2. **Phylogenetic Tree** — Embedded Nextstrain Auspice viewer
3. **Mutation Tracker** — Spike protein mutation heatmap by month
4. **Variant Alerts** — VOC table with growth rates and alerts
5. **Download Center** — CSV/JSON exports for epidemiologists

## Tech Stack

- **Python 3.10+**
- **Streamlit** — Dashboard framework
- **Plotly** — Interactive visualizations
- **Pandas** — Data manipulation
- **Requests** — API fetching
- **GitHub Actions** — Weekly automated data updates (runs in cloud)

## Quick Start

```bash
# 1. Clone and enter
pip install -r requirements.txt

# 2. Fetch initial data (lightweight, runs on your i3)
python scripts/fetch_data.py

# 3. Run dashboard locally
streamlit run dashboard/app.py

# 4. Open http://localhost:8501
```

## Deployment

### Option A: Streamlit Cloud (Recommended)
1. Push to GitHub
2. Connect repo at [share.streamlit.io](https://share.streamlit.io)
3. Free tier, auto-deploys on push
4. Point `hub.ayushnexa.com` CNAME to Streamlit Cloud

### Option B: Self-Hosted
1. Build Docker image: `docker build -t pathowatch .`
2. Deploy on VPS with `docker-compose up -d`

## Weekly Auto-Update

GitHub Actions runs every Sunday at 2 AM UTC:
- Fetches latest data from all sources
- Processes and saves to `data/processed/`
- Commits updated JSON files back to repo
- Dashboard auto-refreshes on next load

## Author

**Ayush** — Bioinformatics & Data Science Portfolio Project
Part of the ayushnexa project suite (SeqLens, OmniGen, CellScribe, PathoWatch)
