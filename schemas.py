from typing import List, Optional
from pydantic import BaseModel


class LeaseBase(BaseModel):
    lease_number:  Optional[str] = None 
    lease_name:  Optional[str] = None 
    operator_name:  Optional[str] = None 

class LeaseCreate(LeaseBase):
    pass

class Lease(LeaseBase):
    id: int

    class Config:
        orm_mode = True

class OperatorBase(BaseModel):
    operator_number:  Optional[str] = None 
    operator_name:  Optional[str] = None 
    location: Optional[str] = None 
    leases_number: Optional[str] = None 

class OperatorCreate(OperatorBase):
    pass

class Operator(OperatorBase):
    id: int

    class Config:
        orm_mode = True

class PermitBase(BaseModel):
    api:  Optional[str] = None 
    well: Optional[str] = None 
    operator: Optional[str] = None 
    application_type: Optional[str] = None 
    drill_type: Optional[str] = None 
    submitted: Optional[str] = None 
    approved: Optional[str] = None 

class PermitCreate(PermitBase):
    pass

class Permit(PermitBase):
    id: int

    class Config:
        orm_mode = True


class CountyBase(BaseModel):
    name:  Optional[str] = None 
    leases: Optional[List[LeaseCreate]] = []
    operators: Optional[List[OperatorCreate]] = []
    permits: Optional[List[PermitCreate]] = []

class CountyCreate(CountyBase):
    pass

class County(CountyBase):
    id: int

    class Config:
       from_attribute = True



# Stripe schema


class CheckoutRequest(BaseModel):
    user_id: int
    price_id: str


class CheckoutResponse(BaseModel):
    session_url: str