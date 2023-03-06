#!/bin/bash

pushd pubsub_demo/utils

# Create topics
python publisher.py my-project create topic-message-bus

# Create subscriptions
python subscriber.py my-project create topic-message-bus subscription-A
python subscriber.py my-project create topic-message-bus subscription-B
python subscriber.py my-project create topic-message-bus subscription-C

# Make sure pubsub emulator has had enough time to send a reponse back
sleep 5 # Unit: seconds