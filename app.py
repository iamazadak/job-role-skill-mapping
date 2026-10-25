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

# Custom Styling for Premium Look
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background-color: #0e1117;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* KPI Card styling */
    .kpi-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 18px 22px;
        margin-bottom: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        backdrop-filter: blur(10px);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.5);
    }
    .kpi-title {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .kpi-value {
        color: #f8fafc;
        font-size: 1.85rem;
        font-weight: 700;
        margin: 0;
        line-height: 1.2;
    }
    .kpi-subtitle {
        color: #64748b;
        font-size: 0.78rem;
        margin-top: 4px;
    }
    
    /* Section Headers */
    .section-title {
        font-size: 1.35rem;
        font-weight: 700;
        color: #f1f5f9;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .section-desc {
        color: #94a3b8;
        font-size: 0.92rem;
        margin-bottom: 1.25rem;
        line-height: 1.5;
    }
    
    /* Pill Tags */
    .skill-pill {
        display: inline-block;
        background: rgba(99, 102, 241, 0.15);
        color: #818cf8;
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 20px;
        padding: 3px 10px;
        font-size: 0.8rem;
        font-weight: 500;
        margin: 3px 4px 3px 0;
    }
    .badge-high {
        background: rgba(34, 197, 94, 0.15);
        color: #4ade80;
        border: 1px solid rgba(34, 197, 94, 0.3);
        border-radius: 12px;
        padding: 2px 8px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: pre-wrap;
        border-radius: 8px 8px 0px 0px;
        padding-top: 10px;
        padding-bottom: 10px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

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
st.sidebar.image("https://img.icons8.com/fluency/96/briefcase.png", width=64)
st.sidebar.title("Filter & Explore")
st.sidebar.caption("Job Data Intelligence Engine")

# 1. Standardized Role Multi-select
all_roles = sorted(df['standardized_role'].unique())
selected_roles = st.sidebar.multiselect(
    "Job Role / Function:",
    options=all_roles,
    default=all_roles
)

# 2. State Multi-select
all_states = sorted([s for s in df['clean_state'].unique() if s != "Not Specified"])
selected_states = st.sidebar.multiselect(
    "State / Region:",
    options=all_states,
    default=[]
)

# 3. Qualification Multi-select
all_quals = sorted(df['clean_qualification'].unique())
selected_quals = st.sidebar.multiselect(
    "Education Tier:",
    options=all_quals,
    default=[]
)

# 4. Industry Sector
all_industries = sorted(df['clean_industry'].unique())
selected_industries = st.sidebar.multiselect(
    "Industry Sector:",
    options=all_industries,
    default=[]
)

# 5. Gender Preference
gender_options = ["All", "Any", "Male", "Female"]
selected_gender = st.sidebar.selectbox("Gender Preference:", gender_options, index=0)

# 6. Salary Filter
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
st.sidebar.markdown(f"**Showing:** {len(filtered_df):,} of {len(df):,} jobs")
st.sidebar.markdown(f"**Total Vacancies:** {filtered_df['vacancy_num'].sum():,}")

# Reset Filters Hint
if st.sidebar.button("Reset All Filters", use_container_width=True):
    st.rerun()

# ==========================================
# MAIN DASHBOARD HEADER & KPI CARDS
# ==========================================
st.markdown("<h1 style='margin-bottom: 4px;'>🎯 Industrial & Technical Job Market Intelligence</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #94a3b8; font-size: 1.05rem; margin-bottom: 1.5rem;'>Deep Data Analysis: <b>Which Job Role Needs Which Skill Sets?</b>, Compensation Benchmarks & Talent Pipelines</p>", unsafe_allow_html=True)

# Compute Top Metrics
total_postings = len(filtered_df)
total_vacancies = filtered_df['vacancy_num'].sum()
median_sal = filtered_df['monthly_salary'].dropna().median()
sal_display = f"₹{int(median_sal):,}/mo" if not np.isnan(median_sal) else "N/A"
unique_employers = filtered_df['client_name'].nunique()

# Find most demanded skill
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
        <div class="kpi-subtitle">{total_postings/len(df)*100:.1f}% of total dataset</div>
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
        <div class="kpi-subtitle">Benchmark monthly rate</div>
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
    st.warning("No job postings match your selected filters. Please expand your filter criteria in the sidebar.")
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
        "<div class='section-desc'>Every functional job role has a distinct technological footprint. "
        "Below, explore the <b>Role vs. Skill Affinity Matrix</b> (percentage of job listings requiring each skill), "
        "drill down into individual job profiles, and analyze which skills naturally bundle together.</div>",
        unsafe_allow_html=True
    )
    
    # 1. Interactive Heatmap
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
        z_title = "% Demand"
        text_template = "%{z:.1f}%"
    else:
        matrix = role_group[active_skills].sum()
        z_title = "Job Count"
        text_template = "%{z}"

    fig_heat = px.imshow(
        matrix.T,
        labels=dict(x="Standardized Job Role", y="Skill Requirement", color=z_title),
        x=matrix.index,
        y=matrix.columns,
        color_continuous_scale="Plasma",
        aspect="auto"
    )
    fig_heat.update_traces(text=matrix.T.values, texttemplate=text_template)
    fig_heat.update_layout(
        title="<b>Job Role vs. Skill Matrix Heatmap</b> (Affinity & Co-occurrence)",
        height=max(450, len(active_skills) * 26 + 120),
        margin=dict(l=20, r=20, t=50, b=40),
        xaxis_tickangle=-30
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
        <div class="kpi-card" style="margin-top: 10px;">
            <div class="kpi-title">Role Profile</div>
            <div class="kpi-value" style="font-size: 1.4rem;">{selected_role_drill}</div>
            <p style="margin: 8px 0 4px 0; color: #cbd5e1; font-size: 0.85rem;">
                <b>Total Listings:</b> {len(role_subset):,}<br>
                <b>Total Vacancies:</b> {role_subset['vacancy_num'].sum():,}<br>
                <b>Median Pay:</b> ₹{role_subset['monthly_salary'].median():,.0f}/mo<br>
                <b>Primary Education:</b> {role_subset['clean_qualification'].mode().iloc[0] if len(role_subset)>0 else 'N/A'}<br>
                <b>Top Hiring Sector:</b> {role_subset['clean_industry'].mode().iloc[0] if len(role_subset)>0 else 'N/A'}
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_dd2:
        role_skills_mean = (role_subset[skill_cols].mean() * 100).sort_values(ascending=True)
        # Filter skills with > 0% demand
        role_skills_nonzero = role_skills_mean[role_skills_mean > 0]
        if len(role_skills_nonzero) == 0:
            role_skills_nonzero = role_skills_mean.tail(8)

        fig_role_bar = px.bar(
            x=role_skills_nonzero.values,
            y=role_skills_nonzero.index,
            orientation='h',
            labels={'x': 'Demand Percentage (% of postings)', 'y': 'Skill'},
            color=role_skills_nonzero.values,
            color_continuous_scale="Blues",
            title=f"<b>Core Skill Requirements for: {selected_role_drill}</b>"
        )
        fig_role_bar.update_layout(
            margin=dict(l=20, r=20, t=40, b=30),
            height=340,
            showlegend=False
        )
        st.plotly_chart(fig_role_bar, use_container_width=True)

    # 3. Radar Chart Across Skill Categories
    st.markdown("<div class='section-title'>🕸️ Skill Category Coverage Radar</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-desc'>Compare how different job roles require breadth across the 5 primary skill domains.</div>", unsafe_allow_html=True)

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

        for r_name in radar_roles:
            r_df = df[df['standardized_role'] == r_name]
            scores = []
            for cat_name, cat_skills in skill_categories.items():
                # Average % demand for skills in this category
                val = (r_df[cat_skills].mean().mean()) * 100
                scores.append(round(val, 1))
            
            # Close the polygon loop
            scores_closed = scores + [scores[0]]
            cats_closed = radar_categories + [radar_categories[0]]
            
            fig_radar.add_trace(go.Scatterpolar(
                r=scores_closed,
                theta=cats_closed,
                fill='toself',
                name=r_name
            ))

        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, max(45, max(scores_closed) + 10)])
            ),
            showlegend=True,
            title="<b>Multidimensional Skill Portfolio by Role</b>",
            margin=dict(l=30, r=30, t=40, b=30),
            height=460
        )
        st.plotly_chart(fig_radar, use_container_width=True)


