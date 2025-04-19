from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request, Response
from typing import List
from database import create_db_and_tables, get_session
from auth import app as auth_app
from list_models import ListItem
from sqlmodel import Session, create_engine, select
from models import ProductCategory, Product
import tempfile
from obs import ObsClient, PutObjectHeader
import time
import os
import traceback
import uuid
import asyncio
from dotenv import load_dotenv
import redis
from contextlib import asynccontextmanager
from auth import router as auth_router

load_dotenv()

OBS_AK = os.environ.get("OBS_AK")
OBS_SK = os.environ.get("OBS_SK")
OBS_SERVER = os.environ.get("OBS_SERVER")
OBS_BUCKET_NAME = os.environ.get("OBS_BUCKET_NAME")
obs_client = ObsClient(access_key_id=OBS_AK, secret_access_key=OBS_SK, server=OBS_SERVER)

# 全局变量，用于存储数据库连接状态
database_connected = True

# 数据库连接重试逻辑
def check_database_connection():
    try:
        create_db_and_tables()
        return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False

# 后台任务，定期检查数据库连接状态
async def monitor_database_connection():
    global database_connected
    while True:
        if not check_database_connection():
            print("Database connection lost. Exiting main app...")
            database_connected = False
            # 这里建议用更优雅的方式停止应用，而不是直接退出
            # sys.exit(1)  
        await asyncio.sleep(300)  # 每5分钟检查一次



@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动事件
    try:
        # 检查数据库连接
        if not check_database_connection():
            print("Failed to connect to the database. Exiting main app...")
            # 这里建议用更优雅的方式停止应用，而不是直接退出
            # sys.exit(1)  
        # 启动后台任务
        asyncio.create_task(monitor_database_connection())
        # 删除 FastAPILimiter 初始化相关代码
        print("应用启动，资源初始化完成")
    except Exception as e:
        print(f"应用启动时出错: {e}")
    yield
    # 关闭事件
    try:
        print("应用关闭，开始清理资源")
        # 这里可以添加应用关闭时需要执行的代码，如关闭数据库连接等
        print("资源清理完成")
    except Exception as e:
        print(f"应用关闭时出错: {e}")

app = FastAPI(lifespan=lifespan)

# 允许所有来源访问后端
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 挂载 auth_app 到 /auth 路径
app.mount("/auth", auth_app)
app.include_router(auth_router, prefix="/auth")

# 提供静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(GZipMiddleware, minimum_size=1000)

templates = Jinja2Templates(directory="static")

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/login")
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register")
def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/forgot_password")
def forgot_password(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})

@app.get("/home")
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/category_management")
def home(request: Request):
    return templates.TemplateResponse("category_management.html", {"request": request})

@app.get("/product_management")
def home(request: Request):
    return templates.TemplateResponse("product_management.html", {"request": request})

@app.get("/items/")
def read_items(session: Session = Depends(get_session)):
    items = session.exec(select(ListItem)).all()
    return items

@app.post("/categories/", response_model=ProductCategory)
def create_category(category: ProductCategory, session: Session = Depends(get_session)):
    db_category = ProductCategory.from_orm(category)
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category

@app.get("/categories/", response_model=List[ProductCategory])
def read_categories(session: Session = Depends(get_session)):
    categories = session.exec(select(ProductCategory)).all()
    return categories

@app.get("/categories/{category_id}", response_model=ProductCategory)
def read_category(category_id: int, session: Session = Depends(get_session)):
    category = session.get(ProductCategory, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@app.put("/categories/{category_id}", response_model=ProductCategory)
def update_category(category_id: int, category: ProductCategory, session: Session = Depends(get_session)):
    db_category = session.get(ProductCategory, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    category_data = category.dict(exclude_unset=True)
    for key, value in category_data.items():
        setattr(db_category, key, value)
    session.commit()
    session.refresh(db_category)
    return db_category

@app.delete("/categories/{category_id}", response_model=ProductCategory)
def delete_category(category_id: int, session: Session = Depends(get_session)):
    db_category = session.get(ProductCategory, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    session.delete(db_category)
    session.commit()
    return db_category

# 创建产品
@app.post("/products/", response_model=Product)
def create_product(product: Product, session: Session = Depends(get_session)):
    # 验证产品分类是否存在
    category = session.get(ProductCategory, product.product_category_id)
    if not category:
        raise HTTPException(status_code=404, detail=f"Category with ID {product.product_category_id} not found")

    session.add(product)
    session.commit()
    session.refresh(product)
    return product

# 获取所有产品
@app.get("/products/")
def read_products(session: Session = Depends(get_session)):
    products = session.exec(select(Product)).all()
    return products

# 获取单个产品
@app.get("/products/{product_id}")
def read_product(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# 更新产品
@app.put("/products/{product_id}", response_model=Product)
def update_product(product_id: int, product_update: Product, session: Session = Depends(get_session)):
    db_product = session.get(Product, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    # 更新字段
    product_data = product_update.dict(exclude_unset=True)
    for key, value in product_data.items():
        setattr(db_product, key, value)

    session.commit()
    session.refresh(db_product)
    return db_product

# 删除产品
@app.delete("/products/{product_id}", response_model=dict)
def delete_product(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    session.delete(product)
    session.commit()
    return {"message": "Product deleted successfully"}

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name
            content = await file.read()
            temp_file.write(content)

        # 上传对象的附加头域
        headers = PutObjectHeader()
        # 【可选】待上传对象的MIME类型
        headers.contentType = file.content_type
        # 使用 UUID 生成唯一文件名
        unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
        object_key = unique_filename
        # 上传文件的自定义元数据
        metadata = {'meta1': 'value1', 'meta2': 'value2'}
        # 文件上传
        resp = obs_client.putFile(OBS_BUCKET_NAME, object_key, temp_file_path, metadata, headers)

        # 删除临时文件
        os.remove(temp_file_path)

        # 返回码为2xx时，接口调用成功，否则接口调用失败
        if resp.status < 300:
            print('Put File Succeeded')
            print('requestId:', resp.requestId)
            print('etag:', resp.body.etag)
            print('versionId:', resp.body.versionId)
            print('storageClass:', resp.body.storageClass)
            # 构建图片URL
            image_url = f"https://{OBS_BUCKET_NAME}.obs.cn-north-4.myhuaweicloud.com/{object_key}"
            return {"image_url": image_url}
        else:
            print('Put File Failed')
            print('requestId:', resp.requestId)
            print('errorCode:', resp.errorCode)
            print('errorMessage:', resp.errorMessage)
            return {"error": resp.errorMessage}
    except Exception as e:
        print('Put File Failed')
        print(traceback.format_exc())
        return {"error": str(e)}
    

    # 获取微信小程序登录配置


