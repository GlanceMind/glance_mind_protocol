"""
GlanceMind Protocol - Protocol definitions for inter-service communication

Usage:
    from glance_mind_protocol import CrawlerTask, Platform, DataType
    
    # Parse task from dict/JSON
    task = CrawlerTask.from_dict(task_data)
    task = CrawlerTask.from_json(json_string)
    
    # Serialize to dict/JSON
    data = task.to_dict()
    json_str = task.to_json()
"""

from .glance_mind import (
    # Enums
    Platform,
    DataType,
    TimeRange,
    CommentStatus,
    # CrawlerTask types (Scheduler -> Agent)
    TaskFilters,
    TaskConfig,
    CrawlerTaskMeta,
    CrawlerTaskSpec,
    CrawlerTask,
    # DeviceComments types (API -> Executor)
    DeviceCommentsQuery,
    CampaignConfig,
    CommentData,
    Pagination,
    DeviceCommentsResponse,
    UpdateCommentStatusRequest,
    UpdateCommentStatusResponse,
)

__all__ = [
    # Enums
    "Platform",
    "DataType",
    "TimeRange",
    "CommentStatus",
    # CrawlerTask types
    "TaskFilters",
    "TaskConfig",
    "CrawlerTaskMeta",
    "CrawlerTaskSpec",
    "CrawlerTask",
    # DeviceComments types
    "DeviceCommentsQuery",
    "CampaignConfig",
    "CommentData",
    "Pagination",
    "DeviceCommentsResponse",
    "UpdateCommentStatusRequest",
    "UpdateCommentStatusResponse",
]

__version__ = "1.0.0"
