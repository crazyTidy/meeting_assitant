#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: Hman.
Time: 2024/12/27.
"""
from sqlalchemy import Column, String

from .base_model import BaseModel


class UserModel(BaseModel):
    __tablename__ = "user_data"

    username = Column(String, nullable=False, comment="用户名")
    hashed_password = Column(String, nullable=False, comment="用户密码")


def main():
    pass


if __name__ == "__main__":
    main()
