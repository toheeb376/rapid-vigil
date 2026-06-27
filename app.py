# =============================================================================
# RAPID VIGIL SECURITY — CLIENT INTELLIGENCE DASHBOARD  (DARK THEME)
# Built by ToheebBI Consulting
# =============================================================================
#
# SETUP INSTRUCTIONS (For Beginners):
# ─────────────────────────────────────────────────────────────────────────────
# 1. Install required libraries:
#       pip install streamlit pandas plotly openpyxl numpy pillow
#
# 2. Place ALL THREE files in the same folder:
#       - rapid_vigil_security_500_Row_Dataset.xlsx
#       - rapid_vigil.jpg            ← official logo file
#       - app.py
#
# 3. In your terminal, navigate to that folder and run:
#       streamlit run app.py
#
# 4. Dashboard opens at: http://localhost:8501
#
# 5. To change colors: edit the rv_colors dictionary below
# 6. To add a KPI: duplicate any st.metric() block
# 7. To add a chart: define a Plotly figure, call st.plotly_chart(fig, use_container_width=True)
# 8. To add a filter: use st.sidebar.multiselect() wired to df.isin()
# =============================================================================

import os
import warnings
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG — must be the FIRST Streamlit call
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Rapid Vigil | Client Intelligence",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# DARK THEME BRAND PALETTE — Rapid Vigil Professional Dark
# ─────────────────────────────────────────────────────────────────────────────
rv = {
    # ── Backgrounds ──
    "bg_app":       "#0D0F1C",   # Main page background — deep dark navy
    "bg_surface":   "#131628",   # Cards, chart backgrounds — slightly lighter
    "bg_sidebar":   "#0A0C18",   # Sidebar — deepest dark
    "bg_elevated":  "#1A1D35",   # Elevated panels, expanders
    "bg_hover":     "#1F2340",   # Hover / active states

    # ── Rapid Vigil Brand Blues ──
    "brand_dark":   "#12166E",   # Deep navy brand
    "brand_core":   "#0804B0",   # Core brand blue
    "brand_mid":    "#3B41A1",   # Mid blue for secondary elements
    "brand_glow":   "#4B52D4",   # Lighter blue for glows / chart lines

    # ── Gold Accents ──
    "gold":         "#D6CA50",   # Primary gold accent
    "gold_light":   "#E8DD79",   # Light gold — hover states

    # ── Text ──
    "text_primary": "#E8EAFF",   # Primary text — near white with blue tint
    "text_secondary":"#8B93C4",  # Secondary text — muted blue-grey
    "text_muted":   "#555C8A",   # Muted — axis ticks, fine print
    "text_heading": "#FFFFFF",   # Headings — pure white

    # ── Semantic Status Colors ──
    "success":      "#1DB954",   # Active, paid — vivid green
    "success_dim":  "#0D5C29",   # Success background fill
    "warning":      "#F5A623",   # Expiring, pending — amber
    "warning_dim":  "#5C3A08",   # Warning background fill
    "danger":       "#E53E3E",   # High risk, overdue — red
    "danger_dim":   "#5C0F0F",   # Danger background fill
    "info":         "#17A2B8",   # Info — teal

    # ── Chart Palette ──
    "chart_seq": [
        "#4B52D4", "#3B41A1", "#0804B0", "#12166E",
        "#D6CA50", "#F5A623", "#1DB954", "#17A2B8",
        "#E53E3E", "#8B93C4",
    ],

    # ── Borders ──
    "border":       "rgba(75, 82, 212, 0.25)",   # Subtle blue border
    "border_card":  "rgba(75, 82, 212, 0.40)",   # Card border
}

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL DARK CSS INJECTION
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
    /* ══ App background ══ */
    .stApp, .stApp > div {{
        background-color: {rv['bg_app']} !important;
        color: {rv['text_primary']} !important;
    }}

    /* ══ Main content block ══ */
    .main .block-container {{
        background-color: {rv['bg_app']} !important;
        padding-top: 1.2rem;
    }}

    /* ══ Sidebar — deep dark ══ */
    section[data-testid="stSidebar"] {{
        background-color: {rv['bg_sidebar']} !important;
        border-right: 1px solid {rv['border']} !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: {rv['text_primary']} !important;
    }}
    section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {{
        background-color: {rv['brand_mid']} !important;
        color: #ffffff !important;
        border: none !important;
    }}
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] .stDateInput input {{
        background-color: {rv['bg_elevated']} !important;
        color: {rv['text_primary']} !important;
        border: 1px solid {rv['border']} !important;
        border-radius: 6px !important;
    }}
    /* Multiselect dropdown backdrop */
    section[data-testid="stSidebar"] [data-baseweb="select"] > div {{
        background-color: {rv['bg_elevated']} !important;
        border: 1px solid {rv['border']} !important;
        color: {rv['text_primary']} !important;
    }}

    /* ══ KPI Metric Cards ══ */
    div[data-testid="metric-container"] {{
        background-color: {rv['bg_surface']} !important;
        border: 1px solid {rv['border_card']} !important;
        border-radius: 10px !important;
        padding: 16px 18px !important;
        box-shadow: 0 0 18px rgba(75, 82, 212, 0.12) !important;
    }}
    div[data-testid="metric-container"] label {{
        color: {rv['text_secondary']} !important;
        font-weight: 700 !important;
        font-size: 0.78rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
    }}
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {{
        color: {rv['text_heading']} !important;
        font-size: 1.5rem !important;
        font-weight: 800 !important;
    }}
    div[data-testid="metric-container"] [data-testid="stMetricDelta"] {{
        font-size: 0.78rem !important;
    }}

    /* ══ All headings ══ */
    h1, h2, h3, h4, h5 {{
        color: {rv['text_heading']} !important;
        font-weight: 800 !important;
    }}

    /* ══ Paragraph / normal text ══ */
    p, span, div, label {{
        color: {rv['text_primary']};
    }}

    /* ══ Sidebar filter labels ══ */
    .stSelectbox label, .stMultiSelect label, .stDateInput label {{
        color: {rv['text_secondary']} !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }}

    /* ══ Horizontal rules ══ */
    hr {{ border-color: {rv['border']} !important; margin: 1.2rem 0; }}

    /* ══ DataFrames ══ */
    .stDataFrame, [data-testid="stDataFrame"] {{
        background-color: {rv['bg_surface']} !important;
    }}
    .stDataFrame tbody tr:nth-child(even) {{
        background-color: {rv['bg_elevated']} !important;
    }}
    .stDataFrame thead tr {{
        background-color: {rv['brand_dark']} !important;
        color: white !important;
    }}

    /* ══ Expander ══ */
    details {{
        background-color: {rv['bg_elevated']} !important;
        border: 1px solid {rv['border_card']} !important;
        border-radius: 10px !important;
    }}
    summary {{
        color: {rv['text_heading']} !important;
        font-weight: 700 !important;
        padding: 12px 16px !important;
        background-color: {rv['bg_elevated']} !important;
        border-radius: 10px !important;
    }}

    /* ══ Plotly chart containers ══ */
    .js-plotly-plot, .plotly, .plot-container {{
        background-color: {rv['bg_surface']} !important;
        border-radius: 10px !important;
    }}

    /* ══ Streamlit tabs ══ */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: {rv['bg_elevated']} !important;
        border-radius: 8px;
    }}
    .stTabs [data-baseweb="tab"] {{
        color: {rv['text_secondary']} !important;
    }}
    .stTabs [aria-selected="true"] {{
        color: {rv['gold']} !important;
        border-bottom-color: {rv['gold']} !important;
    }}

    /* ══ Hide Streamlit branding ══ */
    #MainMenu, footer {{ visibility: hidden; }}
    header[data-testid="stHeader"] {{ background-color: {rv['bg_app']} !important; }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# FILE PATHS
# ─────────────────────────────────────────────────────────────────────────────
DATA_FILE  = "rapid_vigil_security_500_Row_Dataset.xlsx"
LOGO_FILE  = "rapid_vigil.jpg"
SHEET_NAME = "RapidVigilClients"


# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING & PREPROCESSING
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    if not os.path.exists(DATA_FILE):
        return None
    df = pd.read_excel(DATA_FILE, sheet_name=SHEET_NAME)

    # Strip whitespace from all string columns
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip().replace("nan", np.nan)

    # Parse dates safely
    df["Start Date"] = pd.to_datetime(df["Start Date"], errors="coerce")
    df["End Date"]   = pd.to_datetime(df["End Date"],   errors="coerce")
    df["Inspection"] = pd.to_datetime(df["Inspection"], errors="coerce")

    # Derived fields
    df["Contract_Duration_Days"] = (df["End Date"] - df["Start Date"]).dt.days.clip(lower=0)
    df["Days_To_Expiry"]         = (df["End Date"] - pd.Timestamp.today()).dt.days
    df["Start_Month"]            = df["Start Date"].dt.to_period("M").astype(str)

    # SLA numeric
    df["SLA_Numeric"] = pd.to_numeric(
        df["SLA"].str.replace("%", "", regex=False).str.strip(), errors="coerce"
    )

    # Fill numeric nulls
    for col in ["Guards","Monthly Value (NGN)","Annual Revenue (NGN)",
                "Satisfaction","Incidents","Response Min","Renewal %",
                "Contract_Duration_Days","Days_To_Expiry","SLA_Numeric"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


# ─────────────────────────────────────────────────────────────────────────────
# PLOTLY DARK CHART HELPER
# ─────────────────────────────────────────────────────────────────────────────
def dark_layout(fig, title="", height=380):
    """Apply consistent dark-theme Plotly layout."""
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(color=rv["text_heading"], size=13, family="Arial"),
            x=0, xanchor="left",
        ),
        paper_bgcolor=rv["bg_surface"],
        plot_bgcolor=rv["bg_surface"],
        font=dict(color=rv["text_secondary"], family="Arial", size=11),
        height=height,
        margin=dict(l=40, r=20, t=48, b=40),
        legend=dict(
            bgcolor=rv["bg_elevated"],
            bordercolor=rv["border"],
            borderwidth=1,
            font=dict(color=rv["text_secondary"], size=10),
        ),
        hoverlabel=dict(
            bgcolor=rv["bg_elevated"],
            font_color=rv["text_heading"],
            bordercolor=rv["border_card"],
        ),
    )
    fig.update_xaxes(
        gridcolor="rgba(75,82,212,0.12)",
        zerolinecolor="rgba(75,82,212,0.2)",
        tickfont=dict(color=rv["text_muted"], size=10),
        title_font=dict(color=rv["text_secondary"], size=11),
        linecolor=rv["border"],
    )
    fig.update_yaxes(
        gridcolor="rgba(75,82,212,0.12)",
        zerolinecolor="rgba(75,82,212,0.2)",
        tickfont=dict(color=rv["text_muted"], size=10),
        title_font=dict(color=rv["text_secondary"], size=11),
        linecolor=rv["border"],
    )
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────────────────────
df_raw = load_data()

