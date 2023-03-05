import logging

from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


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
    return {"message": "Good morning, Dave."}
