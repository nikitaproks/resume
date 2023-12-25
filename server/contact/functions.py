import requests
from server.settings import RECAPTCHA_SECRET_KEY


def verify_recaptcha(response):
    data = {"secret": RECAPTCHA_SECRET_KEY, "response": response}
    r = requests.post(
        "https://www.google.com/recaptcha/api/siteverify", data=data
    )
    result = r.json()
    return result.get("success", False)
