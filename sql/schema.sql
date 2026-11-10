-- 1. Stations table
CREATE TABLE IF NOT EXISTS stations (
    station_id SERIAL PRIMARY KEY,
    station_name VARCHAR(100) UNIQUE NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL
);

-- 2. Air quality table
CREATE TABLE IF NOT EXISTS air_quality (
    station_id INTEGER REFERENCES stations(station_id),
    observed_at TIMESTAMP NOT NULL,
    pm10 DOUBLE PRECISION,
    pm2_5 DOUBLE PRECISION,
    carbon_monoxide DOUBLE PRECISION,
    nitrogen_dioxide DOUBLE PRECISION,
    ozone DOUBLE PRECISION,
    PRIMARY KEY (station_id, observed_at)
);

-- 3. Weather table (future integration)
CREATE TABLE IF NOT EXISTS weather (
    weather_id SERIAL PRIMARY KEY,
    station_id INTEGER REFERENCES stations(station_id),
    observed_at TIMESTAMP NOT NULL,
    temperature DOUBLE PRECISION,
    humidity DOUBLE PRECISION,
    precipitation DOUBLE PRECISION,
    wind_speed DOUBLE PRECISION
);

-- 4. Rejected records table
CREATE TABLE IF NOT EXISTS rejected_records (
    rejected_id SERIAL PRIMARY KEY,
    observed_at TIMESTAMP,
    station_name VARCHAR(100),
    rejection_reason TEXT,
    raw_record JSONB,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Pipeline execution tracking
CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id SERIAL PRIMARY KEY,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP,
    status VARCHAR(30),
    extracted_count INTEGER DEFAULT 0,
    clean_count INTEGER DEFAULT 0,
    rejected_count INTEGER DEFAULT 0,
    error_message TEXT
);

-- 6. Data quality checks
CREATE TABLE IF NOT EXISTS dq_checks (
    check_id SERIAL PRIMARY KEY,
    run_id INTEGER REFERENCES pipeline_runs(run_id),
    check_name VARCHAR(150),
    status VARCHAR(30),
    records_checked INTEGER,
    failed_records INTEGER,
    details TEXT,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);