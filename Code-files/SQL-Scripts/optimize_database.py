import sqlite3
import time
import os

DB_PATH = "Database/patents.db"

def apply_indexes():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    print(f"Connecting to {DB_PATH} (Size: {os.path.getsize(DB_PATH) / 1e9:.2f} GB)...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Define indexes to create
    indexes = [
        # Table: patents
        "CREATE INDEX IF NOT EXISTS idx_patents_id ON patents(patent_id)",
        "CREATE INDEX IF NOT EXISTS idx_patents_year ON patents(year)",
        
        # Table: inventors
        "CREATE INDEX IF NOT EXISTS idx_inventors_id ON inventors(inventor_id)",
        "CREATE INDEX IF NOT EXISTS idx_inventors_country ON inventors(country)",
        
        # Table: companies
        "CREATE INDEX IF NOT EXISTS idx_companies_id ON companies(company_id)",
        
        # Table: relationships
        "CREATE INDEX IF NOT EXISTS idx_rel_patent ON relationships(patent_id)",
        "CREATE INDEX IF NOT EXISTS idx_rel_inventor ON relationships(inventor_id)",
        "CREATE INDEX IF NOT EXISTS idx_rel_company ON relationships(company_id)",
    ]

    print("Optimizing database performance. This may take a few minutes for a 9GB database...")
    
    for i, cmd in enumerate(indexes, 1):
        start_time = time.time()
        print(f"[{i}/{len(indexes)}] Executing: {cmd}...", end="", flush=True)
        try:
            cursor.execute(cmd)
            conn.commit()
            end_time = time.time()
            print(f" Done ({end_time - start_time:.2f}s)")
        except Exception as e:
            print(f" Failed: {e}")

    print("\nRunning ANALYZE to optimize the query planner...")
    cursor.execute("ANALYZE")
    conn.commit()

    print("\n✅ Database optimization complete!")
    conn.close()

if __name__ == "__main__":
    apply_indexes()
