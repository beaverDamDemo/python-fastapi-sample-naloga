import psycopg2
import os
import re
from dotenv import load_dotenv

# --- CONFIG ---
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

CSV_FOLDER = os.path.dirname(os.path.abspath(__file__))  # same folder as script
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def import_csv_to_db(csv_path, stranka_id):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # 1. Create temp table
    cur.execute(
        """
        CREATE TEMP TABLE fastapi_tmp_import (
            casovna_znacka TEXT,
            poraba TEXT,
            dinamicne_cene TEXT
        );
    """
    )

    # 2. Load CSV into temp table
    with open(csv_path, "r", encoding="utf-8") as f:
        cur.copy_expert(
            "COPY fastapi_tmp_import(casovna_znacka, poraba, dinamicne_cene) FROM STDIN WITH (FORMAT csv, HEADER true, DELIMITER ';')",
            f,
        )

    # 3. Count rows in temp table
    cur.execute("SELECT COUNT(*) FROM fastapi_tmp_import;")
    row_count = cur.fetchone()[0]

    # 4. Insert into main table with fixed stranka_id
    cur.execute(
        """
        INSERT INTO fastapi_vhodni_podatki (casovna_znacka, poraba, dinamicne_cene, stranka_id)
        SELECT
            casovna_znacka::timestamptz,
            REPLACE(poraba, ',', '.')::double precision,
            REPLACE(dinamicne_cene, ',', '.')::double precision,
            %s
        FROM fastapi_tmp_import;
    """,
        (stranka_id,),
    )

    conn.commit()
    cur.close()
    conn.close()

    # 5. Log to terminal (green for success)
    print(
        f"{GREEN}✅ Imported {row_count} rows from '{os.path.basename(csv_path)}' with stranka_id={stranka_id}{RESET}"
    )
    return row_count


def main():
    total_rows = 0

    for filename in os.listdir(CSV_FOLDER):
        if filename.lower().endswith(".csv") and "naloga-lokacija-" in filename:
            match = re.search(r"naloga-lokacija-(\d+)", filename)
            if match:
                stranka_id = int(match.group(1))
                csv_path = os.path.join(CSV_FOLDER, filename)
                total_rows += import_csv_to_db(csv_path, stranka_id)

    if total_rows == 0:
        print(f"{YELLOW}⚠️  No matching CSV files found in {CSV_FOLDER}{RESET}")
    else:
        print(f"{YELLOW}📊 Total rows inserted: {total_rows}{RESET}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("ERROR:", e)
