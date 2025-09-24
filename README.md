paretl-postgres
===============

Pareto Anywhere ETL ("paretl") for PostgreSQL.
This program applies transformation and filter operations on the raw data, and load it into a new table.
The resulting processed data is hence expected to be cleaner and easier to retrieve.
A watchdog process enables the overview of the full operation.

# Quick HOW-TO

You can use the ETL process either with the scripts directly or using a docker image.

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

Run the ETL:

`python -m src.main -c config/config.json`


## Result

Your database contains now two additional tables:
* etl_raddec: filtered data
* etl_watchdog: performances of the ETL process

# Configuring the ETL

# Expected data contents and metrics

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