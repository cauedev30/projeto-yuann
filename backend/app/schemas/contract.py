from pydantic import BaseModel


class ContractListItem(BaseModel):
    id: str
    title: str
    external_reference: str
    status: str


class ContractListResponse(BaseModel):
    items: list[ContractListItem]