# ==============================================================================
# TAB 2: COMPENSATION & SKILL PREMIUMS
# ==============================================================================
with tab2:
    st.markdown("<div class='section-title'>💰 Compensation Benchmarks & The Skill Premium</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-desc'>Does investing in specialized skills translate to tangible wage increases? "
        "Here we examine the median monthly pay per role, pay distributions (25th-75th percentiles), and the exact <b>monetary premium</b> attached to each technical competency.</div>",
        unsafe_allow_html=True
    )

    col_sal1, col_sal2 = st.columns([3, 2])

    with col_sal1:
        # Box plot of salary by role
        sal_clean_df = filtered_df.dropna(subset=['monthly_salary'])
        if len(sal_clean_df) > 0:
            role_order = sal_clean_df.groupby('standardized_role')['monthly_salary'].median().sort_values(ascending=False).index
            fig_box = px.box(
                sal_clean_df,
                x='monthly_salary',
                y='standardized_role',
                category_orders={'standardized_role': role_order},
                color='standardized_role',
                labels={'monthly_salary': 'Monthly Stipend / Salary (₹)', 'standardized_role': 'Job Role'},
                title="<b>Monthly Compensation Distribution by Job Role</b>"
            )
            fig_box.update_layout(
                showlegend=False,
                margin=dict(l=20, r=20, t=40, b=30),
                height=420
            )
            st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.info("No salary data available for the current filter selection.")

    with col_sal2:
        # Salary tier donut breakdown
        tier_counts = filtered_df['salary_tier'].value_counts()
        fig_donut = px.pie(
            values=tier_counts.values,
            names=tier_counts.index,
            hole=0.45,
            title="<b>Job Listings by Salary Band</b>",
            color_discrete_sequence=px.colors.sequential.Teal
        )
        fig_donut.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=420)
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

    fig_prem = px.bar(
        prem_df,
        x="Premium (₹)",
        y="Skill",
        orientation='h',
        color="Premium (₹)",
        color_continuous_scale="Temps",
        labels={"Premium (₹)": "Monthly Salary Difference (₹)"},
        title="<b>Net Skill Premium (₹/month) Relative to Market Baseline</b>"
    )
    fig_prem.add_vline(x=0, line_dash="dash", line_color="#94a3b8")
    fig_prem.update_layout(height=480, margin=dict(l=20, r=20, t=40, b=30))
    st.plotly_chart(fig_prem, use_container_width=True)

    # Detailed Table
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
        "Which credentials serve as strict gatekeepers, and where is hands-on skill valued above formal degrees?</div>",
        unsafe_allow_html=True
    )

    # 1. 100% Stacked Bar: Roles vs Qualifications
    qual_ct = pd.crosstab(filtered_df['standardized_role'], filtered_df['clean_qualification'], normalize='index') * 100
    qual_ct_df = qual_ct.reset_index().melt(id_vars='standardized_role', value_name='Percentage', var_name='Education Level')

    fig_qual_bar = px.bar(
        qual_ct_df,
        x="Percentage",
        y="standardized_role",
        color="Education Level",
        orientation='h',
        title="<b>Educational Distribution within Each Job Role (100% Stacked)</b>",
        color_discrete_sequence=px.colors.qualitative.Bold,
        labels={"Percentage": "Share of Roles (%)", "standardized_role": "Job Role"}
    )
    fig_qual_bar.update_layout(height=420, margin=dict(l=20, r=20, t=40, b=30))
    st.plotly_chart(fig_qual_bar, use_container_width=True)

    col_edu1, col_edu2 = st.columns(2)

    with col_edu1:
        # Salary by Qualification Tier
        sal_qual_df = filtered_df.dropna(subset=['monthly_salary'])
        if len(sal_qual_df) > 0:
            fig_sal_qual = px.box(
                sal_qual_df,
                x='clean_qualification',
                y='monthly_salary',
                color='clean_qualification',
                title="<b>Compensation by Educational Qualification Tier</b>",
                labels={'monthly_salary': 'Monthly Pay (₹)', 'clean_qualification': 'Education Level'}
            )
            fig_sal_qual.update_layout(showlegend=False, xaxis_tickangle=-30, height=380, margin=dict(l=20, r=20, t=40, b=30))
            st.plotly_chart(fig_sal_qual, use_container_width=True)

    with col_edu2:
        # Experience Requirement Breakdown
        exp_counts = filtered_df['clean_experience'].value_counts().reset_index()
        exp_counts.columns = ['Experience Tier', 'Job Count']
        fig_exp = px.pie(
            exp_counts,
            values='Job Count',
            names='Experience Tier',
            hole=0.4,
            title="<b>Experience Requirements across Openings</b>",
            color_discrete_sequence=px.colors.sequential.Aggrnyl
        )
        fig_exp.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_exp, use_container_width=True)

    # Demographic & Inclusivity Insight
    st.markdown("<div class='section-title'>👥 Inclusivity & Gender Preference Profile</div>", unsafe_allow_html=True)
    gender_ct = pd.crosstab(filtered_df['standardized_role'], filtered_df['clean_gender'], normalize='index') * 100
    gender_ct_df = gender_ct.reset_index().melt(id_vars='standardized_role', value_name='Percentage', var_name='Gender Preference')
    
    fig_gen = px.bar(
        gender_ct_df,
        x="Percentage",
        y="standardized_role",
        color="Gender Preference",
        orientation='h',
        color_discrete_map={"Any": "#6366f1", "Male": "#3b82f6", "Female": "#ec4899"},
        title="<b>Gender Hiring Preferences by Functional Role</b>"
    )
    fig_gen.update_layout(height=360, margin=dict(l=20, r=20, t=40, b=30))
    st.plotly_chart(fig_gen, use_container_width=True)


