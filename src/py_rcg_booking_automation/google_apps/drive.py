import os
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from .credentials import google_credentials


class GoogleDrive:

    # If modifying these scopes, delete the file token.json.
    SCOPES = ["https://www.googleapis.com/auth/drive"]

    def __init__(self, creds= None):
        """Shows basic usage of the Docs API.
        Prints the title of a sample document.
        """
        if creds is None:

            # The file token.json stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
            self.__creds = google_credentials(self.SCOPES)
        else:
            self.__creds = creds

        try:
            self.__service = build("drive", "v3", credentials=self.__creds)
        except HttpError as err:
            print(err)

    def create_folder(self, name:str, parent_folder_id: str):
        try:
            file_metadata = {
                "name": name,
                "parents": [parent_folder_id],
                "mimeType": "application/vnd.google-apps.folder",
            }

            # pylint: disable=maybe-no-member
            file = self.__service.files().create(body=file_metadata, fields="id").execute()
            print(f'Created Folder ID: "{file.get("id")}".')
            return file.get("id")

        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def upload_file(self, fqfile_path:Path, parent_folder_id: str):

        try:
            file_metadata = {"name": fqfile_path.name,
                             "parents": [parent_folder_id]}
            media = MediaFileUpload(str(fqfile_path), mimetype="image/jpeg")
            # pylint: disable=maybe-no-member
            file = self.__service.files().create(body=file_metadata, media_body=media, fields="id").execute()
            print(f'File ID: "{file.get("id")}".')
            return file.get("id")

        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def copy_file(self, file_id, new_name, target_folder_id):

        """
        Copies file using Drive API then returns file ID of (new) copy.
        """
        try:
            body = {"name": new_name,
                    "parents": [target_folder_id] }
            return (
                self.__service.files()
                .copy(body=body, fileId=file_id, fields="id")
                .execute()
                .get("id")
            )
        except HttpError as error:
            print(f"An error occurred: {error}")
            return error