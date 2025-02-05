from sqlmodel import create_engine, SQLModel, Session, select
from list_models import ListItem
# MSSQL数据库连接字符串
mssql_url = "mssql+pyodbc://sa:shaoyansa@localhost:1433/yida?driver=ODBC+Driver+17+for+SQL+Server"
engine = create_engine(mssql_url, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        # 插入初始数据之前，您可能想要检查数据是否已经存在，以避免重复插入
        existing_data = session.exec(select(ListItem)).first()
        if not existing_data:
            insert_initial_data(session)


def insert_initial_data(session: Session):
    # 定义一些初始数据
    initial_data = [
        {"name": "顶级菜单", "hierarchy_code": "1-0-0", "level": 1, "target_url": "/top-menu-1"},
        {"name": "二级菜单1", "hierarchy_code": "1-1-0", "level": 2, "target_url": "/second-menu-1-1"},
        {"name": "二级菜单2", "hierarchy_code": "1-2-0", "level": 2, "target_url": "/second-menu-1-2"},
        {"name": "三级菜单1", "hierarchy_code": "1-1-1", "level": 3, "target_url": "/third-menu-1-1-1"},
    ]

    # 遍历初始数据，为每个项目创建 ListItem 实例，并添加到会话中
    for item in initial_data:
        list_item = ListItem(**item)
        session.add(list_item)
    
    # 提交会话以保存更改到数据库
    session.commit()

    print("初始数据已插入到数据库。")