import logging

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class DriveClient:
    SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

    def __init__(self, service):
        self.service = service

    @classmethod
    def from_service_account(cls, file_path):
        creds = Credentials.from_service_account_file(
            file_path,
            scopes=cls.SCOPES,
        )
        return cls(build('drive', 'v3', credentials=creds))

    def get_permissions(self, file_id: str) -> list:
        try:
            response = self.service.permissions().list(
                fileId=file_id,
                fields='permissions(emailAddress, role)',
            ).execute()
        except HttpError as error:
            if int(error.resp.status) == 404:
                return []
        logger.info(
            "Google Drive permissions retrieved - file_id=%s",
            file_id,
        )
        return response.get('permissions', [])