# ==============================================================================
# TAB 4: GEOGRAPHIC & INDUSTRY ECOSYSTEM
# ==============================================================================
with tab4:
    st.markdown("<div class='section-title'>🗺️ Industrial Clusters & Regional Demand Footprint</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-desc'>Vocational and technical hiring is deeply anchored in geographic industrial clusters. "
        "Explore which states drive the bulk of manufacturing vacancies and how sectors allocate headcounts.</div>",
        unsafe_allow_html=True
    )

    col_geo1, col_geo2 = st.columns([3, 2])

    with col_geo1:
        # Vacancies by State
        state_agg = filtered_df.groupby('clean_state').agg(
            Jobs=('job_id', 'count'),
            Vacancies=('vacancy_num', 'sum')
        ).sort_values(by='Vacancies', ascending=False).head(12).reset_index()

        fig_state = px.bar(
            state_agg,
            x='Vacancies',
            y='clean_state',
            orientation='h',
            color='Jobs',
            color_continuous_scale="Viridis",
            title="<b>Top Hiring States by Total Job Vacancies (Openings)</b>",
            labels={'clean_state': 'State', 'Vacancies': 'Total Vacancies'}
        )
        fig_state.update_layout(yaxis=dict(autorange="reversed"), height=420, margin=dict(l=20, r=20, t=40, b=30))
        st.plotly_chart(fig_state, use_container_width=True)

    with col_geo2:
        # Industry Sector Distribution
        ind_agg = filtered_df.groupby('clean_industry')['vacancy_num'].sum().reset_index()
        fig_ind = px.treemap(
            ind_agg,
            path=['clean_industry'],
            values='vacancy_num',
            title="<b>Vacancies by Industry Sector</b>",
            color='vacancy_num',
            color_continuous_scale="Blues"
        )
        fig_ind.update_layout(height=420, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_ind, use_container_width=True)

    st.markdown("---")

    # Top Employers / Clients
    st.markdown("<div class='section-title'>🏭 Top Hiring Employers & Organizations</div>", unsafe_allow_html=True)
    top_clients = filtered_df.groupby('client_name').agg(
        Postings=('job_id', 'count'),
        Vacancies=('vacancy_num', 'sum')
    ).sort_values(by='Vacancies', ascending=False).head(15).reset_index()

    fig_clients = px.bar(
        top_clients,
        x='Vacancies',
        y='client_name',
        orientation='h',
        color='Postings',
        color_continuous_scale="Sunset",
        title="<b>Top 15 Employers by Aggregate Open Vacancies</b>",
        labels={'client_name': 'Employer / Client', 'Vacancies': 'Total Vacancies'}
    )
    fig_clients.update_layout(yaxis=dict(autorange="reversed"), height=450, margin=dict(l=20, r=20, t=40, b=30))
    st.plotly_chart(fig_clients, use_container_width=True)


