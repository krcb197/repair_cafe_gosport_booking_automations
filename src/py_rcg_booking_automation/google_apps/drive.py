import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload




class GoogleDrive:

    # If modifying these scopes, delete the file token.json.
    SCOPES = ["https://www.googleapis.com/auth/drive"]

    def __init__(self):
        """Shows basic usage of the Docs API.
        Prints the title of a sample document.
        """
        self.__creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.json"):
            self.__creds = Credentials.from_authorized_user_file("token.json", self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not self.__creds or not self.__creds.valid:
            if self.__creds and self.__creds.expired and self.__creds.refresh_token:
                self.__creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", self.SCOPES)
                self.__creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(self.__creds.to_json())

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
            print(f'Folder ID: "{file.get("id")}".')
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