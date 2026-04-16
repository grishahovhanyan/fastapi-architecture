from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel
from pydantic.alias_generators import to_camel


class CustomBaseModel(BaseModel):
  class Config:
    alias_generator = to_camel
    populate_by_name = True
    json_encoders = {
      datetime: lambda v: v.isoformat(),
      Decimal: float,
    }
