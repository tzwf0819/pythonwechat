from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from typing import List
from database import create_db_and_tables ,get_session   # 假设你在database.py中定义了这个函数
from auth import app as auth_app  # 导入auth.py中的app
from fastapi import Depends
from list_models import ListItem
from sqlmodel import Session, create_engine, select
from models import ProductCategory, Product

app = FastAPI()


# 允许所有来源访问后端
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    create_db_and_tables()

# 挂载 auth_app 到 /auth 路径
app.mount("/auth", auth_app)

# 提供静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(GZipMiddleware, minimum_size=1000)
'''
@app.get("/")
async def read_root():
    return RedirectResponse(url="/static/home.html")
'''


templates = Jinja2Templates(directory="static")

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

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

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
@app.post("/products/")
def create_product(product: Product, session: Session = Depends(get_session)):
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
@app.put("/products/{product_id}")
def update_product(product_id: int, product: Product, session: Session = Depends(get_session)):
    db_product = session.get(Product, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    product_data = product.dict(exclude_unset=True)
    for key, value in product_data.items():
        setattr(db_product, key, value)
    session.commit()
    session.refresh(db_product)
    return db_product

# 删除产品
@app.delete("/products/{product_id}")
def delete_product(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    session.delete(product)
    session.commit()
    return {"ok": True}