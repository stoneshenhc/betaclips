import tomllib
from dotenv import load_dotenv
from .sync_job import SyncJob

def main() -> None:
    load_dotenv()
    with open("./config/jobs.toml", "rb") as f:
        config = tomllib.load(f)

    for job in config.get('jobs', []):
        if job.get('enabled', False):
            job = SyncJob(job['sql'], job['spreadsheetid'], job['sheetname'])
            job.execute()
