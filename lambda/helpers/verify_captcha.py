import os
import json
import urllib3
from urllib.parse import urlencode

def verify_captcha(token: str, secret_key: str) -> bool:
    payload = {
        'secret': secret_key,
        'response': token
    }
    encoded_payload = urlencode(payload).encode('utf-8')

    http = urllib3.PoolManager()

    try:
        response = http.request(
            'POST',
            'https://www.google.com/recaptcha/api/siteverify',
            body=encoded_payload,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        if response.status != 200:
            print(f"Unexpected HTTP status: {response.status}")
            return False

    except Exception as e:
        print(f"Error during reCAPTCHA verification: {e}")
        return False

    try:
        result = json.loads(response.data.decode('utf-8'))
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return False

    return result.get("success", False)