# ==============================================================================
# TAB 5: CAREER & SKILL FIT MATCHER
# ==============================================================================
with tab5:
    st.markdown("<div class='section-title'>🎯 Realtime Career & Skill Fit Matcher</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-desc'>Select a candidate's background (education level and possessed competencies) to calculate an "
        "affinity match score across all 10 industrial job roles. See expected pay ranges, open vacancies, and skill gap recommendations.</div>",
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
        # Match Calculation
        role_matches = []
        user_vector = np.array([1 if s in user_skills else 0 for s in skill_cols])

        for r_name in df['standardized_role'].unique():
            sub = df[df['standardized_role'] == r_name]
            # Role skill profile (mean affinity)
            role_vector = sub[skill_cols].mean().values
            
            # Weighted Jaccard / Overlap similarity
            if user_vector.sum() == 0:
                similarity = 0.0
            else:
                intersection = np.sum(np.minimum(user_vector, role_vector))
                union = np.sum(np.maximum(user_vector, role_vector))
                similarity = (intersection / max(1e-6, union)) * 100

            # Education match boost
            edu_share = (sub['clean_qualification'] == user_qual).mean() * 100
            
            # Missing top skills for this role
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
                    missing_pills = "<span class='badge-high'>All core skills matched!</span>"
                    
                st.markdown(f"""
                <div class="kpi-card" style="margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin: 0; color: #f8fafc;">{r['Job Role']}</h4>
                        <span class="badge-high" style="font-size: 0.85rem; padding: 4px 10px;">{r['Skill Match Score']}% Match</span>
                    </div>
                    <div style="margin: 8px 0; color: #94a3b8; font-size: 0.85rem;">
                        <b>Vacancies:</b> {r['Open Vacancies']:,} &nbsp;|&nbsp; 
                        <b>Median Pay:</b> {r['Median Salary']} &nbsp;|&nbsp; 
                        <b>Education Fit:</b> {r['Education Fit']}
                    </div>
                    <div style="margin-top: 6px;">
                        <span style="color: #64748b; font-size: 0.8rem; font-weight: 600;">Recommended Skills to Add: </span>
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

    # Column selector
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
        # Download role-skill matrix summary
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
    "<div style='text-align: center; color: #64748b; font-size: 0.82rem; padding: 12px;'>"
    "Job Data Analysis & Skill Intelligence Engine • Built with Streamlit, Plotly & Advanced Feature Engineering"
    "</div>",
    unsafe_allow_html=True
)
