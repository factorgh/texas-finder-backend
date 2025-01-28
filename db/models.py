# schemas.py
from pydantic import BaseModel
from typing import List, Optional, Dict

class Permit(BaseModel):
    data: Dict[str, str]  # Replace with your actual fields

class Operator(BaseModel):
    data: Dict[str, str]  # Replace with your actual fields

class Lease(BaseModel):
    data: Dict[str, str]  # Replace with your actual fields

class CountyBase(BaseModel):
    name: str
    permits: Optional[List[Permit]] = []
    operators: Optional[List[Operator]] = []
    leases: Optional[List[Lease]] = []

    class Config:
        orm_mode = True

class County(CountyBase):
    id: str  # MongoDB uses string _id by default
    permits: List[Permit] = []
    operators: List[Operator] = []
    leases: List[Lease] = []

    class Config:
        orm_mode = True
