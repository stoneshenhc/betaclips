from dataclasses import dataclass

@dataclass
class ValidationResult:
    category: str
    success: bool
    error: str | None = None


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
