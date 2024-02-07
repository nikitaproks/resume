import json
import urllib3
import logging
from typing import Any

from aiogram.types import Message

logger = logging.getLogger(__name__)


class API:
    def __init__(self, api_key: str) -> None:
        self.base_url = "http://nginx:80/api/"
        self.headers = urllib3.make_headers()
        self.headers["Authorization"] = f"Api-Key {api_key}"
        self.headers["Content-Type"] = "application/json"
        self.http = urllib3.PoolManager()

    def _send_request(
        self, method: str, url: str, data: dict | None = None
    ) -> urllib3.BaseHTTPResponse | None:
        try:
            response = self.http.request(
                method,
                url,
                headers=self.headers,
                body=json.dumps(data) if data else None,
            )
            return response
        except Exception as e:
            logger.error(e)
            return None

    def get_user(
        self, telegram_user_id: str
    ) -> urllib3.BaseHTTPResponse | None:
        url = (
            self.base_url
            + f"users/by_telegram_id?telegram_id={telegram_user_id}"
        )
        return self._send_request("GET", url)

    def register_user(
        self, telegram_id: str, email: str
    ) -> urllib3.BaseHTTPResponse | None:
        url = self.base_url + "users/"
        data = {"email": email, "telegram_id": telegram_id}
        return self._send_request("POST", url, data)

    def list_subscriptions(
        self, telegram_id: int
    ) -> urllib3.BaseHTTPResponse | None:
        url = (
            self.base_url
            + f"telegram/subscriptions/?telegram_id={telegram_id}"
        )
        return self._send_request("GET", url)

    def subscribe_stock(
        self, telegram_id: int, ticker: str
    ) -> urllib3.BaseHTTPResponse | None:
        url = self.base_url + "telegram/subscriptions/"
        data = {"telegram_id": telegram_id, "ticker": ticker}
        return self._send_request("POST", url, data)

    def unsubscribe_stock(
        self, telegram_id: int, ticker: str
    ) -> urllib3.BaseHTTPResponse | None:
        url = self.base_url + "telegram/subscriptions/unsubscribe/"
        data = {"telegram_id": telegram_id, "ticker": ticker}
        return self._send_request("POST", url, data)


def authorize(api: API, message: Message) -> dict[str, Any] | str | None:
    response = api.get_user(message.from_user.id)
    if not response:
        return None
    print(response.json())
    if response.status != 200:
        return "User is not registered. Please, use /register."
    return response.json()