if df_raw is None:
    st.error(
        f"⚠️ Data file not found: **{DATA_FILE}**\n\n"
        "Ensure the .xlsx file is in the same folder as app.py and re-run."
    )
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR — Logo + Filters
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:

    # ── Logo ──
    if os.path.exists(LOGO_FILE):
        try:
            from PIL import Image
            img = Image.open(LOGO_FILE)
            buf = BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            st.image(buf, use_container_width=True)
        except Exception:
            st.markdown(
                f"<h2 style='color:{rv['gold']};text-align:center;'>"
                " RAPID VIGIL</h2>", unsafe_allow_html=True
            )
    else:
        st.markdown(
            f"<h2 style='color:{rv['gold']};text-align:center;'>"
            " RAPID VIGIL</h2>", unsafe_allow_html=True
        )

    st.markdown(
        f"<p style='color:{rv['text_muted']};font-size:0.72rem;"
        "text-align:center;margin-top:-6px;letter-spacing:0.08em;'>"
        "SECURITY INTELLIGENCE PORTAL</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<hr style='border-color:{rv['border']};margin:10px 0;'>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='color:{rv['text_muted']};font-size:0.7rem;"
        "font-weight:700;text-transform:uppercase;letter-spacing:0.1em;"
        "margin-bottom:8px;'> Filter Controls</p>",
        unsafe_allow_html=True,
    )

    def opts(col):
        return sorted(df_raw[col].dropna().unique().tolist())

    sel_service  = st.multiselect("Service Type",      opts("Service"),       default=opts("Service"))
    sel_contract = st.multiselect("Contract Status",   opts("Contract"),      default=opts("Contract"))
    sel_risk     = st.multiselect("Risk Level",        opts("Risk"),          default=opts("Risk"))
    sel_industry = st.multiselect("Industry",          opts("Industry"),      default=opts("Industry"))
    sel_state    = st.multiselect("State",             opts("State"),         default=opts("State"))
    sel_invoice  = st.multiselect("Invoice Status",    opts("Invoice"),       default=opts("Invoice"))

    min_date = df_raw["Start Date"].min().date()
    max_date = df_raw["Start Date"].max().date()
    date_range = st.date_input(
        "Contract Start Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    st.markdown(
        f"<hr style='border-color:{rv['border']};margin:16px 0 10px;'>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='color:{rv['text_muted']};font-size:0.65rem;"
        "text-align:center;'>© 2025 Rapid Vigil Security<br>"
        "Built by <strong style='color:{rv[\"gold\"]}'>ToheebBI Consulting</strong></p>",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────────────────────────────────────────
df = df_raw.copy()
if sel_service:  df = df[df["Service"].isin(sel_service)]
if sel_contract: df = df[df["Contract"].isin(sel_contract)]
if sel_risk:     df = df[df["Risk"].isin(sel_risk)]
if sel_industry: df = df[df["Industry"].isin(sel_industry)]
if sel_state:    df = df[df["State"].isin(sel_state)]
if sel_invoice:  df = df[df["Invoice"].isin(sel_invoice)]

if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    d0, d1 = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    df = df[(df["Start Date"] >= d0) & (df["Start Date"] <= d1)]

if df.empty:
    st.warning("⚠️ No data matches the current filter selection. Adjust the sidebar filters.")
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# COMPUTE KPIs
# ─────────────────────────────────────────────────────────────────────────────
total_clients      = len(df)
active_contracts   = int((df["Contract"] == "Active").sum())
expiring_contracts = int((df["Contract"] == "Expiring").sum())
total_annual_rev   = df["Annual Revenue (NGN)"].sum()
total_monthly_rev  = df["Monthly Value (NGN)"].sum()
high_risk_clients  = int((df["Risk"] == "High").sum())
overdue_invoices   = int((df["Invoice"] == "Overdue").sum())
total_guards       = int(df["Guards"].sum())
avg_satisfaction   = df["Satisfaction"].mean() if total_clients > 0 else 0
avg_response       = df["Response Min"].mean()  if total_clients > 0 else 0
avg_sla            = df["SLA_Numeric"].mean()   if total_clients > 0 else 0

def fmt_rev(v):
    if v >= 1_000_000_000:
        return f"₦{v/1_000_000_000:.2f}B"
    return f"₦{v/1_000_000:.1f}M"


# ─────────────────────────────────────────────────────────────────────────────
# HEADER BANNER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="
    background: linear-gradient(135deg, {rv['brand_dark']} 0%, {rv['bg_elevated']} 60%, {rv['bg_app']} 100%);
    border: 1px solid {rv['border_card']};
    border-radius: 14px;
    padding: 22px 28px 18px;
    margin-bottom: 22px;
    box-shadow: 0 4px 32px rgba(8, 4, 141, 0.35);
">
    <div style="display:flex; align-items:center; gap:12px;">
        <span style="font-size:2rem;">️</span>
        <div>
            <h1 style="color:{rv['text_heading']} !important; margin:0; font-size:1.75rem;
                font-weight:900; letter-spacing:-0.01em;">
                Rapid Vigil Security
            </h1>
            <p style="color:{rv['gold']}; margin:2px 0 0; font-size:0.92rem; font-weight:600;">
                Client Intelligence Dashboard &nbsp;|&nbsp; Powered by ToheebBI Consulting
            </p>
        </div>
    </div>
    <p style="color:{rv['text_muted']}; margin:10px 0 0; font-size:0.78rem;">
        Showing&nbsp;<strong style="color:{rv['text_primary']}">{total_clients:,}</strong>&nbsp;clients
        &nbsp;·&nbsp; {len(sel_service)} service type(s)
        &nbsp;·&nbsp; {len(sel_state)} state(s)
        &nbsp;·&nbsp; Avg SLA <strong style="color:{rv['success']}">{avg_sla:.1f}%</strong>
    </p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# KPI CARDS — Row 1
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    f"<p style='color:{rv['text_secondary']};font-size:0.78rem;font-weight:700;"
    "text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;'>"
    " Key Performance Indicators</p>",
    unsafe_allow_html=True,
)

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric(" Total Clients",         f"{total_clients:,}")
k2.metric(" Active Contracts",       f"{active_contracts:,}")
k3.metric(" Expiring Contracts",    f"{expiring_contracts:,}")
k4.metric(" Annual Revenue",         fmt_rev(total_annual_rev))
k5.metric(" Monthly Revenue",        fmt_rev(total_monthly_rev))

