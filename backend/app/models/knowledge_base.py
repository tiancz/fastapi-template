import uuid
from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Column, DateTime


class KnowledgeBaseBase(SQLModel):
    # 知识库名称
    name: str = Field(min_length=1, max_length=255)
    # 知识库描述
    description: str | None = Field(default=None, max_length=255)


# Database model, database table inferred from class name
class KnowledgeBase(KnowledgeBaseBase, table=True):
    __tablename__ = "knowledge_base"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    # 知识库名称
    name: str = Field(min_length=1, max_length=255)
    # 知识库描述
    description: str | None = Field(default=None, max_length=255)
    # 状态 0:不可用 1:可用
    status: int
    created_by: uuid.UUID = Field(
        foreign_key="user.id", nullable=False
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=False))
    )
    updated_by: uuid.UUID = Field(
        foreign_key="user.id", nullable=False
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=False))
    )


class KnowledgeBaseCreate(KnowledgeBaseBase):
    pass


class KnowledgeBaseUpdate(KnowledgeBaseBase):
    pass


class KnowledgeBasePublic(KnowledgeBaseBase):
    id: uuid.UUID
    # 状态 0:不可用 1:可用
    status: int
    created_by: uuid.UUID


class KnowledgeBasesPublic(SQLModel):
    data: list[KnowledgeBasePublic]
    count: int


class KnowledgeBaseFile(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(min_length=1, max_length=255)
    type: int
    # 文件后缀 txt,doc,docx,pdf,ppt,pptx,xls,xlsx,jpg,png,gif,mp4,mp3,zip,rar,7z,tar,gz,bz2,exe,dll,bat,sh,php,html,css,
    # js,java,c,cpp,h,py,cs,vb,sql,mdb,accdb
    extension: str = Field(min_length=1, max_length=20)
    # 文件大小 byte
    size: int
    knowledge_base_id: uuid.UUID = Field(
        foreign_key="knowledge_base.id", nullable=False
    )
    # 存储类型 local,s3,oss,qiniu,aliyun,tencent,huawei,baidu,google,azure
    # ${type}|${path}
    storage: str
    # 状态 0:不可用 1:可用
    status: int
    created_by: uuid.UUID = Field(
        foreign_key="user.id", nullable=False
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=False))
    )
    updated_by: uuid.UUID = Field(
        foreign_key="user.id", nullable=False
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=False))
    )

    # model_config = ConfigDict(arbitrary_types_allowed=True)



