from betaclips.clients.drive_client import DriveClient
from betaclips.results.validation_results import ValidationResult


class SheetsAccessValidator:
    VALID_ROLES = ('writer', 'owner', 'organzier', 'fileOrganizer')

    def __init__(self, drive_client: DriveClient):
        self.drive_client = drive_client

    def validate(self, spreadsheet_id) -> ValidationResult:
        permissions = self.drive_client.get_permissions(spreadsheet_id)
        for perm in permissions:
            email = perm.get('emailAddress', '')
            if email == 'writer@betaclips.iam.gserviceaccount.com':
                role = perm.get('role', '')
                if role in self.VALID_ROLES:
                    return ValidationResult('Sheet access', True, None)
                else:
                    return ValidationResult(
                        'Sheet access',
                        False,
                        f"Current role is {role}, but needs at least writer.",
                    )
        return ValidationResult(
            'Sheet access',
            False,
            "Spreadsheet file does not exist or is not shared with "
            "service account",
        )
