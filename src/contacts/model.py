import pydantic
import datetime
from typing import Optional

class ContactResponse(pydantic.BaseModel):
    id: int
    name: str
    surename: str
    email: str
    phone_number: str
    date_of_birth: datetime.date
    description: str
    

class ContactModel(pydantic.BaseModel):
    name: str
    surename: str
    email: str
    phone_number: str
    date_of_birth: datetime.date
    description: str

class ContactUpdate(pydantic.BaseModel):
    name: Optional[str] = None
    surename: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    date_of_birth: Optional[datetime.date] = None
    description: Optional[str] = None