import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import os

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Job Market & Skill Intelligence Dashboard",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Reference Plot Inspired Theme Settings
FONT_FAMILY = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
COLOR_PALETTE_SPECTRAL = [
    "#5e4fa2", "#3288bd", "#66c2a5", "#abdda4", "#e6f598", 
    "#ffffbf", "#fee08b", "#fdae61", "#f46d43", "#d53e4f", "#9e0142"
]
COLOR_CATEGORICAL = [
    "#d53e4f", "#f46d43", "#fdae61", "#fee08b", 
    "#abdda4", "#66c2a5", "#3288bd", "#5e4fa2", "#9e0142", "#e6f598"
]

# Custom Styling for Dashboard
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main {
        background-color: #0b0f19;
    }
    
    /* KPI Card styling */
    .kpi-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
        backdrop-filter: blur(12px);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: rgba(244, 109, 67, 0.5);
    }
    .kpi-title {
        color: #94a3b8;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 6px;
    }
    .kpi-value {
        color: #f8fafc;
        font-size: 1.85rem;
        font-weight: 800;
        margin: 0;
        line-height: 1.15;
        letter-spacing: -0.02em;
    }
    .kpi-subtitle {
        color: #64748b;
        font-size: 0.78rem;
        margin-top: 5px;
        font-weight: 500;
    }
    
    /* Section Headers */
    .section-title {
        font-size: 1.35rem;
        font-weight: 700;
        color: #f1f5f9;
        margin-top: 1.25rem;
        margin-bottom: 0.4rem;
        display: flex;
        align-items: center;
        gap: 8px;
        letter-spacing: -0.01em;
    }
    .section-desc {
        color: #94a3b8;
        font-size: 0.92rem;
        margin-bottom: 1.25rem;
        line-height: 1.55;
    }
    
    /* Pill Tags */
    .skill-pill {
        display: inline-block;
        background: rgba(244, 109, 67, 0.12);
        color: #fdae61;
        border: 1px solid rgba(244, 109, 67, 0.35);
        border-radius: 16px;
        padding: 3px 10px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 3px 4px 3px 0;
    }
    .badge-match {
        background: linear-gradient(135deg, rgba(213, 62, 79, 0.2) 0%, rgba(244, 109, 67, 0.2) 100%);
        color: #fdae61;
        border: 1px solid rgba(244, 109, 67, 0.4);
        border-radius: 12px;
        padding: 3px 10px;
        font-size: 0.82rem;
        font-weight: 700;
    }
    
    /* Chart Card Container */
    .plot-container {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 8px;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to apply common high-quality font and layout styling to any Plotly figure
def apply_theme_layout(fig, title_text="", height=440, show_legend=True):
    fig.update_layout(
        title=dict(
            text=f"<b>{title_text}</b>" if title_text else "",
            font=dict(family=FONT_FAMILY, size=15, color="#f8fafc"),
            x=0.01,
            y=0.96
        ),
        font=dict(family=FONT_FAMILY, size=12, color="#cbd5e1"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=dict(l=25, r=25, t=55 if title_text else 30, b=45),
        showlegend=show_legend,
        legend=dict(
            font=dict(family=FONT_FAMILY, size=11, color="#cbd5e1"),
            bgcolor="rgba(15, 23, 42, 0.7)",
            bordercolor="rgba(255, 255, 255, 0.1)",
            borderwidth=1
        )
    )
    fig.update_xaxes(
        tickfont=dict(family=FONT_FAMILY, size=11, color="#94a3b8"),
        title_font=dict(family=FONT_FAMILY, size=12, color="#cbd5e1"),
        gridcolor="rgba(255, 255, 255, 0.06)",
        zerolinecolor="rgba(255, 255, 255, 0.12)"
    )
    fig.update_yaxes(
        tickfont=dict(family=FONT_FAMILY, size=11, color="#94a3b8"),
        title_font=dict(family=FONT_FAMILY, size=12, color="#cbd5e1"),
        gridcolor="rgba(255, 255, 255, 0.06)",
        zerolinecolor="rgba(255, 255, 255, 0.12)"
    )
    return fig

# Load data with caching
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "processed_jobs.csv")
    tax_path = os.path.join(base_dir, "skill_taxonomy.json")
    
    df = pd.read_csv(data_path)
    with open(tax_path, "r", encoding="utf-8") as f:
        taxonomy = json.load(f)
        
    return df, taxonomy

try:
    df, taxonomy = load_data()
    skill_cols = taxonomy["skill_list"]
    skill_categories = taxonomy["categories"]
except Exception as e:
    st.error(f"Error loading processed dataset: {e}")
    st.stop()

# ==========================================
# SIDEBAR FILTERS
# ==========================================
st.sidebar.markdown(
    "<div style='display: flex; align-items: center; gap: 10px; margin-bottom: 15px;'>"
    "<span style='font-size: 2rem;'>💼</span>"
    "<div><b style='color: #f8fafc; font-size: 1.15rem;'>Skill Intelligence</b><br>"
    "<span style='color: #94a3b8; font-size: 0.8rem;'>Job Market Analytics Engine</span></div>"
    "</div>",
    unsafe_allow_html=True
)

all_roles = sorted(df['standardized_role'].unique())
selected_roles = st.sidebar.multiselect(
    "Job Role / Function:",
    options=all_roles,
    default=all_roles
)

all_states = sorted([s for s in df['clean_state'].unique() if s != "Not Specified"])
selected_states = st.sidebar.multiselect(
    "State / Region:",
    options=all_states,
    default=[]
)

all_quals = sorted(df['clean_qualification'].unique())
selected_quals = st.sidebar.multiselect(
    "Education Tier:",
    options=all_quals,
    default=[]
)

all_industries = sorted(df['clean_industry'].unique())
selected_industries = st.sidebar.multiselect(
    "Industry Sector:",
    options=all_industries,
    default=[]
)

gender_options = ["All", "Any", "Male", "Female"]
selected_gender = st.sidebar.selectbox("Gender Preference:", gender_options, index=0)

has_salary_only = st.sidebar.checkbox("Only Jobs with Disclosed Pay", value=False)

# Apply Filter Logic
filtered_df = df[df['standardized_role'].isin(selected_roles)]
if selected_states:
    filtered_df = filtered_df[filtered_df['clean_state'].isin(selected_states)]
if selected_quals:
    filtered_df = filtered_df[filtered_df['clean_qualification'].isin(selected_quals)]
if selected_industries:
    filtered_df = filtered_df[filtered_df['clean_industry'].isin(selected_industries)]
if selected_gender != "All":
    filtered_df = filtered_df[filtered_df['clean_gender'] == selected_gender]
if has_salary_only:
    filtered_df = filtered_df[filtered_df['monthly_salary'].notnull()]

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Showing:** `{len(filtered_df):,}` of `{len(df):,}` jobs")
st.sidebar.markdown(f"**Total Vacancies:** `{filtered_df['vacancy_num'].sum():,}` openings")

if st.sidebar.button("Reset All Filters", use_container_width=True):
    st.rerun()

# ==========================================
# MAIN DASHBOARD HEADER & KPI CARDS
# ==========================================
st.markdown("<h1 style='color: #f8fafc; font-weight: 800; font-size: 2.2rem; margin-bottom: 2px; letter-spacing: -0.02em;'>🎯 Industrial & Technical Job Market Intelligence</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #94a3b8; font-size: 1.05rem; margin-bottom: 1.5rem;'>Data Analyst Deep Dive: <b>Which Job Role Needs Which Skill Sets?</b>, Compensation Benchmarks & Talent Pipelines</p>", unsafe_allow_html=True)

# Top Metrics
total_postings = len(filtered_df)
total_vacancies = filtered_df['vacancy_num'].sum()
median_sal = filtered_df['monthly_salary'].dropna().median()
sal_display = f"₹{int(median_sal):,}/mo" if not np.isnan(median_sal) else "N/A"
unique_employers = filtered_df['client_name'].nunique()

if total_postings > 0:
    skill_counts = filtered_df[skill_cols].sum()
    top_demanded_skill = skill_counts.idxmax()
    top_demanded_pct = (skill_counts.max() / total_postings) * 100
else:
    top_demanded_skill = "N/A"
    top_demanded_pct = 0.0

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Job Postings</div>
        <div class="kpi-value">{total_postings:,}</div>
        <div class="kpi-subtitle">{total_postings/len(df)*100:.1f}% of total listings</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Total Openings</div>
        <div class="kpi-value">{total_vacancies:,}</div>
        <div class="kpi-subtitle">Mean {total_vacancies/max(1, total_postings):.0f} per posting</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Median Pay / Stipend</div>
        <div class="kpi-value">{sal_display}</div>
        <div class="kpi-subtitle">Market monthly rate</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Hiring Employers</div>
        <div class="kpi-value">{unique_employers:,}</div>
        <div class="kpi-subtitle">Active client organizations</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Top Core Skill</div>
        <div class="kpi-value" style="font-size: 1.35rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{top_demanded_skill}</div>
        <div class="kpi-subtitle">{top_demanded_pct:.1f}% demand rate</div>
    </div>
    """, unsafe_allow_html=True)

if total_postings == 0:
    st.warning("No job postings match your selected filters. Please adjust the criteria in the sidebar.")
    st.stop()

# ==========================================
# INTERACTIVE TABS
# ==========================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🧩 1. The Core Question: Role vs Skill Sets",
    "💰 2. Compensation & Skill Premiums",
    "🎓 3. Talent Pipeline & Qualifications",
    "🗺️ 4. Geographic & Industry Ecosystem",
    "🎯 5. Career & Skill Fit Matcher",
    "📋 6. Data Explorer & Export"
])

# ==============================================================================
# TAB 1: THE CORE QUESTION - WHICH JOB ROLE NEEDS WHICH SKILL SETS?
# ==============================================================================
with tab1:
    st.markdown("<div class='section-title'>Which Job Role Needs Which Skill Sets?</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-desc'>Every functional role possesses a distinct technological footprint. "
        "The <b>Role vs. Skill Affinity Matrix</b> below shows the percentage of job listings requiring each skill, styled with crisp tile boundaries, high-contrast labels, and a warm-cool palette inspired by statistical correlation maps.</div>",
        unsafe_allow_html=True
    )
    
    col_ctrl1, col_ctrl2 = st.columns([2, 1])
    with col_ctrl1:
        selected_category = st.selectbox(
            "Filter Skill Taxonomy Category:",
            options=["All Categories"] + list(skill_categories.keys())
        )
    with col_ctrl2:
        heatmap_metric = st.radio("Display Values As:", ["Percentage of Jobs (%)", "Total Job Count (#)"], horizontal=True)

    if selected_category == "All Categories":
        active_skills = skill_cols
    else:
        active_skills = skill_categories[selected_category]

    # Calculate Matrix
    role_group = filtered_df.groupby('standardized_role')
    if heatmap_metric == "Percentage of Jobs (%)":
        matrix = (role_group[active_skills].mean() * 100).round(1)
        z_title = "Demand %"
    else:
        matrix = role_group[active_skills].sum()
        z_title = "Jobs Count"

    z_vals = matrix.T.values
    x_roles = matrix.index.tolist()
    y_skills = matrix.columns.tolist()

    # Build annotations for dynamic contrast:
    # Inspired by reference plot: crisp numbers in each tile, high contrast font colors
    annotations = []
    max_z = np.max(z_vals) if np.max(z_vals) > 0 else 1.0

    for i, row_name in enumerate(y_skills):
        for j, col_name in enumerate(x_roles):
            val = z_vals[i][j]
            if heatmap_metric == "Percentage of Jobs (%)":
                txt = f"{val:.1f}%" if val > 0 else "—"
            else:
                txt = f"{int(val)}" if val > 0 else "—"
            
            # Contrast logic:
            # High values (top 40% of range) -> White text (#ffffff)
            # Mid values (10% - 40% of range) -> Charcoal dark text (#1e293b)
            # Zero values -> Subtle muted gray (#64748b)
            norm_val = val / max_z
            if val == 0:
                font_color = "#64748b"
                font_weight = "normal"
            elif norm_val >= 0.45 or norm_val <= 0.08:
                font_color = "#ffffff"
                font_weight = "bold"
            else:
                font_color = "#0f172a"
                font_weight = "bold"

            annotations.append(dict(
                x=col_name,
                y=row_name,
                text=f"<b>{txt}</b>" if font_weight == "bold" else txt,
                font=dict(
                    family=FONT_FAMILY,
                    size=11,
                    color=font_color
                ),
                showarrow=False
            ))

    fig_heat = go.Figure(data=go.Heatmap(
        z=z_vals,
        x=x_roles,
        y=y_skills,
        colorscale="Spectral_r",
        xgap=2.5,  # Tile borders inspired by user reference plot
        ygap=2.5,
        colorbar=dict(
            title=dict(
                text=f"<b>{z_title}</b>",
                font=dict(family=FONT_FAMILY, size=12, color="#f8fafc")
            ),
            tickfont=dict(family=FONT_FAMILY, size=11, color="#cbd5e1"),
            len=0.95,
            thickness=18,
            outlinewidth=1,
            outlinecolor="rgba(255, 255, 255, 0.15)"
        ),
        hoverongaps=False,
        hovertemplate="<b>Role:</b> %{x}<br><b>Skill:</b> %{y}<br><b>Value:</b> %{z:.1f}<extra></extra>"
    ))

    fig_heat.update_layout(
        annotations=annotations,
        title=dict(
            text="<b>Role vs. Skill Affinity Matrix</b> (Percentage Demand)",
            font=dict(family=FONT_FAMILY, size=16, color="#f8fafc"),
            x=0.01,
            y=0.98
        ),
        font=dict(family=FONT_FAMILY, size=12, color="#cbd5e1"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=max(460, len(active_skills) * 27 + 130),
        margin=dict(l=20, r=20, t=55, b=120),
        xaxis=dict(
            tickangle=-32,
            tickfont=dict(family=FONT_FAMILY, size=11, color="#e2e8f0"),
            showgrid=False
        ),
        yaxis=dict(
            tickfont=dict(family=FONT_FAMILY, size=11, color="#e2e8f0"),
            showgrid=False,
            autorange="reversed"
        )
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown("---")

    # 2. Drill-down Role Profile Analysis
    st.markdown("<div class='section-title'>🔍 Role Deep Dive: Signature Skills & Capability Profile</div>", unsafe_allow_html=True)
    
    col_dd1, col_dd2 = st.columns([1, 2])
    with col_dd1:
        selected_role_drill = st.selectbox("Select a Job Role to Inspect:", options=sorted(filtered_df['standardized_role'].unique()))
        role_subset = filtered_df[filtered_df['standardized_role'] == selected_role_drill]
        
        st.markdown(f"""
        <div class="kpi-card" style="margin-top: 8px;">
            <div class="kpi-title">Role Profile</div>
            <div class="kpi-value" style="font-size: 1.4rem;">{selected_role_drill}</div>
            <p style="margin: 10px 0 4px 0; color: #cbd5e1; font-size: 0.88rem; line-height: 1.6;">
                <b>Total Listings:</b> <span style="color: #f8fafc; font-weight: 700;">{len(role_subset):,}</span><br>
                <b>Total Vacancies:</b> <span style="color: #fdae61; font-weight: 700;">{role_subset['vacancy_num'].sum():,} openings</span><br>
                <b>Median Monthly Pay:</b> <span style="color: #66c2a5; font-weight: 700;">₹{role_subset['monthly_salary'].median():,.0f}</span><br>
                <b>Primary Qualification:</b> <span style="color: #f8fafc;">{role_subset['clean_qualification'].mode().iloc[0] if len(role_subset)>0 else 'N/A'}</span><br>
                <b>Top Hiring Industry:</b> <span style="color: #f8fafc;">{role_subset['clean_industry'].mode().iloc[0] if len(role_subset)>0 else 'N/A'}</span>
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_dd2:
        role_skills_mean = (role_subset[skill_cols].mean() * 100).sort_values(ascending=True)
        role_skills_nonzero = role_skills_mean[role_skills_mean > 0]
        if len(role_skills_nonzero) == 0:
            role_skills_nonzero = role_skills_mean.tail(8)

        fig_role_bar = go.Figure(go.Bar(
            x=role_skills_nonzero.values,
            y=role_skills_nonzero.index,
            orientation='h',
            text=[f"<b>{val:.1f}%</b>" for val in role_skills_nonzero.values],
            textposition='outside',
            textfont=dict(family=FONT_FAMILY, size=11, color="#f8fafc"),
            marker=dict(
                color=role_skills_nonzero.values,
                colorscale="Spectral_r",
                line=dict(color="rgba(255, 255, 255, 0.2)", width=1)
            )
        ))
        apply_theme_layout(fig_role_bar, title_text=f"Core Skill Requirements for: {selected_role_drill}", height=360, show_legend=False)
        fig_role_bar.update_xaxes(title_text="Demand Percentage (% of postings)", range=[0, max(15, max(role_skills_nonzero.values) * 1.18)])
        st.plotly_chart(fig_role_bar, use_container_width=True)

    # 3. Radar Chart Across Skill Categories
    st.markdown("<div class='section-title'>🕸️ Multidimensional Skill Portfolio by Role</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-desc'>Compare how different job roles require breadth across the 5 primary industrial skill domains.</div>", unsafe_allow_html=True)

    radar_roles = st.multiselect(
        "Select up to 4 roles to compare on skill dimensions:",
        options=sorted(df['standardized_role'].unique()),
        default=[
            "CNC & Machine Operation", 
            "Material Handling & Heavy Equipment", 
            "Quality Assurance & Inspection",
            "Warehouse, Logistics & Fulfillment"
        ][:len(df['standardized_role'].unique())]
    )

    if radar_roles:
        radar_categories = list(skill_categories.keys())
        fig_radar = go.Figure()

        palette_cycle = ["#d53e4f", "#fdae61", "#66c2a5", "#3288bd", "#5e4fa2"]
        max_radar_val = 20.0

        for idx, r_name in enumerate(radar_roles):
            r_df = df[df['standardized_role'] == r_name]
            scores = []
            for cat_name, cat_skills in skill_categories.items():
                val = (r_df[cat_skills].mean().mean()) * 100
                scores.append(round(val, 1))
            
            max_radar_val = max(max_radar_val, max(scores))
            scores_closed = scores + [scores[0]]
            cats_closed = radar_categories + [radar_categories[0]]
            
            trace_color = palette_cycle[idx % len(palette_cycle)]
            fig_radar.add_trace(go.Scatterpolar(
                r=scores_closed,
                theta=cats_closed,
                fill='toself',
                name=f"<b>{r_name}</b>",
                line=dict(color=trace_color, width=2.5),
                marker=dict(size=6, color=trace_color)
            ))

        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max_radar_val + 8],
                    tickfont=dict(family=FONT_FAMILY, size=10, color="#94a3b8"),
                    gridcolor="rgba(255, 255, 255, 0.08)"
                ),
                angularaxis=dict(
                    tickfont=dict(family=FONT_FAMILY, size=11, color="#f1f5f9", weight=600),
                    gridcolor="rgba(255, 255, 255, 0.08)"
                ),
                bgcolor="rgba(0,0,0,0)"
            ),
            font=dict(family=FONT_FAMILY, size=12, color="#cbd5e1"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=460,
            margin=dict(l=40, r=40, t=50, b=40),
            legend=dict(
                font=dict(family=FONT_FAMILY, size=11, color="#cbd5e1"),
                bgcolor="rgba(15, 23, 42, 0.7)",
                bordercolor="rgba(255, 255, 255, 0.1)"
            ),
            title=dict(
                text="<b>Cross-Category Skill Portfolio Footprint</b>",
                font=dict(family=FONT_FAMILY, size=15, color="#f8fafc")
            )
        )
        st.plotly_chart(fig_radar, use_container_width=True)


