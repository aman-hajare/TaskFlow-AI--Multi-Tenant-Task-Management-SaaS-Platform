from pydantic import BaseModel, ConfigDict
from typing import List


class CompanyCreate(BaseModel):
    name: str

class CompanyResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

class CompanyListResponse(BaseModel):  
    data: List[CompanyResponse]
    total: int
    page: int
    limit: int

    model_config = ConfigDict(from_attributes=True)