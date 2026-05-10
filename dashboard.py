import json
import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import os
import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="Patent Analytics Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Styling ---
st.markdown("""
    <style>
    .main {
        background-color: #0f1116;
        color: #ffffff;
    }
    .stMetric {
        background-color: #1e2128;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        color: #00d4ff;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Database & JSON Cache ---
DB_PATH = "Database/patents.db"
JSON_PATH = "Saved_Files/patent_report.json"

@st.cache_resource
def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

@st.cache_data
def build_json_report():
    conn = get_connection()
    current_year = datetime.datetime.now().year

    total_patents = pd.read_sql_query("SELECT COUNT(*) FROM patents", conn).iloc[0, 0]
    total_inventors = pd.read_sql_query("SELECT COUNT(*) FROM inventors", conn).iloc[0, 0]
    total_companies = pd.read_sql_query("SELECT COUNT(*) FROM companies", conn).iloc[0, 0]

    year_trends_df = pd.read_sql_query(
        "SELECT CAST(year AS INTEGER) AS year, COUNT(*) AS count "
        "FROM patents "
        "WHERE year IS NOT NULL AND year >= 1800 AND year <= ? "
        "GROUP BY year "
        "ORDER BY year ASC",
        conn,
        params=(current_year,),
    )
    year_trends_df['year'] = year_trends_df['year'].astype(int)

    top_companies_df = pd.read_sql_query(
        "SELECT c.name, COUNT(DISTINCT r.patent_id) AS patents "
        "FROM relationships r "
        "JOIN companies c ON r.company_id = c.company_id "
        "GROUP BY c.name "
        "ORDER BY patents DESC "
        "LIMIT 10",
        conn,
    )

    top_countries_df = pd.read_sql_query(
        "SELECT i.country, COUNT(DISTINCT r.patent_id) AS patents "
        "FROM relationships r "
        "JOIN inventors i ON r.inventor_id = i.inventor_id "
        "GROUP BY i.country "
        "ORDER BY patents DESC "
        "LIMIT 10",
        conn,
    )

    if year_trends_df.empty:
        min_year, max_year = 1800, current_year
        highest_year = None
        lowest_year = None
    else:
        min_year = int(year_trends_df['year'].min())
        max_year = int(year_trends_df['year'].max())
        highest_year = year_trends_df.loc[year_trends_df['count'].idxmax()].to_dict()
        lowest_year = year_trends_df.loc[year_trends_df['count'].idxmin()].to_dict()

    report_data = {
        "total_patents": int(total_patents),
        "total_inventors": int(total_inventors),
        "total_companies": int(total_companies),
        "year_range": {"min_year": min_year, "max_year": max_year},
        "patent_trends": year_trends_df.to_dict(orient="records"),
        "year_extremes": {
            "highest_year": highest_year,
            "lowest_year": lowest_year,
        },
        "top_companies": top_companies_df.to_dict(orient="records"),
        "top_countries": top_countries_df.to_dict(orient="records"),
    }

    os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=4)

    return report_data

@st.cache_data
def load_json_report():
    if not os.path.exists(JSON_PATH):
        if not os.path.exists(DB_PATH):
            raise FileNotFoundError(
                f"Neither JSON report nor database was found. Expected {JSON_PATH} or {DB_PATH}."
            )
        return build_json_report()
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data
def load_overview_metrics():
    report = load_json_report()
    return (
        report.get("total_patents", 0),
        report.get("total_inventors", 0),
        report.get("total_companies", 0),
    )

@st.cache_data
def load_year_range():
    report = load_json_report()
    year_range = report.get("year_range", {})
    return (
        year_range.get("min_year", 1800),
        year_range.get("max_year", datetime.datetime.now().year),
    )

@st.cache_data
def load_valid_year_range():
    return load_year_range()

@st.cache_data
def load_patent_trends(min_year, max_year):
    report = load_json_report()
    trends = report.get("patent_trends", [])
    filtered = [row for row in trends if min_year <= row.get("year", 0) <= max_year]
    df = pd.DataFrame(filtered)
    if not df.empty:
        df['year'] = df['year'].astype(int)
    return df

@st.cache_data
def load_year_extremes(min_year, max_year):
    report = load_json_report()
    trends = report.get("patent_trends", [])
    df = pd.DataFrame(trends)
    if df.empty:
        return None, None, pd.DataFrame()
    df = df[df['year'].between(min_year, max_year)]
    if df.empty:
        return None, None, pd.DataFrame()
    best_year = df.loc[df['count'].idxmax()].to_dict()
    worst_year = df.loc[df['count'].idxmin()].to_dict()
    return best_year, worst_year, df

@st.cache_data
def load_top_companies():
    report = load_json_report()
    return pd.DataFrame(report.get("top_companies", []))

@st.cache_data
def load_top_countries():
    report = load_json_report()
    return pd.DataFrame(report.get("top_countries", []))

@st.cache_data
def load_summary_insights():
    report = load_json_report()
    highest = report.get("year_extremes", {}).get("highest_year")
    lowest = report.get("year_extremes", {}).get("lowest_year")
    top_company = report.get("top_companies", [])[0] if report.get("top_companies") else None
    top_country = report.get("top_countries", [])[0] if report.get("top_countries") else None
    return highest, lowest, top_company, top_country

# --- Sidebar ---
st.sidebar.title("🛠️ Dashboard Controls")
st.sidebar.info("This dashboard provides real-time analytics for the patent database.")

if st.sidebar.button("🔄 Clear Cache"):
    if os.path.exists(JSON_PATH):
        os.remove(JSON_PATH)
    st.cache_data.clear()
    st.rerun()

# --- Main Dashboard ---
st.title("💡 Patent Intelligence Dashboard")
st.markdown("### Visualizing Innovation & Patent Landscapes")

if not os.path.exists(DB_PATH):
    st.error(f"Database not found at {DB_PATH}. Please ensure the database is set up.")
else:
    # 1. Metrics Row
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1.2])
    t_patents, t_inventors, t_companies = load_overview_metrics()
    year_min, year_max = load_year_range()

    with col1:
        st.metric("Total Patents", f"{t_patents:,}")
    with col2:
        st.metric("Unique Inventors", f"{t_inventors:,}")
    with col3:
        st.metric("Registered Companies", f"{t_companies:,}")
    with col4:
        st.metric("Patent Year Range", f"{year_min} – {year_max}")

    st.divider()

    # 2. Executive Summary
    valid_min_year, valid_max_year = load_valid_year_range()
    selected_years = st.sidebar.slider(
        "Patent year filter",
        min_value=valid_min_year,
        max_value=valid_max_year,
        value=(valid_min_year, valid_max_year),
        step=1
    )
    trends_df = load_patent_trends(selected_years[0], selected_years[1])
    best_year, worst_year, _ = load_year_extremes(selected_years[0], selected_years[1])
    highest, lowest, top_company, top_country = load_summary_insights()

    st.subheader("🔎 Executive Summary")
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    with summary_col1:
        st.metric(
            "Top Company",
            top_company['name'] if top_company else "N/A",
            f"{int(top_company['patents']):,}" if top_company else ""
        )
    with summary_col2:
        st.metric(
            "Top Country",
            top_country['country'] if top_country else "N/A",
            f"{int(top_country['patents']):,}" if top_country else ""
        )
    with summary_col3:
        st.metric(
            "Peak Patent Year",
            f"{int(highest['year'])}" if highest else "N/A",
            f"{int(highest['count']):,} patents" if highest else ""
        )
    with summary_col4:
        st.metric(
            "Lowest Patent Year",
            f"{int(lowest['year'])}" if lowest else "N/A",
            f"{int(lowest['count']):,} patents" if lowest else ""
        )

    st.markdown(
        """
        **Why this matters**
        - The dashboard is powered by a cached JSON report for faster loads.
        - Use the year filter to focus on specific historic periods.
        - The top company and country reveal the largest patent contributors.
        """
    )

    row2_col1, row2_col2 = st.columns([2, 1])

    with row2_col1:
        st.subheader("📈 Patent Filing Trends Over Time")
        fig_trends = px.line(
            trends_df,
            x='year',
            y='count',
            title="Global Patent Filings",
            labels={'count': 'Number of Patents', 'year': 'Year'},
            template="plotly_dark"
        )
        fig_trends.update_traces(line_color='#00d4ff', line_width=3)
        fig_trends.update_layout(xaxis=dict(tickmode='linear', dtick=10))
        st.plotly_chart(fig_trends, use_container_width=True)

    with row2_col2:
        st.subheader("🌍 Top Countries by Patents")
        country_df = load_top_countries()
        fig_bar = px.bar(
            country_df,
            x='patents',
            y='country',
            orientation='h',
            title='Leading Countries by Patent Volume',
            labels={'patents': 'Number of Patents', 'country': 'Country'},
            color='patents',
            template='plotly_dark',
            color_continuous_scale='Viridis'
        )
        fig_bar.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    if best_year is not None and worst_year is not None:
        st.subheader("📊 Yearly Patent Performance")
        year_col1, year_col2 = st.columns(2)
        with year_col1:
            st.metric(
                "Best Year",
                f"{int(best_year['year'])}",
                f"{int(best_year['count']):,} patents"
            )
        with year_col2:
            st.metric(
                "Worst Year",
                f"{int(worst_year['year'])}",
                f"{int(worst_year['count']):,} patents"
            )

        top_years_df = trends_df.nlargest(5, 'count')
        bottom_years_df = trends_df.nsmallest(5, 'count')
        highlight_df = pd.concat([
            top_years_df.assign(group='Top 5 years'),
            bottom_years_df.assign(group='Bottom 5 years')
        ]).sort_values(['group', 'year'], ascending=[False, True])

        st.subheader("Top and Bottom Patent Years")
        fig_extremes = px.bar(
            highlight_df,
            x='year',
            y='count',
            color='group',
            labels={'count': 'Number of Patents', 'year': 'Year'},
            title='Top 5 and Bottom 5 Years by Patent Volume',
            template='plotly_dark'
        )
        fig_extremes.update_traces(texttemplate='%{y:,}', textposition='outside')
        fig_extremes.update_layout(
            uniformtext_minsize=8,
            uniformtext_mode='hide',
            xaxis=dict(tickmode='linear', dtick=5)
        )
        st.plotly_chart(fig_extremes, use_container_width=True)

    st.divider()

    # 3. Top Companies
    st.subheader("🏢 Top Innovative Companies")
    companies_df = load_top_companies()
    fig_comp = px.bar(companies_df, x='patents', y='name', orientation='h',
                      title="Top 10 Companies by Patent Volume",
                      labels={'patents': 'Number of Patents', 'name': 'Company'},
                      color='patents',
                      color_continuous_scale='Viridis',
                      template="plotly_dark")
    fig_comp.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig_comp, use_container_width=True)

    # 4. Data Explorer (Optional)
    if st.checkbox("🔍 Show Raw Data Sample"):
        st.write("Preview of recent patents:")
        conn = get_connection()
        sample_df = pd.read_sql_query("SELECT title, year, abstract FROM patents LIMIT 50", conn)
        st.dataframe(sample_df, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.write("Developed by Mulondo Asuman")
