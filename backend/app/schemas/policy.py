from typing import Any

from pydantic import BaseModel, ConfigDict


class PolicyRuleCreate(BaseModel):
    code: str
    value: Any
    description: str | None = None


class PolicyCreate(BaseModel):
    name: str
    version: str
    rules: list[PolicyRuleCreate]


class PolicyRuleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    value: Any
    description: str | None = None


class PolicyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    version: str
    rules: list[PolicyRuleRead]
