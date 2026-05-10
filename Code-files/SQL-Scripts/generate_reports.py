import sqlite3
import pandas as pd
import json
import os
import sys
import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# Ensure UTF-8 output for Windows Terminal
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Settings
DB_PATH = "Database/patents.db"
OUTPUT_DIR = "Saved_Files"
VISUALS_DIR = os.path.join(OUTPUT_DIR, "Visuals")

if not os.path.exists(VISUALS_DIR):
    os.makedirs(VISUALS_DIR)


def generate_reports():
    print("=" * 60)
    print(" A. CONSOLE REPORT (TERMINAL OUTPUT)")
    print("=" * 60)

    conn = sqlite3.connect(DB_PATH)

    # 1. Total Patents
    total_patents_q = "SELECT COUNT(*) FROM patents"
    total_patents = pd.read_sql_query(total_patents_q, conn).iloc[0, 0]

    # 2. Top Inventors
    top_inventors_q = """
        SELECT i.name, COUNT(DISTINCT r.patent_id) AS patents
        FROM relationships r
        JOIN inventors i ON r.inventor_id = i.inventor_id
        GROUP BY i.inventor_id, i.name
        ORDER BY patents DESC
        LIMIT 10
    """
    top_inventors_df = pd.read_sql_query(top_inventors_q, conn)

    # 3. Top Companies
    top_companies_q = """
        SELECT c.name, COUNT(DISTINCT r.patent_id) AS patents
        FROM relationships r
        JOIN companies c ON r.company_id = c.company_id
        GROUP BY c.company_id, c.name
        ORDER BY patents DESC
        LIMIT 10
    """
    top_companies_df = pd.read_sql_query(top_companies_q, conn)

    # 4. Top Countries
    top_countries_q = """
        SELECT i.country, COUNT(DISTINCT r.patent_id) AS patents
        FROM relationships r
        JOIN inventors i ON r.inventor_id = i.inventor_id
        GROUP BY i.country
        ORDER BY patents DESC
        LIMIT 10
    """
    top_countries_df = pd.read_sql_query(top_countries_q, conn)

    # Calculate country shares
    top_countries_df['share'] = (top_countries_df['patents'] / total_patents).round(4)

    current_year = datetime.datetime.now().year
    trends_q = """
        SELECT year, COUNT(*) as count FROM patents
        WHERE year IS NOT NULL AND year BETWEEN 1800 AND ?
        GROUP BY year
    """
    year_stats_df = pd.read_sql_query(trends_q, conn, params=(current_year,))
    if not year_stats_df.empty:
        best_year_row = year_stats_df.loc[year_stats_df['count'].idxmax()].to_dict()
        worst_year_row = year_stats_df.loc[year_stats_df['count'].idxmin()].to_dict()
        best_year_row['year'] = int(best_year_row['year'])
        best_year_row['count'] = int(best_year_row['count'])
        worst_year_row['year'] = int(worst_year_row['year'])
        worst_year_row['count'] = int(worst_year_row['count'])
    else:
        best_year_row = None
        worst_year_row = None

    # --- Print Console Report ---
    print(f"Total Patents: {total_patents:,}")
    
    inventors_str = " | ".join([f"{row['name']} ({row['patents']})" for _, row in top_inventors_df.head(2).iterrows()])
    print(f"Top Inventors: {inventors_str}")
    
    companies_str = " | ".join([f"{row['name']} ({row['patents']})" for _, row in top_companies_df.head(1).iterrows()])
    print(f"Top Companies: {companies_str}")
    
    countries_str = " | ".join([f"{row['country']}" for _, row in top_countries_df.head(2).iterrows()])
    print(f"Top Countries: {countries_str}")
    if best_year_row is not None and worst_year_row is not None:
        print(f"Highest Patent Year: {int(best_year_row['year'])} ({int(best_year_row['count']):,})")
        print(f"Lowest Patent Year: {int(worst_year_row['year'])} ({int(worst_year_row['count']):,})")
    print("-" * 60)

    # --- Export CSVs ---
    print("\n B. EXPORTING CSV FILES...")
    top_inventors_df.to_csv(os.path.join(OUTPUT_DIR, "top_inventors.csv"), index=False)
    top_companies_df.to_csv(os.path.join(OUTPUT_DIR, "top_companies.csv"), index=False)
    top_countries_df.to_csv(os.path.join(OUTPUT_DIR, "country_trends.csv"), index=False)
    print(f" Saved to {OUTPUT_DIR}/")

    # --- Advanced Analysis: Patent Categories ---
    print("\n PERFORMING ADVANCED CATEGORY ANALYSIS...")
    
    def classify_patent(title):
        title = str(title).lower()
        if any(w in title for w in ['semiconductor', 'circuit', 'electronic', 'transistor', 'chip']): return 'Electronics'
        if any(w in title for w in ['drug', 'medicine', 'biological', 'protein', 'medical']): return 'Biotech/Health'
        if any(w in title for w in ['software', 'network', 'algorithm', 'data', 'computer']): return 'Software/IT'
        if any(w in title for w in ['vehicle', 'engine', 'motor', 'car']): return 'Automotive'
        return 'Other'

    # Get sample of titles for analysis
    titles_q = "SELECT title FROM patents LIMIT 1000"
    titles_df = pd.read_sql_query(titles_q, conn)
    titles_df['category'] = titles_df['title'].apply(classify_patent)
    category_counts = titles_df['category'].value_counts().reset_index()
    category_counts.columns = ['category', 'count']

    # --- Export JSON ---
    print("\n C. EXPORTING JSON REPORT...")

    json_data = {
        "total_patents": int(total_patents),
        "top_inventors": top_inventors_df.to_dict(orient="records"),
        "top_companies": top_companies_df.to_dict(orient="records"),
        "top_countries": top_countries_df.to_dict(orient="records"),
        "year_extremes": {
            "highest_year": best_year_row,
            "lowest_year": worst_year_row
        },
        "category_analysis": category_counts.to_dict(orient="records")
    }
    
    with open(os.path.join(OUTPUT_DIR, "patent_report.json"), "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4, default=int)
    print(f" Saved to {OUTPUT_DIR}/patent_report.json")

    # Save categories to CSV
    category_counts.to_csv(os.path.join(OUTPUT_DIR, "patent_categories.csv"), index=False)


    # --- Data Visualizations ---
    print("\n D. GENERATING VISUALIZATIONS...")
    
    # 1. Top Companies Bar Chart
    plt.figure(figsize=(10, 6))
    sns.barplot(data=top_companies_df, x='patents', y='name', hue='name', palette='viridis', legend=False)
    plt.title('Top 5 Companies by Patent Count')
    plt.xlabel('Number of Patents')
    plt.ylabel('Company Name')
    plt.tight_layout()
    plt.savefig(os.path.join(VISUALS_DIR, 'top_companies.png'))
    plt.close()

    # 2. Patent Trends Line Chart
    trends_q = "SELECT year, COUNT(*) as count FROM patents WHERE year IS NOT NULL AND year BETWEEN 1800 AND ? GROUP BY year ORDER BY year ASC"
    trends_df = pd.read_sql_query(trends_q, conn, params=(current_year,))
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=trends_df, x='year', y='count', marker='o', color='royalblue')
    plt.title('Patent Filing Trends Over Time')
    plt.xlabel('Year')
    plt.ylabel('Total Patents')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(VISUALS_DIR, 'patent_trends.png'))
    plt.close()

    if best_year_row is not None and worst_year_row is not None:
        extremes_df = pd.concat([
            pd.DataFrame([best_year_row]).assign(group='Highest'),
            pd.DataFrame([worst_year_row]).assign(group='Lowest')
        ])
        plt.figure(figsize=(8, 5))
        sns.barplot(data=extremes_df, x='year', y='count', hue='group', palette=['#00d4ff', '#ff6b6b'])
        plt.title('Highest and Lowest Patent Years (Valid Year Range)')
        plt.xlabel('Year')
        plt.ylabel('Patent Count')
        plt.tight_layout()
        plt.savefig(os.path.join(VISUALS_DIR, 'patent_year_extremes.png'))
        plt.close()

    # 3. Country Distribution Pie Chart
    plt.figure(figsize=(8, 8))
    plt.pie(top_countries_df['patents'], labels=top_countries_df['country'], autopct='%1.1f%%', colors=sns.color_palette('pastel'))
    plt.title('Top 5 Countries Market Share')
    plt.tight_layout()
    plt.savefig(os.path.join(VISUALS_DIR, 'country_distribution.png'))
    plt.close()

    # 4. Category Distribution Bar Chart
    plt.figure(figsize=(10, 6))
    sns.barplot(data=category_counts, x='count', y='category', hue='category', palette='magma', legend=False)
    plt.title('Patent Distribution by Category (Keyword Analysis)')
    plt.xlabel('Count')
    plt.ylabel('Category')
    plt.tight_layout()
    plt.savefig(os.path.join(VISUALS_DIR, 'patent_categories.png'))
    plt.close()

    print(f" Saved to {VISUALS_DIR}/")


    conn.close()
    print("\n" + "=" * 60)
    print("🎉 ALL REPORTS & VISUALS GENERATED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    generate_reports()
