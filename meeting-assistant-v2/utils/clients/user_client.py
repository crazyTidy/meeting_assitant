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


class UserClient:
    """用户信息接口客户端。"""

    def __init__(self):
        self.base_url = environment_config.USER_SERVICE_URL
        self.timeout = environment_config.USER_REQUEST_TIMEOUT

    async def get_user_info(self, user_id: str) -> Optional[Dict]:
        """获取用户信息。

        Args:
            user_id: 用户ID

        Returns:
            用户信息字典，如果用户不存在返回 None
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/users/{user_id}")
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    return None
                else:
                    logging.error(f"获取用户信息失败: {response.status_code}")
                    return None
        except Exception as e:
            logging.error(f"获取用户信息异常: {e}")
            return None

    async def get_user_list(self, page: int = 1, page_size: int = 20) -> List[Dict]:
        """获取用户列表。

        Args:
            page: 页码
            page_size: 每页数量

        Returns:
            用户列表
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {"page": page, "page_size": page_size}
                response = await client.get(f"{self.base_url}/api/users", params=params)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("users", [])
                else:
                    logging.error(f"获取用户列表失败: {response.status_code}")
                    return []
        except Exception as e:
            logging.error(f"获取用户列表异常: {e}")
            return []

    async def search_users(self, keyword: str) -> List[Dict]:
        """搜索用户。

        Args:
            keyword: 搜索关键词（用户名、手机号、邮箱）

        Returns:
            匹配的用户列表
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {"keyword": keyword}
                response = await client.get(f"{self.base_url}/api/users/search", params=params)
                if response.status_code == 200:
                    return response.json()
                else:
                    logging.error(f"搜索用户失败: {response.status_code}")
                    return []
        except Exception as e:
            logging.error(f"搜索用户异常: {e}")
            return []

    async def get_user_by_username(self, username: str) -> Optional[Dict]:
        """根据用户名获取用户信息。

        Args:
            username: 用户名

        Returns:
            用户信息字典，如果用户不存在返回 None
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {"username": username}
                response = await client.get(f"{self.base_url}/api/users/by-username", params=params)
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    return None
                else:
                    logging.error(f"根据用户名获取用户信息失败: {response.status_code}")
                    return None
        except Exception as e:
            logging.error(f"根据用户名获取用户信息异常: {e}")
            return None


# Singleton instance
user_client = UserClient()
