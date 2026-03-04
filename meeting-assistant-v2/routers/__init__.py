#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: system
Time: 2026/03/04
"""
"""Routers package for Meeting Assistant."""

from .meeting_router import router as meeting_router

__all__ = [
    "meeting_router",
]
