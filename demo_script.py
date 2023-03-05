import os

os.environ["PUBSUB_PROJECT_ID"] = "my-project"
os.environ["PUBSUB_EMULATOR_HOST"] = "localhost:8080"

from pubsub_demo.interface import PubSubInterface

pubsub = PubSubInterface("my-project")
pubsub.publish_message(message=dict(body="Hello World"), topic_id="topic-A-bus")
pubsub.publish_message(message=dict(body="Hello World Again!"), topic_id="topic-A-bus")
