import tomllib
from dotenv import load_dotenv
from betaclips.validation.query_validator import QueryValidator
from betaclips.validation.sheets_access_validator import SheetsAccessValidator
from betaclips.clients.snowflake_client import SnowflakeClient
from betaclips.clients.sheets_client import SheetsClient
from betaclips.clients.drive_client import DriveClient
from betaclips.sync_job import SyncJob
from betaclips.sync_engine import SyncEngine

def main() -> None:
    load_dotenv()
    sf_client = SnowflakeClient()
    sheets_client = SheetsClient()
    drive_client = DriveClient()
    engine = SyncEngine(sf_client, sheets_client)
    query_validator = QueryValidator(sf_client)
    sheets_validator = SheetsAccessValidator(drive_client)

    with open("./config/jobs.toml", "rb") as f:
        config = tomllib.load(f)

    for job in config.get('jobs', []):
        query_validity = query_validator.validate(job['sql'])
        access_validity = sheets_validator.validate_access(job['spreadsheetid'])
        print(query_validity.describe(job['name'], 'SQL'))
        print(access_validity.describe(job['name'], 'GSheet file access'))

    #for job in config.get('jobs', []):
    #    if job.get('enabled', False) and job.get('validity', {}).get('valid', False):
    #        job = SyncJob(job['name'], job['sql'], job['spreadsheetid'], job['sheetname'])
    #        engine.execute(job)
    engine.close()
