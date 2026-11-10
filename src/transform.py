import pandas as pd
import os


# ==========================================
# 1. CONFIGURATION
# ==========================================

AIR_COLUMNS = [
    "pm10",
    "pm2_5",
    "carbon_monoxide",
    "nitrogen_dioxide",
    "ozone"
]

REQUIRED_COLUMNS = [
    "time",
    "station",
    "latitude",
    "longitude"
] + AIR_COLUMNS


# ==========================================
# 2. TRANSFORM AIR QUALITY DATA
# ==========================================

def transform_air_quality():

    print("\nStarting data transformation...")

    # Read raw extracted data
    input_path = "data/air_quality_raw.csv"

    df = pd.read_csv(input_path)

    print("\nOriginal records:", len(df))

    # ======================================
    # REMOVE DUPLICATES
    # ======================================

    original_count = len(df)

    df = df.drop_duplicates(
        subset=["time", "station"]
    ).copy()

    duplicate_count = original_count - len(df)

    print("Duplicate records removed:", duplicate_count)

    # ======================================
    # VALIDATE REQUIRED COLUMNS
    # ======================================

    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # ======================================
    # CONVERT DATA TYPES
    # ======================================

    df["time"] = pd.to_datetime(
        df["time"],
        errors="coerce"
    )

    for column in AIR_COLUMNS + ["latitude", "longitude"]:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # ======================================
    # DATA QUALITY CHECKS
    # ======================================

    print("\nChecking missing values:")

    print(df.isnull().sum())

    # Create rejection conditions
    missing_data = df[
        REQUIRED_COLUMNS
    ].isnull().any(axis=1)

    negative_data = (
        (df[AIR_COLUMNS] < 0).any(axis=1)
    )

    # Identify invalid records
    invalid_mask = missing_data | negative_data

    rejected = df[invalid_mask].copy()

    clean_df = df[~invalid_mask].copy()

    # ======================================
    # ADD REJECTION REASONS
    # ======================================

    rejected["rejection_reason"] = rejected.apply(
        lambda row: ", ".join(
            reason for condition, reason in [
                (
                    row[REQUIRED_COLUMNS].isnull().any(),
                    "Missing or invalid values"
                ),
                (
                    (row[AIR_COLUMNS] < 0).any(),
                    "Negative air quality measurement"
                )
            ]
            if condition
        ),
        axis=1
    )

    # ======================================
    # DATA QUALITY SUMMARY
    # ======================================

    print("\n" + "=" * 45)

    print("DATA QUALITY REPORT")

    print("=" * 45)

    print("Original records:", original_count)

    print("Duplicates removed:", duplicate_count)

    print("Rejected records:", len(rejected))

    print("Clean records:", len(clean_df))

    print(
        "Data quality percentage:",
        round(
            (len(clean_df) / max(len(df), 1)) * 100,
            2
        ),
        "%"
    )

    # ======================================
    # SAVE TRANSFORMED DATA
    # ======================================

    os.makedirs("data", exist_ok=True)

    clean_df.to_csv(
        "data/air_quality_clean.csv",
        index=False
    )

    rejected.to_csv(
        "data/rejected_records.csv",
        index=False
    )

    print("\nClean data saved:")
    print("data/air_quality_clean.csv")

    print("\nRejected data saved:")
    print("data/rejected_records.csv")

    print("\nData transformation completed successfully!")

    return clean_df


# ==========================================
# 3. MAIN EXECUTION
# ==========================================

if __name__ == "__main__":

    transformed_data = transform_air_quality()

    print("\nCleaned Data:")

    print(transformed_data.head())

    print("\nCleaned Data Shape:")

    print(transformed_data.shape)