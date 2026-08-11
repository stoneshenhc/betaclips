from dotenv import load_dotenv
from .snowflake_client import SnowflakeClient
from .sheets_client import SheetsClient

def main() -> None:
    load_dotenv()
    sf_client = SnowflakeClient()
    result = sf_client.query("select schedule_id, name from schedules limit 100")
    sf_client.close()

    print(result)

    gs_client = SheetsClient()
    sample = [[1,2,3],[4,5,6]]
    gs_client.write(
        sheetid = '1s3ShDoegxjR5az-IX826vhApE6sCnGoEClxHuKUatHo',
        rangename = 'Sheet1!A1:C2',
        data = sample
    )

