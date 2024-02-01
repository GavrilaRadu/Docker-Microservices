CREATE TABLE IF NOT EXISTS countries (
    id SERIAL PRIMARY KEY,
    country_name VARCHAR(100) NOT NULL,
    latitude FLOAT,
    longitude FLOAT,
    UNIQUE(country_name)
);

CREATE TABLE IF NOT EXISTS cities (
    id SERIAL PRIMARY KEY,
    id_country INT REFERENCES countries(id),
    city_name VARCHAR(255) NOT NULL,
    latitude FLOAT,
    longitude FLOAT,
    UNIQUE(id_country, city_name)
);

CREATE TABLE IF NOT EXISTS temperatures (
    id SERIAL PRIMARY KEY,
    value FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    id_city INT REFERENCES cities(id),
    UNIQUE(id_city, timestamp)
);
