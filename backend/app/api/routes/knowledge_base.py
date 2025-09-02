import os
import uuid
import tempfile
from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter(prefix="/kb", tags=["knowledge_base"])


@router.post("/", response_model=ItemPublic)
def create_knowledge_base(
    *, session: SessionDep, current_user: CurrentUser, item_in: ItemCreate
) -> Any:
    """
    Create new item.
    """
    item = Item.model_validate(item_in, update={"owner_id": current_user.id})
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

