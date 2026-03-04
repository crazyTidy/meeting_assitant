#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: hongxueshu.
Time: 2025/02/19.
"""
import jwt


def jwt_encode(secret_key: str, payload: dict):
    """生成 JWT Token。"""
    # 生成 Token
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token


def jwt_decode(secret_key: str, token):
    """解析 JWT Token。"""
    # 解码 Token
    payload = jwt.decode(token, secret_key, algorithms=["HS256"])
    return payload


def main():
    pass


if __name__ == "__main__":
    main()
