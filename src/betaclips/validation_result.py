class ValidationResult:
    
    def __init__(self, valid: bool, msg: str | None):
        self.valid = valid
        self.msg = msg

    def describe(self, name: str, subject: str) -> str:
        if self.valid:
            return f"Job _{name}_ has valid {subject}. \033[92m\u2714\033[0m"
        else:
            return f"Job _{name}_ does not have valid {subject}. \033[91m\u2718\n{self.msg}\033[0m"
