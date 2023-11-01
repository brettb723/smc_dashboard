import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from base64 import urlsafe_b64decode

def authenticate_google_api(api_name, api_version, scopes):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', scopes)
            creds = flow.run_local_server(port=8501)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build(api_name, api_version, credentials=creds)
    return service


def search_gmail(service, subject):
    try:
        results = service.users().messages().list(userId='me', q=f'subject:{subject}').execute()
        messages = results.get('messages', [])
        
        attachments = []
        for message_info in messages:
            msg_id = message_info['id']
            message = service.users().messages().get(userId='me', id=msg_id).execute()
            for part in message['payload']['parts']:
                if part['filename'] and part['mimeType'] == 'text/csv':
                    data = part['body']['data']
                    file_data = urlsafe_b64decode(data.encode('UTF-8'))
                    attachments.append((part['filename'], file_data))
        return attachments
    except Exception as e:
        print(f"Error: {str(e)}")
        return []
