import os
import logging
from uuid import uuid4
from typing import Optional
from datetime import datetime

from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pubsub_demo.utils.stamps import StampRequest
from pubsub_demo.utils.pubsub import GooglePubsubClient


app = FastAPI()

# can be used for debug messages, set option
# --log-level debug (or appropriate level) when
# starting uvicorn
logger = logging.getLogger("pubsub_demo")

origins = [
    "http://localhost",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Let's get stampin'!."}


@app.get("/stamps/", status_code=200)
async def retrieve_all_stamps():
    print("Retrieving all stamps.")
    return None


@app.get("/stamps/{id}", status_code=200)
async def retrieve_stamps_by_id(id: str):
    print(f"Looking for stamps with id={id}")
    return None


@app.post("/stamps/", status_code=201)
async def create_stamp_request(stamp_request: StampRequest):
    if not stamp_request.id:
        stamp_request.id = str(uuid4())[:8]

    project_id = os.getenv("PUBSUB_PROJECT_ID")
    pubsub = GooglePubsubClient(project_id=project_id)

    print(f"Making stamp request: {stamp_request}")
    request_time = str(datetime.now().isoformat())
    for series_num in range(stamp_request.num):
        message = dict(
            type="AddStamp",
            payload=dict(
                to_stamper="B",
                series_no=series_num + 1,
                request_id=stamp_request.id,
                request_type=stamp_request.type,
                stamps=[],
                times=[request_time],
            ),
        )
        pubsub.publish_to_topic(topic_id="topic-message-bus", message=message)

    return stamp_request.id
