import requests

url = "https://api.mtn.com/v1/transfer/customers/2348164064452"

payload = {
    "receiverMsisdn": "2349062058463",
    "type": "airtime",
    "targetSystem": "CIS",
    "pin": "1234",
    "transferAmount": 100,
    "callbackUrl": "https://logsplace.com",
    "transactionId": 1232412421412,
    "currency": "NGN",
}
headers = {
    "Content-Type": "application/json",
    "channelId": "",
    "X-API-Key": "e5cO3zcrQKzvwGN0GAQpP0GUeTr5GGLi"
}

response = requests.request("POST", url, json=payload, headers=headers)

print(response.text)