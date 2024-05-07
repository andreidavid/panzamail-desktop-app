import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from googleapiclient.errors import HttpError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64

from googleapiclient.errors import HttpError
from email.mime.multipart import MIMEMultipart
import base64

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_sent_emails(service, num_emails=5):
    try:
        # Fetch the list of sent emails
        results = (
            service.users()
            .messages()
            .list(userId="me", labelIds=["SENT"], maxResults=num_emails)
            .execute()
        )
        messages = results.get("messages", [])

        # Create an mbox file to store the emails
        with open("sent_emails.mbox", "w") as mbox_file:
            subjects = []
            for message in messages:
                # Fetch the email message by ID
                msg = (
                    service.users()
                    .messages()
                    .get(userId="me", id=message["id"], format="raw")
                    .execute()
                )

                # Decode the raw message data
                msg_str = base64.urlsafe_b64decode(msg["raw"].encode("ASCII"))

                # Decode the raw message data
                msg_bytes = base64.urlsafe_b64decode(msg["raw"].encode("ASCII"))

                # Parse the email message
                mime_msg = MIMEMultipart()
                mime_msg.set_payload(msg_str)

                # Write the email to the mbox file
                mbox_file.write(mime_msg.as_string(unixfrom=True))
                mbox_file.write("\n")

                # Extract the subject from the raw message data
                subject = "No Subject"
                for line in msg_bytes.decode("utf-8").split("\r\n"):
                    if line.startswith("Subject:"):
                        subject = line[9:].strip()
                        break
                subjects.append(subject)

        # print(f"Successfully downloaded {len(messages)} sent emails.")
        # return len(messages)
        return subjects
    except HttpError as error:
        print(f"An error occurred: {error}")


def get_gmail_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    service = build("gmail", "v1", credentials=creds)
    return service


def get_test_data(service):
    results = service.users().messages().list(userId="me", maxResults=10).execute()
    messages = results.get("messages", [])
    for message in messages:
        msg = service.users().messages().get(userId="me", id=message["id"]).execute()
        print(f"Subject: {msg['payload']['headers'][16]['value']}")
