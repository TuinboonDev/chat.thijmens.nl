from flask import request, session
import json

def check_general_permission():
    if not request:
        return False

    print(session.get("access_token"))

    token = session.get("access_token", "")
    if token:
        with open("accounts.json") as f:
            accounts = json.load(f)
            return any(account["token"] == token for account in accounts)

    return False
