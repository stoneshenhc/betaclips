import tomllib
from dotenv import load_dotenv
from .query_validator import QueryValidator
from .sheets_access_validator import SheetsAccessValidator
from .snowflake_client import SnowflakeClient
from .sheets_client import SheetsClient
from .drive_client import DriveClient
from .sync_job import SyncJob
from .sync_engine import SyncEngine

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

    print(config)

    for job in config.get('jobs', []):
        print(job['name'])
        # TODO: Generalize this validity response to a class
        query_validity = query_validator.validate(job['sql'])
        access_validity = sheets_validator.validate_access(job['spreadsheetid'])
        if query_validity.get('valid', False):
            print(f"Job {job['name']} has valid SQL. \033[92m\u2714\033[0m")
        else:
            query_error = query_validity.get('msg', "Error message not given")
            print(f"Job {job['name']} has invalid SQL. \033[91m\u2718\n{query_error}\033]0m")
        if access_validity.get('valid', False):
            print(f"Job {job['name']} has accessible GSheet. \033[92m\u2714\033[0m")
        else:
            access_error = access_validity.get('msg', "Error message not given")
            print(f"Job {job['name']} points to inaccessible GSheet. \033[91m\u2718\n{access_error}\033]0m")

    #for job in config.get('jobs', []):
    #    if job.get('enabled', False) and job.get('validity', {}).get('valid', False):
    #        job = SyncJob(job['name'], job['sql'], job['spreadsheetid'], job['sheetname'])
    #        engine.execute(job)
    engine.close()
