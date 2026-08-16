from dataclasses import dataclass

@dataclass
class ValidationResult:
    category: str
    success: bool
    error: str | None = None

    def describe(self, name: str, subject: str) -> str:
        if self.valid:
            return f"Job _{name}_ has valid {subject}. \033[92m\u2714\033[0m"
        else:
            return (
                f"Job _{name}_ does not have valid {subject}. "
                f"\033[91m\u2718\n{self.msg}\033[0m"
            )


class JobValidationResult:
    def __init__(self, job_name: str, results: list[ValidationResult]):
        self.job_name = job_name
        self.results = results

    @property
    def success(self) -> bool:
        return all([res.success for res in self.results])

    @property
    def error(self) -> str | None:
        errors = [f"({res.category}) {res.error}" for res in self.results if not res.success]
        error_str = '\n'.join(errors)
        return error_str or None
