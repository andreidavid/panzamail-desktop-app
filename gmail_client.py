import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
import mailbox

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
        mbox_file = mailbox.mbox("sent_emails.mbox")
        mbox_file.lock()

        for message in messages:
            subjects = []
            # Fetch the email message by ID
            msg = (
                service.users()
                .messages()
                .get(userId="me", id=message["id"], format="raw")
                .execute()
            )

            # Decode the raw message data
            msg_raw = base64.urlsafe_b64decode(msg["raw"].encode("ASCII"))

            # Convert the raw message bytes to a string
            msg_str = msg_raw.decode("utf-8")

            # Create an email message object from the raw data
            email_message = mailbox.mboxMessage(msg_str)
            subject = email_message["subject"]
            subjects.append(subject)
            print(f"Subject: {subject}")
            # Add the email message to the mbox file
            mbox_file.add(email_message)

        mbox_file.flush()
        mbox_file.unlock()
        mbox_file.close()

        print(f"Successfully downloaded {len(messages)} sent emails.")
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
