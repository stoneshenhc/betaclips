# betaclips
Simple CLI program for syncing analytical queries from data warehouses to Google Sheets for last mile analysis. Name inspired by Dataclips functionality in Heroku.

## Overview
Betaclips takes a list of jobs, each specifying a database query and a Google Sheet destination, and runs them. Column headers are automatically bolded on the Google Sheet side with a note in A1 specifying the last sync time. Note that you are on the hook for the actual scheduling of these jobs if you want them to run automatically.

## Installation
[Coming soon using git-based tag-pinned install]

### Authentication
After installation, make sure to run `betaclips init` to create all the necessary configuration directories and a starting config template.

Your Snowflake connection and auth method are defined within the main config toml file under the heading `[snowflake]`. The starting template is based off of key-pair authentication, but any method supported by using the connection login parameters can be used. You can view the [Snowflake documentation page here](https://docs.snowflake.com/en/developer-guide/python-connector/python-connector-connect) for more detailed information.

For Google, follow the [official documentation](https://developers.google.com/workspace/guides/create-credentials#service-account) to create a service account, an associated key, and download the json. Rename the json file `betaclips-service-account.json` and put it into the specific credentials folder that was created by the `betaclips init` command (it can be rerun to echo back where all the folder locations are). Note that you will have to share any spreadsheet you want betaclips to sync into with the service account you just created prior.

## Usage
The following commands are supported:

```
betaclips init                                  creates all necessary config and log folders and templates
betaclips validate -j --job-names ...           smoke screen tests all/specific jobs
betaclips sync -j --job-names ...               runs the sync for all/specific jobs
```

If not job names are specified by `validate` or `sync` then all enabled jobs will be in scope. Jobs are defined in the `config.toml` that is generated from the `init` command. The initial template lays out all the supported parameters of a given job.

## Final words
Thanks and happy syncing!
