import logging
import tomllib
import os

from betaclips.validation.query_validator import QueryValidator
from betaclips.validation.sheets_access_validator import SheetsAccessValidator
from betaclips.validation.validation_engine import ValidationEngine
from betaclips.clients.snowflake_client import SnowflakeClient
from betaclips.clients.sheets_client import SheetsClient
from betaclips.clients.drive_client import DriveClient
from betaclips.results.run_result import RunResult
from betaclips.results.validation_results import JobValidationResult
from betaclips.results.reporting import log_result
from betaclips.sync_job import SyncJob
from betaclips.sync_engine import SyncEngine
from betaclips.exceptions import JobError
from betaclips.config import (
    RUN_RESULTS_FILE,
    GOOGLE_SERVICE_ACCOUNT_JSON,
    load_config,
    resolve_env_secrets,
)

logger = logging.getLogger(__name__)

def sync_jobs(job_names: list | None = None) -> list[RunResult]:
    config = load_config()
    conn_params = config['snowflake']
    conn_params = resolve_env_secrets(conn_params)
    sf_client = SnowflakeClient(**conn_params)
    sheets_client = SheetsClient.from_service_account(
        GOOGLE_SERVICE_ACCOUNT_JSON
    )
    sync_engine = SyncEngine(sf_client, sheets_client)

    jobs = [
        job for job in config.get('jobs', []) if job.get('enabled', True)
    ]
    if job_names is not None:
        jobs = [job for job in jobs if job.get('name') in job_names]
    sync_jobs = [SyncJob.from_dict(job) for job in jobs]
    run_results = []
    if len(sync_jobs) == 0:
        logger.info("No matching jobs to sync")
        return []
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
    logger.info("Sync finished")
    return run_results

def validate_jobs(job_names: list | None = None) -> list[JobValidationResult]:
    config = load_config()
    conn_params = config['snowflake']
    conn_params = resolve_env_secrets(conn_params)
    sf_client = SnowflakeClient(**conn_params)
    drive_client = DriveClient.from_service_account(
        GOOGLE_SERVICE_ACCOUNT_JSON
    )
    query_validator = QueryValidator(sf_client)
    sheets_validator = SheetsAccessValidator(drive_client)
    validation_engine = ValidationEngine(query_validator, sheets_validator)
    jobs = [
        job for job in config.get('jobs', []) if job.get('enabled', True)
    ]
    if job_names is not None:
        jobs = [job for job in jobs if job.get('name') in job_names]
    sync_jobs = [SyncJob.from_dict(job) for job in jobs]
    val_results = []
    if len(sync_jobs) == 0:
        logger.info("No matching jobs to validate")
        return []
    logger.info("Validations starting")
    for sync_job in sync_jobs:
        validation = validation_engine.validate(sync_job)
        val_results.append(validation)
    validation_engine.close()
    logger.info("Validation finished")
    return val_results
