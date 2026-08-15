from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class DriveClient:
    SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
    SERVICE_ACCOUNT_FILE = './credentials/betaclips-service-account.json'

    def __init__(self):
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        self.service = build('drive', 'v3', credentials=creds)

    def get_permissions(self, fileid: str) -> list:
        try:
            response = self.service.permissions().list(
                fileId=fileid,
                fields='permissions(emailAddress, role)'
            ).execute()
            return response.get('permissions',[])
        except HttpError as error:
            if int(error.resp.status) == 404:
                return []