k6, k7, k8, k9, k10 = st.columns(5)
k6.metric(" High-Risk Clients",      f"{high_risk_clients:,}")
k7.metric(" Overdue Invoices",       f"{overdue_invoices:,}")
k8.metric(" Guards Deployed",        f"{total_guards:,}")
k9.metric(" Avg Satisfaction",       f"{avg_satisfaction:.2f} / 5.0")
k10.metric("️ Avg Response Time",     f"{avg_response:.1f} min")

st.markdown(f"<hr style='border-color:{rv['border']};margin:20px 0;'>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# CHARTS — ROW A: Contract Status | Revenue by Industry | Monthly Trend
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    f"<p style='color:{rv['gold']};font-size:0.78rem;font-weight:700;"
    "text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px;'>"
    " Contract & Revenue Analytics</p>",
    unsafe_allow_html=True,
)
ca1, ca2, ca3 = st.columns(3)

# Chart 1 — Contract Status Distribution
with ca1:
    cc = df["Contract"].value_counts().reset_index()
    cmap = {"Active": rv["success"], "Expiring": rv["warning"], "Renewed": rv["brand_glow"]}
    fig1 = px.bar(
        cc, x="Contract", y="count",
        color="Contract", color_discrete_map=cmap,
        title="Contract Status Distribution",
        text="count",
    )
    fig1.update_traces(
        textposition="outside",
        textfont=dict(color=rv["text_primary"], size=11),
        marker_line_color=rv["bg_surface"], marker_line_width=1.5,
    )
    fig1.update_layout(showlegend=False)
    dark_layout(fig1, height=360)

