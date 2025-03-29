# 标准库导入
from datetime import datetime, timedelta, timezone
import os
import logging
import base64
import json

# 第三方库导入
import jwt
from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Session, select
from sqlalchemy import Column, NVARCHAR
from redis import asyncio as aioredis
import requests
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from dotenv import load_dotenv
import sqlalchemy
import logging
# 项目内部模块导入
from database import engine, get_session
import asyncio
from contextlib import asynccontextmanager


# 配置日志
logging.basicConfig(level=logging.DEBUG)


# 加载环境变量
load_dotenv()

# 获取 JWT 配置
SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")

# 获取微信登录配置
WECHAT_APP_ID = os.environ.get("WECHAT_APP_ID")
WECHAT_APP_SECRET = os.environ.get("WECHAT_APP_SECRET")

# 访问令牌过期时间（分钟）
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 数据模型定义
class Token(BaseModel):
    """令牌数据模型，包含访问令牌和令牌类型"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """令牌数据，包含用户名"""
    username: str | None = None

class User(SQLModel, table=True):
    """用户数据模型，对应数据库表"""
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(sa_column=Column("username", NVARCHAR(255), unique=True, index=True))
    email: str | None = Field(default=None)
    full_name: str | None = Field(default=None)
    disabled: bool = Field(default=False)
    hashed_password: str
    wechat_openid: str = Field(sa_column=Column(sqlalchemy.String(255)))
    wechat_session_key: str | None = Field(default=None)
    last_login: datetime | None = Field(default=None)
    login_ip: str | None = Field(default=None)
    # 添加 avatar_url 属性
    avatar_url: str | None = Field(default=None)
    phone: str | None = Field(default=None, sa_column=Column(NVARCHAR(20)))
    address: str | None = Field(default=None, sa_column=Column(NVARCHAR(255)))
    
class UserInDB(User):
    """数据库中的用户数据模型"""
    pass

class UserCreate(BaseModel):
    """创建用户请求数据模型"""
    username: str
    email: str | None = None
    full_name: str | None = None
    password: str

class ForgotPasswordRequest(BaseModel):
    """忘记密码请求数据模型"""
    username: str
    full_name: str
    email: str
    new_password: str

class WechatLoginRequest(BaseModel):
    """微信登录请求数据模型"""
    code: str
    encrypted_data: str | None = None
    iv: str | None = None

# 密码处理
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    """验证密码是否匹配"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """获取密码的哈希值"""
    return pwd_context.hash(password)

# 用户操作
def get_user(session: Session, username: str) -> User | None:
    """根据用户名从数据库中获取用户信息"""
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    return user

def authenticate_user(session: Session, username: str, password: str) -> User | bool:
    """验证用户身份，返回用户对象或 False"""
    user = get_user(session, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

# JWT 操作
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 依赖项
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
):
    """获取当前用户信息，验证令牌有效性"""
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
    current_user: User = Depends(get_current_user),
):
    """获取当前活跃用户信息，检查用户是否禁用"""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# FastAPI 应用实例





app = FastAPI()

# 跨域请求处理
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    """用户登录，返回访问令牌"""
    try:
        user = authenticate_user(session, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")
    except Exception as e:
        logging.error(f"Error in login_for_access_token: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {str(e)}"
        )


@app.post("/users/", response_model=User)
async def create_user(user: UserCreate, session: Session = Depends(get_session)):
    """创建新用户"""
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
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """获取完整的用户资料"""
    return {
        "full_name": current_user.full_name,
        "phone": current_user.phone,
        "address": current_user.address,
        "avatar_url": current_user.avatar_url,
        "wechat_openid": current_user.wechat_openid
    }

# 更新资料接口
@app.post("/update-profile")
async def update_user_profile(
    profile_data: dict,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """更新用户资料接口 - 调试版"""
    try:
        # 打印当前值
        print(f"更新前用户数据 - full_name: {current_user.full_name}, phone: {current_user.phone}, address: {current_user.address}")
        
        # 强制更新所有字段
        if 'nickName' in profile_data:
            current_user.full_name = profile_data['nickName']
            print(f"设置 full_name 为: {profile_data['nickName']}")
        
        if 'phone' in profile_data:
            current_user.phone = profile_data['phone']
        
        if 'address' in profile_data:
            current_user.address = profile_data['address']
        
        # 打印变更状态
        print(f"ORM 检测到变更: {session.is_modified(current_user)}")
        print(f"变更后的待提交状态: {current_user.__dict__}")
        
        session.add(current_user)
        session.commit()
        session.refresh(current_user)  # 强制刷新
        
        # 验证更新结果
        print(f"更新后用户数据 - full_name: {current_user.full_name}, phone: {current_user.phone}, address: {current_user.address}")
        
        return {
            "success": True,
            "user_info": {
                "nickName": current_user.full_name,
                "phone": current_user.phone,
                "address": current_user.address
            }
        }
    except Exception as e:
        session.rollback()
        print(f"更新失败: {str(e)}")
        return {
            "success": False,
            "message": str(e)
        }
    
@app.get("/users/me/items/")
async def read_own_items(
    current_user: User = Depends(get_current_active_user),
):
    """获取当前用户的物品信息"""
    return [{"item_id": "Foo", "owner": current_user.username}]

@app.get("/")
async def root():
    """根路由，重定向到主页"""
    return RedirectResponse(url="/home")

@app.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, session: Session = Depends(get_session)):
    """忘记密码，重置用户密码"""
    user = session.exec(select(User).where(User.username == request.username, User.email == request.email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.full_name != request.full_name:
        raise HTTPException(status_code=400, detail="Full name does not match")
    user.hashed_password = get_password_hash(request.new_password)
    session.add(user)
    session.commit()
    return {"message": "Password updated successfully"}

async def get_client_ip(request: Request) -> str:
    return request.client.host

@app.post("/wechat-login")
async def wechat_login(
    request: WechatLoginRequest,
    session: Session = Depends(get_session),
    client_ip: str = Depends(get_client_ip)
):
    """优化后的微信登录接口"""
    try:
        # 1. 获取微信session_key
        wx_url = f"https://api.weixin.qq.com/sns/jscode2session?appid={WECHAT_APP_ID}&secret={WECHAT_APP_SECRET}&js_code={request.code}&grant_type=authorization_code"
        wx_res = requests.get(wx_url, timeout=10)
        wx_res.raise_for_status()
        wx_data = wx_res.json()
        
        if 'errcode' in wx_data:
            raise HTTPException(status_code=400, detail=wx_data['errmsg'])
        
        # 2. 处理用户数据
        user = session.exec(select(User).where(User.wechat_openid == wx_data['openid'])).first()
        is_new_user = False
        
        if not user:
            default_password = get_password_hash("123123")
            user = User(
                wechat_openid=wx_data['openid'],
                wechat_session_key=wx_data['session_key'],
                username=f"wx_{wx_data['openid'][-8:]}",
                full_name="微信用户",  # 临时默认值
                disabled=False,
                hashed_password=default_password
            )
            session.add(user)
            is_new_user = True
        
        # 3. 更新用户信息
        user.wechat_session_key = wx_data['session_key']
        user.last_login = datetime.now(timezone.utc)
        user.login_ip = client_ip
        
        # 4. 解密微信信息（如果有）
        if request.encrypted_data and request.iv:
            try:
                user_info = decrypt_wechat_info(request.encrypted_data, request.iv, wx_data['session_key'])
                user.full_name = user_info.get('nickName', user.full_name)
                user.avatar_url = user_info.get('avatarUrl', user.avatar_url)
            except Exception as e:
                logging.error(f"微信信息解密失败: {e}")
                if is_new_user:
                    raise HTTPException(status_code=400, detail="首次登录需授权用户信息")
        
        session.commit()
        
        # 5. 生成令牌
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return {
            "code": 200,
            "data": {
                "access_token": access_token,
                "token_type": "bearer",
                "nickName": user.full_name,
                "avatarUrl": user.avatar_url or "https://yida-wechat.obs.cn-north-4.myhuaweicloud.com/avatar/default.png"
            },
            "message": "登录成功"
        }
        
    except requests.RequestException as e:
        logging.error(f"微信API请求失败: {e}")
        raise HTTPException(status_code=502, detail="微信服务暂时不可用")
    except Exception as e:
        logging.error(f"登录处理异常: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="服务器内部错误")
    
# 微信信息解密函数
def decrypt_wechat_info(encrypted_data: str, iv: str, session_key: str) -> dict:
    """解密微信用户信息"""
    cipher = Cipher(
        algorithms.AES(base64.b64decode(session_key)),
        modes.CBC(base64.b64decode(iv)),
        backend=default_backend()
    )
    decryptor = cipher.decryptor()
    decrypted = decryptor.update(base64.b64decode(encrypted_data)) + decryptor.finalize()
    pad = decrypted[-1]
    content = decrypted[:-pad].decode('utf-8')
    print(content)
    return json.loads(content)

# 增强安全中间件
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """添加安全响应头"""
    logging.info(f"Received request: {request.method} {request.url}")
    logging.info(f"Request headers: {request.headers}")
    body = await request.body()
    logging.info(f"Request body: {body.decode('utf-8')}")
    
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response

# 补充 Swagger 文档描述
app.description = """
## Authentication API

### 功能说明：
- 标准用户名密码登录
- 微信小程序登录集成
- JWT 令牌管理
- 密码安全重置流程

### 安全要求：
- 所有敏感请求必须使用 HTTPS
- 密码字段传输前需要前端进行 SHA256 哈希
- JWT 令牌有效期 30 分钟
"""