# For Ubuntu 24 - September 2025

# Testing implies:
# (1) the creation of a postgresql DB
# (2) the upload of the test dataset

# (1.1) Install and start postgresql
sudo apt update
sudo apt upgrade -y
sudo apt install postgresql postgresql-contrib -y
sudo systemctl enable postgresql
sudo systemctl start postgresql
sudo systemctl status postgresql

# (1.2) Create the user
sudo -i -u postgres
psql -c "CREATE USER reelyactive WITH PASSWORD 'paretoanywhere';"

# (1.3) Create database owned by the user and grant privileges
psql -c "CREATE DATABASE pareto_anywhere OWNER reelyactive;"
psql -c "GRANT ALL PRIVILEGES ON DATABASE pareto_anywhere TO reelyactive;"

# (1.4) Checks
psql
\l+
\du
exit

# (2.1) Create the table
psql -U reelyactive -d pareto_anywhere -h localhost
CREATE TABLE raddec (
    transmitterId TEXT,
    numberOfDecodings INT,
    receiverId TEXT,
    rssi INT,
    timestamp TIMESTAMP
);

# (2.2) Upload the test dataset
\copy raddec(transmitterId, numberOfDecodings, receiverId, rssi, timestamp)
FROM 'data.csv'
DELIMITER ','
CSV HEADER

# Empty table if needed: TRUNCATE TABLE raddec;

# (2.3) Checks
\dt+
SELECT COUNT(*) FROM raddec;
SELECT COUNT(*) FROM raddec;
exit


# (3.1) Run the ETL
cd ..
python -m src.main -c config/config.json

