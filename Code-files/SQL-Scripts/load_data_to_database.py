import pandas as pd
import sqlite3

conn = sqlite3.connect("Database/patents.db")
conn.execute("PRAGMA synchronous = OFF")

def load_csv(csv_file, table_name, conn):
    print(f"Loading {csv_file}...")
    chunk_num = 0
    for chunk in pd.read_csv(csv_file, chunksize=100000):
        chunk_num += 1
        if chunk_num == 1:
            chunk.to_sql(table_name, conn, if_exists="replace", index=False)
        else:
            chunk.to_sql(table_name, conn, if_exists="append", index=False)
        conn.commit()
        print(f"  Chunk {chunk_num} saved")
    print(f"✓ {table_name} complete\n")

load_csv("Clean-Data-Files/clean_patents.csv", "patents", conn)
load_csv("Clean-Data-Files/clean_inventors.csv", "inventors", conn)
load_csv("Clean-Data-Files/clean_companies.csv", "companies", conn)
load_csv("Clean-Data-Files/clean_relationships.csv", "relationships", conn)

print("Done!")
conn.close()
