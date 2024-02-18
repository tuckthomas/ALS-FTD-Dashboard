# ALS & FTD Clinical Trial Research Dashboard
As part of a non-profit/volunteer contribution, this is the repository to an upcoming Dashboard summarizing the current and historical state of ALS/FTD research, with a preliminary focus on familial ALS/FTD; allowing for further data exploration.

**This is a work in progress.** The API functionaltiy is working with an initial amount of identifed fields that were requested, though additional fields will be added soon. **Furthermore, I still have quite a bit of data cleanup, normalization, and validation to complete.** I am sharing this as-is in case anyone is interested in contributing.

**The front-end has not yet been developed.** I am still contemplating the best front-end approach. Whether it be with custom graphs, charts, and tables. Though, I am currently leaning towards using Metabase as the Dashboard front-end.

# Familial ALS Personal Impact and Donation Link
Within my lifetime, I have witnessed SOD1 Familial ALS claim the lives of my grandmother, my uncle, my father, and most recently my aunt. Our greater extended family has also suffered losses. [Click here to learn more about fALS's impact on my family and I.](https://www.tuckstime.com/)

If you appreciate this work and would like to suppport it, please remit donations to one of the following charities:
- [Everything ALS](https://www.everythingals.org/donate)
- [ALS Hope Foundation](https://www.alshf.org/donate)

# System Requirements
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

## Optional Metabase Front-End Requirements
**What is Metabase?** [Metabase](https://github.com/metabase/metabase) is open-source business intelligence tool that enables users to explore, visualize, and share data insights without the need for extensive technical knowledge. It allows for easy querying through a user-friendly interface, making it accessible for users to generate reports and dashboards from their data sources.

To use Metabase as the dashboard front-end, Docker is required for installation. Ensure Docker is installed and running on your system. I am running Debian 12 within a Proxmox LXC. If using a similar setup or Debian-based system, here's how to install Metabase using Docker:

- Ensure Docker is installed on your system. For Debian-based systems:
  ```sh
  apt-get update
  apt-get install apt-transport-https ca-certificates curl gnupg lsb-release
  curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
  apt-get update
  apt-get install docker-ce docker-ce-cli containerd.io

- Pull latest Metabase image from Docker and run Metabase:
  ```sh
  docker pull metabase/metabase:latest
  docker run -d -p 3000:3000 --name metabase metabase/metabase # Replace Port '3000' with Different Port if Desired
  
- Install PyJWT for Embedding Metabase Dashboard into Webpage:
  ```sh
  pip install PyJWT

Here is an early example of a dashboard using Metabase:

![Early-Metabase-Dashboard-Example](media/Early-Metabase-Dashboard-Example.jpg)

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
