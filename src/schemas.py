from typing import TypedDict, List
from pydantic import BaseModel, Field, field_validator


class WalletSchema(BaseModel):
    address: str = Field(..., description='Address')

    @field_validator('address', mode='before')
    @classmethod
    def validate_address_length(cls, value: str) -> str:
        if len(value) != 34:
            raise ValueError('Tron address must be exactly 34 characters long')
        return value


class ResourcesDict(TypedDict):
    freeNetLimit: int
    TotalNetLimit: int
    TotalNetWeight: int
    TotalEnergyLimit: int
    TotalEnergyWeight: int


class WalletDataDict(TypedDict):
    address: str
    balance: int
    resources: ResourcesDict


class QueryDict(TypedDict):
    cursor: int | None
    queries: List[str]
