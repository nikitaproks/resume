import json
import logging
from typing import Any

import urllib3

logger = logging.getLogger(__name__)


class API:
    def __init__(
        self, base_url: str, authorization: str | None = None
    ) -> None:
        self.base_url = base_url
        self.headers = urllib3.make_headers()
        if authorization:
            self.headers["Authorization"] = authorization
        self.headers["Content-Type"] = "application/json"
        self.http = urllib3.PoolManager()

    def _send_request(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        fields: dict[str, Any] | None = None,
        headers: dict[str, str] = {},
    ) -> urllib3.BaseHTTPResponse | None:
        headers.update(self.headers)
        try:
            response = self.http.request(
                method,
                url,
                headers=headers,
                body=json.dumps(data) if data else None,
                fields=fields,
                redirect=False,
            )
            if response.status == 301:
                redirect_url = response.getheader("Location")
                if not redirect_url.startswith(("http://", "https://")):
                    redirect_url = self.base_url + redirect_url
                response = self.http.request(
                    method,
                    redirect_url,
                    headers=headers,
                    body=json.dumps(data) if data else None,
                    fields=fields,
                )
            return response
        except Exception as e:
            logger.error(e)
            return None


class BackendAPI(API):
    def trigger_analysis(self) -> urllib3.BaseHTTPResponse | None:
        url = self.base_url + "api/analysis/"
        return self._send_request("GET", url)
