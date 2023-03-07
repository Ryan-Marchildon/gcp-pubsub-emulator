from datetime import datetime
import logging
import os
import sqlite3
from typing import Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pubsub_demo.utils.database import SqlClient
from pubsub_demo.utils.pubsub import GooglePubsubClient
from pubsub_demo.utils.stamps import StampRequest


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
    sql = SqlClient()
    results = sql.fetch(
        f"""
        SELECT * FROM stamps
        """
    )
    return results


@app.get("/stamps/{id}", status_code=200)
async def retrieve_stamps_by_id(id: str):
    print(f"Looking for stamps with request_id={id}")
    sql = SqlClient()
    results = sql.fetch(
        f"""
        SELECT * FROM stamps WHERE request_id = '{id}'
        """
    )
    return results


@app.delete("/stamps/", status_code=200)
async def delete_all_stamps():
    print(f"Deleting all stamps from stamps table.")
    sql = SqlClient()
    sql.execute(
        f"""
        DELETE FROM stamps;
        """
    )
    return "OK"


@app.post("/stamps/", status_code=201)
async def create_stamp_request(stamp_request: StampRequest):
    if not stamp_request.id:
        stamp_request.id = str(uuid4())[:8]

    project_id = os.getenv("PUBSUB_PROJECT_ID")
    pubsub = GooglePubsubClient(project_id=project_id)

    print(f"Making stamp request: {stamp_request}")
    for series_num in range(stamp_request.num):
        message = dict(
            type="AddStamp",
            payload=dict(
                to_stamper="B",
                series_num=series_num + 1,
                request_id=stamp_request.id,
                request_type=stamp_request.type,
                stamps=[],
                times=[str(datetime.now().isoformat())],
            ),
        )
        pubsub.publish_to_topic(topic_id="topic-message-bus", message=message)

    return stamp_request.id
