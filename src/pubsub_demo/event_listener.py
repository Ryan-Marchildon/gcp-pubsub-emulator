import os
import argparse
from typing import Callable

from google.cloud import pubsub_v1


def default_callback(message: pubsub_v1.subscriber.message.Message) -> None:
    print(f"Received {message}.")
    message.ack()


def listen_to_subscription(
    project_id: str, subscription_id: str, callback: Callable = default_callback
):
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    print(f"Listening for messages on {subscription_path}..\n")

    with subscriber:
        try:
            streaming_pull_future.result(timeout=None)

        except Exception as err_msg:
            print(
                f"Encountered an exception while listening to "
                f"subscription {subscription_path}: {err_msg}"
            )
            streaming_pull_future.cancel()  # Trigger listner shutdown.
            streaming_pull_future.result()  # Block until shutdown is complete.


if __name__ == "__main__":
    # Note: might need to have it wait until it sees
    # the service is there... what happens for now
    # is that you'll see several cases of "google.api_core.exceptions.NotFound"
    # and 404 for 'subscription does not exist" before it starts working.

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--service-name", type=str, required=True)
    args = parser.parse_args()

    assert args.service_name in ["B1", "B2", "C"]

    listen_to_subscription(
        project_id=os.getenv("PUBSUB_PROJECT_ID"),
        subscription_id="sub-A-bus",
    )