# ==============================================================================
# TAB 2: COMPENSATION & SKILL PREMIUMS
# ==============================================================================
with tab2:
    st.markdown("<div class='section-title'>💰 Compensation Benchmarks & The Skill Premium</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-desc'>Explore monthly pay distributions (25th-75th percentiles) across roles, "
        "and quantify the exact <b>monetary premium</b> attached to each technical competency.</div>",
        unsafe_allow_html=True
    )

    col_sal1, col_sal2 = st.columns([3, 2])

    with col_sal1:
        sal_clean_df = filtered_df.dropna(subset=['monthly_salary'])
        if len(sal_clean_df) > 0:
            role_order = sal_clean_df.groupby('standardized_role')['monthly_salary'].median().sort_values(ascending=False).index
            
            fig_box = px.box(
                sal_clean_df,
                x='monthly_salary',
                y='standardized_role',
                category_orders={'standardized_role': role_order},
                color='standardized_role',
                color_discrete_sequence=COLOR_CATEGORICAL,
                labels={'monthly_salary': 'Monthly Stipend / Salary (₹)', 'standardized_role': 'Job Role'}
            )
            apply_theme_layout(fig_box, title_text="Monthly Compensation Distribution by Job Role", height=420, show_legend=False)
            fig_box.update_xaxes(tickprefix="₹", tickformat=",.0f")
            st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.info("No salary data available for the current filter selection.")

    with col_sal2:
        tier_counts = filtered_df['salary_tier'].value_counts()
        fig_donut = go.Figure(data=[go.Pie(
            labels=tier_counts.index,
            values=tier_counts.values,
            hole=0.52,
            textinfo='label+percent',
            textposition='outside',
            textfont=dict(family=FONT_FAMILY, size=11, color="#e2e8f0"),
            marker=dict(colors=["#5e4fa2", "#3288bd", "#66c2a5", "#fdae61", "#d53e4f"])
        )])
        apply_theme_layout(fig_donut, title_text="Job Postings by Salary Band", height=420, show_legend=False)
        fig_donut.update_layout(margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_donut, use_container_width=True)

    st.markdown("---")

    # Skill Premium Analysis
    st.markdown("<div class='section-title'>💎 The Skill Premium: Monetary Boost by Competency</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-desc'>Calculated as: <i>Median Salary of Jobs Requiring Skill</i> minus <i>Median Salary of Jobs NOT Requiring Skill</i>.</div>", unsafe_allow_html=True)

    premiums = []
    df_with_pay = df.dropna(subset=['monthly_salary'])
    for s in skill_cols:
        with_s = df_with_pay[df_with_pay[s] == 1]['monthly_salary']
        without_s = df_with_pay[df_with_pay[s] == 0]['monthly_salary']
        if len(with_s) >= 4 and len(without_s) >= 4:
            diff = with_s.median() - without_s.median()
            pct = (diff / without_s.median()) * 100
            premiums.append({
                "Skill": s,
                "Sample Size": len(with_s),
                "Median with Skill (₹)": int(with_s.median()),
                "Median without Skill (₹)": int(without_s.median()),
                "Premium (₹)": int(diff),
                "Percentage Boost (%)": round(pct, 1)
            })

    prem_df = pd.DataFrame(premiums).sort_values(by="Premium (₹)", ascending=True)

    # Bar colors: Warm coral/crimson for positive premium, Cool blue/teal for negative premium
    bar_colors = ["#d53e4f" if v >= 0 else "#3288bd" for v in prem_df["Premium (₹)"]]
    label_text = [
        f"<b>+₹{v:,.0f} (+{pct:.1f}%)</b>" if v >= 0 else f"<b>-₹{abs(v):,.0f} ({pct:.1f}%)</b>" 
        for v, pct in zip(prem_df["Premium (₹)"], prem_df["Percentage Boost (%)"])
    ]

    fig_prem = go.Figure(go.Bar(
        x=prem_df["Premium (₹)"],
        y=prem_df["Skill"],
        orientation='h',
        text=label_text,
        textposition='outside',
        textfont=dict(family=FONT_FAMILY, size=11, color="#f8fafc"),
        marker=dict(
            color=bar_colors,
            line=dict(color="rgba(255, 255, 255, 0.15)", width=1)
        )
    ))
    fig_prem.add_vline(x=0, line_dash="dash", line_color="#94a3b8", line_width=1.5)
    apply_theme_layout(fig_prem, title_text="Net Skill Premium (₹/month) Relative to Market Baseline", height=500, show_legend=False)
    fig_prem.update_xaxes(
        title_text="Monthly Wage Premium / Discount (₹)",
        tickprefix="₹",
        range=[min(prem_df["Premium (₹)"]) * 1.35, max(prem_df["Premium (₹)"]) * 1.35]
    )
    st.plotly_chart(fig_prem, use_container_width=True)

    with st.expander("View Full Skill Premium Data Table"):
        st.dataframe(
            prem_df.sort_values(by="Premium (₹)", ascending=False),
            use_container_width=True
        )


