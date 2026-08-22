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
from betaclips.config import (
    CONFIG_FILE,
    LOG_FILE,
    RUN_RESULTS_FILE,
    SNOWFLAKE_PKEY_FILE,
    GOOGLE_SERVICE_ACCOUNT_JSON,
)

logger = logging.getLogger(__name__)

# TODO: Init to create all filepaths for files
def main() -> None:
    logging.basicConfig(
        filename=LOG_FILE,
        encoding='utf8',
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        level=logging.INFO,
    )

    with open(CONFIG_FILE, "rb") as f:
        config = tomllib.load(f)
    logger.info("Snowflake credentials and job configs loaded")

    conn_params = config['snowflake']
    conn_params['private_key_file'] = SNOWFLAKE_PKEY_FILE
    if 'private_key_file_pwd' not in conn_params:
        conn_params['private_key_file_pwd'] = get_passphrase(config)

    sf_client = SnowflakeClient(**conn_params)
    sheets_client = SheetsClient.from_service_account(
        GOOGLE_SERVICE_ACCOUNT_JSON
    )
    drive_client = DriveClient.from_service_account(
        GOOGLE_SERVICE_ACCOUNT_JSON
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
            log_result(result, RUN_RESULTS_FILE)
            run_results.append(result)
    finally:
        sync_engine.close()
    print('\n' + get_report('run', run_results))
    logger.info("Sync finished")

# TODO: remove this?
def validate_timeout(value) -> int:
    timeout = int(value)
    if not 0 <= timeout <= 86400:
        raise ValueError(
            f"Timeout: {timeout} not allowed; must be set between 0 and "
            f"86400 seconds"
        )
    else:
        return timeout

# TODO: find antoher place for this
def get_passphrase(config: dict) -> str:
    env_var_name = config['snowflake'].get('private_key_file_pwd_env')
    return os.environ(env_var) if env_var_name else None
