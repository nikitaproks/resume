import requests


def verify_recaptcha(response):
    data = {"secret": "YOUR_SECRET_KEY", "response": response}
    r = requests.post(
        "https://www.google.com/recaptcha/api/siteverify", data=data
    )
    result = r.json()
    return result.get("success", False)
