from typing import Any
import logging

from google.cloud import pubsub_v1

logging.basicConfig(level=logging.DEBUG)

class PubSubInterface:
    def __init__(self, project_id: str):
        self.project_id = project_id

    def publish_message(self, message: Any, topic_id: str) -> Any:
        """Publishes a message to the given topic.

        Parameters
        ----------
        message : Any
            The message contents to be published to the pubsub topic.

        topic_id : str
            Name of the topic (e.g. `topic_name`).

        Returns
        -------
        message_id : any
            The identifier of the published message.
        """
        # Setup publisher
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(self.project_id, topic_id)

        # Publish
        data = f"{message}"
        api_future = publisher.publish(topic_path, data.encode("utf-8"))
        message_id = api_future.result()

        logging.info(
            f"Published {data} to topic {str(topic_path)} with message id {message_id}."
        )
        return message_id

    def stream_messages(
        self, subscription_id: str, callback_func: Any = None, timeout: float = 10.0
    ) -> None:
        """Stream messages from a subscription to a worker/callback function.
        If a call back function is not provided the messages are logged.

        Parameters
        ----------
        subscription_id : str
            The subscription name from which message will be read.

        callback_func: Any
            Reference to a worker function which takes one message at
            a time and performs an opeartion. The function is responsible
            for acknowledging the message. If not acknowledged, the
            message will be redelivered.
            e.g.
            >>> from google.cloud import pubsub_v1
            >>> def callback(message: pubsub_v1.subscriber.message.Message) -> None:
            >>>    print(message.message_id)
            >>>    message.ack() # acknowledgement

        timeout : float, default = 10.0
            The number of seconds that the subscriber will listen.

        Returns
        -------
        None
        """

        # Setup
        subscriber = pubsub_v1.SubscriberClient()
        subscription_path = subscriber.subscription_path(
            self.project_id, subscription_id
        )
        self.message_list = []

        # Callback function
        if not callback_func:
            def callback_func(message: pubsub_v1.subscriber.message.Message) -> None:
                logging.info(
                    f"Message with message_id:`{message.message_id}` is recieved: \n {message}"
                )
                message.ack()

        # Start Listening
        streaming_pull_future = subscriber.subscribe(
            subscription_path, callback=callback_func
        )
        logging.info(f"Listening for messages on {subscription_path}..\n")

        with subscriber:
            try:
                streaming_pull_future.result(timeout=10)
            except TimeoutError:
                streaming_pull_future.cancel()  # Trigger the shutdown.
                streaming_pull_future.result()  # Block until the shutdown is complete.

    def pull_messages(self, subscription_id: str, max_messages: int = 1):
        """Receieves messages from a subscription.
        Use only when message body is small with a small range of max_messages.

        Parameters
        ----------
        subscription_id : str
            The subscription name from which message will be read

        subscription_id : int, default = 1
            The number of max messages that needs to returned. e.g. 1

        Returns
        -------
        messages : List[google.cloud.pubsub_v1.types.PubsubMessage]
            A list of messages is returned.
            Each elemnt has the following attributes:
            1. data
            2. message_id
            3. publish_time
        """
        # Setup
        client = pubsub_v1.SubscriberClient()
        subscription = client.subscription_path(self.project_id, subscription_id)

        # Receive response: google.cloud.pubsub_v1.types.PullResponse.ReceivedMessage
        logging.info(f"Fetching {max_messages} from {subscription}")
        responses = client.pull(
            subscription=subscription, max_messages=max_messages
        ).received_messages

        # Extract messages from responses and acknowledge them
        messages = []
        ack_ids = []
        if responses:
            for response in responses:
                messages.append(response.message)
                print(type(response.message))
                ack_ids.append(response.ack_id)

            client.acknowledge(subscription=subscription, ack_ids=ack_ids)

        logging.info(f"Pulled {messages} from subscription {str(subscription_id)}.")
        return messages
