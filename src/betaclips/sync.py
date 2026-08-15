import tomllib
import json
from dotenv import load_dotenv
from dataclasses import asdict
from betaclips.validation.query_validator import QueryValidator
from betaclips.validation.sheets_access_validator import SheetsAccessValidator
from betaclips.validation.validation_engine import ValidationEngine
from betaclips.validation.result import JobValidationResult
from betaclips.clients.snowflake_client import SnowflakeClient
from betaclips.clients.sheets_client import SheetsClient
from betaclips.clients.drive_client import DriveClient
from betaclips.sync_job import SyncJob
from betaclips.sync_engine import SyncEngine
from betaclips.exceptions import JobError
from betaclips.run_result import RunResult

def main() -> None:
    load_dotenv()
    with open("./config/jobs.toml", "rb") as f:
        config = tomllib.load(f)
    timeout = config.get('timeout', None)

    sf_client = SnowflakeClient(timeout)
    sheets_client = SheetsClient()
    drive_client = DriveClient()
    query_validator = QueryValidator(sf_client)
    sheets_validator = SheetsAccessValidator(drive_client)
    validation_engine = ValidationEngine(query_validator, sheets_validator)
    sync_engine = SyncEngine(sf_client, sheets_client)

    jobs = [job for job in config.get('jobs', []) if job.get('enabled', True) == True]
    sync_jobs = [SyncJob(job['name'], job['sql'], job['spreadsheetid'], job['sheetname']) for job in jobs]
    for sync_job in jobs:
        validation = validation_engine.validate(sync_job)
        print(validation.describe(sync_job.name))
    try:
        for sync_job in sync_jobs:
            try:
                result = sync_engine.execute(sync_job)
                print(result)
                log_result(result)
            except JobError as error:
                result = RunResult(sync_job.name, 'failure', None, None, str(error))
                print(result)
                log_result(result)
                # log it
    finally:
        sync_engine.close()

# TODO: Move into its own module
def log_result(result: RunResult, log_path: str = 'jobresults.jsonl') -> None:
    result_dict = asdict(result)
    result_dict['timestamp'] = 'test'
    with open(log_path, 'a') as f:
        f.write(json.dumps(result_dict) + '\n')
