# betaclips
Simple tool for syncing analytical queries from data warehouses to Google Sheets for last mile analysis. Name inspired by Dataclips functionality in Heroku.

## Overview
This is currently **under active development** and is not ready for real world usage. Snowflake is the only supported data warehouse for now.

Betaclips allows you to define a list of jobs by specifying for each job:
- The SQL query to be run
- The Google Sheet file and tab for the result to land in

and will sync the query into the sheet. As simple as that.

## Installation
For now while this is under initial development, this is a janky dev-orientated process. Make sure you have `uv` installed first and then clone this repo locally.

### Authentication
You'll need to set up credentials on the Snowflake side and the Google side.

For Snowflake, follow the [official documentation](https://docs.snowflake.com/en/user-guide/key-pair-auth) on configuring key pair auth for your account. Move both the public key file and private key file inside a `credentials/` folder at the root of the project.

Also create a `.env` at the root of the project to hold your connection settings for Snowflake, e.g.:
```env
SNOWFLAKE_ACCOUNT=ACCOUNTID
SNOWFLAKE_USER=USERNAME
SNOWFLAKE_WAREHOUSE=WAREHOUSE
SNOWFLAKE_PRIVATE_KEY_PATH=./credentials/rsa_key.p8
SNOWFLAKE_PRIVATE_KEY_PASSPHRASE=PASSPHRASE
```

For Google, follow the [official documentation](https://developers.google.com/workspace/guides/create-credentials#service-account) to create a service account and an associated key. Take the `credentials.json` file and put it into the `credentials/` folder that was created earlier. Note that you will have to share any spreadsheet you want betaclips to sync into with the service account you just created prior.

### Usage
Run `uv sync` at the root of the cloned repo to finish installation.

And then create a new `config/jobs.toml` file at the root of the project where you will define your jobs as follows:
```toml
timeout = 120

[[jobs]]
name = "name for job 1"
sql = """
SELECT *
FROM sometable
LIMIT 100"""
spreadsheetid = "longstring"
sheetname = "Sheet1"
enabled = True

[[jobs]]
# same for every job you want...
```

Finally doing a `uv run betaclips` will reach out to Snowflake and do a one time sync of all queries into Google Sheets
