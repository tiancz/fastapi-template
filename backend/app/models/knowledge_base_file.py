import uuid
from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Column, DateTime


class KnowledgeBaseFileBase(SQLModel):
    # 文件名称
    name: str = Field(min_length=1, max_length=255)
    # 文件后缀 txt,doc,docx,pdf,ppt,pptx,xls,xlsx,jpg,png,gif,mp4,mp3,zip,rar,7z,tar,gz,bz2,exe,dll,bat,sh,php,html,css,
    # js,java,c,cpp,h,py,cs,vb,sql,mdb,accdb
    extension: str = Field(min_length=1, max_length=255)
    # 文件大小 byte
    size: int
    # 状态 0:不可用 1:可用
    status: int
    # 文件哈希
    file_hash: str | None = Field(default=None, max_length=255)
    # 存储路径 local:/data/knowledge_base/file/, aliyun:/data/knowledge_base/file/ qiniu:/data/knowledge_base/file/,
    # tencent:/data/knowledge_base/file/
    storage: str | None = Field(default=None, max_length=255)
    knowledge_base_id: uuid.UUID = Field(
        foreign_key="knowledge_base.id", nullable=False
    )


class KnowledgeBaseFile(KnowledgeBaseFileBase, table=True):
    __tablename__ = "knowledge_base_file"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    # 文件名称
    name: str = Field(min_length=1, max_length=255)
    # 文件后缀 txt,doc,docx,pdf,ppt,pptx,xls,xlsx,jpg,png,gif,mp4,mp3,zip,rar,7z,tar,gz,bz2,exe,dll,bat,sh,php,html,css
    extension: str = Field(min_length=1, max_length=255)
    # 文件大小 byte
    size: int
    # 文件路径
    storage: str | None = Field(default=None, max_length=255)
    knowledge_base_id: uuid.UUID = Field(
        foreign_key="knowledge_base.id", nullable=False
    )
    file_hash: str | None = Field(default=None, max_length=255)
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


class KnowledgeBaseFileCreate(KnowledgeBaseFileBase):
    pass


class KnowledgeBaseFileUpdate(KnowledgeBaseFileBase):
    pass


class KnowledgeBaseFilePublic(KnowledgeBaseFileBase):
    id: uuid.UUID
    created_by: uuid.UUID
    owner: str


class KnowledgeBaseFilesPublic(SQLModel):
    data: list[KnowledgeBaseFilePublic]
    count: int


class AskQuestion(SQLModel):
    question: str