# Chart 2 — Revenue by Industry
with ca2:
    ri = (
        df.groupby("Industry")["Annual Revenue (NGN)"]
        .sum().reset_index()
        .sort_values("Annual Revenue (NGN)", ascending=True)
    )
    fig2 = px.bar(
        ri, x="Annual Revenue (NGN)", y="Industry",
        orientation="h",
        title="Annual Revenue by Industry",
        color="Annual Revenue (NGN)",
        color_continuous_scale=[rv["brand_mid"], rv["brand_glow"], rv["gold"]],
    )
    fig2.update_traces(marker_line_color=rv["bg_surface"], marker_line_width=1)
    fig2.update_layout(coloraxis_showscale=False)
    dark_layout(fig2, height=360)

# Chart 3 — Monthly Contract Start Trend
with ca3:
    ms = (
        df.dropna(subset=["Start Date"])
        .groupby("Start_Month").size().reset_index(name="Count")
        .sort_values("Start_Month")
    )
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=ms["Start_Month"], y=ms["Count"],
        mode="lines+markers",
        name="New Contracts",
        line=dict(color=rv["brand_glow"], width=2.5),
        marker=dict(color=rv["gold"], size=7,
                    line=dict(color=rv["bg_surface"], width=1.5)),
        fill="tozeroy",
        fillcolor="rgba(75,82,212,0.12)",
    ))
    fig3.update_layout(showlegend=False)
    dark_layout(fig3, "Monthly Contract Start Trend", height=360)


