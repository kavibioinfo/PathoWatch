# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
PathoWatch Data Fetcher v2
Fetches SARS-CoV-2 genomic data with retries and fallback demo data.
"""

import os
import json
import time
import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

print("PathoWatch Data Fetcher v2 Starting...")

# ============================================================
# HELPER: Fetch with retries
# ============================================================

def fetch_with_retry(url, params=None, max_retries=3, timeout=60, stream=False):
    """Fetch URL with retry logic."""
    for attempt in range(max_retries):
        try:
            print(f"   Attempt {attempt + 1}/{max_retries}...", end=" ")
            response = requests.get(url, params=params, timeout=timeout, stream=stream)
            response.raise_for_status()
            print("")
            return response
        except requests.exceptions.Timeout:
            print(f" Timeout")
            if attempt < max_retries - 1:
                wait = 2 ** attempt
                print(f"   Retrying in {wait}s...")
                time.sleep(wait)
        except requests.exceptions.RequestException as e:
            print(f" {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
    return None

# ============================================================
# 1. FETCH NEXTSTRAIN TREE (with streaming for large file)
# ============================================================

def fetch_nextstrain_tree():
    """Download pre-computed phylogenetic tree from Nextstrain."""
    url = "https://data.nextstrain.org/ncov_global.json"
    output_file = DATA_DIR / "ncov_global.json"

    print(f"\nFetching Nextstrain phylogenetic tree...")
    print(f"   URL: {url}")
    print(f"   Note: This file is ~50MB, may take 1-2 minutes on slow connections")

    response = fetch_with_retry(url, max_retries=3, timeout=120, stream=True)
    if not response:
        print("   Failed to fetch. Will use fallback.")
        return False

    try:
        print("   Downloading...", end=" ")
        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        size_mb = os.path.getsize(output_file) / (1024 * 1024)
        print(f"Saved: {output_file} ({size_mb:.1f} MB)")
        return True
    except Exception as e:
        print(f" Error saving: {e}")
        return False

# ============================================================
# 2. FETCH OUTBREAK.INFO MUTATIONS
# ============================================================

def fetch_outbreak_mutations():
    """Fetch mutation data from Outbreak.info API."""
    url = "https://api.outbreak.info/genomics/prevalence-by-location"
    params = {"location_id": "global", "cumulative": "true", "ndays": "180"}

    print(f"\n Fetching mutation data from Outbreak.info...")

    response = fetch_with_retry(url, params=params, max_retries=3, timeout=60)
    if not response:
        return False

    try:
        data = response.json()
        output_file = DATA_DIR / "mutations.json"
        with open(output_file, 'w') as f:
            json.dump(data, f)
        print(f"  Saved: {output_file}")
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False

# ============================================================
# 3. FETCH LINEAGE PREVALENCE
# ============================================================

def fetch_lineage_prevalence():
    """Fetch lineage prevalence from Outbreak.info."""
    url = "https://api.outbreak.info/genomics/prevalence-by-location-all-lineages"
    params = {"location_id": "global", "ndays": "180", "other_threshold": "0.03", "nday_threshold": "5"}

    print(f"\n Fetching lineage prevalence data...")

    response = fetch_with_retry(url, params=params, max_retries=3, timeout=60)
    if not response:
        return False

    try:
        data = response.json()
        output_file = DATA_DIR / "lineages.json"
        with open(output_file, 'w') as f:
            json.dump(data, f)
        print(f"  Saved: {output_file}")
        return True
    except Exception as e:
        print(f"   Error: {e}")
        return False

# ============================================================
# 4. FETCH NCBI METADATA
# ============================================================

def fetch_ncbi_metadata():
    """Fetch SARS-CoV-2 metadata from NCBI."""
    url = "https://api.ncbi.nlm.nih.gov/datasets/v2alpha/virus/taxon/2697049/genome"
    params = {"page_size": 1000, "filters.reference_only": "false", "filters.complete_only": "false"}

    print(f"\n Fetching NCBI metadata...")

    response = fetch_with_retry(url, params=params, max_retries=3, timeout=60)
    if not response:
        return False

    try:
        data = response.json()
        output_file = DATA_DIR / "ncbi_metadata.json"
        with open(output_file, 'w') as f:
            json.dump(data, f)

        record_count = len(data.get("reports", []))
        print(f"    Saved: {output_file} ({record_count} records)")
        return True
    except Exception as e:
        print(f"    Error: {e}")
        return False

# ============================================================
# 5. FETCH VOC DATA
# ============================================================

def fetch_voc_data():
    """Generate VOC reference data."""
    voc_data = {
        "last_updated": datetime.now().isoformat(),
        "variants": [
            {"name": "Omicron", "pango_lineages": ["BA.1", "BA.2", "BA.4", "BA.5", "XBB", "EG.5", "JN.1", "KP.2", "KP.3", "XEC"], "who_label": "VOC", "first_identified": "South Africa", "date_first_identified": "2021-11", "status": "Active", "severity": "Moderate", "transmissibility": "Very High"},
            {"name": "Delta", "pango_lineages": ["B.1.617.2", "AY.1", "AY.2", "AY.3"], "who_label": "Former VOC", "first_identified": "India", "date_first_identified": "2020-10", "status": "Monitored", "severity": "High", "transmissibility": "High"},
            {"name": "Alpha", "pango_lineages": ["B.1.1.7"], "who_label": "Former VOC", "first_identified": "United Kingdom", "date_first_identified": "2020-09", "status": "Monitored", "severity": "High", "transmissibility": "High"},
            {"name": "Beta", "pango_lineages": ["B.1.351"], "who_label": "Former VOC", "first_identified": "South Africa", "date_first_identified": "2020-05", "status": "Monitored", "severity": "High", "transmissibility": "Moderate"},
            {"name": "Gamma", "pango_lineages": ["P.1", "P.1.1", "P.1.2"], "who_label": "Former VOC", "first_identified": "Brazil", "date_first_identified": "2020-11", "status": "Monitored", "severity": "High", "transmissibility": "Moderate"}
        ]
    }

    output_file = DATA_DIR / "voc_data.json"
    with open(output_file, 'w') as f:
        json.dump(voc_data, f, indent=2)

    print(f"\n Generating VOC reference data...")
    print(f"    Saved: {output_file}")
    return True

# ============================================================
# FALLBACK: Generate demo data for failed sources
# ============================================================

def generate_fallback_data():
    """Generate realistic demo data when APIs fail."""
    import random

    print("\n Generating fallback demo data for failed sources...")

    # Fallback lineage data
    months = pd.date_range("2024-01", "2025-06", freq="M").strftime("%Y-%m").tolist()
    lineages = ["JN.1", "KP.2", "KP.3", "XEC", "EG.5", "BA.2.86", "XBB.1.5", "BQ.1.1", "BA.5", "XBB"]

    lineage_results = []
    for lineage in lineages:
        base = random.uniform(0.02, 0.4)
        for month in months:
            trend = random.uniform(-0.01, 0.02)
            prop = max(0.001, min(0.9, base + trend + random.uniform(-0.02, 0.02)))
            lineage_results.append({
                "date": f"{month}-15",
                "lineage": lineage,
                "lineage_count": int(prop * 10000),
                "total_count": 10000
            })

    fallback_lineages = {"results": lineage_results}
    with open(DATA_DIR / "lineages.json", 'w') as f:
        json.dump(fallback_lineages, f)
    print("   Generated fallback lineage data")

    # Fallback mutation data
    mutations = ["D614G", "N501Y", "E484K", "K417N", "L452R", "T478K", "P681R", "N440K", "F486P", "R346T"]
    mutation_results = []
    for mutation in mutations:
        base_freq = random.uniform(0.1, 0.9)
        for month in months:
            freq = max(0, min(1, base_freq + random.uniform(-0.05, 0.05)))
            mutation_results.append({
                "mutation": mutation,
                "gene": "S",
                "date": f"{month}-15",
                "prevalence": round(freq, 4),
                "location": "global"
            })

    fallback_mutations = {"results": mutation_results}
    with open(DATA_DIR / "mutations.json", 'w') as f:
        json.dump(fallback_mutations, f)
    print("   Generated fallback mutation data")

    # Fallback Nextstrain metadata (small placeholder)
    fallback_tree = {"version": "v2", "meta": {"title": "SARS-CoV-2 global phylogeny"}, "tree": {}}
    with open(DATA_DIR / "ncov_global.json", 'w') as f:
        json.dump(fallback_tree, f)
    print("   Generated fallback tree metadata")

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("   PATHOWATCH DATA FETCHER v2")
    print("   With retry logic + fallback demo data")
    print("=" * 60)

    results = {
        "nextstrain_tree": fetch_nextstrain_tree(),
        "outbreak_mutations": fetch_outbreak_mutations(),
        "lineage_prevalence": fetch_lineage_prevalence(),
        "ncbi_metadata": fetch_ncbi_metadata(),
        "voc_data": fetch_voc_data()
    }

    print("\n" + "=" * 60)
    print("FETCH SUMMARY")
    print("=" * 60)

    for source, success in results.items():
        status = "SUCCESS" if success else "FAILED"
        print(f"   {source:25s} {status}")

    success_count = sum(results.values())
    print(f"\n   Total: {success_count}/{len(results)} sources fetched")

    # Generate fallback data for failed sources
    failed_count = len(results) - success_count
    if failed_count > 0:
        print(f"\n   {failed_count} source(s) failed. Generating fallback demo data...")
        generate_fallback_data()
        print("\n   Fallback data generated. Dashboard will show demo data.")
        print("    Run again later when APIs are available for live data.")

    print(f"\n   Next step: Run 'python scripts/process_data.py'")
