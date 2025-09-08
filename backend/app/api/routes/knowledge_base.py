import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, delete, func, select
from datetime import datetime
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
from app.models.user import (
    User,
    UserPublic,
    UsersPublic,
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
    # 查询有效数据 status = 1
    count_statement = select(func.count()).where(col(KnowledgeBase.status) == 1).select_from(KnowledgeBase)
    count = session.exec(count_statement).one()

    # 关联查询
    statement = (
        select(KnowledgeBase, User.full_name)
        .join(User, KnowledgeBase.created_by == User.id)
        .where(col(KnowledgeBase.status) == 1)
        .offset(skip)
        .limit(limit)
    )
    results = session.exec(statement).all()
    # 处理结果
    knowledge_bases = [
        {
            **kb.dict(),
            "owner": username
        }
        for kb, username in results
    ]
    return KnowledgeBasesPublic(data=knowledge_bases, count=count)


@router.get(
    "/{id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=KnowledgeBasePublic,
)
def read_knowledge_base(session: SessionDep, id: uuid.UUID,) -> Any:
    """
    Retrieve knowledge base.
    """
    # 查询有效数据 status = 1
    statement = select(KnowledgeBase).where(KnowledgeBase.status == 1, KnowledgeBase.id == id)
    knowledge_base = session.exec(statement).first()
    if not knowledge_base:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    return knowledge_base


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
    # 检查权限 TODO
    update_data = knowledge_base_in.model_dump(exclude_unset=True)
    # 手动更新字段
    for field, value in update_data.items():
        setattr(knowledge_base, field, value)
    # knowledge_base.sqlmodel_update(update_data)
    # 更新系统字段
    knowledge_base.updated_by = current_user.id
    knowledge_base.updated_at = datetime.utcnow()
    session.add(knowledge_base)
    session.commit()
    session.refresh(knowledge_base)
    return knowledge_base


@router.delete("/{id}", response_model=KnowledgeBasePublic)
def delete_knowledge_base(*, session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Delete a knowledge base.
    """
    knowledge_base = session.get(KnowledgeBase, id)
    if not knowledge_base:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    # 检查权限 TODO
    knowledge_base.status = 0
    knowledge_base.updated_by = current_user.id
    knowledge_base.updated_at = datetime.utcnow()
    session.add(knowledge_base)
    session.commit()
    session.refresh(knowledge_base)
    return knowledge_base

