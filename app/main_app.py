import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# --- Page Config ---
st.set_page_config(
    page_title="Bank Customer Dashboard",
    layout="wide"
)

# --- Load Data ---
@st.cache_data
def load_data():
    BASE_DIR = Path(__file__).resolve().parents[1]
    file_path = BASE_DIR / "data" / "processed_data.xlsx"
    df = pd.read_excel(file_path)
    return df

df = load_data()

## --- For all Unfiltered data Processing -----##
df_og = df.copy()

# --- Title ---
st.title("🏦 Bank Customer Analytics Dashboard")

# --- Sidebar Filters ---
st.sidebar.header("Filters")
geo_filter = st.sidebar.multiselect(
    "Select Geography",
    options=df["Geography"].unique(),
    default=df["Geography"].unique()
)

df = df[df["Geography"].isin(geo_filter)]

## --- Main Body ---

st.header("📊 Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)

# --- KPI Calculations ---
total_customers = len(df)
churn_rate = df["Exited"].mean() * 100
avg_credit_score = df["CreditScore"].mean()
inactive_churn = df[df["IsActiveMember"] == 0]["Exited"].mean() * 100

# --- Display KPIs ---
col1.metric("Total Customers", total_customers)
col2.metric("Avg Credit Score", f"{avg_credit_score:.0f}")
col3.metric("Churn Rate", f"{churn_rate:.2f}%")
col4.metric("Inactive Customer Churn", f"{inactive_churn:.2f}%")

st.markdown('---')

col1, col2, col3 = st.columns(3)

# --- KPI Calculations ---
total_avg_balance = df["Balance"].mean()
non_zero_avg_balance = df[df["Balance"] > 0]["Balance"].mean()
zero_balance_pct = (df["Balance"] == 0).mean() * 100

# --- Display KPIs ---

col1.metric("Avg Balance (All Customers)", f"{total_avg_balance:,.0f}")
col2.metric("Avg Balance (Active Customers)", f"{non_zero_avg_balance:,.0f}")
col3.metric("Zero Balance (%)", f"{zero_balance_pct:.2f}%")

st.markdown(' ')
st.caption("Churn = % of customers who exited")
st.caption("Zero Balance= % of customers who have 0 or unknown balance")
st.markdown('---')

## ------ Details -------##
st.header("📉Detail Churn Analysis")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🌍 Churn by Geography",
    "📊 Segmentation",
    "💰 High Value",
    "👥 Demographics",
    "💰 Financial Stability Overview",
    "🎯 Actionable Business Summary"
])


with tab1:
    st.subheader("🔍 Churn by Geography")
    col1, col2 = st.columns([1.5, 2.5])
    # Use raw data → ignore sidebar geography filter
    churn_geo = (
        df_og[df_og["Exited"] == 1]
        .groupby("Geography")
        .size()
        .reset_index(name="Count")
    )
    with col1:
        fig = px.pie(
            churn_geo,
            names="Geography", values="Count", hole=0.5,
            color_discrete_sequence=px.colors.qualitative.Bold,
            title="Churn Distribution by Geography"
        )
        fig.update_traces(textinfo="percent+label")
        fig.layout.showlegend = False
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        geo_age = (
            df_og.groupby(["Geography", "AgeGroup"])["Exited"]
            .mean()
            .reset_index()
        )
        geo_age["Exited"] *= 100

        fig = px.bar(
            geo_age,
            x="Geography",
            y="Exited",
            color="AgeGroup",
            barmode="group",
            text_auto=".1f",
            title="Churn Rate by Geography and Age Group (%)"
        )

        st.plotly_chart(fig, use_container_width=True)
        st.caption("Shows how churn varies across age groups within each geography. "
                   "Helps identify region-specific customer behavior patterns.")

    st.markdown('---')
    st.subheader("🧾 Executive Summary")
    st.write("1. Germany is the primary churn driver and should be prioritized for retention strategies ")
    st.write("2. Mature customers (45–60) represent the highest-risk segment across all regions")
    st.write("3. The combination of Germany + Mature customers forms the most critical churn hotspot")
    st.write("4. Young customers show strong retention and require lower intervention focus")
    st.write("5. Spain serves as a stable benchmark market for optimizing customer strategies")


