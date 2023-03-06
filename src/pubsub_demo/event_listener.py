import os
import argparse
from typing import Callable, List

from google.cloud import pubsub_v1
from tenacity import retry, wait_fixed, stop_after_attempt, RetryError


def default_callback(message: pubsub_v1.subscriber.message.Message) -> None:
    print(f"Received {message}.")
    message.ack()


def list_subscriptions_in_project(project_id: str) -> List[str]:
    """Lists all subscriptions in the current project."""

    subscriber = pubsub_v1.SubscriberClient()
    project_path = f"projects/{project_id}"

    subs = []
    with subscriber:
        for subscription in subscriber.list_subscriptions(
            request={"project": project_path}
        ):
            subs.append(subscription.name)

    return subs


def listen_to_subscription(
    project_id: str, subscription_id: str, callback: Callable = default_callback
):
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    print(f"Listening for messages on {subscription_path} ...\n")

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


def _get_subscription_id(service_name: str) -> str:
    sub = dict(
        A="subscription-A",
        B="subscription-B",
        C="subscription-C",
    )
    prefix = service_name[0]

    return sub[prefix]


@retry(reraise=True, wait=wait_fixed(6), stop=stop_after_attempt(10))
def _wait_for_subscription_creation(project_id: str, subscription_id: str):
    """Note: wait interval is determined by @retry decorator."""

    subs = list_subscriptions_in_project(project_id=project_id)
    sub_ids = [sub.split("/")[-1] for sub in subs]
    assert subscription_id in sub_ids


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--service-name", type=str, required=True)
    args = parser.parse_args()

    allowed_names = ["A", "B1", "B2", "C"]
    assert (
        args.service_name in allowed_names
    ), f"Service name must be one of {allowed_names} but received {args.service_name}"

    subscription_id = _get_subscription_id(args.service_name)
    project_id = os.getenv("PUBSUB_PROJECT_ID")

    # Wait for subscription creation, if starting in dev mode
    try:
        _wait_for_subscription_creation(
            project_id=project_id, subscription_id=subscription_id
        )
    except RetryError as retry_failure:
        num = retry_failure.last_attempt.attempt_number
        print(f"Failed to find subscription {num} times.")
        raise RuntimeError(retry_failure)

    # Start streaming messages
    listen_to_subscription(
        project_id=project_id,
        subscription_id=subscription_id,
    )
