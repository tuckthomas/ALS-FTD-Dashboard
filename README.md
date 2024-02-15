# ALS-FTD-Dashboard
As part of a non-profit/volunteer contribution, this is the repository to an upcoming Dashboard summarizing the current state of ALS/FTD research, with a preliminary focus on familial ALS/FTD.

# Current State
**This is a work in progress.** The API functionaltiy is working with an initial amount of identifed fields that were requested, though additional fields will be added soon.

**The front-end has not yet been developed.** I am still contimplating the best front-end approach. Whether it be with custom graphs, charts, and tables. Though, I am currently leaning towards using Metabase as the Dashboard front-end.

# Requirements
This project depends on several Python packages. Below is a breakdown of the required packages, along with optional dependencies if you're using PostgreSQL as your database.

**Python Version:** 3.9.2

## Django and Core Dependencies
These packages are required for the project to run:

- `Django==4.2.10` - The web framework used.
- `django-ninja==1.1.0` - For building APIs with Django.
- `beautifulsoup4==4.12.3` - For parsing HTML and XML documents.
- `numpy==1.26.4` - For numerical operations.
- `pandas==2.2.0` - For data manipulation and analysis.
- `openpyxl==3.1.2` - For reading/writing Excel 2010 xlsx/xlsm files.
- `pydantic==2.6.1` - Data validation and settings management using python type annotations.
- `ipython==7.20.0` - For interactive computing.
- `requests==2.25.1` - For making HTTP requests.

## Database Drivers
I opted to use my existing PostgreSQL database. Depending on your database choice, you might need specific drivers:

- `mysqlclient==1.4.4` - A MySQL driver (Optional, only if using MySQL).
- `psycopg2-binary==2.9.9` - A PostgreSQL driver (Optional, specifically for PostgreSQL users).

## Other Dependencies
The following packages might be used for specific functionalities within the project. They are not strictly required for the core functionality but may enhance the project's capabilities or are dependencies of the above packages:

- `asgiref==3.7.2`
- `certifi==2020.6.20`
- `chardet==4.0.0`
- `cryptography==3.3.2`
- `idna==2.10`
- `python-dateutil==2.8.2`
- `pytz==2021.1`
- `sqlparse==0.4.1`
- `urllib3==1.26.5`

## Optional Packages
These packages are optional and might be required under specific circumstances or for development purposes:

- `ipython_genutils==0.2.0`, `jedi==0.18.0`, `parso==0.8.1`, `pexpect==4.8.0`, `pickleshare==0.7.5`, `prompt-toolkit==3.0.14`, `Pygments==2.7.1`, `traitlets==5.0.5`, `wcwidth==0.1.9` - For enhanced IPython interaction.
- `pyOpenSSL==20.0.1`, `pycurl==7.43.0.6`, `pycurl-wrapper===2.0-2-g027c28a` - For secure connection handling and HTTP requests.
