.PHONY: build
build:
	docker build -t demo-app:latest .

.PHONY: run
run: 
	docker compose up

.PHONY: pubsub-only
pubsub-only: 
	docker run --rm -ti -p 8080:8085 \
		gcr.io/google.com/cloudsdktool/cloud-sdk:416.0.0-emulators \
		gcloud beta emulators pubsub start \
		--project=my-project \
		--host-port=0.0.0.0:8085
