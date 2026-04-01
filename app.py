"""
VERA-SD - Verification Engine for Results & Accountability
Streamlit Web Application for South Dakota Education Data

South Dakota context: WIDA ACCESS for ELLs, School Performance Index (SPI),
Native American achievement gap, refugee ELL populations.
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import re
import os
from datetime import datetime

# =============================================================================
# Database Initialization (runs once at startup)
# =============================================================================

DB_PATH = Path(__file__).parent / "vera_demo.db"

def init_database():
    """Initialize database with SD districts and WIDA data if not exists."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Check if tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='districts'")
    if cursor.fetchone():
        conn.close()
        return  # Database already initialized

    # Create districts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS districts (
            district_id TEXT PRIMARY KEY,
            district_name TEXT NOT NULL,
            county TEXT NOT NULL,
            ell_count INTEGER,
            native_pct REAL,
            csi_tsi TEXT
        )
    """)

    # Create WIDA results table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wida_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            district_id TEXT NOT NULL,
            district_name TEXT NOT NULL,
            grade INTEGER NOT NULL,
            subgroup TEXT NOT NULL,
            speaking_score REAL,
            writing_score REAL,
            listening_score REAL,
            reading_score REAL,
            composite_score REAL,
            year INTEGER DEFAULT 2025,
            FOREIGN KEY (district_id) REFERENCES districts(district_id)
        )
    """)

    # 10 Demo Districts
    districts = [
        ("49-5", "Sioux Falls School District", "Minnehaha", 3800, 8.0, "TSI"),
        ("51-4", "Rapid City Area Schools", "Pennington", 900, 25.0, "CSI"),
        ("66-1", "Oglala Lakota County Schools", "Oglala Lakota", 10, 95.0, "CSI"),
        ("6-1", "Aberdeen School District", "Brown", 400, 5.0, "TSI"),
        ("14-4", "Watertown School District", "Codington", 300, 4.0, "CSI"),
        ("17-2", "Mitchell School District", "Davison", 200, 5.0, "CSI"),
        ("2-2", "Huron School District", "Beadle", 600, 4.0, "TSI"),
        ("63-3", "Yankton School District", "Yankton", 150, 6.0, "TSI"),
        ("59-2", "Winner School District", "Tripp", 50, 35.0, "TSI"),
        ("66-2", "Todd County School District", "Todd", 10, 95.0, "CSI"),
    ]
    cursor.executemany("INSERT OR REPLACE INTO districts VALUES (?, ?, ?, ?, ?, ?)", districts)

    # WIDA ACCESS data
    wida_data = [
        ("49-5", "Sioux Falls School District", 3, "Karen", 3.8, 2.9, 3.2, 2.7, 3.2),
        ("49-5", "Sioux Falls School District", 4, "Karen", 3.9, 3.0, 3.3, 2.8, 3.3),
        ("49-5", "Sioux Falls School District", 5, "Karen", 4.0, 3.1, 3.4, 2.9, 3.4),
        ("49-5", "Sioux Falls School District", 3, "Nepali", 3.6, 2.8, 3.1, 2.6, 3.0),
        ("49-5", "Sioux Falls School District", 4, "Nepali", 3.7, 2.9, 3.2, 2.7, 3.1),
        ("49-5", "Sioux Falls School District", 5, "Nepali", 3.8, 3.0, 3.3, 2.8, 3.2),
        ("49-5", "Sioux Falls School District", 3, "Spanish", 3.4, 3.0, 3.2, 2.9, 3.1),
        ("49-5", "Sioux Falls School District", 4, "Spanish", 3.5, 3.1, 3.3, 3.0, 3.2),
        ("49-5", "Sioux Falls School District", 5, "Spanish", 3.6, 3.2, 3.4, 3.1, 3.3),
        ("49-5", "Sioux Falls School District", 6, "All EL", 3.7, 3.1, 3.3, 2.9, 3.2),
        ("49-5", "Sioux Falls School District", 7, "All EL", 3.8, 3.2, 3.4, 3.0, 3.4),
        ("49-5", "Sioux Falls School District", 8, "All EL", 3.9, 3.3, 3.5, 3.1, 3.5),
        ("51-4", "Rapid City Area Schools", 3, "Lakota", 3.2, 2.6, 2.9, 2.4, 2.8),
        ("51-4", "Rapid City Area Schools", 4, "Lakota", 3.3, 2.7, 3.0, 2.5, 2.9),
        ("51-4", "Rapid City Area Schools", 5, "Lakota", 3.4, 2.8, 3.1, 2.6, 3.0),
        ("51-4", "Rapid City Area Schools", 6, "Lakota", 3.5, 2.9, 3.2, 2.7, 3.1),
        ("51-4", "Rapid City Area Schools", 7, "All EL", 3.6, 3.0, 3.2, 2.8, 3.2),
        ("51-4", "Rapid City Area Schools", 8, "All EL", 3.7, 3.1, 3.3, 2.9, 3.3),
        ("66-1", "Oglala Lakota County Schools", 3, "Lakota", 2.8, 2.2, 2.5, 2.0, 2.4),
        ("66-1", "Oglala Lakota County Schools", 4, "Lakota", 2.9, 2.3, 2.6, 2.1, 2.5),
        ("66-1", "Oglala Lakota County Schools", 5, "Lakota", 3.0, 2.4, 2.7, 2.2, 2.6),
        ("66-1", "Oglala Lakota County Schools", 6, "Lakota", 3.1, 2.5, 2.8, 2.3, 2.7),
        ("6-1", "Aberdeen School District", 3, "Karen", 3.5, 2.8, 3.1, 2.6, 3.0),
        ("6-1", "Aberdeen School District", 4, "Karen", 3.6, 2.9, 3.2, 2.7, 3.1),
        ("6-1", "Aberdeen School District", 5, "Nepali", 3.4, 2.7, 3.0, 2.5, 2.9),
        ("6-1", "Aberdeen School District", 6, "All EL", 3.5, 3.0, 3.2, 2.8, 3.1),
        ("14-4", "Watertown School District", 3, "Spanish", 3.3, 2.9, 3.1, 2.8, 3.0),
        ("14-4", "Watertown School District", 4, "Spanish", 3.4, 3.0, 3.2, 2.9, 3.1),
        ("14-4", "Watertown School District", 5, "Karen", 3.6, 2.9, 3.2, 2.7, 3.1),
        ("14-4", "Watertown School District", 6, "All EL", 3.5, 3.0, 3.2, 2.8, 3.1),
        ("17-2", "Mitchell School District", 3, "Spanish", 3.2, 2.8, 3.0, 2.7, 2.9),
        ("17-2", "Mitchell School District", 4, "Spanish", 3.3, 2.9, 3.1, 2.8, 3.0),
        ("17-2", "Mitchell School District", 5, "All EL", 3.4, 3.0, 3.2, 2.9, 3.1),
        ("17-2", "Mitchell School District", 6, "All EL", 3.5, 3.1, 3.3, 3.0, 3.2),
        ("2-2", "Huron School District", 3, "Spanish", 3.4, 2.9, 3.1, 2.7, 3.0),
        ("2-2", "Huron School District", 4, "Spanish", 3.5, 3.0, 3.2, 2.8, 3.1),
        ("2-2", "Huron School District", 5, "Karen", 3.7, 2.9, 3.2, 2.7, 3.1),
        ("2-2", "Huron School District", 6, "Karen", 3.8, 3.0, 3.3, 2.8, 3.2),
        ("2-2", "Huron School District", 7, "All EL", 3.6, 3.1, 3.3, 2.9, 3.2),
        ("63-3", "Yankton School District", 3, "Spanish", 3.3, 2.9, 3.1, 2.8, 3.0),
        ("63-3", "Yankton School District", 4, "Spanish", 3.4, 3.0, 3.2, 2.9, 3.1),
        ("63-3", "Yankton School District", 5, "All EL", 3.5, 3.1, 3.3, 3.0, 3.2),
        ("59-2", "Winner School District", 3, "Lakota", 3.0, 2.5, 2.8, 2.3, 2.6),
        ("59-2", "Winner School District", 4, "Lakota", 3.1, 2.6, 2.9, 2.4, 2.7),
        ("59-2", "Winner School District", 5, "Lakota", 3.2, 2.7, 3.0, 2.5, 2.8),
        ("66-2", "Todd County School District", 3, "Lakota", 2.9, 2.3, 2.6, 2.1, 2.5),
        ("66-2", "Todd County School District", 4, "Lakota", 3.0, 2.4, 2.7, 2.2, 2.6),
        ("66-2", "Todd County School District", 5, "Lakota", 3.1, 2.5, 2.8, 2.3, 2.7),
        ("66-2", "Todd County School District", 6, "Lakota", 3.2, 2.6, 2.9, 2.4, 2.8),
    ]
    cursor.executemany("""
        INSERT INTO wida_results (district_id, district_name, grade, subgroup, speaking_score, writing_score, listening_score, reading_score, composite_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, wida_data)

    conn.commit()
    conn.close()

# Initialize database at startup
init_database()

# =============================================================================
# Configuration
# =============================================================================

st.set_page_config(
    page_title="VERA-SD | South Dakota Education",
    page_icon="🦬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# South Dakota Colors - Prairie sky blue and wheat gold
BLUE = "#1B4F72"
GOLD = "#D4A017"
CREAM = "#FAF8F5"
RED = "#CC0000"
GREEN = "#1A5C38"

# Custom CSS for South Dakota branding
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:wght@400;600;700&family=Source+Sans+3:wght@400;600&display=swap');

    /* Main app background */
    .stApp {{
        background-color: {CREAM};
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: {BLUE};
    }}
    section[data-testid="stSidebar"] .stMarkdown {{
        color: white;
    }}
    section[data-testid="stSidebar"] label {{
        color: white !important;
    }}
    section[data-testid="stSidebar"] .stSelectbox label {{
        color: white !important;
    }}
    section[data-testid="stSidebar"] .stRadio > div {{
        display: flex;
        flex-direction: column;
        gap: 8px;
    }}
    section[data-testid="stSidebar"] .stRadio label,
    section[data-testid="stSidebar"] .stRadio label span,
    section[data-testid="stSidebar"] .stRadio label p,
    section[data-testid="stSidebar"] .stRadio label div,
    section[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"],
    section[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {{
        color: white !important;
        font-size: 1rem;
        position: relative;
        z-index: 1;
    }}
    section[data-testid="stSidebar"] .stRadio label {{
        padding: 8px 12px;
        border-radius: 6px;
        cursor: pointer;
        transition: background-color 0.2s;
    }}
    section[data-testid="stSidebar"] .stRadio label:hover {{
        background-color: rgba(255,255,255,0.1);
    }}
    section[data-testid="stSidebar"] .stRadio input[type="radio"]:checked + div,
    section[data-testid="stSidebar"] .stRadio input[type="radio"]:checked + div p,
    section[data-testid="stSidebar"] .stRadio input[type="radio"]:checked ~ div,
    section[data-testid="stSidebar"] .stRadio input[type="radio"]:checked ~ div p {{
        color: {GOLD} !important;
        font-weight: 600;
    }}

    /* Headers */
    h1, h2, h3 {{
        font-family: 'Lora', serif;
        color: {BLUE};
    }}
    h1 {{
        border-bottom: 3px solid {GOLD};
        padding-bottom: 10px;
    }}

    /* Body text */
    p, li, span {{
        font-family: 'Source Sans 3', sans-serif;
    }}

    /* Stat cards */
    .stat-card {{
        background: white;
        border-left: 4px solid {GOLD};
        padding: 20px;
        border-radius: 4px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 16px;
    }}
    .stat-card .number {{
        font-size: 2.5rem;
        font-weight: 700;
        color: {GOLD};
        font-family: 'Lora', serif;
    }}
    .stat-card .label {{
        font-size: 0.9rem;
        color: #666;
        margin-top: 4px;
    }}

    /* Type 4 flag highlight */
    .type4-flag {{
        background-color: {RED};
        color: white;
        padding: 4px 12px;
        border-radius: 4px;
        font-weight: 600;
    }}

    /* Section headers */
    .section-header {{
        background: {BLUE};
        color: white;
        padding: 12px 20px;
        margin: 24px 0 16px 0;
        font-family: 'Lora', serif;
        font-size: 1.1rem;
    }}

    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# Database Connection
# =============================================================================

@st.cache_resource
def get_connection():
    return sqlite3.connect(str(DB_PATH), check_same_thread=False)

def run_query(query, params=None):
    conn = get_connection()
    if params:
        return pd.read_sql_query(query, conn, params=params)
    return pd.read_sql_query(query, conn)

# =============================================================================
# Data Functions
# =============================================================================

@st.cache_data
def get_districts():
    query = """
        SELECT DISTINCT district_name, district_id, county
        FROM districts
        ORDER BY district_name
    """
    return run_query(query)

@st.cache_data
def get_wida_data(district_name, grade=None, subgroup=None):
    query = "SELECT * FROM wida_results WHERE district_name = ?"
    params = [district_name]

    if grade:
        query += " AND grade = ?"
        params.append(grade)
    if subgroup:
        query += " AND subgroup = ?"
        params.append(subgroup)

    query += " ORDER BY grade, subgroup"
    return run_query(query, params)

@st.cache_data
def compute_owd(district_name, subgroup=None):
    """Compute Oral-Written Delta using WIDA ACCESS Speaking vs Writing scores.
    WIDA scale: 1.0 to 6.0. Type 4 threshold: delta >= 0.5"""
    query = """
        SELECT district_name, district_id, grade, subgroup,
               speaking_score, writing_score,
               (speaking_score - writing_score) as delta
        FROM wida_results
        WHERE district_name = ?
    """
    params = [district_name]

    if subgroup:
        query += " AND subgroup = ?"
        params.append(subgroup)

    query += " ORDER BY grade"
    return run_query(query, params)

@st.cache_data
def get_all_type4_flags(threshold=0.5):
    """Flag Type 4 candidates where Speaking exceeds Writing by threshold.
    WIDA scale uses 0.5 as equivalent to CA's 8-point threshold."""
    query = """
        SELECT w.district_name, w.district_id, d.county, w.grade, w.subgroup,
               w.speaking_score, w.writing_score,
               (w.speaking_score - w.writing_score) as delta
        FROM wida_results w
        JOIN districts d ON w.district_id = d.district_id
        WHERE (w.speaking_score - w.writing_score) >= ?
        ORDER BY delta DESC
    """
    return run_query(query, [threshold])

# =============================================================================
# Sidebar
# =============================================================================

with st.sidebar:
    # Back arrow to h-edu.solutions
    st.markdown("""
        <a href="https://h-edu.solutions" target="_self" style="
            display: flex;
            align-items: center;
            color: white;
            text-decoration: none;
            font-size: 0.9rem;
            padding: 8px 0;
            margin-bottom: 10px;
            opacity: 0.9;
        ">
            <span style="font-size: 1.2rem; margin-right: 8px;">←</span>
            Back to H-EDU
        </a>
    """, unsafe_allow_html=True)

    # South Dakota display
    st.markdown(f"""
        <div style="text-align: center; padding: 10px 0 20px 0;">
            <h2 style="color: white; margin: 10px 0;">🦬 VERA-SD</h2>
            <p style="color: {GOLD}; font-size: 0.9rem;">Verification Engine for Results & Accountability</p>
            <p style="color: rgba(255,255,255,0.6); font-size: 0.8rem;">South Dakota • WIDA ACCESS</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Navigation
    st.markdown("""
        <p style="color: rgba(255,255,255,0.7); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">
            Navigate
        </p>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigate",
        ["📊 District Dashboard", "🔍 Cross-District Scan", "📋 SPI Report", "ℹ️ About VERA"],
        label_visibility="collapsed",
        format_func=lambda x: x
    )

    st.markdown("---")

    # District selector (for relevant pages)
    if page in ["📊 District Dashboard", "📋 SPI Report"]:
        districts = get_districts()
        selected_district = st.selectbox(
            "Select District",
            districts['district_name'].tolist()
        )

        district_data = get_wida_data(selected_district)

        grades = ["All"] + sorted(district_data['grade'].unique().tolist())
        selected_grade = st.selectbox("Grade", grades)

        subgroups = ["All"] + sorted(district_data['subgroup'].unique().tolist())
        selected_subgroup = st.selectbox("Subgroup", subgroups)

    st.markdown("---")
    st.markdown(f"""
        <p style="color: rgba(255,255,255,0.5); font-size: 0.8rem; text-align: center;">
            VERA-SD v1.0<br>
            <a href="https://h-edu.solutions" style="color: {GOLD};">h-edu.solutions</a>
        </p>
    """, unsafe_allow_html=True)

# =============================================================================
# Page: District Dashboard
# =============================================================================

if page == "📊 District Dashboard":
    st.title(f"District Dashboard: {selected_district}")

    st.markdown(f"""
    The **Type 4 student** speaks well but writes poorly — the "oral-written delta." VERA computes
    this using WIDA ACCESS **Speaking** scores against **Writing** scores. When speaking
    exceeds writing by **0.5+ points** on the WIDA scale (1.0-6.0), these students may be receiving
    inappropriate oral language interventions when they need writing support.
    """)

    st.markdown("---")

    district_info = districts[districts['district_name'] == selected_district].iloc[0]
    st.markdown(f"**{district_info['county']} County** | District ID: `{district_info['district_id']}`")

    subgroup_filter = None if selected_subgroup == "All" else selected_subgroup
    owd_data = compute_owd(selected_district, subgroup_filter)

    if selected_grade != "All":
        owd_data = owd_data[owd_data['grade'] == int(selected_grade)]

    col1, col2, col3, col4 = st.columns(4)

    type4_count = len(owd_data[owd_data['delta'] >= 0.5])
    max_delta = owd_data['delta'].max() if len(owd_data) > 0 else 0
    avg_delta = owd_data['delta'].mean() if len(owd_data) > 0 else 0

    with col1:
        st.markdown(f"""
            <div class="stat-card">
                <div class="number">{len(owd_data)}</div>
                <div class="label">Populations Analyzed</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="stat-card">
                <div class="number" style="color: {RED if type4_count > 0 else GOLD};">{type4_count}</div>
                <div class="label">Type 4 Flags (Δ ≥ 0.5)</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="stat-card">
                <div class="number">{max_delta:+.2f}</div>
                <div class="label">Max Delta</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div class="stat-card">
                <div class="number">{avg_delta:+.2f}</div>
                <div class="label">Avg Delta</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">WIDA ACCESS Oral-Written Delta Analysis</div>', unsafe_allow_html=True)

    if len(owd_data) > 0:
        display_df = owd_data[['grade', 'subgroup', 'writing_score', 'speaking_score', 'delta']].copy()
        display_df.columns = ['Grade', 'Subgroup', 'Writing (WIDA)', 'Speaking (WIDA)', 'Delta']
        display_df['Delta'] = display_df['Delta'].apply(lambda x: f"{x:+.2f}" if pd.notna(x) else "N/A")

        def highlight_type4(row):
            delta_val = float(row['Delta'].replace('+', '')) if row['Delta'] != 'N/A' else 0
            if delta_val >= 0.5:
                return ['background-color: #FADBD8'] * len(row)
            return [''] * len(row)

        st.dataframe(
            display_df.style.apply(highlight_type4, axis=1),
            use_container_width=True,
            hide_index=True
        )

        st.markdown('<div class="section-header">Speaking vs. Writing Scores by Grade</div>', unsafe_allow_html=True)

        chart_data = owd_data[owd_data['speaking_score'].notna()].copy()
        if len(chart_data) > 0:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='Writing (WIDA)',
                x=chart_data['grade'].astype(str) + ' - ' + chart_data['subgroup'],
                y=chart_data['writing_score'],
                marker_color=BLUE
            ))
            fig.add_trace(go.Bar(
                name='Speaking (WIDA)',
                x=chart_data['grade'].astype(str) + ' - ' + chart_data['subgroup'],
                y=chart_data['speaking_score'],
                marker_color=GOLD
            ))
            fig.update_layout(
                barmode='group',
                xaxis_title='Grade - Subgroup',
                yaxis_title='WIDA Score (1.0-6.0)',
                plot_bgcolor='white',
                height=400,
                yaxis=dict(range=[0, 6.5])
            )
            st.plotly_chart(fig, use_container_width=True)

        csv = owd_data.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"vera_sd_owd_{selected_district.replace(' ', '_')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No data available for the selected filters.")

# =============================================================================
# Page: Cross-District Scan
# =============================================================================

elif page == "🔍 Cross-District Scan":
    st.title("Cross-District Type 4 Scan")

    st.markdown("""
    South Dakota's **School Performance Index (SPI)** tracks accountability metrics, but Type 4 students
    — those who speak well but write poorly — remain invisible in aggregate reporting. This scan
    identifies Type 4 concentrations across all South Dakota districts using WIDA ACCESS domain scores.
    """)

    threshold = st.slider("Delta Threshold (WIDA scale)", min_value=0.3, max_value=1.5, value=0.5, step=0.1)

    flags_df = get_all_type4_flags(threshold)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
            <div class="stat-card">
                <div class="number" style="color: {RED};">{len(flags_df)}</div>
                <div class="label">Total Flags</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        districts_flagged = flags_df['district_name'].nunique() if len(flags_df) > 0 else 0
        st.markdown(f"""
            <div class="stat-card">
                <div class="number">{districts_flagged}</div>
                <div class="label">Districts Flagged</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        max_delta = flags_df['delta'].max() if len(flags_df) > 0 else 0
        st.markdown(f"""
            <div class="stat-card">
                <div class="number">{max_delta:+.2f}</div>
                <div class="label">Max Delta</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">Flagged Populations</div>', unsafe_allow_html=True)

    if len(flags_df) > 0:
        display_df = flags_df[['district_name', 'county', 'grade', 'subgroup', 'writing_score', 'speaking_score', 'delta']].copy()
        display_df.columns = ['District', 'County', 'Grade', 'Subgroup', 'Writing', 'Speaking', 'Delta']
        display_df['Delta'] = display_df['Delta'].apply(lambda x: f"{x:+.2f}")

        st.dataframe(display_df, use_container_width=True, hide_index=True)

        st.markdown('<div class="section-header">Type 4 Flags by District</div>', unsafe_allow_html=True)

        flag_counts = flags_df.groupby('district_name').size().reset_index(name='flags')
        flag_counts = flag_counts.sort_values('flags', ascending=True)

        fig = px.bar(
            flag_counts,
            x='flags',
            y='district_name',
            orientation='h',
            color_discrete_sequence=[RED]
        )
        fig.update_layout(
            xaxis_title='Number of Flags',
            yaxis_title='',
            plot_bgcolor='white',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        csv = flags_df.to_csv(index=False)
        st.download_button(
            label="Download All Flags CSV",
            data=csv,
            file_name="vera_sd_type4_flags_all_districts.csv",
            mime="text/csv"
        )
    else:
        st.success(f"No Type 4 flags found at threshold {threshold}")

# =============================================================================
# Page: SPI Report
# =============================================================================

elif page == "📋 SPI Report":
    st.title(f"SPI Match-Rate Report")

    st.markdown("""
    South Dakota uses the **School Performance Index (SPI)** for accountability. Districts with
    Comprehensive Support and Improvement (CSI) or Targeted Support and Improvement (TSI)
    designations receive additional scrutiny. VERA's match-rate analysis verifies alignment
    between intervention spending and student need — particularly for the invisible Type 4 gap.
    """)

    st.markdown("---")
    st.markdown(f"**District:** {selected_district}")

    district_info = districts[districts['district_name'] == selected_district].iloc[0]
    district_id = district_info['district_id']

    owd_data = compute_owd(selected_district)
    type4_count = len(owd_data[owd_data['delta'] >= 0.5])
    total_populations = len(owd_data)

    match_rate = max(0, 100 - (type4_count * 15))

    col1, col2 = st.columns([1, 1])

    with col1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=match_rate,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "SPI Match Rate", 'font': {'size': 20}},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': GOLD},
                'steps': [
                    {'range': [0, 50], 'color': '#FADBD8'},
                    {'range': [50, 75], 'color': '#FCF3CF'},
                    {'range': [75, 100], 'color': '#D5F5E3'}
                ],
                'threshold': {
                    'line': {'color': RED, 'width': 4},
                    'thickness': 0.75,
                    'value': 70
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(f"""
            <div class="stat-card">
                <div class="number">{total_populations}</div>
                <div class="label">Grade-Subgroup Combinations Analyzed</div>
            </div>
        """, unsafe_allow_html=True)

        color = RED if type4_count > 2 else (GOLD if type4_count > 0 else GREEN)
        st.markdown(f"""
            <div class="stat-card">
                <div class="number" style="color: {color};">{type4_count}</div>
                <div class="label">Type 4 Gaps (Speaking > Writing by 0.5+ WIDA pts)</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">Finding</div>', unsafe_allow_html=True)

    if match_rate >= 75:
        st.success(f"**MATCH RATE: {match_rate}%** — ELD interventions appear well-aligned with student needs.")
    elif match_rate >= 50:
        st.warning(f"**MATCH RATE: {match_rate}%** — Some misalignment detected. Review ELD intervention targeting.")
    else:
        st.error(f"**MATCH RATE: {match_rate}%** — Significant misalignment. Immediate review recommended.")

    st.markdown("---")
    st.markdown(f"""
        <div style="background: {GREEN}; color: white; padding: 16px; border-radius: 4px; text-align: center; margin-top: 30px;">
            <strong>NON-EVALUATION GUARANTEE</strong><br>
            No teacher identity is attached to any result in this dashboard.<br>
            VERA measures whether <em>policy</em> works, not whether <em>teachers</em> work.
        </div>
    """, unsafe_allow_html=True)

# =============================================================================
# Page: About VERA
# =============================================================================

elif page == "ℹ️ About VERA":
    st.title("About VERA-SD")

    st.markdown(f"""
    <div style="background: {BLUE}; color: white; padding: 24px; border-radius: 8px; margin-bottom: 24px;">
        <p style="font-size: 1.2rem; margin: 0 0 12px 0; font-weight: 600; color: {GOLD};">
            The 5th most literate state in America.
        </p>
        <p style="font-size: 1.1rem; margin: 0; line-height: 1.7;">
            A <strong>36-point reading gap</strong> between Native and white students.
            The <strong>lowest ELL progress baseline</strong> in the country (1.9%).
            The state that looks fine — until you look at who's inside it.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    ## Verification Engine for Results & Accountability
    ### South Dakota Edition

    VERA-SD is South Dakota's instance of the Verification Engine, providing data infrastructure
    for identifying the **oral-written gap** in English Learner populations.

    ### The South Dakota Context

    - **Adult literacy rate:** 93.0% — 5th highest in the US
    - **Native American ELA proficiency:** 23% (vs. 59% White — a 36-point gap)
    - **Native American graduation rate:** 46%
    - **ELL progress baseline (2017):** 1.9% — the lowest in the nation
    - **ELL growth goal:** 100% — a 98-point gap to close

    ### The Three Gaps

    **Gap 1: Native American Achievement**
    Nine tribal nations. Three school systems. High student mobility.
    Lakota is an oral language — students may have strong spoken Lakota and weak written English.

    **Gap 2: Refugee ELL Profile**
    Karen and Nepali students arrive with strong oral community language
    but limited academic literacy. Classic Type 4 profiles.

    **Gap 3: ELP Progress Collapse**
    1.9% baseline. 100% goal. The intervention system exists. The verification layer does not.

    ### Data Sources

    - **WIDA ACCESS for ELLs 2.0** — Speaking and Writing domain scores
    - **School Performance Index (SPI)** — South Dakota's accountability framework
    - **CSI/TSI Classifications** — Federal accountability designations

    ### The Type 4 Gap

    H-EDU's differentiator is identifying students who **speak well but write poorly**.

    - **WIDA Speaking score** (oral proxy)
    - **WIDA Writing score** (written proxy)
    - **Delta ≥ 0.5** on the 1.0-6.0 WIDA scale = Type 4 flag

    ---

    **Contact:** [brian@h-edu.solutions](mailto:brian@h-edu.solutions)

    **Website:** [h-edu.solutions](https://h-edu.solutions)
    """)

    st.markdown(f"""
        <div style="background: {BLUE}; color: white; padding: 24px; text-align: center; margin-top: 40px; border-radius: 4px;">
            <p style="color: {GOLD}; font-size: 1.2rem; font-weight: 600; margin: 0;">
                VERA: The verification layer South Dakota education accountability has been missing.
            </p>
        </div>
    """, unsafe_allow_html=True)
