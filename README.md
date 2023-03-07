# Google Pub/Sub Local Emulator Demo

A sandbox for experimenting with Google Pub/Sub in a local development setup, centered around an asynchronous messaging demo. 

Creates a dedicated pubsub container and demo publisher/subscriber app using docker-compose.

## Purpose

This sandbox and demo sets us up for experimentation with the following:

- Topology of topics and subscriptions
- Load balancing
- Stress testing
- Authentication schemes
- Message encoding (e.g. primitives vs serialized objects)
- Internal architecture (e.g. organization of commands vs events and their handlers)
- Integration with the live Pub/Sub service on GCP


## Quickstart

1. For first-time setup, start with `make build`.
2. In a separate terminal, run `make run`.
3. Explore `demo.ipynb`
4. Try the cli tool: `pip install -e src/` into your virtual env, then `stamps --help`


## Description

In this bureaucracy-flavoured demo, a user requests `N` letters (messages) to be 'rubber-stamped' by one or more services. After being stamped by all requested stampers, the letters are persisted to a database that tracks the identity of the 'stampers' on each letter and the total transit time for that letter. 

An outline of the communication flow as well as the "short" (one-stamper) and "long" (two-stamper) request paths is displayed below. 

![System Diagram](./docs/img/PubSub-Demo-AsyncStamping.svg)
