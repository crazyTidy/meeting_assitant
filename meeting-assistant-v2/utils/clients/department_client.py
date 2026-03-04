#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: system
Time: 2026/03/04
"""
import logging
from typing import Dict, List, Optional

import httpx

from ...settings import environment_config


class DepartmentClient:
    """部门树接口客户端。"""

    def __init__(self):
        self.base_url = environment_config.DEPARTMENT_SERVICE_URL
        self.timeout = environment_config.USER_REQUEST_TIMEOUT

    async def get_department_tree(self) -> List[Dict]:
        """获取完整的部门树。

        Returns:
            部门树列表
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/departments/tree")
                if response.status_code == 200:
                    return response.json()
                else:
                    logging.error(f"获取部门树失败: {response.status_code}")
                    return []
        except Exception as e:
            logging.error(f"获取部门树异常: {e}")
            return []

    async def get_department_info(self, department_id: str) -> Optional[Dict]:
        """获取部门信息。

        Args:
            department_id: 部门ID

        Returns:
            部门信息字典，如果部门不存在返回 None
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/departments/{department_id}")
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    return None
                else:
                    logging.error(f"获取部门信息失败: {response.status_code}")
                    return None
        except Exception as e:
            logging.error(f"获取部门信息异常: {e}")
            return None

    async def get_department_members(self, department_id: str) -> List[Dict]:
        """获取部门成员列表。

        Args:
            department_id: 部门ID

        Returns:
            成员用户列表
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/departments/{department_id}/members")
                if response.status_code == 200:
                    return response.json()
                else:
                    logging.error(f"获取部门成员失败: {response.status_code}")
                    return []
        except Exception as e:
            logging.error(f"获取部门成员异常: {e}")
            return []

    async def get_user_department(self, user_id: str) -> Optional[Dict]:
        """获取用户所属的部门。

        Args:
            user_id: 用户ID

        Returns:
            部门信息字典，如果用户没有部门返回 None
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/departments/by-user/{user_id}")
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    return None
                else:
                    logging.error(f"获取用户部门失败: {response.status_code}")
                    return None
        except Exception as e:
            logging.error(f"获取用户部门异常: {e}")
            return None

    async def get_child_departments(self, department_id: str) -> List[Dict]:
        """获取子部门列表。

        Args:
            department_id: 父部门ID

        Returns:
            子部门列表
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/departments/{department_id}/children")
                if response.status_code == 200:
                    return response.json()
                else:
                    logging.error(f"获取子部门失败: {response.status_code}")
                    return []
        except Exception as e:
            logging.error(f"获取子部门异常: {e}")
            return []


# Singleton instance
department_client = DepartmentClient()