# ─────────────────────────────────────────────────────────────────────────────
# CHARTS — ROW B: Risk Donut | Top Managers | State Distribution
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"<hr style='border-color:{rv['border']};margin:8px 0 16px;'>", unsafe_allow_html=True)
st.markdown(
    f"<p style='color:{rv['gold']};font-size:0.78rem;font-weight:700;"
    "text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px;'>"
    " Risk, Client & Account Management</p>",
    unsafe_allow_html=True,
)
cb1, cb2, cb3 = st.columns(3)

# Chart 4 — Risk Donut
with cb1:
    rc = df["Risk"].value_counts().reset_index()
    rmap = {"High": rv["danger"], "Medium": rv["warning"], "Low": rv["success"]}
    fig4 = go.Figure(go.Pie(
        labels=rc["Risk"],
        values=rc["count"],
        hole=0.55,
        marker=dict(
            colors=[rmap.get(r, rv["brand_mid"]) for r in rc["Risk"]],
            line=dict(color=rv["bg_surface"], width=3),
        ),
        textinfo="label+percent",
        textfont=dict(color=rv["text_primary"], size=11),
        hovertemplate="<b>%{label}</b><br>Clients: %{value}<br>Share: %{percent}<extra></extra>",
    ))
    fig4.update_layout(
        annotations=[dict(
            text=f"<b style='font-size:16px'>{len(df)}</b><br>Clients",
            x=0.5, y=0.5, showarrow=False,
            font=dict(color=rv["text_heading"], size=13),
        )],
        legend=dict(
            font=dict(color=rv["text_secondary"]),
            bgcolor=rv["bg_elevated"],
            bordercolor=rv["border"],
        ),
    )
    dark_layout(fig4, "Risk Level Breakdown", height=360)

# Chart 5 — Top 10 Account Managers by Revenue
with cb2:
    tm = (
        df.groupby("Account Manager")["Annual Revenue (NGN)"]
        .sum().reset_index()
        .sort_values("Annual Revenue (NGN)", ascending=False)
        .head(10)
        .sort_values("Annual Revenue (NGN)", ascending=True)
    )
    fig5 = px.bar(
        tm, x="Annual Revenue (NGN)", y="Account Manager",
        orientation="h",
        title="Top 10 Account Managers by Revenue",
        color="Annual Revenue (NGN)",
        color_continuous_scale=[rv["brand_mid"], rv["brand_glow"], rv["gold"]],
    )
    fig5.update_traces(marker_line_color=rv["bg_surface"], marker_line_width=1)
    fig5.update_layout(coloraxis_showscale=False)
    dark_layout(fig5, height=360)

# Chart 6 — Client Distribution by State
with cb3:
    sc = df["State"].value_counts().reset_index()
    fig6 = px.bar(
        sc, x="State", y="count",
        title="Client Distribution by State",
        color="count",
        color_continuous_scale=[rv["brand_mid"], rv["brand_glow"], rv["gold_light"]],
        text="count",
    )
    fig6.update_traces(
        textposition="outside",
        textfont=dict(color=rv["text_primary"], size=10),
        marker_line_color=rv["bg_surface"], marker_line_width=1,
    )
    fig6.update_layout(coloraxis_showscale=False)
    dark_layout(fig6, height=360)