with tab2:
    st.subheader("🔍 Churn by Segments")
    display_map = {
        "CreditScoreGroup": "Credit Score Segment",
        "AgeGroup": "Age Segment",
        "SalaryGroup": "Salary Segment",
        "TenureGroup": "Tenure Segment"
    }
    segment_option = st.selectbox(
        "Select Segmentation Dimension",
        ["CreditScoreGroup", "AgeGroup", "SalaryGroup", "TenureGroup"]
    )
    churn_segment = (df.groupby(segment_option)["Exited"].mean().reset_index())
    churn_segment["Exited"] = churn_segment["Exited"] * 100

    # Custom ordering for known groups
    order_map = {
        "AgeGroup": [
            'Young (0–30)', 'Mid-age (30–45)',
            'Mature (45–60)', 'Senior (60+)'
        ],
        "CreditScoreGroup": [
            'Low (300–580)', 'Medium (580–720)', 'High (720+)'
        ],
        "SalaryGroup": [
            'Low (0–50K)', 'Medium (50K–150K)', 'High (150K+)'
        ],
        "TenureGroup": [
            'New (0–3 yrs)', 'Mid-term (4–7 yrs)', 'Long-term (8+ yrs)'
        ]
    }
    color_maps = {
        "AgeGroup": {
            'Young (0–30)': '#6A1B9A',
            'Mid-age (30–45)': '#1B9E77',
            'Mature (45–60)': '#4C72B0',
            'Senior (60+)': '#F1B300'
        },
        "CreditScoreGroup": {
            'Low (300–580)': '#D32F2F',
            'Medium (580–720)': '#F57C00',
            'High (720+)': '#388E3C'
        },
        "SalaryGroup": {
            'Low (0–50K)': '#D32F2F',
            'Medium (50K–150K)': '#FBC02D',
            'High (150K+)': '#388E3C'
        },
        "TenureGroup": {
            'New (0–3 yrs)': '#EF5350',
            'Mid-term (4–7 yrs)': '#42A5F5',
            'Long-term (8+ yrs)': '#66BB6A'
        }
    }

    if segment_option in order_map:
        churn_segment[segment_option] = pd.Categorical(
            churn_segment[segment_option],
            categories=order_map[segment_option],
            ordered=True
        )
        churn_segment = churn_segment.sort_values(segment_option)
        churn_segment = churn_segment.set_index(segment_option).reindex(order_map[segment_option]).reset_index()

    current_color_map = color_maps.get(segment_option, {})

    col1, col2 = st.columns([2, 1])
    with col1:
        fig = px.bar(
            churn_segment,
            x=segment_option,
            y="Exited",
            color=segment_option,
            color_discrete_map=current_color_map,
            text_auto=".2f",
            title=f"Churn Rate by {display_map[segment_option]} (%)"
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🧠 Insights")
        # Top & bottom segments
        sorted_df = churn_segment.sort_values(by="Exited", ascending=False)
        top_seg = sorted_df.iloc[0]
        low_seg = sorted_df.iloc[-1]
        # Spread (variation)
        max_val = top_seg["Exited"]
        min_val = low_seg["Exited"]
        spread = max_val - min_val
        # 1. Key finding
        st.write(
            f"• **{top_seg[segment_option]}** has the highest churn rate "
            f"(**{max_val:.2f}%**)"
        )
        # 2. Lowest segment (context matters)
        st.write(
            f"• Lowest churn observed in **{low_seg[segment_option]}** "
            f"(**{min_val:.2f}%**)"
        )
        # 3. Spread interpretation
        st.write(f"• Churn gap across segments: **{spread:.2f}%**")
        if spread > 20:
            st.warning("⚠️ Significant variation → strong segment-based churn behavior")
        else:
            st.info("ℹ️ Churn is relatively consistent across segments")
        # 4. Strategic takeaway
        st.write("• High-risk segments require targeted retention strategies")
        st.write("• Low-risk segments indicate stable customer base")

    st.caption("Displays the churn rate (%) within each selected segment. "
               "Helps identify which customer groups have a higher likelihood of exiting.")

    st.markdown('---')
    churn_contribution = (df[df["Exited"] == 1].groupby(segment_option).size().reset_index(name="ChurnCount"))
    total_churn = churn_contribution["ChurnCount"].sum()
    churn_contribution["Contribution (%)"] = (churn_contribution["ChurnCount"] / total_churn * 100)

    col1, col2 = st.columns([2, 1])

    with col1:
        fig = px.pie(
            churn_contribution,
            names=segment_option,
            values="ChurnCount",
            hole=0.5,
            color=segment_option,
            color_discrete_map=current_color_map,
            title=f"Churn Contribution by {display_map[segment_option]}"
        )
        fig.update_traces(textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🧠 Insights")

        # Top contributing segment
        top_seg = churn_contribution.sort_values(by="Contribution (%)", ascending=False).iloc[0]
        st.write(f"• **{top_seg[segment_option]}** contributes the most to churn")
        st.write(f"• Accounts for **{top_seg['Contribution (%)']:.2f}%** of total churn")

        # Spread analysis
        max_val = churn_contribution["Contribution (%)"].max()
        min_val = churn_contribution["Contribution (%)"].min()
        spread = max_val - min_val

        if spread > 20:
            st.warning("⚠️ Churn is heavily concentrated in specific segments")
        else:
            st.info("ℹ️ Churn is relatively distributed across segments")

        # Strategic takeaway
        st.write("• Focus retention efforts on top contributing segment")
        st.write("• Segment size + churn rate both influence contribution")

    st.caption("Shows the percentage contribution of each segment to total churn. "
               "Highlights which groups drive the largest share of customer exits.")

with tab3:
    st.header("💰 High-Value Customer Churn Analysis")

    high_value_df = df[df["BalanceGroup"] == "High (100K+)"]
    hv_total = len(high_value_df)
    hv_churned = high_value_df["Exited"].sum()
    hv_churn_rate = high_value_df["Exited"].mean() * 100
    high_value_ratio = (df[df["BalanceGroup"] == "High (100K+)"]["Exited"].mean() * 100)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("High-Balance Customers", hv_total)
    col2.metric("Churned (High Balance)", int(hv_churned))
    col3.metric("Churn Rate (High Balance)", f"{hv_churn_rate:.2f}%")
    col4.metric("High-Value Churn Ratio", f"{high_value_ratio:.2f}%")

    churn_matrix = (
        df.groupby(["BalanceGroup", "SalaryGroup"])["Exited"]
        .mean()
        .reset_index()
    )
    churn_matrix["Exited"] *= 100

    st.markdown('---')
    col1, col2 = st.columns([2, 1])

    with col1:
        fig = px.bar(
            churn_matrix,
            x="BalanceGroup",
            y="Exited",
            color="SalaryGroup",
            barmode="group",
            text_auto=".2f",
            title="Churn Rate by Balance & Salary Segment (%)",
            color_discrete_sequence=px.colors.qualitative.Bold
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("💸 Revenue Risk from Churn")
        churned_high_value = high_value_df[high_value_df["Exited"] == 1]
        revenue_risk = churned_high_value["Balance"].sum()
        st.metric("Estimated Balance Lost", f"{revenue_risk:,.0f}")
        st.write("• Represents total balance held by churned high-value customers")
        st.write("• Indicates potential financial exposure due to churn")

    st.markdown('---')

    st.subheader("🧾 Executive Summary")
    top_combo = churn_matrix.sort_values(by="Exited", ascending=False).iloc[0]
    st.write(  f"• Highest churn in **{top_combo['BalanceGroup']} + {top_combo['SalaryGroup']}** segment")
    st.write(f"• Churn rate: **{top_combo['Exited']:.2f}%**")
    st.write("• High-balance customers represent the most critical churn risk due to their financial value ")
    st.write("• Customers with high balance but low salary show the highest churn propensity, indicating financial stress factors ")
    st.write("• Salary significantly influences churn behavior even within the same balance segment ")
    st.write("• Approximately 159M in customer balance is at risk, highlighting the need for targeted retention strategies  ")


with tab4:
    st.subheader("👤 Gender-Based Churn Analysis")
    gender_churn = (df.groupby("Gender")["Exited"].mean().reset_index())
    gender_churn["Exited"] *= 100

    col1, col2 = st.columns([2, 1])

    with col1:
        fig = px.bar(
            gender_churn,
            x="Gender",
            y="Exited",
            color="Gender",
            text_auto=".2f",
            title="Churn Rate by Gender (%)"
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🧠 Insights")
        sorted_df = gender_churn.sort_values(by="Exited", ascending=False)
        top = sorted_df.iloc[0]
        low = sorted_df.iloc[-1]
        diff = top["Exited"] - low["Exited"]
        st.write(f"• Higher churn in **{top['Gender']}** (**{top['Exited']:.2f}%**)")
        st.write(f"• Lower churn in **{low['Gender']}** (**{low['Exited']:.2f}%**)")
        st.write(f"• Gap: **{diff:.2f}%**")

        if diff > 5:
            st.warning("⚠️ Noticeable gender-based churn difference")
        else:
            st.info("ℹ️ Minimal variation across genders")

        st.write("• Consider gender-specific engagement strategies")

    st.markdown('---')

    st.subheader("👤 Engagement-Based Churn Analysis")
    tenure_engagement = (df.groupby(["TenureGroup", "IsActiveMember"])["Exited"].mean().reset_index())
    tenure_engagement["Exited"] *= 100
    tenure_engagement["IsActiveMember"] = tenure_engagement["IsActiveMember"].map({
        0: "Inactive",
        1: "Active"
    })

    col1, col2 = st.columns([2, 1])
    with col1:
        fig = px.bar(
            tenure_engagement,
            x="TenureGroup",
            y="Exited",
            color="IsActiveMember",
            barmode="group",
            text_auto=".2f",
            title="Churn Rate by Customer Activity (%)"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        inactive_churn = df[df["IsActiveMember"] == 0]["Exited"].mean() * 100
        st.metric("Inactive Customer Churn", f"{inactive_churn:.2f}%")
        st.markdown('---')
        st.subheader("🧾 Executive Summary")
        st.write("Churn is driven more by customer inactivity than tenure, "
                 "and inactive users representing the highest-risk segment.")

with tab5:
    st.subheader("💰 Financial Stability Overview")
    balance_churn = (df.groupby("BalanceGroup")["Exited"].mean().reset_index())
    balance_churn["Exited"] *= 100

    col1, col2 = st.columns([2, 1])

    with col1:
        fig = px.bar(
            balance_churn,
            x="BalanceGroup",
            y="Exited",
            color="BalanceGroup",
            text_auto=".2f",
            title="Churn Rate by Balance Segment (%)"
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("🧠 Insights")

        sorted_df = balance_churn.sort_values(by="Exited", ascending=False)
        top = sorted_df.iloc[0]
        low = sorted_df.iloc[-1]

        st.write(f"• Highest churn in **{top['BalanceGroup']}** segment")
        st.write(f"• Lowest churn in **{low['BalanceGroup']}** segment")
        st.write("• Balance is a strong indicator of customer stability")
        st.write("• High-balance customers show higher churn risk,"
                 " indicating potential financial or service dissatisfaction")
        st.write("• Churn risk is highest among high-balance customers with low income, "
                 "indicating that financial stress—not just wealth—drives customer exit.")

    st.markdown('---')

    st.subheader("🔍 Balance vs Salary (Drill-down)")
    financial = ( df.groupby(["BalanceGroup", "SalaryGroup"])["Exited"].mean().reset_index())
    financial["Exited"] *= 100
    fig = px.bar(
        financial,
        x="BalanceGroup",
        y="Exited",
        color="SalaryGroup",
        barmode="group",
        text_auto=".1f",
        title="Churn Rate by Balance and Salary (%)"
    )

    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Shows how salary influences churn within each balance segment. "
        "Helps identify financially vulnerable customer groups."
    )

with tab6:
        st.markdown("### 🎯 Actionable Summary")

        st.write("""
        **🔍 Key Drivers**
        • Churn is primarily driven by geography, engagement, and financial behavior  
        • Germany and mature customers (45–60) show the highest risk  
        • Inactive customers are consistently more likely to churn  

        **🔥 Top Risk Segments**
        • Germany + Mature customers  
        • High Balance (100K+) + Low Salary  
        • Inactive customers across all tenure groups  

        **💼 What to Do**
        • Prioritize Germany with targeted retention campaigns  
        • Re-engage inactive customers (biggest impact lever)  
        • Protect high-value customers with personalized/VIP strategies  
        • Use combined segmentation (Balance + Salary + Activity)  

        **💰 Business Impact**
        • High-value churn drives major financial risk  
        • Reducing churn in key segments directly improves revenue  
        """)

        top_combo = churn_matrix.sort_values(by="Exited", ascending=False).iloc[0]
        st.success(
            f"🔥 Highest Risk Segment: Customer with {top_combo['BalanceGroup']} balance and {top_combo['SalaryGroup']} salary "
            f"({top_combo['Exited']:.2f}% churn)")
        st.info("📌 Focus Area: High-value, inactive, and mature customers in Germany" )

