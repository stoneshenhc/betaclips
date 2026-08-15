from betaclips.validation.query_validator import QueryValidator
from betaclips.validation.sheets_access_validator import SheetsAccessValidator
from betaclips.validation.result import JobValidationResult
from betaclips.sync_job import SyncJob


class ValidationEngine:
    def __init__(
        self,
        query_validator: QueryValidator,
        access_validator: SheetsAccessValidator,
    ):
        self.query_validator = query_validator
        self.access_validator = access_validator

    def validate(self, job: SyncJob) -> JobValidationResult:
        query_check = self.query_validator.validate(job.query)
        access_check = self.access_validator.validate(job.spreadsheet_id)
        return JobValidationResult(query_check, access_check)

    def validate_all(self, jobs: list[SyncJob]) -> list[JobValidationResult]:
        # TODO: Add error handling functionality, error does not kill the
        # validation. Otherwise this method is useless.
        # return [self.validate(job) for job in jobs]
        pass
