paretl-postgres
===============

Pareto Anywhere ETL ("paretl") for PostgreSQL.
This program applies transformation and filter operations on the raw data, and load it into a new table.
The resulting processed data is hence expected to be cleaner and easier to retrieve.
A watchdog process enables the overview of the full operation.

# Quick HOW-TO

You can use the ETL process either with the scripts directly or using a docker image.

## Conditions

You need a local postgresql database with a `raddec` table whose columns are:
* **transmitterid** (alphanumeric variable): MAC address of the transmitting device  
* **receiverid** (alphanumeric variable): MAC address of the receiving device  
* **numberofdecodings** (integer variable): number of signals from the transmitter observed by the receiver during one minute  
* **rssi** (integer variable): detection power  
* **timestamp** (time variable YYYY-MM-DD HH:MM:SS): time of detection  


## Using Docker

The ETL is avalaible as a docker image stored in Docker Hub.

Make sure you have docker installed:

`docker --version`

if you don't have docker, install it:

`sudo snap install docker`

Pull the docker image:

`sudo docker pull prudentxavier/paretl:latest`

Check you have the image:

`sudo docker images`

Download the configuration file

`mkdir config`

`wget https://github.com/reelyactive/paretl-postgres/blob/ba47af6cf082b0998bd76e4b162a28f9adafa697/config/config.json` 

`sudo docker run \
  --add-host=host.docker.internal:host-gateway \
  -v $(pwd)/config:/app/config \
  prudentxavier/paretl:latest python -m src.main -c config/config.json`

## Using the plain code

Make sure you have the following configuration (consider using a [dedicated environment](https://www.youtube.com/watch?v=IAvAlS0CuxI) like [anaconda](https://youtu.be/hVcEv7rEN24?si=xHN6zLnYidVYLEej)):

* Python 3.13

Python libraries:
* pandas
* psycopg2-binary
* sqlalchemy
* psutil
* tabulate
* logging
* argparse

If missing you can install them using:

`pip install <LIBRARY NAME>`

Retrieve the code:

`git clone https://github.com/reelyactive/paretl-postgres.git`

Go to the ETL repository:

`cd paretl-postgres`

In the configuration file `config/config.json`, make sure that the DB host link be set to:

`"db_host": "localhost"`

Run the ETL:

`python -m src.main -c config/config.json`

## Result

Your database contains now two additional tables:
* etl_raddec: filtered data
* etl_watchdog: performances of the ETL process

The `etl_raddec` table contains the rows of the `raddec` table that passed the filters defined in the configuration file. Its columns are the same as the raddec's, plus various metrics:

* **time_window** (numeric variable): duration in seconds between the first and the last observation of a transmitter over all the receivers  
* **max_rssi** (numeric variable): maximum observed detection power rssi of a transmitter over all the receivers  
* **nb_counts** (integer variable): total number of observations of a transmitter over all the receivers  
* **digit_2** (alphanumeric variable): second character of the MAC address of the transmitter  
* **isPrivate** (boolean): does the MAC address of the transmitter correspond to a private device  
* **date** (date variable): simple conversion of timestamp to date  
* **watchdog_id** (table key): processing index, to be crossed with the primary key of the `etl_watchdog` table  


The `etl_watchdog` table contains one row per ETL processing with the following columns:

* **id** (table primary key): processing index  
* **event_name** (alphanumeric variable): name of the event during which the receivers have been deployed, defined in the configuration file  
* **ts** (time variable): timestamp of the processing  
* **rows** (integer variable): number of rows  
* **duration_sec** (integer variable): duration in seconds of the ETL processing  
* **cpu_percent** (numeric variable): fraction of the local CPU used for the ETL processing  
* **memory_mb** (numeric variable): RAM in Mb used for the ETL processing  
* **n_transmitters** (integer variable): number of transmitters observed in the filtered raddec table  
* **n_transmitters_per_day** (alphanumeric variable YYYY-MM-DD: N): number of transmitters per day observed in the filtered raddec table  
* **median_time_window** (numeric variable): [median](https://en.wikipedia.org/wiki/Median) time window of the transmitters in the filtered raddec table  
* **mean_time_window** (numeric variable): [mean](https://en.wikipedia.org/wiki/Arithmetic_mean) time window of the transmitters in the filtered raddec table  
* **std_time_window** (numeric variable): [standard deviation](https://en.wikipedia.org/wiki/Standard_deviation) (spread) time window of the transmitters in the filtered raddec table  



# Configuring the ETL

The ETL process requires as unique imput a json configuration file. An example of such file can be found in:

`config/config.json`

## Content of the json configuration file

The configuration file requires the following fields:

* **event_name** : name of the event (for instance "F1 Montreal 2022")
* **start_ts** : start timestamp in the raddec table for ETL in format YYYY-MM-DD HH:MM:SS
* **end_ts** : end timestamp in the raddec table for ETL in format YYYY-MM-DD HH:MM:SS
* **receivers_id** : list of receiver IDs (array of strings)
* **db_type** : database type (currently supported "postgresql")
* **db_host** : database host ("host.docker.internal" if running with docker, "localhost" if running with plain code)
* **db_port** : database port (typically 5432)
* **db_user** : database username
* **db_pass** : database password
* **db_name** : database name
* **source_table** : source table name (typically "raddec")
* **target_table** : target table name (typically "etl_raddec")
* **watchdog_table** : watchdog table name (typically "etl_watchdog")
* **log_level** : logging level ("INFO", "DEBUG", "ERROR")
* **dry_run** : boolean flag (true/false) to enable dry-run mode (no DB writes)
* **filtering** : list of filtering rules, each object containing:
  * **name** : user defined filter name (for instance "Trying a filter on time window")
  * **col** : column name to filter on, must be a column of the `etl_raddec` table (see above) (for instance "time_window")
  * **op** : operator (==, !=, >=, <=, <, >)
  * **val** : filter value (string, number, or boolean)


## Creating the json configuration file

Even though such a json file can easily be created using any text editor, you are welcome to use the following local webpage:

`tools/create_config.html`

1. click on the html document, which should open in a browser
2. fill the configuration fileds
3. click generate JSON

You will need a csv file with all the receivers, from which you can then pick the ones used at that event, for instance:

|                 |
|-----------------|
| 02a3416dc4f7    |
| 02a3bd59e2dc    |
| 02a3e5351a16    |
| 02a37341e3ff    |
| 02a384aafe9f    |
| 02a38b484e43    |



You can then add an arbitrary number of user defined filters.

# Building the ETL

# Testing the ETL

# Structure of the ETL


Contributing
------------

Discover [how to contribute](CONTRIBUTING.md) to this open source project which upholds a standard [code of conduct](CODE_OF_CONDUCT.md).


Security
--------

Consult our [security policy](SECURITY.md) for best practices using this open source software and to report vulnerabilities.


License
-------

MIT License

Copyright (c) 2025 [reelyActive](https://www.reelyactive.com)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN 
THE SOFTWARE.