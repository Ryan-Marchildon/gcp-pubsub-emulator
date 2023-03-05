up: 
	docker run --rm -ti -p 8080:8085 \
		gcr.io/google.com/cloudsdktool/cloud-sdk:416.0.0-emulators \
		gcloud beta emulators pubsub start \
		--project=my-project \
		--host-port=0.0.0.0:8085

# NOTE: you have to issue these export statements separately, 
# because running them through make does not actually persist them
# in your shell session
init: 
	echo "Execute these export statements in your local shell session."
	export PUBSUB_PROJECT_ID=my-project
	export PUBSUB_EMULATOR_HOST=localhost:8080
	python src/publisher.py my-project create my-topic
	python src/publisher.py my-project list
