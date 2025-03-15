from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Session, select
from sqlalchemy import Column, NVARCHAR

from database import engine, get_session
from fastapi import BackgroundTasks
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis 
import requests
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import json
from fastapi import Request
from dotenv import load_dotenv
load_dotenv()
# 获取 JWT 配置
SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")

# 获取 API 配置

# 获取微信登录配置
WECHAT_APP_ID = os.environ.get("WECHAT_APP_ID")
WECHAT_APP_SECRET = os.environ.get("WECHAT_APP_SECRET")

ACCESS_TOKEN_EXPIRE_MINUTES = 30




class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(sa_column=Column("username", NVARCHAR(255), unique=True, index=True))
    email: str | None = Field(default=None)
    full_name: str | None = Field(default=None)
    disabled: bool = Field(default=False)
    hashed_password: str
    wechat_openid: str | None = Field(default=None, index=True, unique=True)
    wechat_session_key: str | None = Field(default=None)
    last_login: datetime | None = Field(default=None)
    login_ip: str | None = Field(default=None)

class UserInDB(User):
    pass

class UserCreate(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    password: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(session: Session, username: str) -> User | None:
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    return user

def authenticate_user(session: Session, username: str, password: str) -> User | bool:
    user = get_user(session, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[Session, Depends(get_session)]
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(session, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

app = FastAPI()

@app.post("/token", response_model=Token, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_session)]
):
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@app.post("/users/", response_model=User)
async def create_user(user: UserCreate, session: Annotated[Session, Depends(get_session)]):
    db_user = get_user(session, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@app.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    print("Debug: current_user:", current_user)
    return current_user

@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]

@app.get("/")
async def root():
    return RedirectResponse(url="/static/home.html")


class ForgotPasswordRequest(BaseModel):
    username: str
    full_name: str
    email: str
    new_password: str

@app.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, session: Annotated[Session, Depends(get_session)]):
    user = session.exec(select(User).where(User.username == request.username, User.email == request.email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.full_name != request.full_name:
        raise HTTPException(status_code=400, detail="Full name does not match")
    
    # 更新密码
    user.hashed_password = get_password_hash(request.new_password)
    session.add(user)
    session.commit()
    

class WechatLoginRequest(BaseModel):
    code: str
    encrypted_data: str | None = None
    iv: str | None = None

# 微信登录路由
@app.post("/auth/wechat-login")
async def wechat_login(
    request: WechatLoginRequest,
    session: Annotated[Session, Depends(get_session)],
    client_ip: str = Depends(lambda x: x.client.host)
):
    # 获取微信session_key和openid
    wx_url = f"https://api.weixin.qq.com/sns/jscode2session?appid={WECHAT_APP_ID}&secret={WECHAT_APP_SECRET}&js_code={request.code}&grant_type=authorization_code" 
    wx_res = requests.get(wx_url, timeout=10)
    wx_data = wx_res.json()
    
    if 'errcode' in wx_data:
        raise HTTPException(status_code=400, detail=wx_data['errmsg'])
    
    # 查找或创建用户
    user = session.exec(select(User).where(User.wechat_openid == wx_data['openid'])).first()
    if not user:
        user = User(
            wechat_openid=wx_data['openid'],
            wechat_session_key=wx_data['session_key'],
            username=f"wx_{wx_data['openid'][-8:]}",
            disabled=False
        )
        session.add(user)
    else:
        user.wechat_session_key = wx_data['session_key']
    
    # 更新登录信息
    user.last_login = datetime.now(timezone.utc)
    user.login_ip = client_ip
    session.commit()
    
    # 生成JWT
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    # 解密用户信息（如果需要）
    if request.encrypted_data and request.iv:
        try:
            user_info = decrypt_wechat_info(
                request.encrypted_data,
                request.iv,
                wx_data['session_key']
            )
            user.full_name = user_info.get('nickName')
            user.email = user_info.get('email')
            session.commit()
        except Exception as e:
            print(f"解密失败: {str(e)}")
    
    return Token(access_token=access_token, token_type="bearer")
# 微信信息解密函数
def decrypt_wechat_info(encrypted_data: str, iv: str, session_key: str) -> dict:
    cipher = Cipher(
        algorithms.AES(base64.b64decode(session_key)),
        modes.CBC(base64.b64decode(iv)),
        backend=default_backend()
    )
    decryptor = cipher.decryptor()
    decrypted = decryptor.update(base64.b64decode(encrypted_data)) + decryptor.finalize()
    pad = decrypted[-1]
    content = decrypted[:-pad].decode('utf-8')
    return json.loads(content)

# 增强安全中间件（在app实例后添加）
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response

# 补充Swagger文档描述
app.description = """
## Authentication API

### 功能说明：
- 标准用户名密码登录
- 微信小程序登录集成
- JWT令牌管理
- 密码安全重置流程

### 安全要求：
- 所有敏感请求必须使用HTTPS
- 密码字段传输前需要前端进行SHA256哈希
- JWT令牌有效期30分钟
"""


@app.on_event("startup")
async def startup():
    FastAPILimiter.init(redis.Redis.from_url("redis://localhost"))  # 修正后


