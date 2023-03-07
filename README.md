# gcp-pubsub-emulator

Local test/dev setup with the Google Pubsub Emulator.

Creates a dedicated pubsub container and demo publisher/subscriber app using docker-compose.

## Usage

1. For first-time setup, start with `make build`.
2. In a separate terminal, run `make run`.
3. Explore `demo.ipynb`
4. Try the cli tool: `pip install -e src/` into your virtual env, then `stamps --help`

Helpful reference:
- https://medium.com/google-cloud/things-i-wish-i-knew-about-pub-sub-part-3-b8947b49224b
- https://medium.com/google-cloud/use-pub-sub-emulator-in-minikube-67cd1f289daf
