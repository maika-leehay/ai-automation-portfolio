import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account


def get_drive_service(credentials_path: str = None):
    """
    Initializes and returns a Google Drive API client service.
    """
    cred_file = credentials_path or os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")
    scopes = ["https://www.googleapis.com/auth/drive"]

    credentials = service_account.Credentials.from_service_account_file(
        cred_file, scopes=scopes
    )
    return build("drive", "v3", credentials=credentials)


def upload_to_drive(service, file_path: str, file_name: str) -> str:
    """
    Uploads MP4 to Google Drive and returns a publicly viewable link.

    :param service: Google Drive API service instance.
    :param file_path: Local file path of the video.
    :param file_name: Target filename in Google Drive.
    :return: webViewLink (Publicly accessible URL)
    """
    file_metadata = {"name": file_name, "mimeType": "video/mp4"}
    media = MediaFileUpload(file_path, mimetype="video/mp4", resumable=True)

    # 1. Upload File
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, webViewLink"
    ).execute()

    file_id = file.get("id")

    # 2. Set Public Read Permission
    permission = {"type": "anyone", "role": "reader"}
    service.permissions().create(fileId=file_id, body=permission).execute()

    return file.get("webViewLink")
