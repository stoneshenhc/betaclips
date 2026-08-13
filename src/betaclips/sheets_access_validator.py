from .drive_client import DriveClient
from .validation_result import ValidationResult

class SheetsAccessValidator:

    VALID_ROLES = ('writer', 'owner', 'organzier', 'fileOrganizer')

    def __init__(self, drive_client: DriveClient):
        self.drive_client = drive_client

    def validate_access(self, spreadsheetid) -> ValidationResult:
        # figure out how to deal with files that don't exist or cannot be accessed
        permissions = self.drive_client.get_permissions(spreadsheetid)
        for perm in permissions:
            if perm.get('emailAddress', '') == 'writer@betaclips.iam.gserviceaccount.com':
                role = perm.get('role', '')
                if role in self.VALID_ROLES:
                    return ValidationResult(True, None)
                else:
                    return ValidationResult(False, f"Current role is {role}, but needs at least writer.")
        return ValidationResult(False, "Spreadsheet file does not exist or is not shared with service account")
