# betaclips
A small and simple CLI program for syncing analytical queries from Snowflake to Google Sheets for last mile analysis.

## Installation
One of:
```
pipx install "git+https://github.com/stoneshenhc/betaclips.git@v0.1.0"
uv tool install "git+https://github.com/stoneshenhc/betaclips.git@v0.1.0"
```

### Authentication
After installation, make sure to run `betaclips init` to create all the necessary configuration directories and a starting config template.

Your Snowflake connection and auth method are defined within the main config toml file under the heading `[snowflake]`. The starting template is based off of key-pair authentication, but any method supported by using the connection login parameters can be used. You can view the [Snowflake documentation page here](https://docs.snowflake.com/en/developer-guide/python-connector/python-connector-connect) for more detailed information.

For Google, follow the [official documentation](https://developers.google.com/workspace/guides/create-credentials#service-account) to create a service account, an associated key, and download the json. Rename the json file `betaclips-service-account.json` and put it into the specific credentials folder that was created by the `betaclips init` command (it can be rerun to echo back where all the folder locations are). Note that you will have to share any spreadsheet you want betaclips to sync into with the service account you just created prior.

## Usage
The following commands are available:

```
usage: betaclips {init,validate,sync} ...
positional arguments:
  {init,validate,sync}  Choose what you want betaclips to do
    init                Sets up the initial folders required for betaclips
    validate            Runs series of smoke checks on configured jobs
    sync                Executes a sync run of all enabled configured jobs

usage: betaclips init

usage: betaclips validate [-j JOB_NAMES [JOB_NAMES ...]]
options:
  -j JOB_NAMES [JOB_NAMES ...], --job-names JOB_NAMES [JOB_NAMES ...]
                        Run checks on one specific job

usage: betaclips sync [-j JOB_NAMES [JOB_NAMES ...]]
options:
  -j JOB_NAMES [JOB_NAMES ...], --job-names JOB_NAMES [JOB_NAMES ...]
                        Executes a sync run of one specific job
```

Jobs are defined in the `config.toml` that is generated from the `init` command. The initial template lays out all the supported parameters of a given job.

In addition, betaclips supports:
- Bolding of column headers in Google Sheets
- Notes in all written-to Google Sheets indicating time of last sync
- Chunks large query result sets into 2MB batch writes to Sheets for performance
- Environment variable indirection in snowflake config parameters using `_env` suffix for keys

Note that you are on the hook for scheduling or distributing these syncs.
