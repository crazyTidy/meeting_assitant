#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: system
Time: 2026/03/04
"""
"""User-related Pydantic items for Meeting Assistant."""
from pydantic import BaseModel, Field
from typing import Optional


class UserItem(BaseModel):
    """用户数据项。"""
    user_id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    real_name: str = Field(..., description="真实姓名")
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    department_id: Optional[str] = Field(None, description="部门ID")
    is_active: bool = Field(True, description="是否激活")


class UserListItem(BaseModel):
    """用户列表项。"""
    user_id: str
    username: str
    real_name: str
    department_name: Optional[str] = None
