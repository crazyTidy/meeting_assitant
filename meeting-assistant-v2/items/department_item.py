#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: system
Time: 2026/03/04
"""
"""Department-related Pydantic items for Meeting Assistant."""
from pydantic import BaseModel, Field
from typing import List, Optional


class DepartmentItem(BaseModel):
    """部门数据项。"""
    department_id: str = Field(..., description="部门ID")
    department_name: str = Field(..., description="部门名称")
    parent_id: Optional[str] = Field(None, description="父部门ID")
    level: int = Field(..., description="部门层级")
    sort_order: int = Field(..., description="排序顺序")


class DepartmentTreeItem(BaseModel):
    """部门树数据项。"""
    department_id: str
    department_name: str
    parent_id: Optional[str] = None
    level: int
    children: List["DepartmentTreeItem"] = []
