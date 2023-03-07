import os
import argparse

from tenacity import retry, wait_fixed, stop_after_attempt, RetryError

from pubsub_demo.utils.pubsub import GooglePubsubClient
from pubsub_demo.handlers import get_handler


def _get_subscription_id(service_name: str) -> str:
    sub = dict(
        A="subscription-A",
        B="subscription-B",
        C="subscription-C",
    )
    prefix = service_name[0]

    return sub[prefix]


@retry(reraise=True, wait=wait_fixed(6), stop=stop_after_attempt(10))
def _wait_for_subscription_creation(client: GooglePubsubClient, subscription_id: str):
    """Note: wait interval is determined by @retry decorator."""

    subs = client.list_subscriptions_in_project()
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

    pubsub = GooglePubsubClient(project_id=project_id)

    # Wait for subscription creation, if starting in dev mode
    try:
        _wait_for_subscription_creation(client=pubsub, subscription_id=subscription_id)
    except RetryError as retry_failure:
        num = retry_failure.last_attempt.attempt_number
        print(f"Failed to find subscription {num} times.")
        raise RuntimeError(retry_failure)

    # Start streaming messages
    pubsub.listen_to_subscription(
        subscription_id=subscription_id,
        callback=get_handler(service_name=args.service_name),
    )
