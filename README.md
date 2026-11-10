Kerala Air Quality Monitoring System

An end-to-end data engineering and analytics project that collects, processes, stores, and visualizes air quality data from major cities in Kerala, India.

The project demonstrates a complete data pipeline using Python, PostgreSQL, and Tableau to monitor air pollution indicators and generate meaningful insights.

Project Overview

Air pollution is an important environmental concern. This project aims to monitor air quality across selected locations in Kerala by collecting environmental data, transforming it into a structured format, storing it in a relational database, and presenting the results through interactive visualizations.

Technologies Used

* Python – Data extraction, transformation, and pipeline automation.
* Pandas & NumPy – Data processing and manipulation.
* PostgreSQL – Relational database management.
* SQL – Database schema and analytical queries.
* Tableau – Data visualization and dashboard development.
* Git & GitHub – Version control and project management.

Project Architecture

The project follows an ETL (Extract, Transform, Load) architecture.

1. Extract: Collect air quality data for selected locations in Kerala.
2. Transform: Clean the collected data, handle missing values, and prepare structured datasets.
3. Load: Store processed data in PostgreSQL.
4. Analyze: Generate analytical summaries using SQL.
5. Visualize: Present air quality indicators through Tableau dashboards.

Locations Monitored

* Thrissur
* Kochi
* Thiruvananthapuram

Air Quality Indicators

The pipeline processes environmental measurements including:

* PM2.5
* PM10
* Carbon Monoxide
* Nitrogen Dioxide
* Sulphur Dioxide
* Ozone

Project Structure

Kerala-Air-Quality-Monitoring-System/
│
├── dashboard/
│   └── kerala air quality system.twbx
│
├── data/
│   ├── air_quality_raw.csv
│   ├── air_quality_clean.csv
│   ├── exports/
│   └── rejected_records.csv
│
├── logs/
│   └── pipeline.log
│
├── sql/
│   └── schema.sql
│
├── src/
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   └── main.py
│
├── .gitignore
├── docker-compose.yml
├── requirements.txt
└── README.md

Data Pipeline Execution

To run the project locally:

1. Clone the repository

git clone <YOUR_GITHUB_REPOSITORY_URL>

2. Navigate to the project directory

cd Kerala-Air-Quality-Monitoring-System

3. Create a virtual environment

python -m venv .venv

4. Activate the environment

For macOS/Linux:

source .venv/bin/activate

5. Install dependencies

pip install -r requirements.txt

6. Configure PostgreSQL

Ensure PostgreSQL is running and configure the database connection according to your local environment.

7. Execute the pipeline

python src/main.py

Dashboard & Visualization

Tableau dashboards provide visual insights into air quality measurements across the monitored locations.

The visualizations include:

* Average PM2.5 levels
* Average PM10 levels
* Maximum and minimum pollution measurements
* Key Performance Indicators (KPIs)
* Station-level comparisons

Key Learning Outcomes

* Understanding ETL pipeline architecture.
* Working with real-world environmental datasets.
* Data cleaning and preprocessing using Python.
* Relational database design using PostgreSQL.
* SQL-based analytical data processing.
* Developing dashboards using Tableau.
* Managing projects using Git and GitHub.

Project Status

Completed initial implementation of the data extraction, transformation, loading, PostgreSQL integration, and Tableau dashboard components.

Author

Archana

BCA – Artificial Intelligence and Machine Learning

Kerala, India