import os
import pickle
import base64
import time
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import smtplib

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify', 'https://www.googleapis.com/auth/gmail.send']

# Authenticate and create the service

def authenticate_gmail():
    creds = None
    # The token.pickle file stores the user's access and refresh tokens, and is created automatically when the authorization flow completes for the first time
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('google_credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    service = build('gmail', 'v1', credentials=creds)
    return service


# Function to send an email or reply to a previous message
def send_email(service, to, subject, body, thread_id=None):
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    message['from'] = 'henrysaihelper@gmail.com'   
    message['reply-to'] = 'henrysaihelper@gmail.com'  
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    message = {'raw': raw_message}
    
    if thread_id:
        message['threadId'] = thread_id
    
    try:
        message = service.users().messages().send(userId='me', body=message).execute()
        print(f"Message Id: {message['id']}")
        return message
    except Exception as error:
        print(f"An error occurred: {error}")
        return None

# Function to check for replies
def check_for_replies(service, thread_id, timeout=300, check_interval=15):
    start_time = time.time()
    while time.time() - start_time < timeout:
        results = service.users().threads().get(userId='me', id=thread_id).execute()
        messages = results.get('messages', [])
        if len(messages) > 1:
            latest_message = messages[-1]
            if latest_message['id'] != thread_id:
                payload = latest_message.get('payload', {})
                parts = payload.get('parts', [])
                for part in parts:
                    if part.get('mimeType') == 'text/plain':
                        text = base64.urlsafe_b64decode(part.get('body', {}).get('data', '')).decode('utf-8')
                        print(f"Reply found: {text}")
                        return text
        time.sleep(check_interval)
    print('No reply found within the given time.')
    return None


if __name__ == '__main__':
    # Authenticate and create Gmail API service
    service = authenticate_gmail()
    
    # Send an email
    to = 'henryaspegren@gmail.com'
    subject = 'Hello from Henrys AI Assistant'
    body = 'This is a test email. Please reply to this message.'
    sent_message = send_email(service, to, subject, body)
    print(sent_message)
    
    # Wait for a reply
    if sent_message:
        print('Waiting for a reply...')
        reply_text = check_for_replies(service, thread_id=sent_message['threadId'])
        
        # Reply back to the user if a reply is found
        if reply_text:
            reply_to = 'recipient@example.com'
            reply_subject = f"Re: {subject}"
            reply_body = 'Thank you for your reply!'
            send_email(service, reply_to, reply_subject, reply_body, thread_id=sent_message['threadId'])