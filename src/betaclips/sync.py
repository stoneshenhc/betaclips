import tomllib
from dotenv import load_dotenv
from .query_validator import QueryValidator
from .snowflake_client import SnowflakeClient
from .sheets_client import SheetsClient
from .sync_job import SyncJob
from .sync_engine import SyncEngine

def main() -> None:
    load_dotenv()
    sf_client = SnowflakeClient()
    sheets_client = SheetsClient()
    engine = SyncEngine(sf_client, sheets_client)
    validator = QueryValidator(sf_client)

    with open("./config/jobs.toml", "rb") as f:
        config = tomllib.load(f)

    for job in config.get('jobs', []):
        job['validity'] = validator.validate(job['sql'])
        if job.get('validity', {}).get('valid', False):
            print(f"Job {job['name']} has valid SQL. \033[92m\u2714\033[0m")
        else:
            error_msg = job.get('validity', {}).get('msg', "Error message not given")
            print(f"Job {job['name']} has invalid SQL. \033[91m\u2718\n{error_msg}\033]0m")

    for job in config.get('jobs', []):
        if job.get('enabled', False) and job.get('validity', {}).get('valid', False):
            job = SyncJob(job['name'], job['sql'], job['spreadsheetid'], job['sheetname'])
            engine.execute(job)
    engine.close()
