#!/bin/bash

pushd pubsub_demo/utils

# Create topics
python publisher.py my-project create topic-A-bus
python publisher.py my-project create topic-B-bus
python publisher.py my-project create topic-return-bus

# Create subscriptions
python subscriber.py my-project create topic-A-bus sub-A-bus
python subscriber.py my-project create topic-B-bus sub-B-bus
python subscriber.py my-project create topic-return-bus sub-return-bus

# Make sure pubsub emulator has had enough time to send a reponse back
sleep 5 # In seconds