import requests
import pandas as pd
import os

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# ==========================================
# 1. CREATE HTTP SESSION WITH RETRY MECHANISM
# ==========================================

def create_session():

    retry_strategy = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        respect_retry_after_header=True
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)

    session = requests.Session()

    session.mount("https://", adapter)
    session.mount("http://", adapter)

    return session


# ==========================================
# 2. MONITORING LOCATIONS IN KERALA
# ==========================================

STATIONS = {
    "Thrissur": {
        "latitude": 10.5276,
        "longitude": 76.2144
    },

    "Kochi": {
        "latitude": 9.9312,
        "longitude": 76.2673
    },

    "Thiruvananthapuram": {
        "latitude": 8.5241,
        "longitude": 76.9366
    }
}


# ==========================================
# 3. API CONFIGURATION
# ==========================================

AIR_QUALITY_URL = (
    "https://air-quality-api.open-meteo.com/v1/air-quality"
)


# ==========================================
# 4. EXTRACT AIR QUALITY DATA
# ==========================================

def extract_air_quality():

    all_data = []

    # Create reusable HTTP session
    session = create_session()

    try:

        for city, coordinates in STATIONS.items():

            print(f"\nCollecting data for {city}...")

            params = {

                "latitude": coordinates["latitude"],

                "longitude": coordinates["longitude"],

                "hourly": [
                    "pm10",
                    "pm2_5",
                    "carbon_monoxide",
                    "nitrogen_dioxide",
                    "ozone"
                ],

                "forecast_days": 1,

                "timezone": "Asia/Kolkata"
            }

            try:

                response = session.get(
                    AIR_QUALITY_URL,
                    params=params,
                    timeout=30
                )

                # Check HTTP response
                response.raise_for_status()

                # Convert JSON response
                result = response.json()

                # Extract hourly measurements
                hourly_data = result["hourly"]

                # Convert to DataFrame
                df = pd.DataFrame(hourly_data)

                # Add station information
                df["station"] = city

                df["latitude"] = coordinates["latitude"]

                df["longitude"] = coordinates["longitude"]

                # Store extracted data
                all_data.append(df)

                print(
                    f"Successfully collected "
                    f"{len(df)} records for {city}."
                )

            except requests.exceptions.RequestException as e:

                print(f"API request failed for {city}: {e}")

            except (KeyError, ValueError) as e:

                print(f"Invalid API response for {city}: {e}")

        # Check whether any data was collected
        if not all_data:

            raise RuntimeError(
                "Data extraction failed for all monitoring stations."
            )

        # Combine all station data
        final_df = pd.concat(
            all_data,
            ignore_index=True
        )

        print("\nTotal extracted records:", len(final_df))

        return final_df

    finally:

        # Close HTTP session
        session.close()


# ==========================================
# 5. SAVE RAW DATA
# ==========================================

def save_raw_data(data):

    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)

    output_path = "data/air_quality_raw.csv"

    data.to_csv(
        output_path,
        index=False
    )

    print(f"\nRaw data saved successfully: {output_path}")


# ==========================================
# 6. MAIN EXECUTION
# ==========================================

if __name__ == "__main__":

    print("=" * 50)

    print("AIR QUALITY DATA EXTRACTION")

    print("=" * 50)

    try:

        # Extract data
        data = extract_air_quality()

        # Display extracted records
        print("\nExtracted Air Quality Data:")

        print(data.head(10))

        # Save raw data
        save_raw_data(data)

        print("\nData extraction completed successfully!")

    except Exception as e:

        print("\nDATA EXTRACTION FAILED!")

        print("Error:", e)