# ==============================================================================
# TAB 3: TALENT PIPELINE & QUALIFICATIONS
# ==============================================================================
with tab3:
    st.markdown("<div class='section-title'>🎓 The Education-to-Role Talent Pathway</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-desc'>How do candidates of varying academic qualifications (from 8th Pass to B.Tech Engineers) get funneled into vocational roles? "
        "Which credentials serve as strict gatekeepers, and where is hands-on machinery skill valued above formal degrees?</div>",
        unsafe_allow_html=True
    )

    # 100% Stacked Bar: Roles vs Qualifications
    qual_ct = pd.crosstab(filtered_df['standardized_role'], filtered_df['clean_qualification'], normalize='index') * 100
    
    fig_qual_bar = go.Figure()
    qual_levels = qual_ct.columns.tolist()
    
    for idx, q_lvl in enumerate(qual_levels):
        vals = qual_ct[q_lvl].values
        # Add text labels inside bar if share >= 7%
        bar_texts = [f"<b>{v:.0f}%</b>" if v >= 7.0 else "" for v in vals]
        
        color_segment = COLOR_CATEGORICAL[idx % len(COLOR_CATEGORICAL)]
        fig_qual_bar.add_trace(go.Bar(
            name=q_lvl,
            y=qual_ct.index,
            x=vals,
            orientation='h',
            text=bar_texts,
            textposition='inside',
            textfont=dict(family=FONT_FAMILY, size=11, color="#ffffff"),
            marker=dict(color=color_segment, line=dict(color="rgba(255, 255, 255, 0.2)", width=1))
        ))

    fig_qual_bar.update_layout(barmode='stack')
    apply_theme_layout(fig_qual_bar, title_text="Educational Distribution within Each Job Role (100% Stacked)", height=440)
    fig_qual_bar.update_xaxes(title_text="Share of Roles (%)", range=[0, 100], ticksuffix="%")
    st.plotly_chart(fig_qual_bar, use_container_width=True)

    col_edu1, col_edu2 = st.columns(2)

    with col_edu1:
        sal_qual_df = filtered_df.dropna(subset=['monthly_salary'])
        if len(sal_qual_df) > 0:
            fig_sal_qual = px.box(
                sal_qual_df,
                x='clean_qualification',
                y='monthly_salary',
                color='clean_qualification',
                color_discrete_sequence=COLOR_CATEGORICAL,
                labels={'monthly_salary': 'Monthly Pay (₹)', 'clean_qualification': 'Education Level'}
            )
            apply_theme_layout(fig_sal_qual, title_text="Compensation by Educational Qualification Tier", height=390, show_legend=False)
            fig_sal_qual.update_xaxes(tickangle=-25)
            fig_sal_qual.update_yaxes(tickprefix="₹", tickformat=",.0f")
            st.plotly_chart(fig_sal_qual, use_container_width=True)

    with col_edu2:
        exp_counts = filtered_df['clean_experience'].value_counts()
        fig_exp = go.Figure(data=[go.Pie(
            labels=exp_counts.index,
            values=exp_counts.values,
            hole=0.48,
            textinfo='label+percent',
            textposition='outside',
            textfont=dict(family=FONT_FAMILY, size=11, color="#e2e8f0"),
            marker=dict(colors=["#66c2a5", "#3288bd", "#fdae61", "#d53e4f"])
        )])
        apply_theme_layout(fig_exp, title_text="Experience Requirements across Openings", height=390, show_legend=False)
        fig_exp.update_layout(margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_exp, use_container_width=True)

    # Inclusivity & Gender Preference Profile
    st.markdown("<div class='section-title'>👥 Inclusivity & Gender Preference Profile</div>", unsafe_allow_html=True)
    gender_ct = pd.crosstab(filtered_df['standardized_role'], filtered_df['clean_gender'], normalize='index') * 100
    
    fig_gen = go.Figure()
    gender_colors = {"Any": "#3288bd", "Male": "#f46d43", "Female": "#d53e4f"}
    
    for g_col in gender_ct.columns:
        vals = gender_ct[g_col].values
        bar_texts = [f"<b>{v:.0f}%</b>" if v >= 6.0 else "" for v in vals]
        fig_gen.add_trace(go.Bar(
            name=g_col,
            y=gender_ct.index,
            x=vals,
            orientation='h',
            text=bar_texts,
            textposition='inside',
            textfont=dict(family=FONT_FAMILY, size=11, color="#ffffff"),
            marker=dict(color=gender_colors.get(g_col, "#94a3b8"), line=dict(color="rgba(255, 255, 255, 0.2)", width=1))
        ))

    fig_gen.update_layout(barmode='stack')
    apply_theme_layout(fig_gen, title_text="Gender Hiring Preferences by Functional Role", height=380)
    fig_gen.update_xaxes(title_text="Share (%)", range=[0, 100], ticksuffix="%")
    st.plotly_chart(fig_gen, use_container_width=True)


