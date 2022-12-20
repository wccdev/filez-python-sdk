from typing import Optional

from pydantic import BaseModel

# from datetime import datetime


class ConfigInfo(BaseModel):
    app_key: str  # 应用key
    app_secret: str  # 应用secret
    https: bool = False  # 是否使用https
    host: str  # filez服务地址"filez.xxx.cn:3334"
    version: str = "v2"  # 版本号


class UserInfo(BaseModel):
    email: str  # required unique
    mobile: Optional[str] = None
    password: str  # required
    quota: Optional[int] = None  # 单位Bytes
    status: Optional[int] = None  # 用户状态 {冻结:-1,激活:1}
    user_name: str  # required unique
    user_slug: str  # required unique
