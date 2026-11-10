import pandas as pd
import psycopg2
import json
import os

from psycopg2.extras import execute_values


# ==========================================
# 1. DATABASE CONFIGURATION
# ==========================================

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "air_quality"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "local_dev_password"),
    "port": int(os.getenv("DB_PORT", "5432"))
}


# ==========================================
# 2. LOAD DATA INTO POSTGRESQL
# ==========================================

def load_data():

    connection = None
    run_id = None

    try:

        print("\nConnecting to PostgreSQL...")

        connection = psycopg2.connect(**DB_CONFIG)

        cursor = connection.cursor()

        print("Database connection successful!")

        # ==================================
        # READ DATA FILES
        # ==================================

        df = pd.read_csv("data/air_quality_clean.csv")

        rejected = pd.read_csv(
            "data/rejected_records.csv"
        )

        raw_df = pd.read_csv("data/air_quality_raw.csv")

        print("\nClean records:", len(df))
        print("Rejected records:", len(rejected))

        # ==================================
        # CREATE PIPELINE RUN
        # ==================================

        cursor.execute("""
            INSERT INTO pipeline_runs (status)
            VALUES ('running')
            RETURNING run_id
        """)

        run_id = cursor.fetchone()[0]

        connection.commit()

        print("Pipeline Run ID:", run_id)

        # ==================================
        # INSERT MONITORING STATIONS
        # ==================================

        station_ids = {}

        stations = df[
            ["station", "latitude", "longitude"]
        ].drop_duplicates(subset=["station"])

        for _, row in stations.iterrows():

            cursor.execute("""
                INSERT INTO stations (
                    station_name,
                    latitude,
                    longitude
                )
                VALUES (%s, %s, %s)

                ON CONFLICT (station_name)
                DO UPDATE SET
                    latitude = EXCLUDED.latitude,
                    longitude = EXCLUDED.longitude

                RETURNING station_id
            """, (
                row["station"],
                row["latitude"],
                row["longitude"]
            ))

            station_ids[row["station"]] = cursor.fetchone()[0]

        print("\nStations loaded:", len(station_ids))

        # ==================================
        # INSERT AIR QUALITY MEASUREMENTS
        # ==================================

        air_quality_records = []

        for _, row in df.iterrows():

            air_quality_records.append((
                station_ids[row["station"]],
                pd.to_datetime(row["time"]).to_pydatetime(),
                row["pm10"],
                row["pm2_5"],
                row["carbon_monoxide"],
                row["nitrogen_dioxide"],
                row["ozone"]
            ))

        if air_quality_records:

            execute_values(
                cursor,
                """
                INSERT INTO air_quality (
                    station_id,
                    observed_at,
                    pm10,
                    pm2_5,
                    carbon_monoxide,
                    nitrogen_dioxide,
                    ozone
                )
                VALUES %s

                ON CONFLICT (station_id, observed_at)
                DO UPDATE SET
                    pm10 = EXCLUDED.pm10,
                    pm2_5 = EXCLUDED.pm2_5,
                    carbon_monoxide = EXCLUDED.carbon_monoxide,
                    nitrogen_dioxide = EXCLUDED.nitrogen_dioxide,
                    ozone = EXCLUDED.ozone
                """,
                air_quality_records
            )

        print(
            "Air quality records loaded:",
            len(air_quality_records)
        )

        # ==================================
        # STORE REJECTED RECORDS
        # ==================================

        rejected_records = []

        for _, row in rejected.iterrows():

            rejected_records.append((
                pd.to_datetime(row["time"]).to_pydatetime()
                if pd.notna(row["time"]) else None,

                row["station"]
                if pd.notna(row["station"]) else None,

                row["rejection_reason"]
                if "rejection_reason" in row and pd.notna(row["rejection_reason"])
                else "Missing or invalid measurements",

                json.dumps(row.to_dict(), default=str)
            ))

        if rejected_records:

            execute_values(
                cursor,
                """
                INSERT INTO rejected_records (
                    observed_at,
                    station_name,
                    rejection_reason,
                    raw_record
                )
                VALUES %s
                """,
                rejected_records
            )

        print(
            "Rejected records stored:",
            len(rejected_records)
        )

        # ==================================
        # DATA QUALITY CHECKS
        # ==================================

        air_columns = [
            "pm10",
            "pm2_5",
            "carbon_monoxide",
            "nitrogen_dioxide",
            "ozone"
        ]

        missing_count = int(
            df[air_columns].isnull().any(axis=1).sum()
        )

        negative_count = int(
            (df[air_columns] < 0).any(axis=1).sum()
        )

        checks = [

            (
                "No missing measurements",
                missing_count == 0,
                missing_count
            ),

            (
                "No negative measurements",
                negative_count == 0,
                negative_count
            ),

            (
                "Clean records available",
                len(df) > 0,
                0 if len(df) > 0 else 1
            ),

            (
                "All monitoring stations identified",
                len(station_ids) == len(stations),
                len(stations) - len(station_ids)
            )

        ]

        for name, passed, failed_count in checks:

            cursor.execute("""
                INSERT INTO dq_checks (
                    run_id,
                    check_name,
                    status,
                    records_checked,
                    failed_records,
                    details
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                run_id,
                name,
                "PASS" if passed else "FAIL",
                len(df),
                failed_count,
                f"Validation result: {'Passed' if passed else 'Failed'}"
            ))

        # ==================================
        # UPDATE PIPELINE EXECUTION STATUS
        # ==================================

        cursor.execute("""
            UPDATE pipeline_runs

            SET
                finished_at = CURRENT_TIMESTAMP,
                status = 'completed',
                extracted_count = %s,
                clean_count = %s,
                rejected_count = %s

            WHERE run_id = %s
        """, (
            len(raw_df),
            len(df),
            len(rejected),
            run_id
        ))

        # Commit all loading operations
        connection.commit()

        print("\n" + "=" * 45)

        print("DATABASE LOADING COMPLETED")

        print("=" * 45)

        print("Pipeline Run ID:", run_id)
        print("Extracted records:", len(raw_df))
        print("Clean records:", len(df))
        print("Rejected records:", len(rejected))
        print("Stations loaded:", len(station_ids))

        print("\nData quality checks:")

        for name, passed, failed_count in checks:

            print(
                name,
                "PASS" if passed else "FAIL"
            )

        print("\nAll database operations completed successfully!")

    except Exception as error:

        if connection:

            connection.rollback()

            if run_id is not None:

                try:

                    with connection.cursor() as error_cursor:

                        error_cursor.execute("""
                            UPDATE pipeline_runs

                            SET
                                finished_at = CURRENT_TIMESTAMP,
                                status = 'failed',
                                error_message = %s

                            WHERE run_id = %s
                        """, (str(error), run_id))

                    connection.commit()

                except Exception:

                    connection.rollback()

        print("\nDATABASE LOADING FAILED!")

        print("Error:", error)

        raise

    finally:

        if connection:

            connection.close()

            print("\nDatabase connection closed.")


# ==========================================
# 3. MAIN EXECUTION
# ==========================================

if __name__ == "__main__":

    load_data()