# ==============================================================================
# TAB 4: GEOGRAPHIC & INDUSTRY ECOSYSTEM
# ==============================================================================
with tab4:
    st.markdown("<div class='section-title'>🗺️ Industrial Clusters & Regional Demand Footprint</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-desc'>Vocational hiring is deeply anchored in geographic manufacturing corridors. "
        "Explore which states drive the bulk of industrial vacancies and how sectors allocate headcounts.</div>",
        unsafe_allow_html=True
    )

    col_geo1, col_geo2 = st.columns([3, 2])

    with col_geo1:
        state_agg = filtered_df.groupby('clean_state').agg(
            Jobs=('job_id', 'count'),
            Vacancies=('vacancy_num', 'sum')
        ).sort_values(by='Vacancies', ascending=True).tail(12).reset_index()

        fig_state = go.Figure(go.Bar(
            x=state_agg['Vacancies'],
            y=state_agg['clean_state'],
            orientation='h',
            text=[f"<b>{v:,.0f}</b>" for v in state_agg['Vacancies']],
            textposition='outside',
            textfont=dict(family=FONT_FAMILY, size=11, color="#f8fafc"),
            marker=dict(
                color=state_agg['Vacancies'],
                colorscale="Spectral_r",
                line=dict(color="rgba(255, 255, 255, 0.2)", width=1)
            )
        ))
        apply_theme_layout(fig_state, title_text="Top Hiring States by Total Job Vacancies (Openings)", height=440, show_legend=False)
        fig_state.update_xaxes(
            title_text="Total Vacancies",
            range=[0, max(state_agg['Vacancies']) * 1.2]
        )
        st.plotly_chart(fig_state, use_container_width=True)

    with col_geo2:
        ind_agg = filtered_df.groupby('clean_industry')['vacancy_num'].sum().reset_index()
        fig_ind = px.treemap(
            ind_agg,
            path=['clean_industry'],
            values='vacancy_num',
            color='vacancy_num',
            color_continuous_scale="Spectral_r"
        )
        fig_ind.update_traces(
            textinfo="label+value+percent root",
            textfont=dict(family=FONT_FAMILY, size=13, color="#ffffff")
        )
        apply_theme_layout(fig_ind, title_text="Vacancies by Industry Sector", height=440, show_legend=False)
        fig_ind.update_layout(margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig_ind, use_container_width=True)

    st.markdown("---")

    # Top Employers / Clients
    st.markdown("<div class='section-title'>🏭 Top Hiring Employers & Organizations</div>", unsafe_allow_html=True)
    top_clients = filtered_df.groupby('client_name').agg(
        Postings=('job_id', 'count'),
        Vacancies=('vacancy_num', 'sum')
    ).sort_values(by='Vacancies', ascending=True).tail(15).reset_index()

    fig_clients = go.Figure(go.Bar(
        x=top_clients['Vacancies'],
        y=top_clients['client_name'],
        orientation='h',
        text=[f"<b>{v:,.0f} openings</b>" for v in top_clients['Vacancies']],
        textposition='outside',
        textfont=dict(family=FONT_FAMILY, size=11, color="#f8fafc"),
        marker=dict(
            color=top_clients['Vacancies'],
            colorscale="Spectral_r",
            line=dict(color="rgba(255, 255, 255, 0.2)", width=1)
        )
    ))
    apply_theme_layout(fig_clients, title_text="Top 15 Employers by Aggregate Open Vacancies", height=480, show_legend=False)
    fig_clients.update_xaxes(
        title_text="Total Vacancies",
        range=[0, max(top_clients['Vacancies']) * 1.25]
    )
    st.plotly_chart(fig_clients, use_container_width=True)


