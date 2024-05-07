# POC for email download using Gmail API

## Set Up Credentials

1. Go to the Google Cloud Console (https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Enable the Gmail API for your project.
4. Configure the OAuth consent screen and set up the required scopes (e.g., https://www.googleapis.com/auth/gmail.readonly for read-only access to Gmail).
5. Create OAuth 2.0 credentials (Client ID and Client Secret) for a desktop application.
6. Download the credentials JSON file and save it as credentials.json in your project directory.

## How to run

``` bash
python main.py
```
