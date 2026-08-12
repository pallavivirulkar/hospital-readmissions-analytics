"""
Hospital Readmissions & Patient Flow Analytics — Streamlit Dashboard
Author: Pallavi Virulkar

Data source: UCI Diabetes 130-US hospitals (1999-2008), cleaned + feature-engineered
via Python/SQL pipeline (see /python and /sql folders in the main project).

Run locally:
    pip install -r requirements.txt
    streamlit run dashboard.py
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ----------------------------------------------------------------------------
# PAGE CONFIG + GLOBAL STYLE
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Hospital Readmissions Analytics",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

PRIMARY = "#2563EB"      # blue
DANGER = "#DC2626"       # red
SUCCESS = "#059669"      # green
WARNING = "#D97706"      # amber
MUTED = "#64748B"        # slate
BG_CARD = "#FFFFFF"
PALETTE = ["#2563EB", "#0891B2", "#7C3AED", "#DB2777", "#D97706", "#059669", "#DC2626", "#4F46E5"]

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    .main {
        background-color: #F8FAFC;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1300px;
    }
    /* KPI card */
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 20px 22px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        height: 100%;
    }
    .kpi-label {
        font-size: 13px;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 30px;
        font-weight: 800;
        color: #0F172A;
        line-height: 1.2;
    }
    .kpi-sub {
        font-size: 12.5px;
        color: #94A3B8;
        margin-top: 4px;
    }
    .kpi-delta-up { color: #DC2626; font-weight: 600; font-size: 12.5px; }
    .kpi-delta-down { color: #059669; font-weight: 600; font-size: 12.5px; }

    .section-title {
        font-size: 20px;
        font-weight: 700;
        color: #0F172A;
        margin-top: 6px;
        margin-bottom: 2px;
    }
    .section-sub {
        font-size: 13.5px;
        color: #64748B;
        margin-bottom: 14px;
    }
    .insight-box {
        background: #EFF6FF;
        border-left: 4px solid #2563EB;
        border-radius: 8px;
        padding: 14px 18px;
        font-size: 14px;
        color: #1E3A5F;
        margin: 10px 0 18px 0;
    }
    .insight-box b { color: #0F172A; }

    [data-testid="stSidebar"] {
        background-color: #0F172A;
    }
    [data-testid="stSidebar"] * {
        color: #E2E8F0 !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        font-size: 14.5px;
    }

    hr {
        margin: 8px 0 18px 0;
        border-color: #E2E8F0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------------
# DATA LOADING
# ----------------------------------------------------------------------------
@st.cache_data
def load_data():
    fact = pd.read_csv("data/fact_encounters.csv")
    dim_patient = pd.read_csv("data/dim_patient.csv")
    dim_adm_type = pd.read_csv("data/dim_admission_type.csv")
    dim_disch = pd.read_csv("data/dim_discharge_disposition.csv")
    dim_adm_src = pd.read_csv("data/dim_admission_source.csv")

    df = fact.merge(dim_patient, on="patient_nbr", how="left")
    df = df.merge(
        dim_adm_type.rename(columns={"description": "admission_type"}),
        on="admission_type_id", how="left",
    )
    df = df.merge(
        dim_disch.rename(columns={"description": "discharge_disposition"}),
        on="discharge_disposition_id", how="left",
    )
    df = df.merge(
        dim_adm_src.rename(columns={"description": "admission_source"}),
        on="admission_source_id", how="left",
    )

    # Calculated fields (mirrors Tableau calculated fields)
    df["repeat_patient"] = df["total_encounters"].apply(
        lambda x: "Repeat Patient" if x > 1 else "First-Time Patient"
    )
    df["high_risk_patient"] = df["number_inpatient"].apply(
        lambda x: "High Risk (Prior Inpatient Stay)" if x >= 1 else "Standard Risk"
    )
    df["financial_risk"] = df["readmitted_flag"] * 16300

    # Age sort order
    age_order = [f"[{i}-{i+10})" for i in range(0, 100, 10)]
    df["age"] = pd.Categorical(df["age"], categories=age_order, ordered=True)

    return df


df = load_data()
COST_PER_READMISSION = 16300  # HCUP/AHRQ 2020 estimate, all-cause 30-day adult readmission


def kpi_card(label, value, sub=""):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section(title, sub=""):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if sub:
        st.markdown(f'<div class="section-sub">{sub}</div>', unsafe_allow_html=True)


def insight(text):
    st.markdown(f'<div class="insight-box">💡 {text}</div>', unsafe_allow_html=True)


PLOTLY_LAYOUT = dict(
    font=dict(family="Inter, sans-serif", size=13, color="#334155"),
    plot_bgcolor="white",
    paper_bgcolor="white",
    margin=dict(l=10, r=10, t=40, b=10),
    title_font=dict(size=15, color="#0F172A"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)

# ----------------------------------------------------------------------------
# SIDEBAR NAV
# ----------------------------------------------------------------------------
st.sidebar.markdown("## 🏥 Hospital Analytics")
st.sidebar.caption("Readmissions & Patient Flow · UCI Diabetes 130-US Hospitals")
page = st.sidebar.radio(
    "Navigate",
    [
        "📊 Executive Overview",
        "🎯 Readmission Drivers",
        "🔁 Patient Flow",
        "💰 Financial Impact",
        "🧮 What-If Simulator",
    ],
    label_visibility="collapsed",
)
st.sidebar.markdown("---")
st.sidebar.caption(f"Dataset: **{len(df):,}** encounters · **{df['patient_nbr'].nunique():,}** unique patients")
st.sidebar.caption("Cost assumption: $16,300 per 30-day readmission (HCUP/AHRQ, 2020)")


# ----------------------------------------------------------------------------
# PAGE 1: EXECUTIVE OVERVIEW
# ----------------------------------------------------------------------------
if page == "📊 Executive Overview":
    st.title("Executive Overview")
    st.caption("High-level KPIs across all encounters, 1999–2008")

    total_enc = len(df)
    total_patients = df["patient_nbr"].nunique()
    readmit_rate = df["readmitted_flag"].mean() * 100
    total_risk = df["financial_risk"].sum()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Total Encounters", f"{total_enc:,}", "Hospital visits recorded")
    with c2:
        kpi_card("Unique Patients", f"{total_patients:,}", "Distinct patient_nbr")
    with c3:
        kpi_card("30-Day Readmission Rate", f"{readmit_rate:.2f}%", "Share of encounters readmitted <30 days")
    with c4:
        kpi_card("Est. Financial Risk", f"${total_risk/1e6:,.1f}M", f"${total_risk:,.0f} total exposure")

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([1.3, 1])
    with col1:
        section("Readmission Rate by Age Group", "Where readmission risk concentrates across the patient lifespan")
        by_age = df.groupby("age", observed=True)["readmitted_flag"].mean().reset_index()
        by_age["rate"] = by_age["readmitted_flag"] * 100
        fig = px.bar(by_age, x="age", y="rate", text=by_age["rate"].round(1),
                     color_discrete_sequence=[PRIMARY])
        fig.update_traces(texttemplate="%{text}%", textposition="outside", marker_line_width=0)
        fig.update_layout(**PLOTLY_LAYOUT, xaxis_title="Age Group", yaxis_title="Readmission Rate (%)",
                           height=380, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        insight("Readmission risk <b>peaks at ages 20–30 (~14.3%)</b> rather than rising steadily with age — "
                "a non-obvious pattern worth flagging to clinical teams.")

    with col2:
        section("Readmission Outcome Mix", "NO / >30 days / <30 days")
        outcome_counts = df["readmitted"].value_counts().reindex(["NO", ">30", "<30"]).reset_index()
        outcome_counts.columns = ["outcome", "count"]
        labels = {"NO": "Not Readmitted", ">30": "Readmitted >30 days", "<30": "Readmitted <30 days (HRRP)"}
        outcome_counts["label"] = outcome_counts["outcome"].map(labels)
        fig = px.pie(outcome_counts, names="label", values="count", hole=0.55,
                     color_discrete_sequence=[SUCCESS, WARNING, DANGER])
        fig.update_traces(textinfo="percent+label", textfont_size=12)
        fig.update_layout(**PLOTLY_LAYOUT, height=380, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    section("Repeat vs. First-Time Patients — Risk Concentration", "")
    grp = df.groupby("repeat_patient", observed=True).agg(
        encounters=("encounter_id", "count"),
        readmit_rate=("readmitted_flag", "mean"),
        risk=("financial_risk", "sum"),
    ).reset_index()
    grp["readmit_rate"] = (grp["readmit_rate"] * 100).round(2)

    c1, c2, c3 = st.columns(3)
    for i, row in grp.iterrows():
        with [c1, c2][i % 2]:
            kpi_card(row["repeat_patient"], f"{row['readmit_rate']}% readmit rate",
                      f"${row['risk']:,.0f} financial risk · {row['encounters']:,} encounters")
    with c3:
        pct_risk = grp.loc[grp["repeat_patient"] == "Repeat Patient", "risk"].sum() / total_risk * 100
        kpi_card("Risk Concentration", f"{pct_risk:.0f}%", "of total financial risk sits with repeat patients")


# ----------------------------------------------------------------------------
# PAGE 2: READMISSION DRIVERS
# ----------------------------------------------------------------------------
elif page == "🎯 Readmission Drivers":
    st.title("Readmission Drivers")
    st.caption("Which patient and encounter characteristics correlate with 30-day readmission")

    col1, col2 = st.columns(2)
    with col1:
        section("By Admission Type")
        g = df.groupby("admission_type", observed=True)["readmitted_flag"].agg(["mean", "count"]).reset_index()
        g = g[g["count"] >= 50]
        g["rate"] = (g["mean"] * 100).round(2)
        g = g.sort_values("rate", ascending=True)
        fig = px.bar(g, x="rate", y="admission_type", orientation="h", text=g["rate"],
                     color_discrete_sequence=[PRIMARY])
        fig.update_traces(texttemplate="%{text}%", textposition="outside")
        fig.update_layout(**PLOTLY_LAYOUT, xaxis_title="Readmission Rate (%)", yaxis_title="",
                           height=420, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section("By Race")
        g = df.groupby("race", observed=True)["readmitted_flag"].agg(["mean", "count"]).reset_index()
        g = g[g["count"] >= 50]
        g["rate"] = (g["mean"] * 100).round(2)
        g = g.sort_values("rate", ascending=True)
        fig = px.bar(g, x="rate", y="race", orientation="h", text=g["rate"],
                     color_discrete_sequence=["#7C3AED"])
        fig.update_traces(texttemplate="%{text}%", textposition="outside")
        fig.update_layout(**PLOTLY_LAYOUT, xaxis_title="Readmission Rate (%)", yaxis_title="",
                           height=420, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    section("By Discharge Disposition", "Top 10 dispositions by encounter volume")
    g = df.groupby("discharge_disposition", observed=True)["readmitted_flag"].agg(["mean", "count"]).reset_index()
    g = g.sort_values("count", ascending=False).head(10)
    g["rate"] = (g["mean"] * 100).round(2)
    g = g.sort_values("rate", ascending=True)
    fig = px.bar(g, x="rate", y="discharge_disposition", orientation="h", text=g["rate"],
                 color_discrete_sequence=[WARNING])
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(**PLOTLY_LAYOUT, xaxis_title="Readmission Rate (%)", yaxis_title="",
                       height=420, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    section("By Number of Prior Inpatient Stays", "Readmission rate climbs sharply with prior inpatient history")
    g = df.groupby("number_inpatient")["readmitted_flag"].agg(["mean", "count"]).reset_index()
    g = g[g["number_inpatient"] <= 10]
    g["rate"] = (g["mean"] * 100).round(2)
    fig = px.line(g, x="number_inpatient", y="rate", markers=True,
                  color_discrete_sequence=[DANGER])
    fig.update_layout(**PLOTLY_LAYOUT, xaxis_title="Prior Inpatient Stays", yaxis_title="Readmission Rate (%)",
                       height=350, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    insight("Patients with <b>1+ prior inpatient stays</b> show a markedly higher readmission rate — "
            "this is the single strongest predictor in the dataset, and the basis for the High-Risk flag.")


# ----------------------------------------------------------------------------
# PAGE 3: PATIENT FLOW
# ----------------------------------------------------------------------------
elif page == "🔁 Patient Flow":
    st.title("Patient Flow Analysis")
    st.caption("How patients move through the system — repeat visits and risk segments")

    c1, c2 = st.columns(2)
    with c1:
        section("Repeat vs. First-Time Patients")
        g = df["repeat_patient"].value_counts().reset_index()
        g.columns = ["segment", "count"]
        fig = px.pie(g, names="segment", values="count", hole=0.55,
                     color_discrete_sequence=[PRIMARY, MUTED])
        fig.update_traces(textinfo="percent+label")
        fig.update_layout(**PLOTLY_LAYOUT, height=360, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        section("High-Risk vs. Standard Risk")
        g = df["high_risk_patient"].value_counts().reset_index()
        g.columns = ["segment", "count"]
        fig = px.pie(g, names="segment", values="count", hole=0.55,
                     color_discrete_sequence=[DANGER, SUCCESS])
        fig.update_traces(textinfo="percent+label")
        fig.update_layout(**PLOTLY_LAYOUT, height=360, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    section("Visit Number Distribution", "How many times does a patient re-appear in this dataset?")
    g = df["visit_number"].value_counts().reset_index()
    g.columns = ["visit_number", "count"]
    g = g[g["visit_number"] <= 10].sort_values("visit_number")
    fig = px.bar(g, x="visit_number", y="count", text=g["count"],
                 color_discrete_sequence=[PRIMARY])
    fig.update_traces(texttemplate="%{text:,}", textposition="outside")
    fig.update_layout(**PLOTLY_LAYOUT, xaxis_title="Visit Number", yaxis_title="Encounters",
                       height=380, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    section("Readmission Rate: Repeat × High-Risk Segments", "Cross-tab of the two patient-flow flags")
    cross = df.groupby(["repeat_patient", "high_risk_patient"], observed=True)["readmitted_flag"].mean().reset_index()
    cross["rate"] = (cross["readmitted_flag"] * 100).round(2)
    fig = px.bar(cross, x="repeat_patient", y="rate", color="high_risk_patient", barmode="group",
                 text=cross["rate"], color_discrete_sequence=[SUCCESS, DANGER])
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(**PLOTLY_LAYOUT, xaxis_title="", yaxis_title="Readmission Rate (%)",
                       height=380, legend_title_text="")
    st.plotly_chart(fig, use_container_width=True)


# ----------------------------------------------------------------------------
# PAGE 4: FINANCIAL IMPACT
# ----------------------------------------------------------------------------
elif page == "💰 Financial Impact":
    st.title("Financial Impact")
    st.caption(f"Estimated cost exposure at ${COST_PER_READMISSION:,} per 30-day readmission (HCUP/AHRQ, 2020)")

    total_risk = df["financial_risk"].sum()
    repeat_risk = df.loc[df["repeat_patient"] == "Repeat Patient", "financial_risk"].sum()
    highrisk_risk = df.loc[df["high_risk_patient"].str.startswith("High"), "financial_risk"].sum()

    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_card("Total Estimated Risk", f"${total_risk:,.0f}", f"{df['readmitted_flag'].sum():,} readmissions")
    with c2:
        kpi_card("Risk from Repeat Patients", f"${repeat_risk:,.0f}", f"{repeat_risk/total_risk*100:.0f}% of total")
    with c3:
        kpi_card("Risk from High-Risk Patients", f"${highrisk_risk:,.0f}", f"{highrisk_risk/total_risk*100:.0f}% of total")

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        section("Financial Risk by Admission Type")
        g = df.groupby("admission_type", observed=True)["financial_risk"].sum().reset_index()
        g = g.sort_values("financial_risk", ascending=True)
        fig = px.bar(g, x="financial_risk", y="admission_type", orientation="h",
                     text=g["financial_risk"].apply(lambda x: f"${x/1e6:.1f}M" if x >= 1e6 else f"${x/1e3:.0f}K"),
                     color_discrete_sequence=[PRIMARY])
        fig.update_traces(textposition="outside")
        fig.update_layout(**PLOTLY_LAYOUT, xaxis_title="Financial Risk ($)", yaxis_title="",
                           height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section("Financial Risk by Discharge Disposition", "Top 8 by risk exposure")
        g = df.groupby("discharge_disposition", observed=True)["financial_risk"].sum().reset_index()
        g = g.sort_values("financial_risk", ascending=False).head(8).sort_values("financial_risk", ascending=True)
        fig = px.bar(g, x="financial_risk", y="discharge_disposition", orientation="h",
                     text=g["financial_risk"].apply(lambda x: f"${x/1e6:.1f}M" if x >= 1e6 else f"${x/1e3:.0f}K"),
                     color_discrete_sequence=[WARNING])
        fig.update_traces(textposition="outside")
        fig.update_layout(**PLOTLY_LAYOUT, xaxis_title="Financial Risk ($)", yaxis_title="",
                           height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    section("Financial Risk by Age Group")
    g = df.groupby("age", observed=True)["financial_risk"].sum().reset_index()
    fig = px.area(g, x="age", y="financial_risk", color_discrete_sequence=[DANGER])
    fig.update_traces(line=dict(width=2.5), fillcolor="rgba(220,38,38,0.12)")
    fig.update_layout(**PLOTLY_LAYOUT, xaxis_title="Age Group", yaxis_title="Financial Risk ($)",
                       height=350, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    insight(f"Repeat patients are a <b>minority of the patient base</b> but account for "
            f"<b>{repeat_risk/total_risk*100:.0f}% (${repeat_risk/1e6:.0f}M) of total financial risk</b> — "
            f"targeting this segment offers the highest ROI for readmission-reduction programs.")


# ----------------------------------------------------------------------------
# PAGE 5: WHAT-IF SIMULATOR
# ----------------------------------------------------------------------------
elif page == "🧮 What-If Simulator":
    st.title("What-If Simulator")
    st.caption("Model the financial impact of reducing readmission rates in targeted patient segments")

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.4])

    with col1:
        section("Simulation Controls")
        segment = st.selectbox(
            "Target segment",
            ["All Patients", "Repeat Patients Only", "High-Risk Patients Only"],
        )
        reduction = st.slider("Readmission rate reduction (%)", 0, 50, 10, step=5)
        st.caption(f"Cost per readmission assumption: ${COST_PER_READMISSION:,} (editable below)")
        cost_override = st.number_input("Cost per readmission ($)", min_value=1000, max_value=100000,
                                         value=COST_PER_READMISSION, step=500)

    if segment == "Repeat Patients Only":
        seg_df = df[df["repeat_patient"] == "Repeat Patient"]
    elif segment == "High-Risk Patients Only":
        seg_df = df[df["high_risk_patient"].str.startswith("High")]
    else:
        seg_df = df

    current_readmits = seg_df["readmitted_flag"].sum()
    current_risk = current_readmits * cost_override
    new_readmits = current_readmits * (1 - reduction / 100)
    new_risk = new_readmits * cost_override
    savings = current_risk - new_risk

    with col2:
        section("Projected Impact")
        c1, c2 = st.columns(2)
        with c1:
            kpi_card("Current Readmissions", f"{current_readmits:,.0f}", f"${current_risk:,.0f} risk")
        with c2:
            kpi_card("Projected Readmissions", f"{new_readmits:,.0f}", f"${new_risk:,.0f} risk")
        st.markdown("<br>", unsafe_allow_html=True)
        kpi_card("💵 Estimated Annual Savings", f"${savings:,.0f}",
                  f"from a {reduction}% reduction in {segment.lower()}")

    st.markdown("<br>", unsafe_allow_html=True)
    section("Before vs. After")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=["Current"], y=[current_risk], name="Current Risk",
                          marker_color=DANGER, text=[f"${current_risk:,.0f}"], textposition="outside"))
    fig.add_trace(go.Bar(x=["Projected"], y=[new_risk], name="Projected Risk",
                          marker_color=SUCCESS, text=[f"${new_risk:,.0f}"], textposition="outside"))
    fig.update_layout(**PLOTLY_LAYOUT, height=380, showlegend=False, yaxis_title="Financial Risk ($)")
    st.plotly_chart(fig, use_container_width=True)

    insight("This simulator is a simplified linear model for illustration — it assumes readmission cost "
            "and segment size stay constant while only the readmission <i>rate</i> changes. Useful for "
            "quick scenario comparisons in stakeholder conversations, not a clinical forecasting tool.")
