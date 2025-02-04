from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

from database import create_db_and_tables  # 假设你在database.py中定义了这个函数
from auth import app as auth_app  # 导入auth.py中的app

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

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})