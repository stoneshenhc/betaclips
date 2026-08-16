import json
from dataclasses import asdict
from pathlib import Path

from betaclips.results.run_result import RunResult


RESULTS_DIR_PATH = 'logs'
RESULTS_FILENAME = 'jobresults.jsonl'

def log_result(
    result: RunResult,
    dir_path: str = RESULTS_DIR_PATH,
    filename: str = RESULTS_FILENAME,
    ) -> None:
    result_dict = asdict(result)
    try:
        with open(f"{dir_path}/{filename}", 'a') as f:
            f.write(json.dumps(result_dict, default=str) + '\n')
    except FileNotFoundError as error:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        with open(f"{dir_path}/{filename}", 'a') as f:
            f.write(json.dumps(result_dict, default=str) + '\n')

def get_report(results: list[RunResult]) -> str:
    good_runs = len([res for res in results if res.status == 'success'])
    bad_runs = len([res for res in results if res.status == 'failure'])
    bad_names = [res.name for res in results if res.status == 'failure']
    total_runs = len(results)
    return (
        "\033[1mJob runs results:\033[0m\n"
        f"{good_runs}/{total_runs} jobs succeeded.\n"
        f"{bad_runs}/{total_runs} jobs failed.\n"
        f"Names of failed jobs: {bad_names}"
    )
