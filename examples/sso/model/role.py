# coding: utf-8
from sqlalchemy import Column, String, Integer, Text
from .base import Base


class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)  # 主键
    name = Column(String(20))  # 用户名称
    password = Column(String(64)) # 用户密码，sha256加密
    create_at = Column(Integer)  # 创建时间
    update_at = Column(Integer) # 用户信息更新时间
    status = Column(Integer, default=0)
    login_at = Column(Integer)
    role_id = Column(Integer, default=1) # 角色信息
    meta = Column(Text)
