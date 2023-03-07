from typing import Callable, Any, Optional, Dict, List
from concurrent import futures

from google.api_core import retry
from google.cloud import pubsub_v1


def _default_received_callback(message: pubsub_v1.subscriber.message.Message) -> None:
    print(f"Received {message}.")
    message.ack()


class GooglePubsubClient:
    def __init__(self, project_id: str):
        self.project_id = project_id

    def publish_to_topic(
        self,
        topic_id: str,
        message: Any,
        timeout: int = 10,
        attributes: Optional[Dict[str, str]] = None,
    ) -> str:
        """Publishes a message to a Pub/Sub topic.

        Parameters
        ----------
        topic_id: str
            The topic_id for the topic.

        message: Any
            The message to be published.

        timeout: int
            How long to wait (in seconds) for Pub/Sub to respond.

        attributes: Optional[Dict[str, str]]
            Attribute metadata used by consumers for
            filtering or logging.

        Returns
        -------
        message_id: str
            Unique message identifier for the topic.

        """

        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(self.project_id, topic_id)

        data = str(message)
        if attributes:
            future = publisher.publish(topic_path, data.encode("utf-8"), **attributes)
        else:
            future = publisher.publish(topic_path, data.encode("utf-8"))

        # Handle any failures using a callback
        future.add_done_callback(
            self._get_publish_callback(future, data, timeout=timeout)
        )

        message_id = future.result()

        print(f"Published message {data} to topic {topic_path}")

        return message_id

    # TODO: troubleshoot the timeout when no response is received
    # (it currently seems fixed at > 120s)
    def pull_messages_from_subscription(
        self, subscription_id: str, max_messages: int = 1, timeout: int = 10
    ) -> List[pubsub_v1.subscriber.message.Message]:
        subscriber = pubsub_v1.SubscriberClient()
        subscription_path = subscriber.subscription_path(
            self.project_id, subscription_id
        )

        with subscriber:
            response = subscriber.pull(
                request={
                    "subscription": subscription_path,
                    "max_messages": max_messages,
                },
                retry=retry.Retry(timeout=timeout),
            )

            if len(response.received_messages) == 0:
                return None

            ack_ids, messages = [], []
            for msg in response.received_messages:
                messages.append(msg.message)
                ack_ids.append(msg.ack_id)

            # Acknowledge received messages so they will not be sent again.
            subscriber.acknowledge(
                request={"subscription": subscription_path, "ack_ids": ack_ids}
            )

        return messages

    def listen_to_subscription(
        self, subscription_id: str, callback: Callable = _default_received_callback
    ):
        subscriber = pubsub_v1.SubscriberClient()
        subscription_path = subscriber.subscription_path(
            self.project_id, subscription_id
        )

        streaming_pull_future = subscriber.subscribe(
            subscription_path, callback=callback
        )
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

    def list_subscriptions_in_project(
        self,
    ) -> List[str]:
        """Lists all subscriptions in the current project."""

        subscriber = pubsub_v1.SubscriberClient()
        project_path = f"projects/{self.project_id}"

        subs = []
        with subscriber:
            for subscription in subscriber.list_subscriptions(
                request={"project": project_path}
            ):
                subs.append(subscription.name)

        return subs

    def _get_publish_callback(
        self, future: pubsub_v1.publisher.futures.Future, data: str, timeout: int = 60
    ) -> Callable[[pubsub_v1.publisher.futures.Future], None]:
        """Handles errors that occur while publishing to a topic."""

        def callback(future: pubsub_v1.publisher.futures.Future) -> None:
            try:
                future.result(timeout=timeout)
            except futures.TimeoutError as err:
                print(f"Publishing {data} timed out after {timeout} seconds.")
                raise futures.TimeoutError(err)

        return callback
