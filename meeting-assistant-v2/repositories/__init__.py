#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: system
Time: 2026/03/04
"""
"""Repositories package for Meeting Assistant."""

from .meeting_repository import (
    meeting_repository,
    participant_repository,
    summary_repository
)

__all__ = [
    "meeting_repository",
    "participant_repository",
    "summary_repository",
]
