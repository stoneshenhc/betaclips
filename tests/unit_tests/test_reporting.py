from betaclips.results.run_result import RunResult
from betaclips.results.reporting import get_report

def test_report_template():
    results = [
        RunResult('job1', True, 5000, 2, None),
        RunResult('job2', True, 200, 10, None),
        RunResult('job3', False, None, None, "TypeA error happened"),
        RunResult('job4', False, None, None, "TypeB error happened"),
    ]
    printout = get_report('run', results)
    assert printout == (
        "\033[1mrun report:\033[0m\n"
        "2/4 runs succeeded.\n"
        "2/4 runs failed.\n"
        "Names of failed runs: ['job3', 'job4']\n"
        "Failed runs errors:\n"
        "job3 - TypeA error happened\n"
        "job4 - TypeB error happened"
    )

