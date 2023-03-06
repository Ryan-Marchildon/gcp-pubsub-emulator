from dataclasses import dataclass
from datetime import datetime, date
import json
from typing import List, Optional

from pydantic import BaseModel


@dataclass
class Stamp:
    source: str
    timestamp: datetime


def add_stamp(stamps: List[Stamp], source: str):
    stamps.append(Stamp(source, datetime.now()))


class StampRequest(BaseModel):
    type: str  # 'short' or 'long'
    num: int
    id: Optional[str] = None


# class StampEncoder(json.JSONEncoder):
#     """Makes Stamp dataclass json-serializable.

#     Example
#     -------
#     Usage:
#     >>> stamps: List[Stamp] = [stamp1, stamp2, ...]
#     >>> json.dumps(stamps, cls=StampEncoder)

#     """

#     def default(self, obj):
#         if isinstance(obj, Stamp):
#             return obj.__dict__
#         return json.JSONEncoder.default(self, obj)


def json_serializer(obj):
    """JSON serializer for objects not serializable by default."""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    if isinstance(obj, Stamp):
        return obj.__dict__

    raise TypeError(f"Type {type(obj)} not JSON-serializable.")


if __name__ == "__main__":
    """Example use"""

    stamps = []
    add_stamp(stamps, source="B")
    add_stamp(stamps, source="C")

    payload = json.dumps(stamps, default=json_serializer)
    print(payload)

    retrieved_obj = json.loads(payload)
    print(retrieved_obj)
