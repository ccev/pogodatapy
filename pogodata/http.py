from typing import Optional, Dict, Any

import requests


API_VERSION = "1"


class _Http:
    _endpoint_base: str = ""

    def __init__(self, host: str):
        if not host.startswith("http"):
            self._endpoint_base += "http://"
        self._endpoint_base += host + f"/v{API_VERSION}/"

    def get(self, endpoint: str, body: Optional[Dict[str, Any]] = None) -> dict:
        pass


class SyncHttp(_Http):
    _session: requests.Session

    def __init__(self, host: str):
        super().__init__(host)
        self._session = requests.Session()

    def get(self, endpoint: str, body: Optional[Dict[str, Any]] = None) -> dict:
        if not body:
            body = {}
        result = self._session.get(self._endpoint_base + endpoint, json=body)
        return result.json()


class AsyncHttp(_Http):
    async def get(self, endpoint: str, body: Optional[Dict[str, Any]] = None) -> dict:
        pass