# ==============================================================================
# TAB 5: CAREER & SKILL FIT MATCHER
# ==============================================================================
with tab5:
    st.markdown("<div class='section-title'>🎯 Realtime Career & Skill Fit Matcher</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-desc'>Select a candidate's background to calculate an "
        "affinity match score across all industrial job roles. Inspect expected pay ranges, open openings, and recommended skills to acquire.</div>",
        unsafe_allow_html=True
    )

    col_m1, col_m2 = st.columns([1, 2])

    with col_m1:
        user_qual = st.selectbox("Candidate Education Level:", options=all_quals)
        user_skills = st.multiselect(
            "Select Candidate's Skills / Competencies:",
            options=skill_cols,
            default=["CNC Operation", "Vernier Caliper & Micrometer"]
        )
        min_match_thresh = st.slider("Minimum Match Threshold (%):", min_value=10, max_value=80, value=25, step=5)

    with col_m2:
        role_matches = []
        user_vector = np.array([1 if s in user_skills else 0 for s in skill_cols])

        for r_name in df['standardized_role'].unique():
            sub = df[df['standardized_role'] == r_name]
            role_vector = sub[skill_cols].mean().values
            
            if user_vector.sum() == 0:
                similarity = 0.0
            else:
                intersection = np.sum(np.minimum(user_vector, role_vector))
                union = np.sum(np.maximum(user_vector, role_vector))
                similarity = (intersection / max(1e-6, union)) * 100

            edu_share = (sub['clean_qualification'] == user_qual).mean() * 100
            
            role_top_skills = sub[skill_cols].mean().sort_values(ascending=False).head(5)
            missing_skills = [s for s in role_top_skills.index if s not in user_skills and role_top_skills[s] > 0.05]

            med_p = sub['monthly_salary'].median()
            pay_str = f"₹{int(med_p):,}/mo" if not np.isnan(med_p) else "Negotiable"

            role_matches.append({
                "Job Role": r_name,
                "Skill Match Score": round(similarity, 1),
                "Education Fit": f"{edu_share:.0f}% of role has this degree",
                "Open Vacancies": int(sub['vacancy_num'].sum()),
                "Median Salary": pay_str,
                "Key Skills to Acquire": missing_skills[:3]
            })

        match_df = pd.DataFrame(role_matches).sort_values(by="Skill Match Score", ascending=False)
        qualified_matches = match_df[match_df['Skill Match Score'] >= min_match_thresh]

        if len(qualified_matches) > 0:
            st.markdown(f"### Found {len(qualified_matches)} Recommended Roles")
            for idx, r in qualified_matches.iterrows():
                missing_pills = " ".join([f"<span class='skill-pill'>{s}</span>" for s in r['Key Skills to Acquire']])
                if not missing_pills:
                    missing_pills = "<span class='badge-match'>All core skills matched!</span>"
                    
                st.markdown(f"""
                <div class="kpi-card" style="margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin: 0; color: #f8fafc; font-weight: 700;">{r['Job Role']}</h4>
                        <span class="badge-match">{r['Skill Match Score']}% Match</span>
                    </div>
                    <div style="margin: 8px 0; color: #cbd5e1; font-size: 0.88rem;">
                        <b>Vacancies:</b> <span style="color: #fdae61; font-weight: 600;">{r['Open Vacancies']:,}</span> &nbsp;|&nbsp; 
                        <b>Median Pay:</b> <span style="color: #66c2a5; font-weight: 600;">{r['Median Salary']}</span> &nbsp;|&nbsp; 
                        <b>Education Fit:</b> {r['Education Fit']}
                    </div>
                    <div style="margin-top: 6px;">
                        <span style="color: #94a3b8; font-size: 0.82rem; font-weight: 600;">Recommended Skills to Add: </span>
                        {missing_pills}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No job roles met the threshold. Try adding more skills or lowering the match threshold slider.")


# ==============================================================================
# TAB 6: DATA EXPLORER & EXPORT
# ==============================================================================
with tab6:
    st.markdown("<div class='section-title'>📋 Raw Records & Analytical Export</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-desc'>Filter, inspect, and export cleaned job postings and their engineered attributes.</div>", unsafe_allow_html=True)

    view_cols = [
        'job_id', 'job_name', 'standardized_role', 'client_name', 'clean_state', 
        'clean_qualification', 'monthly_salary', 'vacancy_num', 'clean_experience', 
        'clean_gender', 'total_skills_tagged'
    ]
    
    st.dataframe(
        filtered_df[view_cols],
        use_container_width=True,
        hide_index=True
    )

    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        csv_filtered = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Data (CSV)",
            data=csv_filtered,
            file_name="filtered_jobs_analysis.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col_dl2:
        role_skill_summary = filtered_df.groupby('standardized_role')[skill_cols].mean() * 100
        matrix_csv = role_skill_summary.round(2).to_csv().encode('utf-8')
        st.download_button(
            label="📥 Download Role-Skill Affinity Matrix (CSV)",
            data=matrix_csv,
            file_name="role_skill_affinity_matrix.csv",
            mime="text/csv",
            use_container_width=True
        )

# Footer
st.markdown("---")
st.markdown(
    f"<div style='text-align: center; color: #64748b; font-family: {FONT_FAMILY}; font-size: 0.82rem; padding: 12px;'>"
    "Job Data Analysis & Skill Intelligence Engine • Styled with High-Contrast Typography & Spectral Palette Theme"
    "</div>",
    unsafe_allow_html=True
)
