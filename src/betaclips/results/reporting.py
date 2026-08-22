import json
from dataclasses import asdict
from pathlib import Path

from betaclips.results.run_result import RunResult
from betaclips.results.validation_results import JobValidationResult


def create_log_dir(dir_path) -> None:
    Path(dir_path).mkdir(parents=True, exist_ok=True)

def log_result(
    result: RunResult,
    file_path: Path,
    ) -> None:
    result_dict = asdict(result)
    try:
        with open(file_path, 'a') as f:
            f.write(json.dumps(result_dict, default=str) + '\n')
    except FileNotFoundError as error:
        dir_path = file_path.parent
        if not dir_path.is_dir():
            create_log_dir(dir_path)
        with open(file_path, 'a') as f:
            f.write(json.dumps(result_dict, default=str) + '\n')

def get_report(
        heading: str,
        results: list[RunResult] | list[JobValidationResult]
    ) -> str:
    good_runs = len([res for res in results if res.success])
    bad_runs = len([res for res in results if not res.success])
    bad_names = [res.job_name for res in results if not res.success]
    total_runs = len(results)
    error_strs = [f"{res.job_name} - {res.error}" for res in results if not res.success]
    error_str = '\n'.join(error_strs)
    full_report = (
        f"\033[1m{heading} report:\033[0m\n"
        f"{good_runs}/{total_runs} {heading}s succeeded.\n"
        f"{bad_runs}/{total_runs} {heading}s failed.\n"
    )
    if bad_runs > 0:
        full_report += (
            f"Names of failed {heading}s: {bad_names}\n"
            f"Failed {heading}s errors:\n"
            f"{error_str}"
        )
    return full_report
