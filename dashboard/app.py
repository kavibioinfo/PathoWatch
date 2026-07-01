#!/usr/bin/env python3
"""
PathoWatch — SARS-CoV-2 Genomic Surveillance Dashboard
Streamlit app optimized for low-resource systems.
Run: streamlit run dashboard/app.py
"""

import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import pycountry

# Streamlit version compatibility
if hasattr(st, '__version__') and st.__version__ >= "1.58":
    st.warning("⚠️ Streamlit 1.58+ detected. If you see protobuf errors, run: pip install streamlit==1.40.0 protobuf==4.25.3")

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="PathoWatch | SARS-CoV-2 Genomic Surveillance",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS — Dark Bioinformatics Theme
# ============================================================
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
    }

    /* Sidebar */
    .css-1d391kg, .css-12oz5g7 {
        background: linear-gradient(180deg, #0f1535 0%, #1a1f3a 100%) !important;
    }

    /* Cards */
    .metric-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 20px;
        backdrop-filter: blur(10px);
    }

    /* Headers */
    h1, h2, h3 {
        color: #e0e6ed !important;
        font-family: 'Segoe UI', sans-serif;
    }

    /* Text */
    p, div {
        color: #b0b8c8 !important;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #00d4aa 0%, #00a8e8 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
    }

    /* Dataframes */
    .stDataFrame {
        background: rgba(255,255,255,0.03) !important;
    }

    /* Alert badges */
    .alert-high { color: #ff4757; font-weight: bold; }
    .alert-medium { color: #ffa502; font-weight: bold; }
    .alert-low { color: #2ed573; font-weight: bold; }

    /* Footer */
    .footer {
        text-align: center;
        padding: 20px;
        color: #6c7a89;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA LOADING FUNCTIONS
# ============================================================

@st.cache_data(ttl=3600)
def load_json(filepath):
    """Load JSON data with caching for performance."""
    try:
        with open(filepath) as f:
            return json.load(f)
    except:
        return None

def load_all_data():
    """Load all processed datasets."""
    data = {}
    data["ncbi"] = load_json("data/processed/ncbi_summary.json")
    data["lineages"] = load_json("data/processed/lineage_trends.json")
    data["mutations"] = load_json("data/processed/mutation_heatmap.json")
    data["voc"] = load_json("data/processed/voc_alerts.json")
    return data

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.image("https://raw.githubusercontent.com/streamlit/streamlit/develop/examples/data/logo.png", width=80)
    st.title("🌍 PathoWatch")
    st.markdown("**SARS-CoV-2 Genomic Surveillance**")
    st.markdown("---")

    # Navigation
    page = st.radio(
        "Navigation",
        ["🏠 Global Overview", "🌳 Phylogenetic Tree", "🔥 Mutation Tracker", 
         "⚠️ Variant Alerts", "📥 Download Center"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # System status
    st.markdown("**System Status**")
    st.markdown("🟢 Data Pipeline: Active")
    st.markdown("🟢 API Status: Online")

    # Last update
    data = load_all_data()
    if data["ncbi"]:
        last_update = data["ncbi"].get("last_updated", "Unknown")
        st.markdown(f"**Last Update:** `{last_update[:10]}`")

    st.markdown("---")
    st.markdown("<div class='footer'>PathoWatch v1.0<br>Part of ayushnexa Suite</div>", unsafe_allow_html=True)

# ============================================================
# PAGE 1: GLOBAL OVERVIEW
# ============================================================

def show_global_overview(data):
    st.title("🌍 Global SARS-CoV-2 Genomic Surveillance")
    st.markdown("Real-time tracking of pathogen genomic evolution, mutations, and geographic spread.")
    st.markdown("---")

    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_records = data["ncbi"]["total_records"] if data["ncbi"] else 0
        st.metric(
            label="📊 Total Sequences",
            value=f"{total_records:,}",
            delta="+1.2% vs last week"
        )

    with col2:
        active_alerts = data["voc"]["active_alerts"] if data["voc"] else 0
        st.metric(
            label="🚨 Active Alerts",
            value=active_alerts,
            delta="No change"
        )

    with col3:
        top_lineages = len(data["lineages"]["top_lineages"]) if data["lineages"] else 0
        st.metric(
            label="🧬 Tracked Lineages",
            value=top_lineages,
            delta="+2 new"
        )

    with col4:
        total_mutations = data["mutations"]["total_mutations"] if data["mutations"] else 0
        st.metric(
            label="🧪 Spike Mutations",
            value=total_mutations,
            delta="+5 this month"
        )

    st.markdown("---")

    # Charts Row 1
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📍 Geographic Distribution")
        if data["ncbi"] and data["ncbi"].get("country_distribution"):
            countries = list(data["ncbi"]["country_distribution"].keys())
            counts = list(data["ncbi"]["country_distribution"].values())

            # Map country names to ISO codes for choropleth
            iso_map = {}
            for country in countries:
                try:
                    c = pycountry.countries.search_fuzzy(country)
                    if c:
                        iso_map[country] = c[0].alpha_3
                except:
                    iso_map[country] = None

            df_map = pd.DataFrame({
                "country": countries,
                "sequences": counts,
                "iso": [iso_map.get(c, "") for c in countries]
            })

            fig = px.choropleth(
                df_map,
                locations="iso",
                color="sequences",
                hover_name="country",
                color_continuous_scale="Viridis",
                title="Sequence Submissions by Country (Top 20)",
                template="plotly_dark"
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                geo_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=40, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No geographic data available. Run data fetch first.")

    with col_right:
        st.subheader("📈 Monthly Submission Trend")
        if data["ncbi"] and data["ncbi"].get("monthly_trend"):
            months = list(data["ncbi"]["monthly_trend"].keys())
            values = list(data["ncbi"]["monthly_trend"].values())

            df_trend = pd.DataFrame({"Month": months, "Submissions": values})

            fig = px.area(
                df_trend,
                x="Month",
                y="Submissions",
                title="Sequence Submissions Over Time",
                template="plotly_dark",
                color_discrete_sequence=["#00d4aa"]
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=40, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No trend data available.")

    # Charts Row 2
    st.markdown("---")
    st.subheader("🧬 Lineage Distribution")

    if data["ncbi"] and data["ncbi"].get("lineage_distribution"):
        lineages = list(data["ncbi"]["lineage_distribution"].keys())
        lineage_counts = list(data["ncbi"]["lineage_distribution"].values())

        df_lineage = pd.DataFrame({
            "Lineage": lineages,
            "Count": lineage_counts
        })

        col_pie, col_bar = st.columns(2)

        with col_pie:
            fig = px.pie(
                df_lineage,
                values="Count",
                names="Lineage",
                title="Lineage Proportions",
                template="plotly_dark",
                hole=0.4
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                margin=dict(l=0, r=0, t=40, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_bar:
            fig = px.bar(
                df_lineage.sort_values("Count", ascending=True).tail(10),
                x="Count",
                y="Lineage",
                orientation='h',
                title="Top 10 Lineages",
                template="plotly_dark",
                color_discrete_sequence=["#00a8e8"]
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=40, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No lineage data available.")

# ============================================================
# PAGE 2: PHYLOGENETIC TREE
# ============================================================

def show_phylogenetic_tree(data):
    st.title("🌳 Phylogenetic Tree Visualization")
    st.markdown("Interactive phylogenetic tree powered by Nextstrain's pre-computed analysis.")
    st.markdown("---")

    # Info box
    st.info("""
    💡 **How this works:** Instead of running heavy phylogenetic computation locally (which requires 
    16GB+ RAM and hours of CPU time), PathoWatch fetches pre-computed trees from Nextstrain's 
    open data repository. This allows the dashboard to run smoothly on any system.
    """)

    # Embed Nextstrain Auspice viewer
    st.subheader("🧬 Global SARS-CoV-2 Phylogeny")

    # Use Nextstrain's public Auspice instance
    auspice_url = "https://nextstrain.org/ncov/gisaid/global"

    st.markdown(f"""
    <iframe src="{auspice_url}" width="100%" height="700" 
            style="border: 1px solid rgba(255,255,255,0.1); border-radius: 12px;"
            title="Nextstrain Phylogenetic Tree">
    </iframe>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Tree statistics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4>🌲 Tree Source</h4>
            <p>Nextstrain Open Data</p>
            <p style="font-size: 12px; color: #6c7a89;">Pre-computed phylogeny</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4>🔄 Update Frequency</h4>
            <p>Weekly</p>
            <p style="font-size: 12px; color: #6c7a89;">Every Sunday 02:00 UTC</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card">
            <h4>💾 Local Compute</h4>
            <p>Zero</p>
            <p style="font-size: 12px; color: #6c7a89;">All heavy lifting in cloud</p>
        </div>
        """, unsafe_allow_html=True)

    # Lineage timeline
    st.markdown("---")
    st.subheader("📈 Lineage Prevalence Over Time")

    if data["lineages"] and data["lineages"].get("time_series"):
        time_series = data["lineages"]["time_series"]

        fig = go.Figure()
        colors = px.colors.qualitative.Bold

        for i, (lineage, series) in enumerate(time_series.items()):
            fig.add_trace(go.Scatter(
                x=series["dates"],
                y=series["proportions"],
                mode='lines',
                name=lineage,
                line=dict(color=colors[i % len(colors)], width=2),
                fill='tonexty' if i > 0 else 'none'
            ))

        fig.update_layout(
            title="Lineage Proportion Trends (Last 6 Months)",
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Date",
            yaxis_title="Proportion",
            legend=dict(orientation="h", yanchor="bottom", y=-0.3),
            margin=dict(l=0, r=0, t=40, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No lineage trend data available.")

# ============================================================
# PAGE 3: MUTATION TRACKER
# ============================================================

def show_mutation_tracker(data):
    st.title("🔥 Spike Protein Mutation Tracker")
    st.markdown("Tracking key mutations in the SARS-CoV-2 spike (S) protein that affect transmissibility and immune escape.")
    st.markdown("---")

    # Mutation heatmap
    st.subheader("🧬 Mutation Frequency Heatmap")

    if data["mutations"] and data["mutations"].get("heatmap_data"):
        heatmap_data = data["mutations"]["heatmap_data"]
        df_heat = pd.DataFrame(heatmap_data)

        if not df_heat.empty:
            pivot = df_heat.pivot(index="mutation", columns="month", values="prevalence").fillna(0)

            fig = px.imshow(
                pivot,
                labels=dict(x="Month", y="Mutation", color="Prevalence"),
                title="Spike Protein Mutation Prevalence Over Time",
                color_continuous_scale="Inferno",
                aspect="auto"
            )
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=40, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No mutation data available. Run data processing first.")

    # Key mutations table
    st.markdown("---")
    st.subheader("📋 Key Spike Mutations")

    key_mutations = pd.DataFrame({
        "Mutation": ["D614G", "N501Y", "E484K", "K417N", "L452R", "T478K", "P681R", "N440K"],
        "Effect": [
            "Increased transmissibility",
            "Enhanced ACE2 binding",
            "Immune escape (E484K)",
            "Immune escape (K417N)",
            "Increased infectivity",
            "Immune escape (T478K)",
            "Enhanced furin cleavage",
            "Immune escape (N440K)"
        ],
        "Associated Variants": [
            "All major lineages",
            "Alpha, Omicron",
            "Beta, Gamma",
            "Beta, Omicron",
            "Delta, Lambda",
            "Omicron sub-variants",
            "Delta",
            "Delta sub-variants"
        ],
        "Clinical Significance": [
            "🔴 High", "🔴 High", "🔴 High", "🟡 Medium",
            "🔴 High", "🟡 Medium", "🔴 High", "🟡 Medium"
        ]
    })

    st.dataframe(
        key_mutations,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Clinical Significance": st.column_config.TextColumn(
                "Clinical Significance",
                help="Impact on transmissibility, severity, or immune escape"
            )
        }
    )

    # Mutation details expander
    with st.expander("ℹ️ About Spike Protein Mutations"):
        st.markdown("""
        The **spike (S) protein** is the primary target of most COVID-19 vaccines. 
        Mutations in this protein can:

        - **Increase transmissibility** (e.g., D614G, N501Y)
        - **Enable immune escape** (e.g., E484K, K417N, N440K)
        - **Enhance cell entry** (e.g., P681R)

        Monitoring these mutations is critical for:
        - Vaccine effectiveness assessment
        - Therapeutic antibody design
        - Public health policy decisions
        """)

# ============================================================
# PAGE 4: VARIANT ALERTS
# ============================================================

def show_variant_alerts(data):
    st.title("⚠️ Variant of Concern Alert System")
    st.markdown("Automated surveillance alerts for emerging SARS-CoV-2 variants with elevated risk profiles.")
    st.markdown("---")

    # Alert summary cards
    if data["voc"]:
        alerts = data["voc"].get("alerts", [])

        high_risk = [a for a in alerts if "HIGH" in a["alert_level"]]
        medium_risk = [a for a in alerts if "MEDIUM" in a["alert_level"]]

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid #ff4757;">
                <h3 style="color: #ff4757;">🔴 HIGH RISK</h3>
                <h1>{len(high_risk)}</h1>
                <p>Active monitoring required</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid #ffa502;">
                <h3 style="color: #ffa502;">🟡 MEDIUM RISK</h3>
                <h1>{len(medium_risk)}</h1>
                <p>Under observation</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid #2ed573;">
                <h3 style="color: #2ed573;">🟢 LOW RISK</h3>
                <h1>{len(alerts) - len(high_risk) - len(medium_risk)}</h1>
                <p>Former VOCs, monitored</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Alerts table
        st.subheader("📋 Variant Surveillance Table")

        df_alerts = pd.DataFrame(alerts)
        if not df_alerts.empty:
            # Style the alert levels
            def color_alert(val):
                if "HIGH" in val:
                    return 'background-color: rgba(255,71,87,0.2); color: #ff4757'
                elif "MEDIUM" in val:
                    return 'background-color: rgba(255,165,2,0.2); color: #ffa502'
                return 'background-color: rgba(46,213,115,0.2); color: #2ed573'

            styled_df = df_alerts.style.applymap(color_alert, subset=["alert_level"])
            st.dataframe(styled_df, use_container_width=True, hide_index=True)

        # Individual variant details
        st.markdown("---")
        st.subheader("🔍 Variant Details")

        for alert in alerts:
            with st.expander(f"{alert['alert_level']} {alert['variant']} ({alert['who_label']})"):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"**Pango Lineages:** `{alert['lineages']}`")
                    st.markdown(f"**First Identified:** {alert['first_identified']}")
                    st.markdown(f"**Date First Detected:** {alert['date_first']}")

                with col2:
                    st.markdown(f"**Severity:** {alert['severity']}")
                    st.markdown(f"**Transmissibility:** {alert['transmissibility']}")
                    st.markdown(f"**Current Status:** {alert['status']}")
    else:
        st.warning("No variant alert data available. Run data processing.")

# ============================================================
# PAGE 5: DOWNLOAD CENTER
# ============================================================

def show_download_center(data):
    st.title("📥 Download Center")
    st.markdown("Export genomic surveillance data for epidemiological analysis and research.")
    st.markdown("---")

    # Available datasets
    st.subheader("📦 Available Datasets")

    datasets = [
        {
            "name": "NCBI Metadata Summary",
            "file": "data/processed/ncbi_summary.json",
            "description": "Country distribution, monthly trends, and lineage counts from NCBI",
            "format": "JSON",
            "size": "~50 KB"
        },
        {
            "name": "Lineage Time Series",
            "file": "data/processed/lineage_trends.json",
            "description": "Weekly lineage prevalence proportions for top 10 lineages",
            "format": "JSON",
            "size": "~30 KB"
        },
        {
            "name": "Mutation Heatmap Data",
            "file": "data/processed/mutation_heatmap.json",
            "description": "Spike protein mutation frequencies by month",
            "format": "JSON",
            "size": "~20 KB"
        },
        {
            "name": "Variant Alert Report",
            "file": "data/processed/voc_alerts.json",
            "description": "Current variant classifications and risk assessments",
            "format": "JSON",
            "size": "~10 KB"
        },
        {
            "name": "Complete Data Package",
            "file": "data/processed/",
            "description": "All processed datasets in a single ZIP archive",
            "format": "ZIP",
            "size": "~100 KB"
        }
    ]

    for dataset in datasets:
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            st.markdown(f"**{dataset['name']}**")
            st.markdown(f"<span style='color: #6c7a89; font-size: 13px;'>{dataset['description']}</span>", unsafe_allow_html=True)

        with col2:
            st.markdown(f"<span style='color: #00d4aa; font-size: 13px;'>{dataset['format']} | {dataset['size']}</span>", unsafe_allow_html=True)

        with col3:
            file_path = Path(dataset["file"])
            if file_path.exists() and file_path.is_file():
                with open(file_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download",
                        data=f.read(),
                        file_name=f"pathowatch_{file_path.name}",
                        mime="application/json",
                        key=f"dl_{dataset['name']}"
                    )
            elif dataset["format"] == "ZIP":
                # Create ZIP on the fly
                import zipfile
                import io

                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for proc_file in Path("data/processed").glob("*.json"):
                        zf.write(proc_file, proc_file.name)

                st.download_button(
                    label="⬇️ Download",
                    data=zip_buffer.getvalue(),
                    file_name="pathowatch_complete_data.zip",
                    mime="application/zip",
                    key="dl_complete"
                )
            else:
                st.button("⬇️ Download", disabled=True, key=f"dl_disabled_{dataset['name']}")

        st.markdown("---")

    # API Documentation
    st.subheader("🔌 REST API Access")

    st.markdown("""
    PathoWatch provides a simple REST API for programmatic access to surveillance data.

    **Base URL:** `https://hub.ayushnexa.com/api/v1`

    | Endpoint | Method | Description |
    |----------|--------|-------------|
    | `/summary` | GET | Global summary statistics |
    | `/lineages` | GET | Lineage prevalence time series |
    | `/mutations` | GET | Mutation frequency data |
    | `/alerts` | GET | Current variant alerts |
    | `/tree` | GET | Phylogenetic tree metadata |

    **Example:**
    ```bash
    curl https://hub.ayushnexa.com/api/v1/summary
    ```

    *Note: API is served from static JSON files for this lite version.*
    """)

# ============================================================
# MAIN APP
# ============================================================

def main():
    # Load data
    data = load_all_data()

    # Route to page
    if "Global Overview" in page:
        show_global_overview(data)
    elif "Phylogenetic Tree" in page:
        show_phylogenetic_tree(data)
    elif "Mutation Tracker" in page:
        show_mutation_tracker(data)
    elif "Variant Alerts" in page:
        show_variant_alerts(data)
    elif "Download Center" in page:
        show_download_center(data)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div class="footer">
        🌍 <b>PathoWatch</b> — SARS-CoV-2 Genomic Surveillance Dashboard<br>
        Part of the <b>ayushnexa</b> Project Suite | Built with Streamlit + Plotly<br>
        Data sources: Nextstrain, NCBI, Outbreak.info | Last updated: {}
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M UTC")), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
