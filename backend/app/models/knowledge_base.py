import uuid
import datetime

from sqlmodel import Field, Relationship, SQLModel


class KnowledgeBase(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    # 知识库名称
    name: str = Field(min_length=1, max_length=255)
    # 知识库描述
    description: str | None = Field(default=None, max_length=255)
    # 状态 0:不可用 1:可用
    status: int = Field(min=0, max=1)
    created_by: uuid.UUID = Field(
        foreign_key="user.id", nullable=False
    )
    created_at: str = Field(default_factory=datetime.datetime.now)
    updated_by: uuid.UUID = Field(
        foreign_key="user.id", nullable=False
    )
    updated_at: str = Field(default_factory=datetime.datetime.now)


class KnowledgeBaseFile(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(min_length=1, max_length=255)
    type: int = Field(min=0, max=1)
    # 文件后缀 txt,doc,docx,pdf,ppt,pptx,xls,xlsx,jpg,png,gif,mp4,mp3,zip,rar,7z,tar,gz,bz2,exe,dll,bat,sh,php,html,css,
    # js,java,c,cpp,h,py,cs,vb,sql,mdb,accdb
    extension: str = Field(min_length=1, max_length=20)
    # 文件大小 byte
    size: int = Field(min=0)
    knowledge_base_id: uuid.UUID = Field(
        foreign_key="knowledge_base.id", nullable=False
    )
    # 存储类型 local,s3,oss,qiniu,aliyun,tencent,huawei,baidu,google,azure
    # ${type}|${path}
    storage: str
    # 状态 0:未处理 1:处理中 2:处理成功 3:处理失败
    status: int = Field(min=0, max=1)
    created_by: uuid.UUID = Field(
        foreign_key="user.id", nullable=False
    )
    created_at: str = Field(default_factory=datetime.datetime.now)
    updated_by: uuid.UUID = Field(
        foreign_key="user.id", nullable=False
    )
    updated_at: str = Field(default_factory=datetime.datetime.now)




