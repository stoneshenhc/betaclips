class ValidationResult:
    def __init__(self, valid: bool, msg: str | None):
        self.valid = valid
        self.msg = msg

    def describe(self, name: str, subject: str) -> str:
        if self.valid:
            return f"Job _{name}_ has valid {subject}. \033[92m\u2714\033[0m"
        else:
            return (
                f"Job _{name}_ does not have valid {subject}. "
                f"\033[91m\u2718\n{self.msg}\033[0m"
            )


class JobValidationResult:
    def __init__(
        self,
        query_check: ValidationResult,
        access_check: ValidationResult,
    ):
        self.query_check = query_check
        self.access_check = access_check

    def all_valid(self) -> bool:
        return self.query_check.valid and self.access_check.valid

    def describe(self, name: str) -> str:
        query_desc = self.query_check.describe(name, 'SQL')
        access_desc = self.access_check.describe(name, 'GSheet access')
        return f"{query_desc}\n{access_desc}"