# ─────────────────────────────────────────────────────────────────────────────
# CHARTS — ROW C: Treemap | Invoice by Contract Type
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"<hr style='border-color:{rv['border']};margin:8px 0 16px;'>", unsafe_allow_html=True)
st.markdown(
    f"<p style='color:{rv['gold']};font-size:0.78rem;font-weight:700;"
    "text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px;'>"
    "🔧 Service, Invoice & Equipment Analytics</p>",
    unsafe_allow_html=True,
)
cc1, cc2 = st.columns(2)

# Chart 7 — Service Treemap
with cc1:
    sr = df.groupby("Service")["Annual Revenue (NGN)"].sum().reset_index()
    fig7 = px.treemap(
        sr, path=["Service"], values="Annual Revenue (NGN)",
        title="Service Type — Revenue Distribution",
        color="Annual Revenue (NGN)",
        color_continuous_scale=[rv["brand_dark"], rv["brand_mid"], rv["brand_glow"], rv["gold"]],
    )
    fig7.update_traces(
        textinfo="label+value+percent root",
        textfont=dict(color="white", size=12),
        marker=dict(line=dict(color=rv["bg_surface"], width=2)),
        hovertemplate=(
            "<b>%{label}</b><br>Revenue: ₦%{value:,.0f}"
            "<br>Share: %{percentRoot:.1%}<extra></extra>"
        ),
    )
    fig7.update_layout(
        coloraxis_colorbar=dict(
            title=dict(text="Revenue", font=dict(color=rv["text_secondary"])),
            tickfont=dict(color=rv["text_muted"]),
        )
    )
    dark_layout(fig7, height=400)

# Chart 8 — Invoice Status by Contract Type
with cc2:
    ic = df.groupby(["Contract Type", "Invoice"]).size().reset_index(name="Count")
    imap = {"Paid": rv["success"], "Pending": rv["warning"], "Overdue": rv["danger"]}
    fig8 = px.bar(
        ic, x="Contract Type", y="Count", color="Invoice",
        barmode="group",
        title="Invoice Status by Contract Type",
        color_discrete_map=imap,
        text="Count",
    )
    fig8.update_traces(
        textposition="outside",
        textfont=dict(color=rv["text_primary"], size=10),
        marker_line_color=rv["bg_surface"], marker_line_width=1,
    )
    dark_layout(fig8, height=400)


# ─────────────────────────────────────────────────────────────────────────────
# CHARTS — ROW D: Equipment by Risk | SLA by Service
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"<hr style='border-color:{rv['border']};margin:8px 0 16px;'>", unsafe_allow_html=True)
st.markdown(
    f"<p style='color:{rv['gold']};font-size:0.78rem;font-weight:700;"
    "text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px;'>"
    "🛠️ Equipment & SLA Intelligence</p>",
    unsafe_allow_html=True,
)
cd1, cd2 = st.columns([1.2, 0.8])

# Chart 9 — Equipment by Risk (Stacked)
with cd1:
    er = df.groupby(["Equipment", "Risk"]).size().reset_index(name="Count")
    rmap2 = {"High": rv["danger"], "Medium": rv["warning"], "Low": rv["success"]}
    fig9 = px.bar(
        er, x="Equipment", y="Count", color="Risk",
        barmode="stack",
        title="Equipment Type by Risk Level",
        color_discrete_map=rmap2,
        text="Count",
    )
    fig9.update_traces(
        textposition="inside",
        textfont=dict(color="white", size=10),
        marker_line_color=rv["bg_surface"], marker_line_width=1,
    )
    dark_layout(fig9, height=380)

# Chart — SLA Compliance by Service
with cd2:
    sla_s = (
        df.groupby("Service")["SLA_Numeric"].mean().reset_index()
        .sort_values("SLA_Numeric", ascending=True)
    )
    fig_sla = px.bar(
        sla_s,
        x="SLA_Numeric", y="Service",
        orientation="h",
        title="Avg SLA Compliance by Service (%)",
        color="SLA_Numeric",
        color_continuous_scale=[rv["warning"], rv["success"]],
        text=sla_s["SLA_Numeric"].map(lambda x: f"{x:.1f}%"),
    )
    fig_sla.update_traces(
        textposition="outside",
        textfont=dict(color=rv["text_primary"], size=10),
        marker_line_color=rv["bg_surface"], marker_line_width=1,
    )
    fig_sla.update_layout(coloraxis_showscale=False)
    fig_sla.update_xaxes(range=[88, 102])
    dark_layout(fig_sla, height=380)


