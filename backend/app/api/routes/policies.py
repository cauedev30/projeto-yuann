from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_session
from app.db.models.policy import Policy, PolicyRule
from app.schemas.policy import PolicyCreate, PolicyRead, PolicyRuleRead

router = APIRouter(prefix="/api/policies", tags=["policies"])


@router.post("", response_model=PolicyRead, status_code=status.HTTP_201_CREATED)
def create_policy(payload: PolicyCreate, session: Session = Depends(get_session)) -> Policy:
    policy = Policy(
        name=payload.name,
        version=payload.version,
        rules=[
            PolicyRule(code=rule.code, value=rule.value, description=rule.description)
            for rule in payload.rules
        ],
    )

    session.add(policy)
    session.commit()
    session.refresh(policy)

    return policy
