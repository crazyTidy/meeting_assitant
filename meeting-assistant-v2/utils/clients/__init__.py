#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: system
Time: 2026/03/04
"""
"""Clients package for Meeting Assistant."""

from .minio_client import minio_client
from .redis_client import redis_client
from .user_client import user_client, UserClient
from .permission_client import permission_client, PermissionClient
from .department_client import department_client, DepartmentClient

__all__ = [
    "minio_client",
    "redis_client",
    "user_client",
    "UserClient",
    "permission_client",
    "PermissionClient",
    "department_client",
    "DepartmentClient",
]
