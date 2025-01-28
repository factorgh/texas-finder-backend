from typing import List, Optional
from pydantic import BaseModel


class LeaseBase(BaseModel):
    lease_number: str
    lease_name: str
    lease_link: str
    operator_name: str

class LeaseCreate(LeaseBase):
    pass

class Lease(LeaseBase):
    id: int

    class Config:
        orm_mode = True

class CountyBase(BaseModel):
    name: str
    leases: Optional[List[LeaseCreate]] = []

class CountyCreate(CountyBase):
    pass

class County(CountyBase):
    id: int

    class Config:
        orm_mode = True

class OperatorBase(BaseModel):
    name: str

class OperatorCreate(OperatorBase):
    pass

class Operator(OperatorBase):
    id: int

    class Config:
        orm_mode = True
