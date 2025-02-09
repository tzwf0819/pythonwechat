from sqlmodel import Field, SQLModel, Session, create_engine, select
from typing import Optional
from datetime import datetime

class ProductCategory(SQLModel, table=True):
    category_id: Optional[int] = Field(default=None, primary_key=True)
    category_name: str
    category_status: bool = Field(default=True)  # True为激活，False为非激活状态
    creator: str
    creation_time: Optional[datetime] = None  # 使用默认值None，具体值由数据库在插入时生成
    update_time: Optional[datetime] = None  # 同上


class Product(SQLModel, table=True):
    product_category_id: int = Field(foreign_key="productcategory.category_id", index=True)
    product_id: int = Field(default=None, primary_key=True)
    product_name: str
    product_specification: str
    product_price: float
    product_description: str | None = None
    product_image: str | None = None  # URL或路径
    product_parameters: str | None = None  # JSON字符串或其他格式