# ─────────────────────────────────────────────────────────────────────────────
# CHART 10 — ADVANCED 3D INTELLIGENCE SCATTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"<hr style='border-color:{rv['border']};margin:8px 0 16px;'>", unsafe_allow_html=True)
st.markdown(
    f"<p style='color:{rv['gold']};font-size:0.78rem;font-weight:700;"
    "text-transform:uppercase;letter-spacing:0.08em;margin-bottom:4px;'>"
    " 3D Client Intelligence Scatter</p>",
    unsafe_allow_html=True,
)
st.markdown(
    f"<p style='color:{rv['text_muted']};font-size:0.82rem;margin-top:0;margin-bottom:12px;'>"
    "Rotate · Zoom · Hover — Identify high-revenue clients with low satisfaction or elevated incident rates.</p>",
    unsafe_allow_html=True,
)

risk_3d = {"High": rv["danger"], "Medium": rv["warning"], "Low": rv["success"]}
df3d = df.dropna(subset=["Annual Revenue (NGN)", "Satisfaction", "Incidents"])

fig10 = go.Figure()
for rl, grp in df3d.groupby("Risk"):
    fig10.add_trace(go.Scatter3d(
        x=grp["Annual Revenue (NGN)"],
        y=grp["Satisfaction"],
        z=grp["Incidents"],
        mode="markers",
        name=rl,
        marker=dict(
            size=5,
            color=risk_3d.get(rl, rv["brand_mid"]),
            opacity=0.85,
            line=dict(color=rv["bg_surface"], width=0.5),
        ),
        customdata=grp[["Client Name","Service","Account Manager","State","Contract"]].values,
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Service: %{customdata[1]}<br>"
            "Manager: %{customdata[2]}<br>"
            "State: %{customdata[3]}<br>"
            "Contract: %{customdata[4]}<br>"
            "Revenue: ₦%{x:,.0f}<br>"
            "Satisfaction: %{y:.2f}<br>"
            "Incidents: %{z}<extra></extra>"
        ),
    ))

