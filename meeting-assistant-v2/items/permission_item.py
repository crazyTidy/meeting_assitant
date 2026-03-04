#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: system
Time: 2026/03/04
"""
"""Permission-related Pydantic items for Meeting Assistant."""
from pydantic import BaseModel, Field


class PermissionItem(BaseModel):
    """权限数据项。"""
    permission_id: str = Field(..., description="权限ID")
    resource: str = Field(..., description="资源标识")
    action: str = Field(..., description="操作类型")
    description: Optional[str] = Field(None, description="权限描述")


class RoleItem(BaseModel):
    """角色数据项。"""
    role_id: str = Field(..., description="角色ID")
    role_name: str = Field(..., description="角色名称")
    description: Optional[str] = Field(None, description="角色描述")
