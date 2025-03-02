class GoogleDoc:

    # The ID of a sample document.
    #TEMPLATE_DOC_ID = "1InmXBUeZNSj1w0jaPPEhkodD0DVIy87IkKZHcbS6O0o"
    TEMPLATE_DOC_ID = "19NlCxTi_5NlgECJNyzaLMgi7QXmq6YGt29HfgCP_zvY"

    # If modifying these scopes, delete the file token.json.
    SCOPES = ["https://www.googleapis.com/auth/documents"]

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
            self.__service = build("docs", "v1", credentials=self.__creds)

            # Retrieve the documents contents from the Docs service.
            self._template = self.__service.documents().get(documentId=self.TEMPLATE_DOC_ID).execute()

            print(f"The title of the document is: {self._template.get('title')}")
        except HttpError as err:
            print(err)