import tomllib
from dotenv import load_dotenv
from betaclips.validation.query_validator import QueryValidator
from betaclips.validation.sheets_access_validator import SheetsAccessValidator
from betaclips.validation.validation_engine import ValidationEngine
from betaclips.validation.result import JobValidationResult
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
    query_validator = QueryValidator(sf_client)
    sheets_validator = SheetsAccessValidator(drive_client)
    validation_engine = ValidationEngine(query_validator, sheets_validator)
    sync_engine = SyncEngine(sf_client, sheets_client)

    with open("./config/jobs.toml", "rb") as f:
        config = tomllib.load(f)

    jobs = [SyncJob(job['name'], job['sql'], job['spreadsheetid'], job['sheetname']) for job in config.get('jobs', [])]
    for sync_job in jobs:
        validation = validation_engine.validate(sync_job)
        print(validation.describe(sync_job.name))
    #for job in config.get('jobs', []):
    #    if job.get('enabled', False) and job.get('validity', {}).get('valid', False):
    #        job = SyncJob(job['name'], job['sql'], job['spreadsheetid'], job['sheetname'])
    #        engine.execute(job)
    sync_engine.close()
