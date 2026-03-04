#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: Hman.
Time: 2024/08/14.
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def do_get_hello_world():
    return "Hello World!"


@router.post("/")
async def do_post_hello_world(input_item: dict):
    return input_item


def main():
    pass


if __name__ == "__main__":
    main()
