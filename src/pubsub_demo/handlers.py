import os
from ast import literal_eval
from datetime import datetime
from typing import Callable

from google.cloud import pubsub_v1

from pubsub_demo.utils.pubsub import GooglePubsubClient


# NOTE: this can definitely be re-written in a cleaner way
def get_handler(service_name: str) -> Callable:
    if service_name.startswith("A"):

        def _callback(message: pubsub_v1.subscriber.message.Message) -> None:
            message.ack()
            message = literal_eval(message.data.decode("utf-8"))

            if message["type"] == "StampsAdded":
                print(f"Processing message: {message}")

    elif service_name.startswith("B"):
        _stamp = service_name
        _next = "C"

        def _callback(message: pubsub_v1.subscriber.message.Message) -> None:
            message.ack()
            message = literal_eval(message.data.decode("utf-8"))

            if message["type"] == "AddStamp":
                if message["payload"]["to_stamper"] == "B":
                    print(f"Processing message: {message}")
                    payload = message["payload"]

                    stamp_time = str(datetime.now().isoformat())

                    payload["stamps"].append(_stamp)
                    payload["times"].append(stamp_time)

                    pubsub = GooglePubsubClient(
                        project_id=os.getenv("PUBSUB_PROJECT_ID")
                    )
                    if payload["request_type"] == "short":
                        payload["to_stamper"] = None
                        new_message = dict(type="StampsAdded", payload=payload)
                    elif payload["request_type"] == "long":
                        payload["to_stamper"] = _next
                        new_message = dict(type="AddStamp", payload=payload)
                    else:
                        raise ValueError(
                            f"Encountered invalid request type: {payload['request_type']}"
                        )

                    pubsub.publish_to_topic(
                        topic_id="topic-message-bus", message=new_message
                    )

    elif service_name.startswith("C"):

        def _callback(message: pubsub_v1.subscriber.message.Message) -> None:
            message.ack()
            message = literal_eval(message.data.decode("utf-8"))

            if message["type"] == "AddStamp":
                if message["payload"]["to_stamper"] == "C":
                    print(f"Processing message: {message}")
                    payload = message["payload"]

                    stamp_time = str(datetime.now().isoformat())

                    payload["stamps"].append("C")
                    payload["times"].append(stamp_time)

                    pubsub = GooglePubsubClient(
                        project_id=os.getenv("PUBSUB_PROJECT_ID")
                    )
                    payload["to_stamper"] = None
                    new_message = dict(type="StampsAdded", payload=payload)

                    pubsub.publish_to_topic(
                        topic_id="topic-message-bus", message=new_message
                    )

    return _callback
