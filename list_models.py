from sqlmodel import Field, SQLModel
from typing import Optional

class ListItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    # 正确设置 hierarchy_code 的最大长度并索引
    hierarchy_code: str = Field(max_length=255, index=True)
    level: int
    target_url: Optional[str] = None