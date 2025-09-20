import psycopg2
import os
import re
import csv
from dotenv import load_dotenv
import argparse


# --- CONFIG ---
load_dotenv()
DATABASE_URL = (
    os.getenv("DATABASE_URL") or "postgresql://devuser:password@localhost:5432/devdb"
)

CSV_FOLDER = os.path.dirname(os.path.abspath(__file__))  # same folder as script
GREEN = "\033[92m"
YELLOW = "\033[93m"
VIOLET = "\033[95m"
RESET = "\033[0m"


def import_csv_to_db(csv_path, stranka_id, DATABASE_URL):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # 0. Ensure stranka_id exists in fastapi_stranke
    cur.execute(
        """
        INSERT INTO fastapi_stranke (stranka_id)
        OVERRIDING SYSTEM VALUE
        VALUES (%s)
        ON CONFLICT (stranka_id) DO NOTHING;
    """,
        (stranka_id,),
    )

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
        reader = csv.reader(f, delimiter=";")
        rows = list(reader)

        # Check if first row is a header
        try:
            float(rows[0][1].replace(",", "."))
            float(rows[0][2].replace(",", "."))
            has_header = False
        except (ValueError, IndexError):
            has_header = True

        # Write to temp file for COPY
        from tempfile import NamedTemporaryFile

        with NamedTemporaryFile("w", encoding="utf-8", delete=False) as tmp:
            writer = csv.writer(tmp, delimiter=";")
            for row in rows[1:] if has_header else rows:
                writer.writerow(row)
            tmp_path = tmp.name

        with open(tmp_path, "r", encoding="utf-8") as tmp_file:
            cur.copy_expert(
                "COPY fastapi_tmp_import(casovna_znacka, poraba, dinamicne_cene) FROM STDIN WITH (FORMAT csv, DELIMITER ';')",
                tmp_file,
            )

    # 3. Count rows in temp table
    cur.execute("SELECT COUNT(*) FROM fastapi_tmp_import;")
    row_count = cur.fetchone()[0]

    # Insert into main table with fixed stranka_id
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

    # Compute period_start, period_end, and total
    cur.execute(
        """
        SELECT MIN(casovna_znacka), MAX(casovna_znacka), SUM(poraba * dinamicne_cene)
        FROM fastapi_vhodni_podatki
        WHERE stranka_id = %s;
        """,
        (stranka_id,),
    )
    period_start, period_end, koncni_znesek = cur.fetchone()

    # 6. Insert into racuni table
    cur.execute(
        """
        INSERT INTO fastapi_racuni (stranka_id, period_start, period_end, koncni_znesek)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
        """,
        (stranka_id, period_start, period_end, koncni_znesek),
    )
    racun_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    print(
        f"{GREEN}✅ Imported {row_count} rows for stranka_id={stranka_id}, "
        f"created racun_id={racun_id} with period {period_start} → {period_end}{RESET}"
    )
    return row_count


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Import CSVs into the database")
    parser.add_argument(
        "--env", choices=["dev", "prod"], required=True, help="Which environment to use"
    )
    args = parser.parse_args()

    # Load the appropriate .env file
    env_file = ".env.dev" if args.env == "dev" else ".env.prod"

    if not os.path.exists(env_file):
        print(
            f"{YELLOW}❌ Environment file '{env_file}' not found. Please create it or specify the correct path.{RESET}"
        )
        return

    load_dotenv(dotenv_path=env_file)

    # Get the database URL
    DATABASE_URL = (
        os.getenv("DATABASE_URL")
        or "postgresql://devuser:password@localhost:5432/devdb"
    )
    if not DATABASE_URL:
        print(f"{YELLOW}❌ DATABASE_URL not found in {env_file}{RESET}")
        return

    print(f"{GREEN}🔌 Connecting to database defined in {env_file}{RESET}")

    total_rows = 0
    for filename in os.listdir(CSV_FOLDER):
        print(f"{VIOLET}📄 Found file: {filename}{RESET}")

        if filename.lower().endswith(".csv") and "naloga-lokacija-" in filename:
            match = re.search(r"naloga-lokacija-(\d+)", filename)
            if match:
                stranka_id = int(match.group(1))
                csv_path = os.path.join(CSV_FOLDER, filename)
                print(f"{YELLOW}📄 Processing file: {filename}{RESET}")
                total_rows += import_csv_to_db(csv_path, stranka_id, DATABASE_URL)

    if total_rows == 0:
        print(f"{YELLOW}⚠️  No matching CSV files found in {CSV_FOLDER}{RESET}")
    else:
        print(f"{YELLOW}📊 Total rows inserted: {total_rows}{RESET}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("ERROR:", e)
