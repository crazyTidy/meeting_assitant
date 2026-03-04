#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: system
Time: 2026/03/04
"""
import logging
from typing import List, Optional

import httpx

from ...settings import environment_config


class PermissionClient:
    """权限验证接口客户端。"""

    def __init__(self):
        self.base_url = environment_config.PERMISSION_SERVICE_URL
        self.timeout = environment_config.USER_REQUEST_TIMEOUT

    async def check_permission(self, user_id: str, resource: str, action: str) -> bool:
        """检查用户是否有权限。

        Args:
            user_id: 用户ID
            resource: 资源标识（如 "order:create"）
            action: 操作类型（如 "create", "read", "update", "delete"）

        Returns:
            是否有权限
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                data = {
                    "user_id": user_id,
                    "resource": resource,
                    "action": action
                }
                response = await client.post(f"{self.base_url}/api/permissions/check", json=data)
                if response.status_code == 200:
                    result = response.json()
                    return result.get("has_permission", False)
                else:
                    logging.error(f"检查权限失败: {response.status_code}")
                    return False
        except Exception as e:
            logging.error(f"检查权限异常: {e}")
            return False

    async def get_user_permissions(self, user_id: str) -> List[Dict]:
        """获取用户的所有权限。

        Args:
            user_id: 用户ID

        Returns:
            权限列表
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/permissions/users/{user_id}")
                if response.status_code == 200:
                    return response.json()
                else:
                    logging.error(f"获取用户权限失败: {response.status_code}")
                    return []
        except Exception as e:
            logging.error(f"获取用户权限异常: {e}")
            return []

    async def get_user_roles(self, user_id: str) -> List[str]:
        """获取用户的角色列表。

        Args:
            user_id: 用户ID

        Returns:
            角色列表
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/permissions/users/{user_id}/roles")
                if response.status_code == 200:
                    return response.json()
                else:
                    logging.error(f"获取用户角色失败: {response.status_code}")
                    return []
        except Exception as e:
            logging.error(f"获取用户角色异常: {e}")
            return []

    async def check_role(self, user_id: str, role: str) -> bool:
        """检查用户是否有某个角色。

        Args:
            user_id: 用户ID
            role: 角色名称

        Returns:
            是否有该角色
        """
        roles = await self.get_user_roles(user_id)
        return role in roles


# Singleton instance
permission_client = PermissionClient()
