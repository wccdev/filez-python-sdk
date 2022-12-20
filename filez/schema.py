from typing import Optional

from pydantic import BaseModel

# from datetime import datetime


class UserInfo(BaseModel):
    email: str  # required unique
    mobile: Optional[str] = None
    password: str  # required
    quota: Optional[int] = None  # 单位Bytes
    status: Optional[int] = None  # 用户状态 {冻结:-1,激活:1}
    user_name: str  # required unique
    user_slug: str  # required unique
