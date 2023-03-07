import json
import requests
from typing import Optional

from pubsub_demo.utils.stamps import StampRequest


class StampsApi:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def create_stamps(self, type: str, num: int, id: Optional[str] = None):
        if type not in ["short", "long"]:
            raise ValueError("Stamp 'type' must be one of: 'short', 'long'.")

        url = self.base_url + "/stamps/"
        headers = {
            "content-type": "application/json",
        }
        payload = StampRequest(type=type, num=num, id=id)
        print(f"Sending stamp creation request to {url} for: {payload}")
        resp = requests.post(url, headers=headers, data=json.dumps(payload.dict()))
        resp_body = resp.json()
        if resp.status_code != 201:
            print(f"Error {resp.status_code}: {resp_body}")
        return resp_body

    def retrieve_stamps(self, id: Optional[str] = None):
        if not id:
            id = ""  # Will fetch all stamps
        url = self.base_url + "/stamps/" + id
        print(f"Sending stamp retrieval request to {url}.")
        resp = requests.get(url)
        resp_body = resp.json()
        if resp.status_code != 200:
            print(f"Error {resp.status_code}: {resp_body}")

        return resp_body

    def delete_stamps(self):
        url = self.base_url + "/stamps/"
        print(f"Sending stamp deletion request to {url}.")
        resp = requests.delete(url)
        resp_body = resp.json()
        if resp.status_code != 200:
            print(f"Error {resp.status_code}: {resp_body}")

        return resp_body
