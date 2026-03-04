#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: system
Time: 2026/03/04
"""
"""Items (Pydantic schemas) package for Meeting Assistant."""

from .meeting_item import (
    ParticipantItem,
    ParticipantCreateItem,
    ParticipantUpdateItem,
    ParticipantResponseItem,
    SpeakerSegmentResponseItem,
    MergedSegmentResponseItem,
    SummaryItem,
    SummaryResponseItem,
    MeetingCreateItem,
    MeetingResponseItem,
    MeetingDetailResponseItem,
    MeetingStatusResponseItem,
    MeetingListResponseItem,
    ErrorResponseItem,
)
from .user_item import UserItem, UserListItem
from .permission_item import PermissionItem, RoleItem
from .department_item import DepartmentItem, DepartmentTreeItem

__all__ = [
    "ParticipantItem",
    "ParticipantCreateItem",
    "ParticipantUpdateItem",
    "ParticipantResponseItem",
    "SpeakerSegmentResponseItem",
    "MergedSegmentResponseItem",
    "SummaryItem",
    "SummaryResponseItem",
    "MeetingCreateItem",
    "MeetingResponseItem",
    "MeetingDetailResponseItem",
    "MeetingStatusResponseItem",
    "MeetingListResponseItem",
    "ErrorResponseItem",
    "UserItem",
    "UserListItem",
    "PermissionItem",
    "RoleItem",
    "DepartmentItem",
    "DepartmentTreeItem",
]
