from dotenv import load_dotenv
from .sync_job import SyncJob

def main() -> None:
    load_dotenv()
    sql = "select schedule_id, name from schedules limit 100"
    job = SyncJob(sql, '1s3ShDoegxjR5az-IX826vhApE6sCnGoEClxHuKUatHo')
    job.execute()
