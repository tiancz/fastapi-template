import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, delete, func, select

from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.models.knowledge_base import (
    KnowledgeBase,
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    KnowledgeBasePublic,
    KnowledgeBasesPublic,
)


router = APIRouter(prefix="/kb", tags=["knowledge_base"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=KnowledgeBasesPublic,
)
def read_knowledge_bases(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve knowledge bases.
    """

    count_statement = select(func.count()).select_from(KnowledgeBase)
    count = session.exec(count_statement).one()

    statement = select(KnowledgeBase).offset(skip).limit(limit)
    knowledge_bases = session.exec(statement).all()

    return KnowledgeBasesPublic(data=knowledge_bases, count=count)


@router.post("/", response_model=KnowledgeBasePublic)
def create_knowledge_base(
    *, session: SessionDep, current_user: CurrentUser, knowledge_base_in: KnowledgeBaseCreate
) -> Any:
    """
    Create new knowledge base.
    """
    knowledge_base = KnowledgeBase.model_validate(knowledge_base_in,
                                                  update={
                                                      "status": 1,
                                                      "created_by": current_user.id,
                                                      "updated_by": current_user.id
                                                  })
    session.add(knowledge_base)
    session.commit()
    session.refresh(knowledge_base)
    return knowledge_base


@router.put("/{id}", response_model=KnowledgeBasePublic)
def update_knowledge_base(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    knowledge_base_in: KnowledgeBaseUpdate,
) -> Any:
    """
    Update a knowledge base.
    """
    knowledge_base = session.get(KnowledgeBase, id)
    if not knowledge_base:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    knowledge_base = KnowledgeBase.model_validate(knowledge_base_in,
                                                  update={
                                                      "status": 1,
                                                      "updated_by": current_user.id
                                                  })

    update_dict = knowledge_base_in.model_dump(exclude_unset=True)
    knowledge_base.sqlmodel_update(update_dict)
    session.add(knowledge_base)
    session.commit()
    session.refresh(knowledge_base)
    return knowledge_base


