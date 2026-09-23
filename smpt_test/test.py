import os

import requests

# Your API token
api_token = os.environ.get("MAILERSEND_API_TOKEN", "")

# MailerSend API URL
url = "https://api.mailersend.com/v1/email"

# Email details
payload = {
    "from": {
        "email": "MS_Bw6JFF@trial-3vz9dle6onngkj50.mlsender.net",
        "name": "Logsplace"
    },
    "to": [
        {
            "email": "opemummy466@gmail.com",
            "name": "Dex"
        }
    ],
    "subject": "Test Email from MailerSend",
    "text": "This is a plain text body of the email.",
    # "html": email_template,
}

# Headers with authorization and content type
headers = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/json"
}

# Send the request to MailerSend API
response = requests.post(url, json=payload, headers=headers)

# Check response status
if response.status_code == 202:
    print("Email sent successfully!")
else:
    print(f"Failed to send email: {response.status_code}")
    print(response.text)
