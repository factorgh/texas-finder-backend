from typing import List, Optional
from pydantic import BaseModel


class LeaseBase(BaseModel):
    lease_number: str
    lease_name: str
    operator_name: str

class LeaseCreate(LeaseBase):
    pass

class Lease(LeaseBase):
    id: int

    class Config:
        orm_mode = True

class OperatorBase(BaseModel):
    operator_number: str
    operator_name: str
    location:str
    leases_number:str

class OperatorCreate(OperatorBase):
    pass

class Operator(OperatorBase):
    id: int

    class Config:
        orm_mode = True

class PermitBase(BaseModel):
    api: str
    well:str
    operator:str
    application_type:str
    drill_type:str
    submitted:str
    approved:str

class PermitCreate(PermitBase):
    pass

class Permit(PermitBase):
    id: int

    class Config:
        orm_mode = True


class CountyBase(BaseModel):
    name: str
    leases: Optional[List[LeaseCreate]] = []
    operators: Optional[List[OperatorCreate]] = []
    permits: Optional[List[PermitCreate]] = []

class CountyCreate(CountyBase):
    pass

class County(CountyBase):
    id: int

    class Config:
        orm_mode = True