fig10.update_layout(
    title=dict(
        text="Revenue × Satisfaction × Incidents — Risk Intelligence View",
        font=dict(color=rv["text_heading"], size=14),
    ),
    paper_bgcolor=rv["bg_surface"],
    scene=dict(
        bgcolor=rv["bg_elevated"],
        xaxis=dict(
            title=dict(text="Annual Revenue (NGN)",
                       font=dict(color=rv["text_secondary"], size=11)),
            tickfont=dict(color=rv["text_muted"], size=9),
            backgroundcolor=rv["bg_elevated"],
            gridcolor="rgba(75,82,212,0.18)",
            zerolinecolor="rgba(75,82,212,0.25)",
        ),
        yaxis=dict(
            title=dict(text="Satisfaction Score",
                       font=dict(color=rv["text_secondary"], size=11)),
            tickfont=dict(color=rv["text_muted"], size=9),
            backgroundcolor=rv["bg_elevated"],
            gridcolor="rgba(75,82,212,0.18)",
            zerolinecolor="rgba(75,82,212,0.25)",
        ),
        zaxis=dict(
            title=dict(text="Incidents",
                       font=dict(color=rv["text_secondary"], size=11)),
            tickfont=dict(color=rv["text_muted"], size=9),
            backgroundcolor=rv["bg_elevated"],
            gridcolor="rgba(75,82,212,0.18)",
            zerolinecolor="rgba(75,82,212,0.25)",
        ),
        camera=dict(eye=dict(x=1.6, y=1.6, z=0.9)),
    ),
    legend=dict(
        title=dict(text="Risk Level", font=dict(color=rv["text_secondary"])),
        bgcolor=rv["bg_elevated"],
        bordercolor=rv["border"],
        borderwidth=1,
        font=dict(color=rv["text_secondary"]),
    ),
    height=580,
    margin=dict(l=0, r=0, t=50, b=0),
    hoverlabel=dict(
        bgcolor=rv["bg_elevated"],
        font_color=rv["text_heading"],
        bordercolor=rv["border_card"],
    ),
)
st.plotly_chart(fig10, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# RAW DATA TABLE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"<hr style='border-color:{rv['border']};margin:8px 0 16px;'>", unsafe_allow_html=True)
with st.expander(" View Filtered Client Data Table"):
    display_cols = [
        "Client ID","Client Name","Industry","State","Service",
        "Contract Type","Contract","Risk","Invoice",
        "Annual Revenue (NGN)","Guards","Satisfaction",
        "Incidents","Response Min","SLA",
    ]
    st.dataframe(df[display_cols].reset_index(drop=True), use_container_width=True, height=360)
    st.caption(f"Showing {len(df):,} of {len(df_raw):,} total records.")


# ─────────────────────────────────────────────────────────────────────────────
# EXECUTIVE INSIGHT SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
with st.expander(" Executive Insight Summary — Rapid Vigil Security Intelligence"):
    st.markdown(f"""
    <div style="color:{rv['text_primary']}; font-size:0.91rem; line-height:1.85;">

    <h4 style="color:{rv['gold']} !important; border-bottom:1px solid {rv['border']};
        padding-bottom:6px;"> 1. Revenue Concentration & Geographic Risk</h4>
    <p>The Revenue by Industry chart reveals which sectors generate the highest share of
    Rapid Vigil's annual contract value. A high concentration in one or two industries
    represents a portfolio risk — loss of a major sector client could materially impact
    revenue. The State distribution chart surfaces geographic dependency; states with high
    client counts but lower average revenue may indicate growth opportunities at underserved
    price points.</p>

    <h4 style="color:{rv['gold']} !important; border-bottom:1px solid {rv['border']};
        padding-bottom:6px; margin-top:1.2rem;"> 2. Contract Lifecycle & Renewal Pipeline</h4>
    <p>A high proportion of Expiring contracts relative to Renewed ones signals an at-risk
    renewal pipeline. The Top 10 Account Managers chart isolates which individuals carry the
    heaviest revenue responsibility — those managing the largest share of Expiring contracts
    require immediate escalation support and renewal playbooks to protect revenue retention.</p>

    <h4 style="color:{rv['gold']} !important; border-bottom:1px solid {rv['border']};
        padding-bottom:6px; margin-top:1.2rem;"> 3. Risk Portfolio & Resource Deployment</h4>
    <p>A portfolio skewed toward High-risk clients demands proportionally greater guard
    deployment, more frequent incident response readiness, and higher equipment investment.
    These patterns directly drive workforce planning, staffing budgets, and contract pricing
    strategy — High-risk sites must be appropriately priced to protect operational margins.</p>

    <h4 style="color:{rv['gold']} !important; border-bottom:1px solid {rv['border']};
        padding-bottom:6px; margin-top:1.2rem;"> 4. Cash Flow Vulnerability — Invoice Status</h4>
    <p>The Invoice Status by Contract Type chart highlights payment behavior across Annual,
    Monthly, and Biannual cycles. High Overdue rates — especially in Annual contracts —
    represent a receivables risk. Targeted follow-up protocols, tighter payment terms on
    renewal, and escalation triggers by account manager are the recommended remedies.</p>

    <h4 style="color:{rv['gold']} !important; border-bottom:1px solid {rv['border']};
        padding-bottom:6px; margin-top:1.2rem;"> 5. Operational Efficiency — Response Time & SLA</h4>
    <p>Service types with response times exceeding contractual thresholds are SLA breach
    risks. The SLA Compliance chart identifies which service categories consistently meet
    their performance standards and which require supervisor reassignment, patrol frequency
    adjustment, or equipment upgrades to close compliance gaps.</p>

    <h4 style="color:{rv['gold']} !important; border-bottom:1px solid {rv['border']};
        padding-bottom:6px; margin-top:1.2rem;"> 6. Satisfaction, Incidents & Retention Drivers</h4>
    <p>Clients with low satisfaction scores and high incident counts are at the highest
    churn risk regardless of contract value. High-satisfaction clients with few incidents
    and consistent patrol frequency represent long-term renewers. These patterns directly
    inform service configuration standards, supervisor training priorities, and client
    review cadences.</p>

    <h4 style="color:{rv['gold']} !important; border-bottom:1px solid {rv['border']};
        padding-bottom:6px; margin-top:1.2rem;"> 7. 3D Intelligence — Outlier Client Detection</h4>
    <p>The 3D scatter (Revenue × Satisfaction × Incidents) surfaces the clients that demand
    immediate executive attention: high-revenue accounts with below-average satisfaction or
    above-average incident counts. These outliers represent the highest churn risk per unit
    of revenue and should trigger priority account reviews and service remediation plans.</p>

    <h4 style="color:{rv['gold']} !important; border-bottom:1px solid {rv['border']};
        padding-bottom:6px; margin-top:1.2rem;"> 8. Daily Dashboard Usage Guide</h4>
    <p>Use sidebar filters to isolate specific states, service types, or risk bands before
    client meetings. Monitor the Expiring Contracts KPI weekly for proactive renewal action.
    Use Overdue Invoices in weekly finance reviews to drive accounts receivable escalations.
    Review the 3D scatter monthly to update the at-risk client watchlist. All KPIs and
    charts update in real time as filters change — no manual refresh required.</p>

    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="
    text-align:center;
    padding:16px;
    margin-top:28px;
    border-top:1px solid {rv['border']};
    color:{rv['text_muted']};
    font-size:0.76rem;
">
    ️ <strong style="color:{rv['text_secondary']}">Rapid Vigil Security</strong>
    &nbsp;|&nbsp; Client Intelligence Dashboard
    &nbsp;|&nbsp; Built by <strong style="color:{rv['gold']}">ToheebBI Consulting</strong>
    &nbsp;|&nbsp; {len(df_raw):,} clients · {df_raw['State'].nunique()} states · {df_raw['Industry'].nunique()} industries
</div>
""", unsafe_allow_html=True)