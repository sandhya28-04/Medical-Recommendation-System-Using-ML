import requests

def is_valid_email(email):
    response = requests.get(f"https://api.eva.pingutil.com/email?email={email}")
    data = response.json()
    return data.get("data", {}).get("deliverable", False)
