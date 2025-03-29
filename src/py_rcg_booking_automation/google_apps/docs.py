
import os

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .credentials import google_credentials

class GoogleDoc:

    # If modifying these scopes, delete the file token.json.
    SCOPES = ["https://www.googleapis.com/auth/documents"]

    def __init__(self, creds = None):
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
            self.__service = build("docs", "v1", credentials=self.__creds)

        except HttpError as err:
            print(err)

    def get_document(self, document_id:str):
        # Retrieve the documents contents from the Docs service.
        return self.__service.documents().get(documentId=document_id).execute()

    def update_strings(self, document_id, updates: dict[str, str]):

        try:
            # "search & replace" API requests for mail merge substitutions
            reqs = [
                {
                    "replaceAllText": {
                        "containsText": {
                            "text": "*|%s|*" % key,
                            "matchCase": True,
                        },
                        "replaceText": value,
                    }
                }
                for key, value in updates.items()
            ]

            # send requests to Docs API to do actual merge
            self.__service.documents().batchUpdate(
                body={"requests": reqs}, documentId=document_id, fields=""
            ).execute()
            return document_id
        except HttpError as error:
            print(f"An error occurred: {error}")
            return error

    def merge_google_docs(self, doc_ids, new_doc_title):

        # Create a new document

        new_doc = self.__service.documents().create(body={'title': new_doc_title}).execute()
        new_doc_id = new_doc['documentId']

        for doc_id in doc_ids:
            # Get content from each document

            # Get the source document's content
            source_doc = self.__service.documents().get(documentId=doc_id).execute()
            source_body = source_doc.get('body', {}).get('content', [])

            # Construct the requests to append the content to the target document
            requests = []
            insert_index = self.__get_document_end_index(new_doc_id)  # Find the end of the document.

            for element in source_body:
                requests.append({
                    'insertContent': {
                        'location': {
                            'index': insert_index
                        },
                        'content': element
                    }
                })
                # Increment the index appropriately. This is crucial.
                insert_index += self.__get_element_length(element)

            # Execute the requests to append the content
            if requests:
                self.__service.documents().batchUpdate(
                    documentId=new_doc_id, body={'requests': requests}
                ).execute()

        return new_doc_id

    def __get_document_end_index(self, document_id):
        """Gets the index of the end of the document."""
        doc = self.__service.documents().get(documentId=document_id).execute()
        return len(doc.get('body', {}).get('content', []))

    def __get_element_length(self, element):
        """Gets the length of a document element for index incrementing."""
        if 'paragraph' in element:
            paragraph = element['paragraph']
            if 'elements' in paragraph:
                length = 0
                for el in paragraph['elements']:
                    if 'textRun' in el and 'content' in el['textRun']:
                        length += len(el['textRun']['content'])
                    elif 'inlineObjectElement' in el:
                        length += 1  # Inline objects are single characters in terms of index
                    elif 'horizontalRule' in el:
                        length += 1  # Horizontal rules are single characters in terms of index.
                    elif 'pageBreak' in el:
                        length += 1  # Page breaks are single characters in terms of index.
                return length
        elif 'table' in element:
            table = element['table']
            rows = table.get('tableRows', [])
            length = 0
            for row in rows:
                cells = row.get('tableCells', [])
                for cell in cells:
                    length += self.__get_element_length({'paragraph': cell.get('content', [])[0]})  # Treat cell content as a paragraph.
            return length
        elif 'sectionBreak' in element:
            return 1  # Section breaks are single characters in terms of index.
        elif 'tableOfContents' in element:
            return 1  # TOC are single characters in terms of index.
        elif 'lists' in element:
            return 1  # Lists are single characters in terms of index.
        else:
            return 1  # Default to 1 if the type is unknown.



