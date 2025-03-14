from sqlmodel import create_engine, SQLModel, Session, select
from list_models import ListItem
import os

DATABASE_USER = os.environ.get("DATABASE_USER")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")
DATABASE_HOST = os.environ.get("DATABASE_HOST")
DATABASE_PORT = os.environ.get("DATABASE_PORT")
DATABASE_NAME = os.environ.get("DATABASE_NAME")

# MSSQL数据库连接字符串
mssql_url = f"mssql+pyodbc://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}?driver=ODBC+Driver+17+for+SQL+Server"
#mssql_url = "mssql+pyodbc://sa:ABCabc123@150.158.136.4:1433/yida?driver=ODBC+Driver+17+for+SQL+Server"
engine = create_engine(mssql_url, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    try:
        SQLModel.metadata.create_all(engine)
        with Session(engine) as session:
            existing_data = session.exec(select(ListItem)).first()
            if not existing_data:
                insert_initial_data(session)
    except Exception as e:
        print(f"Database connection error: {e}")
        raise e

def insert_initial_data(session: Session):
    # 定义一些初始数据
    initial_data = [
        {"name": "产品管理", "hierarchy_code": "1-0", "level": 1, "target_url": None},
        {"name": "产品分类", "hierarchy_code": "1-1", "level": 2, "target_url": "/category_management"},
        {"name": "产品信息", "hierarchy_code": "1-2", "level": 2, "target_url": "/product_management"},
        {"name": "库房管理", "hierarchy_code": "2-0", "level": 1, "target_url": None},
        {"name": "库存查询", "hierarchy_code": "2-1", "level": 2, "target_url": None},
        {"name": "入库管理", "hierarchy_code": "2-2", "level": 2, "target_url": None},
        {"name": "出库管理", "hierarchy_code": "2-3", "level": 2, "target_url": None},
        {"name": "财务管理", "hierarchy_code": "3-0", "level": 1, "target_url": None},
        {"name": "客户管理", "hierarchy_code": "3-1", "level": 2, "target_url": None},
        {"name": "供应商管理", "hierarchy_code": "3-2", "level": 2, "target_url": None},
        {"name": "客户收付款", "hierarchy_code": "3-3", "level": 2, "target_url": None},
        {"name": "供应商收付款", "hierarchy_code": "3-4", "level": 2, "target_url": None},
        {"name": "系统管理", "hierarchy_code": "4-0", "level": 1, "target_url": None},
    ]
    for item in initial_data:
        list_item = ListItem(**item)
        session.add(list_item)
    session.commit()
    print("初始数据已插入到数据库。")