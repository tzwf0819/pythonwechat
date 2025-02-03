from sqlmodel import create_engine, SQLModel, Session

# MSSQL数据库连接字符串
mssql_url = "mssql+pyodbc://sa:shaoyansa@localhost:1433/yida?driver=ODBC+Driver+17+for+SQL+Server"
connect_args = {"check_same_thread": False}
engine = create_engine(mssql_url, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)