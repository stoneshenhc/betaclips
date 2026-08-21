import logging
import tomllib
import json
import os

from dotenv import load_dotenv

from betaclips.validation.query_validator import QueryValidator
from betaclips.validation.sheets_access_validator import SheetsAccessValidator
from betaclips.validation.validation_engine import ValidationEngine
from betaclips.clients.snowflake_client import SnowflakeClient
from betaclips.clients.sheets_client import SheetsClient
from betaclips.clients.drive_client import DriveClient
from betaclips.results.run_result import RunResult
from betaclips.results.reporting import log_result, get_report
from betaclips.sync_job import SyncJob
from betaclips.sync_engine import SyncEngine
from betaclips.exceptions import JobError

SERVICE_ACCOUNT_FILEPATH = './credentials/betaclips-service-account.json'

logger = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(
        filename='app.log',
        encoding='utf8',
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        level=logging.INFO,
    )
    load_dotenv()
    with open("./config/jobs.toml", "rb") as f:
        config = tomllib.load(f)
    timeout = config.get('timeout', None)
    logger.info("Snowflake credentials and job configs loaded")

    session_params = {}
    if timeout is not None:
        session_params[
            'STATEMENT_TIMEOUT_IN_SECONDS'
        ] = validate_timeout(timeout)
    conn_params = {
        'account': os.environ['SNOWFLAKE_ACCOUNT'],
        'user': os.environ['SNOWFLAKE_USER'],
        'authenticator': 'SNOWFLAKE_JWT',
        'warehouse': os.environ['SNOWFLAKE_WAREHOUSE'],
        'database': os.environ['SNOWFLAKE_DATABASE'],
        'schema': os.environ['SNOWFLAKE_SCHEMA'],
        'role': os.environ['SNOWFLAKE_ROLE'],
        'secondary_roles': os.environ['SNOWFLAKE_SECONDARY_ROLES'],
        'private_key_file': os.environ['SNOWFLAKE_PRIVATE_KEY_PATH'],
        'private_key_file_pwd': (
            os.environ['SNOWFLAKE_PRIVATE_KEY_PASSPHRASE']
        ),
        'session_parameters': session_params
    }

    sf_client = SnowflakeClient(**conn_params)
    sheets_client = SheetsClient.from_service_account(
        SERVICE_ACCOUNT_FILEPATH
    )
    drive_client = DriveClient.from_service_account(
        SERVICE_ACCOUNT_FILEPATH
    )
    query_validator = QueryValidator(sf_client)
    sheets_validator = SheetsAccessValidator(drive_client)
    validation_engine = ValidationEngine(query_validator, sheets_validator)
    sync_engine = SyncEngine(sf_client, sheets_client)

    jobs = [
        job for job in config.get('jobs', []) if job.get('enabled', True)
    ]
    sync_jobs = [
        SyncJob(
            job['name'], job['sql'], job['spreadsheet_id'], job['sheet_name']
        )
        for job in jobs
    ]
    val_results = []
    run_results = []

    logger.info("Validations starting")
    for sync_job in sync_jobs:
        validation = validation_engine.validate(sync_job)
        val_results.append(validation)
    validation_engine.close()
    print(get_report('validation', val_results))
    logger.info("Validation finished")

    logger.info("Sync starting")
    try:
        for sync_job in sync_jobs:
            try:
                result = sync_engine.execute(sync_job)
            except JobError as error:
                result = RunResult(
                    sync_job.name,
                    False,
                    None,
                    None,
                    str(error),
                )
                logger.error(
                    "Job failed - name=%s: %s",
                    sync_job.name, 
                    error,
                )
            log_result(result)
            run_results.append(result)
    finally:
        sync_engine.close()
    print('\n' + get_report('run', run_results))
    logger.info("Sync finished")

def validate_timeout(value) -> int:
    timeout = int(value)
    if not 0 <= timeout <= 86400:
        raise ValueError(
            f"Timeout: {timeout} not allowed; must be set between 0 and "
            f"86400 seconds"
        )
    else:
        return timeout
