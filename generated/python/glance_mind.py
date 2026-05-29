"""
GlanceMind Protocol - Auto-generated from Protocol Buffers
DO NOT EDIT - Generated from proto/*.proto

This module provides protocol definitions for:
- Queue messages (Scheduler <-> Agent)
- REST API (API <-> Executor)
- DM group control (Executor <-> NATS <-> API)
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional
import json


# ============================================================
# Common Types (from common.proto)
# ============================================================

class Platform(str, Enum):
    """Supported social media platforms"""
    UNSPECIFIED = "unspecified"
    REDDIT = "reddit"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    YOUTUBE = "youtube"
    
    @classmethod
    def from_string(cls, value: str) -> "Platform":
        """Parse from string (case-insensitive)"""
        value_lower = value.lower()
        for member in cls:
            if member.value == value_lower:
                return member
        return cls.UNSPECIFIED
    
    @classmethod
    def from_platform_id(cls, platform_id: int) -> "Platform":
        """Convert from database platform_id"""
        mapping = {
            1: cls.REDDIT,
            2: cls.TIKTOK,
            3: cls.FACEBOOK,
            4: cls.INSTAGRAM,
            5: cls.TWITTER,
            6: cls.YOUTUBE,
        }
        return mapping.get(platform_id, cls.UNSPECIFIED)


class DataType(str, Enum):
    """Type of data to crawl"""
    UNSPECIFIED = "unspecified"
    VIDEO_CONTENT = "video_content"
    VIDEO_METADATA = "video_metadata"
    VIDEO_COMMENTS = "video_comments"
    KEYWORD_SEARCH = "keyword_search"
    
    @classmethod
    def from_string(cls, value: str) -> "DataType":
        for member in cls:
            if member.value == value:
                return member
        return cls.UNSPECIFIED


class TimeRange(str, Enum):
    """Time range filter for search"""
    UNSPECIFIED = "unspecified"
    ALL_TIME = "all_time"
    LAST_24H = "last_24h"
    LAST_7D = "last_7d"
    LAST_30D = "last_30d"
    LAST_180D = "last_180d"
    
    @classmethod
    def from_string(cls, value: str) -> "TimeRange":
        for member in cls:
            if member.value == value:
                return member
        return cls.UNSPECIFIED


class CommentStatus(str, Enum):
    """Comment processing status"""
    UNSPECIFIED = "unspecified"
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    
    @classmethod
    def from_string(cls, value: str) -> "CommentStatus":
        for member in cls:
            if member.value == value:
                return member
        return cls.UNSPECIFIED
    
    @classmethod
    def from_i16(cls, status: int) -> "CommentStatus":
        """Convert from database status code (i16)"""
        mapping = {
            0: cls.PENDING,
            1: cls.PROCESSING,
            2: cls.COMPLETED,
        }
        return mapping.get(status, cls.UNSPECIFIED)
    
    def to_i16(self) -> int:
        """Convert to database status code (i16)"""
        mapping = {
            self.PENDING: 0,
            self.PROCESSING: 1,
            self.COMPLETED: 2,
        }
        return mapping.get(self, -1)


# ============================================================
# CrawlerTask Types (from crawler_task.proto)
# Scheduler -> Agent via Redis Queue
# ============================================================

@dataclass
class TaskFilters:
    """Task filters"""
    time_range: Optional[TimeRange] = None
    region: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {}
        if self.time_range is not None:
            result["time_range"] = self.time_range.value
        if self.region is not None:
            result["region"] = self.region
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskFilters":
        return cls(
            time_range=TimeRange.from_string(data["time_range"]) if data.get("time_range") else None,
            region=data.get("region"),
        )


@dataclass
class TaskConfig:
    """Task configuration"""
    keywords: List[str] = field(default_factory=list)
    max_count: int = 50
    search_offset: int = 0
    search_limit: int = 20
    filters: Optional[TaskFilters] = None
    search_options: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "keywords": self.keywords,
            "max_count": self.max_count,
            "search_offset": self.search_offset,
            "search_limit": self.search_limit,
        }
        if self.filters is not None:
            result["filters"] = self.filters.to_dict()
        if self.search_options is not None:
            result["search_options"] = self.search_options
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskConfig":
        filters = None
        if data.get("filters"):
            filters = TaskFilters.from_dict(data["filters"])
        return cls(
            keywords=data.get("keywords", []),
            max_count=data.get("max_count", 50),
            search_offset=data.get("search_offset", 0),
            search_limit=data.get("search_limit", 20),
            filters=filters,
            search_options=data.get("search_options"),
        )


@dataclass
class CrawlerTaskMeta:
    """Task metadata"""
    task_id: int
    source: str
    timestamp: float
    campaign_id: int = 0

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "task_id": self.task_id,
            "source": self.source,
            "timestamp": self.timestamp,
        }
        if self.campaign_id:
            d["campaign_id"] = self.campaign_id
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CrawlerTaskMeta":
        return cls(
            task_id=data["task_id"],
            source=data["source"],
            timestamp=data["timestamp"],
            campaign_id=data.get("campaign_id", 0),
        )


@dataclass
class CrawlerTaskSpec:
    """Task specification"""
    platform: Platform
    data_type: DataType
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "platform": self.platform.value,
            "data_type": self.data_type.value,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CrawlerTaskSpec":
        return cls(
            platform=Platform.from_string(data["platform"]),
            data_type=DataType.from_string(data["data_type"]),
        )


@dataclass
class CrawlerTask:
    """Task message sent from Scheduler to Agent via Redis Queue"""
    meta: CrawlerTaskMeta
    spec: CrawlerTaskSpec
    config: TaskConfig
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "meta": self.meta.to_dict(),
            "spec": self.spec.to_dict(),
            "config": self.config.to_dict(),
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CrawlerTask":
        return cls(
            meta=CrawlerTaskMeta.from_dict(data["meta"]),
            spec=CrawlerTaskSpec.from_dict(data["spec"]),
            config=TaskConfig.from_dict(data["config"]),
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "CrawlerTask":
        return cls.from_dict(json.loads(json_str))


# ============================================================
# DeviceComments Types (from device_comments.proto)
# API -> Executor via REST
# ============================================================

@dataclass
class DeviceCommentsQuery:
    """Request parameters for device-based comment query"""
    device_id: str
    status: Optional[int] = None
    page: int = 1
    per_page: int = 20
    platform: str = "tiktok"
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "device_id": self.device_id,
            "page": self.page,
            "per_page": self.per_page,
            "platform": self.platform,
        }
        if self.status is not None:
            result["status"] = self.status
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeviceCommentsQuery":
        return cls(
            device_id=data["device_id"],
            status=data.get("status"),
            page=data.get("page", 1),
            per_page=data.get("per_page", 20),
            platform=data.get("platform", "tiktok"),
        )


@dataclass
class CampaignConfig:
    """Campaign auto-interaction configuration"""
    campaign_id: int = 0
    auto_like: bool = False
    auto_follow: bool = False
    auto_dm: bool = False
    auto_reply_comments: bool = False
    auto_reply_post: bool = False
    profile_name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "campaign_id": self.campaign_id,
            "auto_like": self.auto_like,
            "auto_follow": self.auto_follow,
            "auto_dm": self.auto_dm,
            "auto_reply_comments": self.auto_reply_comments,
            "auto_reply_post": self.auto_reply_post,
        }
        if self.profile_name is not None:
            result["profile_name"] = self.profile_name
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CampaignConfig":
        return cls(
            campaign_id=data.get("campaign_id", 0),
            auto_like=data.get("auto_like", False),
            auto_follow=data.get("auto_follow", False),
            auto_dm=data.get("auto_dm", False),
            auto_reply_comments=data.get("auto_reply_comments", False),
            auto_reply_post=data.get("auto_reply_post", False),
            profile_name=data.get("profile_name"),
        )


@dataclass
class CommentData:
    """Individual comment data"""
    id: int
    comment_id: str
    content_id: str
    platform: Platform
    status: CommentStatus
    created_at: str
    content: Optional[str] = None
    user_nickname: Optional[str] = None
    user_unique_id: Optional[str] = None
    suggested_reply: Optional[str] = None
    suggested_dm: Optional[str] = None
    suggested_reply_post: Optional[str] = None
    reason: Optional[str] = None
    create_time: Optional[str] = None
    # Platform-specific fields for URL construction
    content_url: Optional[str] = None      # Direct URL to the content (post/video/tweet)
    content_type: Optional[str] = None     # Content type: POST/VIDEO/REEL (mainly for Facebook)
    author_unique_id: Optional[str] = None # Author's unique ID (for TikTok URL construction)
    comment_url: Optional[str] = None      # Direct URL to the comment
    comment_user_url: Optional[str] = None # Direct URL to the comment author's profile
    # Profile name for task execution
    # Randomly selected from campaign's associated social group
    # Used by executor to determine which browser profile to use
    profile_name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "id": self.id,
            "comment_id": self.comment_id,
            "content_id": self.content_id,
            "platform": self.platform.value,
            "status": self.status.value,
            "created_at": self.created_at,
        }
        # Add optional fields if present
        optional_fields = [
            "content", "user_nickname", "user_unique_id",
            "suggested_reply", "suggested_dm", "suggested_reply_post",
            "reason", "create_time",
            "content_url", "content_type", "author_unique_id", "comment_url",
            "comment_user_url",
            "profile_name"
        ]
        for field_name in optional_fields:
            value = getattr(self, field_name)
            if value is not None:
                result[field_name] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CommentData":
        return cls(
            id=data["id"],
            comment_id=data["comment_id"],
            content_id=data["content_id"],
            platform=Platform.from_string(data["platform"]) if isinstance(data["platform"], str) else Platform.from_platform_id(data["platform"]),
            status=CommentStatus.from_string(data["status"]) if isinstance(data["status"], str) else CommentStatus.from_i16(data["status"]),
            created_at=data["created_at"],
            content=data.get("content"),
            user_nickname=data.get("user_nickname"),
            user_unique_id=data.get("user_unique_id"),
            suggested_reply=data.get("suggested_reply"),
            suggested_dm=data.get("suggested_dm"),
            suggested_reply_post=data.get("suggested_reply_post"),
            reason=data.get("reason"),
            create_time=data.get("create_time"),
            content_url=data.get("content_url"),
            content_type=data.get("content_type"),
            author_unique_id=data.get("author_unique_id"),
            comment_url=data.get("comment_url"),
            comment_user_url=data.get("comment_user_url"),
            profile_name=data.get("profile_name"),
        )
    
    def get_target_url(self) -> Optional[str]:
        """
        Get the target URL for browser automation.
        Returns content_url if available, otherwise constructs URL based on platform.
        """
        if self.content_url:
            return self.content_url
        
        # Construct URL based on platform
        if self.platform == Platform.TIKTOK:
            # TikTok URL: https://www.tiktok.com/@{author}/video/{video_id}
            author = self.author_unique_id or self.user_unique_id
            if author and self.content_id:
                return f"https://www.tiktok.com/@{author}/video/{self.content_id}"
        elif self.platform == Platform.FACEBOOK:
            # Facebook URL varies by content_type
            if self.content_id:
                return f"https://www.facebook.com/{self.content_id}"
        elif self.platform == Platform.INSTAGRAM:
            # Instagram URL: https://www.instagram.com/p/{shortcode}/
            if self.content_id:
                return f"https://www.instagram.com/p/{self.content_id}/"
        elif self.platform == Platform.TWITTER:
            # Twitter/X URL: https://twitter.com/{user}/status/{tweet_id}
            if self.user_unique_id and self.content_id:
                return f"https://twitter.com/{self.user_unique_id}/status/{self.content_id}"
        elif self.platform == Platform.REDDIT:
            # Reddit URL: Need full URL from content_url
            pass
        
        return None


@dataclass
class Pagination:
    """Pagination information"""
    total: int
    page: int
    per_page: int
    total_pages: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total": self.total,
            "page": self.page,
            "per_page": self.per_page,
            "total_pages": self.total_pages,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Pagination":
        return cls(
            total=data["total"],
            page=data["page"],
            per_page=data["per_page"],
            total_pages=data["total_pages"],
        )


@dataclass
class DeviceCommentsResponse:
    """Optimized response structure: campaign config extracted, comments as array"""
    campaign: CampaignConfig
    comments: List[CommentData]
    pagination: Pagination
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "campaign": self.campaign.to_dict(),
            "comments": [c.to_dict() for c in self.comments],
            "pagination": self.pagination.to_dict(),
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeviceCommentsResponse":
        return cls(
            campaign=CampaignConfig.from_dict(data["campaign"]),
            comments=[CommentData.from_dict(c) for c in data["comments"]],
            pagination=Pagination.from_dict(data["pagination"]),
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "DeviceCommentsResponse":
        return cls.from_dict(json.loads(json_str))


@dataclass
class UpdateCommentStatusRequest:
    """Request to update comment status"""
    comment_id: str
    status: CommentStatus
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "comment_id": self.comment_id,
            "status": self.status.value,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UpdateCommentStatusRequest":
        return cls(
            comment_id=data["comment_id"],
            status=CommentStatus.from_string(data["status"]),
        )


@dataclass
class UpdateCommentStatusResponse:
    """Response for status update"""
    success: bool
    message: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "message": self.message,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UpdateCommentStatusResponse":
        return cls(
            success=data["success"],
            message=data["message"],
        )


# ============================================================
# AIPub Types (from aipub.proto)
# API <-> Scheduler for AI Publish feature
#
# Version History:
# - v1 (2026-01-26): Initial protocol with AiPubInput, AiPubTaskContent,
#                    AiTaskInput, AiTaskResult
# ============================================================

# Current protocol version
AIPUB_PROTOCOL_VERSION = 2


# ============================================================
# AIPub Enums (SINGLE SOURCE OF TRUTH - from aipub.proto)
# MUST match: DB CHECK constraints, Rust entity enums
# ============================================================

# ============================================================
# AIPub Enums (SINGLE SOURCE OF TRUTH - from aipub.proto)
#
# These classes define ALL valid string values for each enum.
# MUST match: DB CHECK constraints, Rust entity enums, proto spec.
#
# IMPORTANT: Includes all historical values for backward compat.
# ============================================================


class PlanType:
    """
    Plan type - gm_aipub_plans.plan_type
    Determines the processing strategy for a publish plan.

    DB CHECK: ('batch_text', 'single_video', 'account_grooming',
               'reddit_text', 'reddit_image', 'reddit_link',
               'direct_publish')
    Source of truth: aipub.proto PlanType (Phase 4 Round 3 Task 4).
    """
    BATCH_TEXT = "batch_text"
    SINGLE_VIDEO = "single_video"
    ACCOUNT_GROOMING = "account_grooming"
    REDDIT_TEXT = "reddit_text"
    REDDIT_IMAGE = "reddit_image"
    REDDIT_LINK = "reddit_link"
    ALL = [
        BATCH_TEXT,
        SINGLE_VIDEO,
        ACCOUNT_GROOMING,
        REDDIT_TEXT,
        REDDIT_IMAGE,
        REDDIT_LINK,
    ]
    REDDIT_PLAN_TYPES = (REDDIT_TEXT, REDDIT_IMAGE, REDDIT_LINK)


class ContentType:
    """
    Content type - gm_aipub_plans.content_type
    DB CHECK: ('post', 'video', 'reel', 'story', 'profile')
    """
    POST = "post"
    VIDEO = "video"
    REEL = "reel"
    STORY = "story"
    PROFILE = "profile"
    ALL = [POST, VIDEO, REEL, STORY, PROFILE]

# Backward-compatible alias
ContentTypeEnum = ContentType


class PlanStatus:
    """
    Plan status - gm_aipub_plans.status
    Plan-level lifecycle (NOT publish task level).
    DB CHECK: ('pending', 'ai_processing', 'ready', 'completed', 'failed')
    """
    PENDING = "pending"
    AI_PROCESSING = "ai_processing"
    READY = "ready"
    COMPLETED = "completed"
    FAILED = "failed"
    ALL = [PENDING, AI_PROCESSING, READY, COMPLETED, FAILED]

# Backward-compatible alias
PlanStatusEnum = PlanStatus


class PublishTaskStatus:
    """
    Publish task status - gm_aipub_tasks.status
    Task-level lifecycle, used by Executor <-> API communication.
    Includes historical video-pipeline states for backward compat.
    DB CHECK: ('pending','video_pending','video_processing','ready',
               'processing','completed','failed')
    """
    PENDING = "pending"
    VIDEO_PENDING = "video_pending"          # historical: waiting for video gen
    VIDEO_PROCESSING = "video_processing"    # historical: video being generated
    READY = "ready"                          # ready for executor to pick up
    PROCESSING = "processing"                # executor is working on it
    COMPLETED = "completed"                  # published successfully
    FAILED = "failed"
    ALL = [PENDING, VIDEO_PENDING, VIDEO_PROCESSING, READY, PROCESSING, COMPLETED, FAILED]


class AiTaskType:
    """
    AI task type - gm_aipub_ai_tasks.task_type
    Determines scheduler processing logic.
    DB CHECK: ('video_gen','content_gen','image_gen','combined','account_grooming')
    """
    CONTENT_GEN = "content_gen"
    VIDEO_GEN = "video_gen"
    IMAGE_GEN = "image_gen"
    COMBINED = "combined"
    ACCOUNT_GROOMING = "account_grooming"
    ALL = [CONTENT_GEN, VIDEO_GEN, IMAGE_GEN, COMBINED, ACCOUNT_GROOMING]

# Backward-compatible alias
AiTaskTypeEnum = AiTaskType


class AiTaskStatus:
    """
    AI task status - gm_aipub_ai_tasks.status
    DB CHECK: ('pending', 'processing', 'completed', 'failed')
    """
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ALL = [PENDING, PROCESSING, COMPLETED, FAILED]


@dataclass
class AiPubImageConfig:
    """Image configuration for FL video models"""
    start_frame_url: Optional[str] = None
    end_frame_url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {}
        if self.start_frame_url is not None:
            result["start_frame_url"] = self.start_frame_url
        if self.end_frame_url is not None:
            result["end_frame_url"] = self.end_frame_url
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AiPubImageConfig":
        return cls(
            start_frame_url=data.get("start_frame_url"),
            end_frame_url=data.get("end_frame_url"),
        )


# ============================================================
# AI Task Input/Result Protocol
# Structure for gm_aipub_ai_tasks.input and result fields
# Used by: Scheduler (creates/reads)
# ============================================================

@dataclass
class AiTaskInput:
    """
    AI Task Input - stored in gm_aipub_ai_tasks.input
    Supports multiple task types: content_gen, video_gen, combined
    """
    # Protocol version for forward compatibility
    version: int = AIPUB_PROTOCOL_VERSION
    
    # === Content Generation Input ===
    
    # Video generation base prompt (from AiPubInput.video_prompt)
    video_prompt: Optional[str] = None
    
    # Content generation prompt (from AiPubInput.content_prompt)
    content_prompt: Optional[str] = None
    
    # === Video Generation Input ===
    
    # AI model name (e.g., "veo-3.1", "sora-1.0")
    model: Optional[str] = None
    
    # Final assembled prompt for video generation
    prompt: Optional[str] = None
    
    # Associated aipub_task ID (for video_gen tasks)
    aipub_task_id: Optional[int] = None
    
    # Start frame image URL (for image-to-video)
    start_image_url: Optional[str] = None
    
    # End frame image URL (for FL models)
    end_image_url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {"version": self.version}
        if self.video_prompt is not None:
            result["video_prompt"] = self.video_prompt
        if self.content_prompt is not None:
            result["content_prompt"] = self.content_prompt
        if self.model is not None:
            result["model"] = self.model
        if self.prompt is not None:
            result["prompt"] = self.prompt
        if self.aipub_task_id is not None:
            result["aipub_task_id"] = self.aipub_task_id
        if self.start_image_url is not None:
            result["start_image_url"] = self.start_image_url
        if self.end_image_url is not None:
            result["end_image_url"] = self.end_image_url
        return result
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AiTaskInput":
        return cls(
            version=data.get("version", AIPUB_PROTOCOL_VERSION),
            video_prompt=data.get("video_prompt"),
            content_prompt=data.get("content_prompt"),
            model=data.get("model"),
            prompt=data.get("prompt"),
            aipub_task_id=data.get("aipub_task_id"),
            start_image_url=data.get("start_image_url"),
            end_image_url=data.get("end_image_url"),
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "AiTaskInput":
        return cls.from_dict(json.loads(json_str))
    
    @classmethod
    def for_content_gen(cls, video_prompt: Optional[str] = None, content_prompt: Optional[str] = None) -> "AiTaskInput":
        """Create input for content generation task"""
        return cls(
            version=AIPUB_PROTOCOL_VERSION,
            video_prompt=video_prompt,
            content_prompt=content_prompt,
        )
    
    @classmethod
    def for_video_gen(cls, model: str, prompt: str, aipub_task_id: int) -> "AiTaskInput":
        """Create input for video generation task"""
        return cls(
            version=AIPUB_PROTOCOL_VERSION,
            model=model,
            prompt=prompt,
            aipub_task_id=aipub_task_id,
        )
    
    @classmethod
    def for_video_gen_with_images(
        cls,
        model: str,
        prompt: str,
        aipub_task_id: int,
        start_image_url: Optional[str] = None,
        end_image_url: Optional[str] = None,
    ) -> "AiTaskInput":
        """Create input for video generation with images (FL models)"""
        return cls(
            version=AIPUB_PROTOCOL_VERSION,
            model=model,
            prompt=prompt,
            aipub_task_id=aipub_task_id,
            start_image_url=start_image_url,
            end_image_url=end_image_url,
        )


@dataclass
class ContentVariation:
    """
    Content variation - single generated content item.
    Used in AiTaskResult.content_variations for batch content generation.
    Matches proto message ContentVariation.
    """
    # Post title (for TikTok, YouTube, etc.)
    title: str = ""
    
    # Main text content (description/caption)
    # Note: Accepts both "text_content" (proto) and "description" (legacy) for deserialization
    text_content: str = ""
    
    # Hashtags for the post
    hashtags: List[str] = field(default_factory=list)
    
    # Location tag (for TikTok/Instagram geo-tagging, e.g., "New York", "Tokyo")
    location: Optional[str] = None
    
    # Video scene description - unique visual elements for this variation
    # Used to differentiate videos when same base video_prompt is shared
    video_scene: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "title": self.title,
            "text_content": self.text_content,
            "hashtags": self.hashtags,
        }
        if self.location is not None:
            result["location"] = self.location
        if self.video_scene is not None:
            result["video_scene"] = self.video_scene
        return result
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContentVariation":
        # Support both "text_content" (proto) and "description" (legacy)
        text_content = data.get("text_content", data.get("description", ""))
        return cls(
            title=data.get("title", ""),
            text_content=text_content,
            hashtags=data.get("hashtags", []),
            location=data.get("location"),
            video_scene=data.get("video_scene"),
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "ContentVariation":
        return cls.from_dict(json.loads(json_str))


@dataclass
class AiTaskResult:
    """
    AI Task Result - stored in gm_aipub_ai_tasks.result
    """
    # Protocol version for forward compatibility
    version: int = AIPUB_PROTOCOL_VERSION
    
    # === Content Generation Result ===
    
    # Number of content variations generated
    content_count: Optional[int] = None
    
    # Number of video tasks pending
    video_pending_count: Optional[int] = None
    
    # Generated content variations (for batch_text plans)
    content_variations: List[ContentVariation] = field(default_factory=list)
    
    # === Video Generation Result ===
    
    # Generated video URL
    video_url: Optional[str] = None
    
    # Video duration in seconds
    video_duration: Optional[float] = None
    
    # === Common Fields ===
    
    # Timestamp when task completed (ISO 8601 format)
    generated_at: Optional[str] = None
    
    # Error message if task failed
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {"version": self.version}
        if self.content_count is not None:
            result["content_count"] = self.content_count
        if self.video_pending_count is not None:
            result["video_pending_count"] = self.video_pending_count
        if self.content_variations:
            result["content_variations"] = [v.to_dict() for v in self.content_variations]
        if self.video_url is not None:
            result["video_url"] = self.video_url
        if self.video_duration is not None:
            result["video_duration"] = self.video_duration
        if self.generated_at is not None:
            result["generated_at"] = self.generated_at
        if self.error is not None:
            result["error"] = self.error
        return result
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AiTaskResult":
        content_variations = []
        if data.get("content_variations"):
            content_variations = [ContentVariation.from_dict(v) for v in data["content_variations"]]
        return cls(
            version=data.get("version", AIPUB_PROTOCOL_VERSION),
            content_count=data.get("content_count"),
            video_pending_count=data.get("video_pending_count"),
            content_variations=content_variations,
            video_url=data.get("video_url"),
            video_duration=data.get("video_duration"),
            generated_at=data.get("generated_at"),
            error=data.get("error"),
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "AiTaskResult":
        return cls.from_dict(json.loads(json_str))
    
    @classmethod
    def for_content_gen(cls, content_count: int, video_pending_count: int) -> "AiTaskResult":
        """Create result for content generation task"""
        from datetime import datetime, timezone
        return cls(
            version=AIPUB_PROTOCOL_VERSION,
            content_count=content_count,
            video_pending_count=video_pending_count,
            generated_at=datetime.now(timezone.utc).isoformat(),
        )
    
    @classmethod
    def for_content_gen_with_variations(
        cls, 
        content_variations: List[ContentVariation], 
        video_pending_count: int
    ) -> "AiTaskResult":
        """Create result for content generation task with variations"""
        from datetime import datetime, timezone
        return cls(
            version=AIPUB_PROTOCOL_VERSION,
            content_count=len(content_variations),
            video_pending_count=video_pending_count,
            content_variations=content_variations,
            generated_at=datetime.now(timezone.utc).isoformat(),
        )
    
    @classmethod
    def for_video_gen(cls, video_url: str) -> "AiTaskResult":
        """Create result for video generation task"""
        from datetime import datetime, timezone
        return cls(
            version=AIPUB_PROTOCOL_VERSION,
            video_url=video_url,
            generated_at=datetime.now(timezone.utc).isoformat(),
        )
    
    @classmethod
    def for_error(cls, error_msg: str) -> "AiTaskResult":
        """Create error result"""
        from datetime import datetime, timezone
        return cls(
            version=AIPUB_PROTOCOL_VERSION,
            error=error_msg,
            generated_at=datetime.now(timezone.utc).isoformat(),
        )


@dataclass
class AiPubInput:
    """
    AI Publish input configuration.
    Used by API to create plans and by Scheduler to generate AI tasks.
    
    Contains prompts for different content types and optional image configurations for FL models.
    
    ## Prompt Fields
    - video_prompt: Used for video generation (e.g., scene description, transitions, visual style)
    - content_prompt: Used for text content generation (captions, titles, descriptions, hashtags)
    - prompt: Legacy field, kept for backward compatibility. If set, used as fallback when specific prompts are empty.
    
    ## Usage Examples
    - Video content: Set both video_prompt (for video AI) and content_prompt (for text/captions)
    - Text-only content: Only set content_prompt
    - Legacy API calls: Only set prompt (both tasks will use this)
    """
    # Video generation prompt - describes the visual content, scenes, transitions, and style
    # Used by video AI models (e.g., Sora, Veo) to generate video content
    video_prompt: str = ""
    
    # Content/text generation prompt - for titles, captions, descriptions, and hashtags
    # Used by chat AI models (e.g., GPT, DeepSeek) to generate accompanying text
    content_prompt: str = ""
    
    # Legacy prompt field - kept for backward compatibility
    # If video_prompt or content_prompt is empty, this value is used as fallback
    prompt: str = ""
    
    # Default images for FL video models (used for all accounts if no per-account images)
    default_images: Optional[AiPubImageConfig] = None
    
    # Per-account images for FL video models (key: account_id as string)
    # Overrides default_images for specific accounts
    account_images: Optional[Dict[str, AiPubImageConfig]] = None
    # Optional nested configs (JSON-compatible dicts; mirror aipub.proto)
    reference_video: Optional[Dict[str, Any]] = None
    video_config: Optional[Dict[str, Any]] = None
    seedance_config: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        if self.video_prompt:
            result["video_prompt"] = self.video_prompt
        if self.content_prompt:
            result["content_prompt"] = self.content_prompt
        if self.prompt:
            result["prompt"] = self.prompt
        if self.default_images is not None:
            result["default_images"] = self.default_images.to_dict()
        if self.account_images is not None:
            result["account_images"] = {
                k: v.to_dict() for k, v in self.account_images.items()
            }
        if self.reference_video is not None:
            result["reference_video"] = self.reference_video
        if self.video_config is not None:
            result["video_config"] = self.video_config
        if self.seedance_config is not None:
            result["seedance_config"] = self.seedance_config
        return result
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AiPubInput":
        default_images = None
        if data.get("default_images"):
            default_images = AiPubImageConfig.from_dict(data["default_images"])
        
        account_images = None
        if data.get("account_images"):
            account_images = {
                k: AiPubImageConfig.from_dict(v) 
                for k, v in data["account_images"].items()
            }
        
        return cls(
            video_prompt=data.get("video_prompt", ""),
            content_prompt=data.get("content_prompt", ""),
            prompt=data.get("prompt", ""),
            default_images=default_images,
            account_images=account_images,
            reference_video=data.get("reference_video"),
            video_config=data.get("video_config"),
            seedance_config=data.get("seedance_config"),
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "AiPubInput":
        return cls.from_dict(json.loads(json_str))
    
    def get_video_prompt(self) -> str:
        """Get the effective video prompt (falls back to legacy prompt if empty)"""
        return self.video_prompt if self.video_prompt else self.prompt
    
    def get_content_prompt(self) -> str:
        """Get the effective content prompt (falls back to legacy prompt if empty)"""
        return self.content_prompt if self.content_prompt else self.prompt
    
    def get_images_for_account(self, account_id: str) -> Optional[AiPubImageConfig]:
        """
        Get the image configuration for a specific account.
        Returns per-account images if available, otherwise default images.
        """
        if self.account_images and account_id in self.account_images:
            return self.account_images[account_id]
        return self.default_images

    def has_reference_video(self) -> bool:
        return self.reference_video is not None

    def with_reference_video(self, reference_video: Dict[str, Any]) -> "AiPubInput":
        self.reference_video = reference_video
        return self
    
    @classmethod
    def with_prompts(cls, video_prompt: str, content_prompt: str) -> "AiPubInput":
        """Create a new AiPubInput with separate video and content prompts"""
        return cls(video_prompt=video_prompt, content_prompt=content_prompt)


@dataclass
class AiPubTaskContent:
    """
    Content structure for gm_aipub_tasks.content field.
    Used by: Scheduler (creates), API (reads), Executor (reads for publishing)
    
    This is the standardized structure for task content stored in the database.
    """
    # === Publishing Content ===
    
    # Main text content for the post (description/caption)
    text_content: str = ""
    
    # Post title (for TikTok, YouTube, etc.)
    title: str = ""
    
    # Hashtags for the post
    hashtags: List[str] = field(default_factory=list)
    
    # Location tag (for TikTok/Instagram geo-tagging)
    location: Optional[str] = None
    
    # Video scene description - unique visual elements for this variation
    # Used to differentiate videos when same base video_prompt is shared
    video_scene: Optional[str] = None
    
    # === Video Generation ===
    
    # Final video generation prompt (base_prompt + video_scene + title)
    # Sent to video AI for generation
    video_prompt: Optional[str] = None
    
    # Start frame image URL (for image-to-video generation)
    start_frame_url: Optional[str] = None
    
    # End frame image URL (for FL models with transitions)
    end_frame_url: Optional[str] = None
    
    # Generated video URL (filled after video generation completes)
    video_url: Optional[str] = None
    
    # === Task State Flags ===
    
    # Whether this task requires video generation
    video_generation_needed: bool = False
    
    # Whether video has been submitted to generation service
    video_submitted: bool = False
    
    # Associated AI task ID (references gm_aipub_ai_tasks.id)
    ai_task_id: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (for database storage)"""
        result: Dict[str, Any] = {
            "text_content": self.text_content,
            "title": self.title,
            "hashtags": self.hashtags,
        }
        # Add optional fields if present
        if self.location is not None:
            result["location"] = self.location
        if self.video_scene is not None:
            result["video_scene"] = self.video_scene
        if self.video_prompt is not None:
            result["video_prompt"] = self.video_prompt
        if self.start_frame_url is not None:
            result["start_frame_url"] = self.start_frame_url
        if self.end_frame_url is not None:
            result["end_frame_url"] = self.end_frame_url
        if self.video_url is not None:
            result["video_url"] = self.video_url
        if self.video_generation_needed:
            result["video_generation_needed"] = True
        if self.video_submitted:
            result["video_submitted"] = True
        if self.ai_task_id is not None:
            result["ai_task_id"] = self.ai_task_id
        return result
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AiPubTaskContent":
        """Parse from dictionary (from database)"""
        return cls(
            text_content=data.get("text_content", ""),
            title=data.get("title", ""),
            hashtags=data.get("hashtags", []),
            location=data.get("location"),
            video_scene=data.get("video_scene"),
            video_prompt=data.get("video_prompt"),
            start_frame_url=data.get("start_frame_url"),
            end_frame_url=data.get("end_frame_url"),
            video_url=data.get("video_url"),
            video_generation_needed=data.get("video_generation_needed", False),
            video_submitted=data.get("video_submitted", False),
            ai_task_id=data.get("ai_task_id"),
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "AiPubTaskContent":
        return cls.from_dict(json.loads(json_str))
    
    def has_video(self) -> bool:
        """Check if this task has a video (either generated or to be generated)"""
        return bool(self.video_url or self.video_generation_needed)
    
    def is_ready_for_publish(self) -> bool:
        """Check if this task is ready for publishing"""
        # If video needed, must have video_url
        if self.video_generation_needed and not self.video_url:
            return False
        # Must have content
        return bool(self.title or self.text_content)


# ============================================================
# Upload Task Protocol (API -> Executor)
# Endpoint: GET /api/v1/public/tasks/by-device
# ============================================================

@dataclass
class UploadTaskMeta:
    """Upload task metadata (from gm_upload_tasks.metadata JSON)"""
    platform: str = ""
    video_url: str = ""
    description: str = ""
    profile_name: str = ""
    location: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "platform": self.platform,
            "video_url": self.video_url,
            "description": self.description,
            "profile_name": self.profile_name,
        }
        if self.location is not None:
            result["location"] = self.location
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UploadTaskMeta":
        return cls(
            platform=data.get("platform", ""),
            video_url=data.get("video_url", ""),
            description=data.get("description", ""),
            profile_name=data.get("profile_name", ""),
            location=data.get("location"),
        )
    
    def validate(self) -> bool:
        if not self.platform:
            return False
        if not self.video_url:
            return False
        if not self.profile_name:
            return False
        return True


@dataclass
class UploadTaskMessage:
    """
    Upload task - returned by API for executor to process.
    
    API response format:
        { "id": 123, "task_type": "upload", "meta": { ... } }
    """
    id: int = 0
    task_type: str = "upload"
    meta: Optional[UploadTaskMeta] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UploadTaskMessage":
        meta_data = data.get("meta", {})
        return cls(
            id=data.get("id", 0),
            task_type=data.get("task_type", "upload"),
            meta=UploadTaskMeta.from_dict(meta_data) if meta_data else None,
        )
    
    def validate(self) -> bool:
        if not self.meta:
            return False
        return self.meta.validate()


# ============================================================
# Account Grooming Content (shared by Scheduler + Executor)
# ============================================================

@dataclass
class AccountGroomingTaskContent:
    """
    Account grooming task content - stored in gm_aipub_tasks.content
    for plan_type = "account_grooming"
    """
    generated_name: str = ""
    avatar_url: Optional[str] = None
    avatar_prompt: Optional[str] = None
    generated_bio: Optional[str] = None  # Bio text (max ~80 chars)
    
    def to_dict(self) -> Dict[str, Any]:
        result = {"generated_name": self.generated_name}
        if self.avatar_url is not None:
            result["avatar_url"] = self.avatar_url
        if self.avatar_prompt is not None:
            result["avatar_prompt"] = self.avatar_prompt
        if self.generated_bio is not None:
            result["generated_bio"] = self.generated_bio
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AccountGroomingTaskContent":
        return cls(
            generated_name=data.get("generated_name", ""),
            avatar_url=data.get("avatar_url"),
            avatar_prompt=data.get("avatar_prompt"),
            generated_bio=data.get("generated_bio"),
        )


# ============================================================
# Reddit Publish Content (Phase 4 Round 3 Task 4)
# Source of truth: aipub.proto RedditPublishContent (message at line 567).
# Used by plan_type = reddit_text / reddit_image / reddit_link.
# ============================================================

@dataclass
class RedditPublishContent:
    """Reddit publish content - stored in gm_aipub_tasks.content for the
    reddit_text / reddit_image / reddit_link plan types.

    Field-for-field mirror of proto RedditPublishContent. Optional
    fields elide from :meth:`to_dict` output when None so the JSON on
    the wire stays proto-compatible.
    """

    subreddit: str = ""
    reddit_post_type: str = ""  # "TEXT", "IMAGE", "LINK"
    title: str = ""
    body: Optional[str] = None
    link_url: Optional[str] = None
    image_urls: List[str] = field(default_factory=list)
    flair_text: Optional[str] = None
    is_nsfw: bool = False
    is_spoiler: bool = False
    use_markdown: bool = False
    is_brand_affiliate: bool = False

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "subreddit": self.subreddit,
            "reddit_post_type": self.reddit_post_type,
            "title": self.title,
            "is_nsfw": self.is_nsfw,
            "is_spoiler": self.is_spoiler,
            "use_markdown": self.use_markdown,
            "is_brand_affiliate": self.is_brand_affiliate,
        }
        if self.image_urls:
            d["image_urls"] = list(self.image_urls)
        for k in ("body", "link_url", "flair_text"):
            v = getattr(self, k)
            if v is not None:
                d[k] = v
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RedditPublishContent":
        return cls(
            subreddit=data.get("subreddit", ""),
            reddit_post_type=data.get("reddit_post_type", ""),
            title=data.get("title", ""),
            body=data.get("body"),
            link_url=data.get("link_url"),
            image_urls=list(data.get("image_urls") or []),
            flair_text=data.get("flair_text"),
            is_nsfw=bool(data.get("is_nsfw", False)),
            is_spoiler=bool(data.get("is_spoiler", False)),
            use_markdown=bool(data.get("use_markdown", False)),
            is_brand_affiliate=bool(data.get("is_brand_affiliate", False)),
        )


# ============================================================
# AIPub Executor Publish Task Protocol (API -> Executor)
# Endpoint: GET /api/v1/public/aipub/publish_tasks
#
# The "content" field in the API JSON response depends on plan_type:
#   - batch_text/single_video: AiPubTaskContent structure
#   - account_grooming: AccountGroomingTaskContent structure
# ============================================================

@dataclass
class ExecutorPublishTask:
    """
    Executor publish task - returned by API for executor to process.
    
    Routes by plan_type:
      batch_text/single_video -> publish content (video/text)
      account_grooming -> update profile (name + avatar)
    """
    task_id: int = 0
    plan_id: int = 0
    social_account_id: int = 0
    platform: str = ""
    platform_id: int = 0
    content_type: str = ""    # See ContentType enum
    plan_type: str = ""       # See PlanType enum
    profile_name: str = ""
    content: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutorPublishTask":
        """
        Parse from API JSON response.
        
        Note: API returns `content` as a JSON object, not a string.
        The content structure depends on plan_type.
        """
        content = data.get("content", {})
        if isinstance(content, str):
            content = json.loads(content)
        return cls(
            task_id=data.get("task_id", 0),
            plan_id=data.get("plan_id", 0),
            social_account_id=data.get("social_account_id", 0),
            platform=data.get("platform", "").lower(),
            platform_id=data.get("platform_id", 0),
            content_type=data.get("content_type", ""),
            plan_type=data.get("plan_type", ""),
            profile_name=data.get("profile_name", ""),
            content=content,
            created_at=data.get("created_at", ""),
        )
    
    def is_account_grooming(self) -> bool:
        return self.plan_type == PlanType.ACCOUNT_GROOMING

    def is_video_publish(self) -> bool:
        return self.content_type == ContentTypeEnum.VIDEO

    def is_reddit(self) -> bool:
        """Phase 4 Round 3 Task 4 — true for any reddit plan type."""
        return self.plan_type in PlanType.REDDIT_PLAN_TYPES

    def get_grooming_content(self) -> Optional[AccountGroomingTaskContent]:
        """Parse content as AccountGroomingTaskContent"""
        if not self.is_account_grooming():
            return None
        return AccountGroomingTaskContent.from_dict(self.content)

    def get_publish_content(self) -> Optional[AiPubTaskContent]:
        """Parse content as AiPubTaskContent.

        Returns None for non-AiPubTaskContent shapes (account grooming
        and reddit posts have their own content dataclasses).
        """
        if self.is_account_grooming() or self.is_reddit():
            return None
        return AiPubTaskContent.from_dict(self.content)

    def get_reddit_content(self) -> Optional[RedditPublishContent]:
        """Parse content as RedditPublishContent for reddit plan types."""
        if not self.is_reddit():
            return None
        return RedditPublishContent.from_dict(self.content)

    def validate(self) -> bool:
        if not self.task_id or not self.platform or not self.profile_name:
            return False
        if self.is_account_grooming():
            gc = self.get_grooming_content()
            return gc is not None and bool(gc.generated_name)
        if self.is_reddit():
            rc = self.get_reddit_content()
            if rc is None or not rc.subreddit or not rc.title:
                return False
            if self.plan_type == PlanType.REDDIT_LINK:
                return bool(rc.link_url)
            if self.plan_type == PlanType.REDDIT_IMAGE:
                return bool(rc.image_urls)
            # REDDIT_TEXT: subreddit + title are sufficient
            # (body is optional even for text posts — a title-only
            #  post is valid Reddit content).
            return True
        if self.is_video_publish():
            pc = self.get_publish_content()
            return pc is not None and bool(pc.video_url)
        return True


@dataclass
class ExecutorTaskStatusUpdate:
    """Executor task status update (Executor -> API)"""
    task_id: int = 0
    status: str = ""
    result_url: Optional[str] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {"task_id": self.task_id, "status": self.status}
        if self.result_url is not None:
            result["result_url"] = self.result_url
        if self.error_message is not None:
            result["error_message"] = self.error_message
        return result


# ============================================================
# DM Group Control Types (from dm.proto)
# NATS JetStream message formats for DM monitoring and reply
# ============================================================

class DmDirection(str, Enum):
    """Direction of a DM message"""
    INBOUND = "inbound"
    OUTBOUND = "outbound"

    @classmethod
    def from_string(cls, value: str) -> "DmDirection":
        for member in cls:
            if member.value == value.lower():
                return member
        return cls.INBOUND


class DmMessageStatus(str, Enum):
    """Status of a DM message"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"

    @classmethod
    def from_string(cls, value: str) -> "DmMessageStatus":
        for member in cls:
            if member.value == value.lower():
                return member
        return cls.PENDING


class DmEventType(str, Enum):
    """Type of DM event notification"""
    NEW_MESSAGE = "new_message"
    MESSAGE_SENT = "message_sent"
    MESSAGE_FAILED = "message_failed"

    @classmethod
    def from_string(cls, value: str) -> "DmEventType":
        for member in cls:
            if member.value == value.lower():
                return member
        return cls.NEW_MESSAGE


class DmContentType(str, Enum):
    """Content type of a DM message"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    LINK = "link"

    @classmethod
    def from_string(cls, value: str) -> "DmContentType":
        for member in cls:
            if member.value == value.lower():
                return member
        return cls.TEXT


class DmConversationStatus(str, Enum):
    """Conversation status"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    MUTED = "muted"

    @classmethod
    def from_string(cls, value: str) -> "DmConversationStatus":
        for member in cls:
            if member.value == value.lower():
                return member
        return cls.ACTIVE


class DmReplyMode(str, Enum):
    """Reply mode for a conversation"""
    MANUAL = "manual"
    AUTO = "auto"

    @classmethod
    def from_string(cls, value: str) -> "DmReplyMode":
        for member in cls:
            if member.value == value.lower():
                return member
        return cls.MANUAL


@dataclass
class DmMessage:
    """DM message stored in NATS Stream DM_MESSAGES, subject: dm.msg.{conv_id}"""
    msg_id: str = ""
    conv_id: str = ""
    direction: str = "inbound"
    content: str = ""
    content_type: str = "text"
    attachments: List[str] = field(default_factory=list)
    status: str = "delivered"
    platform_msg_id: str = ""
    timestamp: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "msg_id": self.msg_id,
            "conv_id": self.conv_id,
            "direction": self.direction,
            "content": self.content,
            "content_type": self.content_type,
            "attachments": self.attachments,
            "status": self.status,
            "platform_msg_id": self.platform_msg_id,
            "timestamp": self.timestamp,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DmMessage":
        return cls(
            msg_id=data.get("msg_id", ""),
            conv_id=data.get("conv_id", ""),
            direction=data.get("direction", "inbound"),
            content=data.get("content", ""),
            content_type=data.get("content_type", "text"),
            attachments=data.get("attachments", []),
            status=data.get("status", "delivered"),
            platform_msg_id=data.get("platform_msg_id", ""),
            timestamp=data.get("timestamp", ""),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "DmMessage":
        return cls.from_dict(json.loads(json_str))


@dataclass
class ConversationMeta:
    """Conversation metadata stored in NATS KV dm_conversations, key: {user_id}.{conv_id}"""
    conv_id: str = ""
    user_id: int = 0
    social_account_id: int = 0
    device_id: str = ""
    platform_id: int = 0
    platform_name: str = ""
    my_username: str = ""
    my_profile_name: str = ""
    remote_user_id: str = ""
    remote_username: str = ""
    remote_display_name: Optional[str] = None
    remote_avatar_url: Optional[str] = None
    last_message_at: str = ""
    last_message_preview: str = ""
    last_message_direction: str = "inbound"
    unread_count: int = 0
    status: str = "active"
    reply_mode: str = "manual"
    ai_suggestion: Optional[str] = None
    updated_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "conv_id": self.conv_id,
            "user_id": self.user_id,
            "social_account_id": self.social_account_id,
            "device_id": self.device_id,
            "platform_id": self.platform_id,
            "platform_name": self.platform_name,
            "my_username": self.my_username,
            "my_profile_name": self.my_profile_name,
            "remote_user_id": self.remote_user_id,
            "remote_username": self.remote_username,
            "remote_display_name": self.remote_display_name,
            "remote_avatar_url": self.remote_avatar_url,
            "last_message_at": self.last_message_at,
            "last_message_preview": self.last_message_preview,
            "last_message_direction": self.last_message_direction,
            "unread_count": self.unread_count,
            "status": self.status,
            "reply_mode": self.reply_mode,
            "ai_suggestion": self.ai_suggestion,
            "updated_at": self.updated_at,
        }
        return result

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationMeta":
        return cls(
            conv_id=data.get("conv_id", ""),
            user_id=data.get("user_id", 0),
            social_account_id=data.get("social_account_id", 0),
            device_id=data.get("device_id", ""),
            platform_id=data.get("platform_id", 0),
            platform_name=data.get("platform_name", ""),
            my_username=data.get("my_username", ""),
            my_profile_name=data.get("my_profile_name", ""),
            remote_user_id=data.get("remote_user_id", ""),
            remote_username=data.get("remote_username", ""),
            remote_display_name=data.get("remote_display_name"),
            remote_avatar_url=data.get("remote_avatar_url"),
            last_message_at=data.get("last_message_at", ""),
            last_message_preview=data.get("last_message_preview", ""),
            last_message_direction=data.get("last_message_direction", "inbound"),
            unread_count=data.get("unread_count", 0),
            status=data.get("status", "active"),
            reply_mode=data.get("reply_mode", "manual"),
            ai_suggestion=data.get("ai_suggestion"),
            updated_at=data.get("updated_at", ""),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "ConversationMeta":
        return cls.from_dict(json.loads(json_str))


@dataclass
class DmEvent:
    """DM event published to NATS DM_EVENTS, subject: dm.evt.{user_id}"""
    event_type: str = "new_message"
    user_id: int = 0
    conv_id: str = ""
    device_id: str = ""
    social_account_id: int = 0
    platform_id: int = 0
    platform_name: str = ""
    remote_username: str = ""
    preview: str = ""
    direction: str = "inbound"
    unread_count: int = 0
    timestamp: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "user_id": self.user_id,
            "conv_id": self.conv_id,
            "device_id": self.device_id,
            "social_account_id": self.social_account_id,
            "platform_id": self.platform_id,
            "platform_name": self.platform_name,
            "remote_username": self.remote_username,
            "preview": self.preview,
            "direction": self.direction,
            "unread_count": self.unread_count,
            "timestamp": self.timestamp,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DmEvent":
        return cls(
            event_type=data.get("event_type", "new_message"),
            user_id=data.get("user_id", 0),
            conv_id=data.get("conv_id", ""),
            device_id=data.get("device_id", ""),
            social_account_id=data.get("social_account_id", 0),
            platform_id=data.get("platform_id", 0),
            platform_name=data.get("platform_name", ""),
            remote_username=data.get("remote_username", ""),
            preview=data.get("preview", ""),
            direction=data.get("direction", "inbound"),
            unread_count=data.get("unread_count", 0),
            timestamp=data.get("timestamp", ""),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "DmEvent":
        return cls.from_dict(json.loads(json_str))


@dataclass
class ReplyCommand:
    """Reply command published to NATS DM_COMMANDS, subject: dm.cmd.{device_id}"""
    cmd_id: str = ""
    conv_id: str = ""
    social_account_id: int = 0
    platform_id: int = 0
    profile_name: str = ""
    remote_username: str = ""
    content: str = ""
    content_type: str = "text"
    timestamp: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cmd_id": self.cmd_id,
            "conv_id": self.conv_id,
            "social_account_id": self.social_account_id,
            "platform_id": self.platform_id,
            "profile_name": self.profile_name,
            "remote_username": self.remote_username,
            "content": self.content,
            "content_type": self.content_type,
            "timestamp": self.timestamp,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReplyCommand":
        return cls(
            cmd_id=data.get("cmd_id", ""),
            conv_id=data.get("conv_id", ""),
            social_account_id=data.get("social_account_id", 0),
            platform_id=data.get("platform_id", 0),
            profile_name=data.get("profile_name", ""),
            remote_username=data.get("remote_username", ""),
            content=data.get("content", ""),
            content_type=data.get("content_type", "text"),
            timestamp=data.get("timestamp", ""),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "ReplyCommand":
        return cls.from_dict(json.loads(json_str))


@dataclass
class DeviceHeartbeat:
    """Device heartbeat stored in NATS KV dm_device_heartbeat, key: {device_id}, TTL: 120s"""
    user_id: int = 0
    device_id: str = ""
    last_seen: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "device_id": self.device_id,
            "last_seen": self.last_seen,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeviceHeartbeat":
        return cls(
            user_id=data.get("user_id", 0),
            device_id=data.get("device_id", ""),
            last_seen=data.get("last_seen", ""),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "DeviceHeartbeat":
        return cls.from_dict(json.loads(json_str))


# ============================================================
# Patrol Group Control Types (from patrol.proto)
# NATS JetStream message formats for account statistics patrol
#
# Streams:   PATROL (subject: patrol.>)
# Subjects:  patrol.profile.{user_id}, patrol.notif.{user_id}
# KV:        patrol_latest (key: {user_id}), patrol_config (key: {device_id})
# ============================================================


@dataclass
class AccountStats:
    """Platform-agnostic collection result for a single account.
    Profile fields are filled by low-frequency collection; notification fields by high-frequency.
    """
    # Profile page fields (low-frequency)
    followers_count: int = 0
    following_count: int = 0
    posts_count: int = 0
    total_likes: int = 0
    # Notification page fields (high-frequency)
    new_followers: int = 0
    received_likes: int = 0
    received_comments: int = 0
    received_dms: int = 0
    received_shares: int = 0
    received_mentions: int = 0
    received_friend_requests: int = 0
    # Metadata
    collected_at: str = ""
    collection_type: str = "profile"   # "profile" | "notification"
    partial: bool = False
    warnings: List[str] = field(default_factory=list)
    error: str = ""
    unread_total: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "followers_count": self.followers_count,
            "following_count": self.following_count,
            "posts_count": self.posts_count,
            "total_likes": self.total_likes,
            "new_followers": self.new_followers,
            "received_likes": self.received_likes,
            "received_comments": self.received_comments,
            "received_dms": self.received_dms,
            "received_shares": self.received_shares,
            "received_mentions": self.received_mentions,
            "received_friend_requests": self.received_friend_requests,
            "collected_at": self.collected_at,
            "collection_type": self.collection_type,
            "partial": self.partial,
            "warnings": self.warnings,
            "error": self.error,
            "unread_total": self.unread_total,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AccountStats":
        return cls(
            followers_count=data.get("followers_count", 0),
            following_count=data.get("following_count", 0),
            posts_count=data.get("posts_count", 0),
            total_likes=data.get("total_likes", 0),
            new_followers=data.get("new_followers", 0),
            received_likes=data.get("received_likes", 0),
            received_comments=data.get("received_comments", 0),
            received_dms=data.get("received_dms", 0),
            received_shares=data.get("received_shares", 0),
            received_mentions=data.get("received_mentions", 0),
            received_friend_requests=data.get("received_friend_requests", 0),
            collected_at=data.get("collected_at", ""),
            collection_type=data.get("collection_type", "profile"),
            partial=data.get("partial", False),
            warnings=data.get("warnings", []),
            error=data.get("error", ""),
            unread_total=data.get("unread_total", 0),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "AccountStats":
        return cls.from_dict(json.loads(json_str))


@dataclass
class AccountPatrolStats:
    """Single account patrol snapshot published to NATS."""
    social_account_id: int = 0
    device_id: str = ""
    user_id: int = 0
    platform_id: int = 0
    platform_name: str = ""
    username: str = ""
    profile_name: str = ""
    stats: Optional[AccountStats] = None
    collected_at: str = ""
    error: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "social_account_id": self.social_account_id,
            "device_id": self.device_id,
            "user_id": self.user_id,
            "platform_id": self.platform_id,
            "platform_name": self.platform_name,
            "username": self.username,
            "profile_name": self.profile_name,
            "stats": self.stats.to_dict() if self.stats else {},
            "collected_at": self.collected_at,
            "error": self.error,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AccountPatrolStats":
        stats_data = data.get("stats")
        return cls(
            social_account_id=data.get("social_account_id", 0),
            device_id=data.get("device_id", ""),
            user_id=data.get("user_id", 0),
            platform_id=data.get("platform_id", 0),
            platform_name=data.get("platform_name", ""),
            username=data.get("username", ""),
            profile_name=data.get("profile_name", ""),
            stats=AccountStats.from_dict(stats_data) if stats_data else None,
            collected_at=data.get("collected_at", ""),
            error=data.get("error", ""),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "AccountPatrolStats":
        return cls.from_dict(json.loads(json_str))


@dataclass
class PatrolReport:
    """One collection cycle report.
    Published to patrol.profile.{user_id} or patrol.notif.{user_id}.
    """
    report_id: str = ""
    report_type: str = "profile"        # "profile" | "notification"
    device_id: str = ""
    user_id: int = 0
    accounts: List[AccountPatrolStats] = field(default_factory=list)
    started_at: str = ""
    completed_at: str = ""
    total_accounts: int = 0
    success_count: int = 0
    error_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "report_type": self.report_type,
            "device_id": self.device_id,
            "user_id": self.user_id,
            "accounts": [a.to_dict() for a in self.accounts],
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "total_accounts": self.total_accounts,
            "success_count": self.success_count,
            "error_count": self.error_count,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PatrolReport":
        accounts_data = data.get("accounts", [])
        return cls(
            report_id=data.get("report_id", ""),
            report_type=data.get("report_type", "profile"),
            device_id=data.get("device_id", ""),
            user_id=data.get("user_id", 0),
            accounts=[AccountPatrolStats.from_dict(a) for a in accounts_data],
            started_at=data.get("started_at", ""),
            completed_at=data.get("completed_at", ""),
            total_accounts=data.get("total_accounts", 0),
            success_count=data.get("success_count", 0),
            error_count=data.get("error_count", 0),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "PatrolReport":
        return cls.from_dict(json.loads(json_str))


@dataclass
class PatrolConfig:
    """Patrol configuration stored in NATS KV patrol_config, key: {device_id}."""
    device_id: str = ""
    enabled: bool = False
    profile_interval_seconds: int = 600
    notification_interval_seconds: int = 180
    platforms: List[str] = field(default_factory=list)
    updated_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "device_id": self.device_id,
            "enabled": self.enabled,
            "profile_interval_seconds": self.profile_interval_seconds,
            "notification_interval_seconds": self.notification_interval_seconds,
            "platforms": self.platforms,
            "updated_at": self.updated_at,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PatrolConfig":
        return cls(
            device_id=data.get("device_id", ""),
            enabled=data.get("enabled", False),
            profile_interval_seconds=data.get("profile_interval_seconds", 600),
            notification_interval_seconds=data.get("notification_interval_seconds", 180),
            platforms=data.get("platforms", []),
            updated_at=data.get("updated_at", ""),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "PatrolConfig":
        return cls.from_dict(json.loads(json_str))


# ============================================================
# AIPub v2 — Unified Content Schema
# Mirror of glance_mind_protocol/proto/aipub.proto v2 section.
# Wire-compatible with Rust prost-generated types in
# generated/rust/src/lib.rs (after build.rs refactor).
# ============================================================


class MediaKind(str, Enum):
    UNSPECIFIED = "unspecified"
    VIDEO = "video"
    IMAGE = "image"
    AUDIO = "audio"
    GIF = "gif"
    SUBTITLE = "subtitle"  # SRT/VTT track bound to a parent video

    @classmethod
    def from_string(cls, v: Any) -> "MediaKind":
        if isinstance(v, cls):
            return v
        try:
            return cls(str(v).lower()) if v is not None else cls.UNSPECIFIED
        except ValueError:
            return cls.UNSPECIFIED


class MediaSource(str, Enum):
    UNSPECIFIED = "unspecified"
    AI_GENERATED = "ai_generated"
    USER_UPLOADED = "user_uploaded"
    REFERENCE = "reference"

    @classmethod
    def from_string(cls, v: Any) -> "MediaSource":
        if isinstance(v, cls):
            return v
        try:
            return cls(str(v).lower()) if v is not None else cls.UNSPECIFIED
        except ValueError:
            return cls.UNSPECIFIED


class MediaStatus(str, Enum):
    UNSPECIFIED = "unspecified"
    PENDING = "pending"
    READY = "ready"
    FAILED = "failed"

    @classmethod
    def from_string(cls, v: Any) -> "MediaStatus":
        if isinstance(v, cls):
            return v
        try:
            return cls(str(v).lower()) if v is not None else cls.UNSPECIFIED
        except ValueError:
            return cls.UNSPECIFIED


class MediaRole(str, Enum):
    UNSPECIFIED = "unspecified"
    PRIMARY = "primary"
    COVER = "cover"
    START_FRAME = "start_frame"
    END_FRAME = "end_frame"
    CAROUSEL_ITEM = "carousel_item"
    REFERENCE = "reference"
    BACKGROUND = "background"
    SOURCE = "source"

    @classmethod
    def from_string(cls, v: Any) -> "MediaRole":
        if isinstance(v, cls):
            return v
        try:
            return cls(str(v).lower()) if v is not None else cls.UNSPECIFIED
        except ValueError:
            return cls.UNSPECIFIED


class TextRole(str, Enum):
    UNSPECIFIED = "unspecified"
    TITLE = "title"
    BODY = "body"
    CAPTION = "caption"
    HASHTAG = "hashtag"
    SUBREDDIT = "subreddit"
    FLAIR = "flair"
    LOCATION = "location"
    VIDEO_SCENE = "video_scene"

    @classmethod
    def from_string(cls, v: Any) -> "TextRole":
        if isinstance(v, cls):
            return v
        try:
            return cls(str(v).lower()) if v is not None else cls.UNSPECIFIED
        except ValueError:
            return cls.UNSPECIFIED


class TextSource(str, Enum):
    UNSPECIFIED = "unspecified"
    AI_GENERATED = "ai_generated"
    USER_PROVIDED = "user_provided"

    @classmethod
    def from_string(cls, v: Any) -> "TextSource":
        if isinstance(v, cls):
            return v
        try:
            return cls(str(v).lower()) if v is not None else cls.UNSPECIFIED
        except ValueError:
            return cls.UNSPECIFIED


class LinkRole(str, Enum):
    UNSPECIFIED = "unspecified"
    EXTERNAL = "external"
    REDDIT_TARGET = "reddit_target"
    PRODUCT = "product"
    PROFILE = "profile"

    @classmethod
    def from_string(cls, v: Any) -> "LinkRole":
        if isinstance(v, cls):
            return v
        try:
            return cls(str(v).lower()) if v is not None else cls.UNSPECIFIED
        except ValueError:
            return cls.UNSPECIFIED


class Visibility(str, Enum):
    UNSPECIFIED = "unspecified"
    PUBLIC = "public"
    UNLISTED = "unlisted"
    FRIENDS = "friends"
    PRIVATE = "private"

    @classmethod
    def from_string(cls, v: Any) -> "Visibility":
        if isinstance(v, cls):
            return v
        try:
            return cls(str(v).lower()) if v is not None else cls.UNSPECIFIED
        except ValueError:
            return cls.UNSPECIFIED


class EntityTagKind(str, Enum):
    UNSPECIFIED = "unspecified"
    MUSIC = "music"
    PRODUCT = "product"
    LOCATION = "location"
    TOPIC = "topic"
    BRAND_PARTNER = "brand_partner"
    # NOTE: USER mention intentionally NOT here; see UserMention message.

    @classmethod
    def from_string(cls, v: Any) -> "EntityTagKind":
        if isinstance(v, cls):
            return v
        try:
            return cls(str(v).lower()) if v is not None else cls.UNSPECIFIED
        except ValueError:
            return cls.UNSPECIFIED


class PostPublishActionKind(str, Enum):
    UNSPECIFIED = "unspecified"
    AUTO_FIRST_COMMENT = "auto_first_comment"
    PIN_TO_PROFILE = "pin_to_profile"
    CROSSPOST = "crosspost"
    SHARE_TO_STORY = "share_to_story"
    NOTIFY_WEBHOOK = "notify_webhook"

    @classmethod
    def from_string(cls, v: Any) -> "PostPublishActionKind":
        if isinstance(v, cls):
            return v
        try:
            return cls(str(v).lower()) if v is not None else cls.UNSPECIFIED
        except ValueError:
            return cls.UNSPECIFIED


class PublishResultStatus(str, Enum):
    UNSPECIFIED = "unspecified"
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"
    RETRYING = "retrying"

    @classmethod
    def from_string(cls, v: Any) -> "PublishResultStatus":
        if isinstance(v, cls):
            return v
        try:
            return cls(str(v).lower()) if v is not None else cls.UNSPECIFIED
        except ValueError:
            return cls.UNSPECIFIED


# ------------------------------------------------------------
# Helper: dump enums as their string value for JSON
# ------------------------------------------------------------


def _enum_val(e: Any) -> Any:
    """Convert a str-Enum to its .value for JSON dump (or pass through)."""
    return e.value if isinstance(e, Enum) else e


# ============================================================
# v2 message: MediaItem
# ============================================================


@dataclass
class MediaItem:
    kind: MediaKind = MediaKind.UNSPECIFIED
    source: MediaSource = MediaSource.UNSPECIFIED
    status: MediaStatus = MediaStatus.UNSPECIFIED
    role: MediaRole = MediaRole.UNSPECIFIED
    order: int = 0
    url: str = ""
    ai_task_id: Optional[int] = None
    mime: Optional[str] = None
    width_px: Optional[int] = None
    height_px: Optional[int] = None
    duration_ms: Optional[int] = None
    bytes: Optional[int] = None
    provider_asset_uri: Optional[str] = None
    language: Optional[str] = None  # BCP-47, required for SUBTITLE
    parent_media_index: Optional[int] = None  # required for SUBTITLE

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "kind": _enum_val(self.kind),
            "source": _enum_val(self.source),
            "status": _enum_val(self.status),
            "role": _enum_val(self.role),
            "order": self.order,
            "url": self.url,
        }
        for k in ("ai_task_id", "mime", "width_px", "height_px", "duration_ms",
                  "bytes", "provider_asset_uri", "language", "parent_media_index"):
            v = getattr(self, k)
            if v is not None:
                d[k] = v
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MediaItem":
        return cls(
            kind=MediaKind.from_string(data.get("kind")),
            source=MediaSource.from_string(data.get("source")),
            status=MediaStatus.from_string(data.get("status")),
            role=MediaRole.from_string(data.get("role")),
            order=data.get("order", 0),
            url=data.get("url", ""),
            ai_task_id=data.get("ai_task_id"),
            mime=data.get("mime"),
            width_px=data.get("width_px"),
            height_px=data.get("height_px"),
            duration_ms=data.get("duration_ms"),
            bytes=data.get("bytes"),
            provider_asset_uri=data.get("provider_asset_uri"),
            language=data.get("language"),
            parent_media_index=data.get("parent_media_index"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "MediaItem":
        return cls.from_dict(json.loads(json_str))


@dataclass
class TextBlock:
    role: TextRole = TextRole.UNSPECIFIED
    value: str = ""
    source: TextSource = TextSource.UNSPECIFIED
    order: int = 0
    variation_index: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "role": _enum_val(self.role),
            "value": self.value,
            "source": _enum_val(self.source),
            "order": self.order,
        }
        if self.variation_index is not None:
            d["variation_index"] = self.variation_index
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TextBlock":
        return cls(
            role=TextRole.from_string(data.get("role")),
            value=data.get("value", ""),
            source=TextSource.from_string(data.get("source")),
            order=data.get("order", 0),
            variation_index=data.get("variation_index"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "TextBlock":
        return cls.from_dict(json.loads(json_str))


@dataclass
class LinkItem:
    role: LinkRole = LinkRole.UNSPECIFIED
    url: str = ""
    label: Optional[str] = None
    order: int = 0

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "role": _enum_val(self.role),
            "url": self.url,
            "order": self.order,
        }
        if self.label is not None:
            d["label"] = self.label
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LinkItem":
        return cls(
            role=LinkRole.from_string(data.get("role")),
            url=data.get("url", ""),
            label=data.get("label"),
            order=data.get("order", 0),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "LinkItem":
        return cls.from_dict(json.loads(json_str))


@dataclass
class EntityTag:
    kind: EntityTagKind = EntityTagKind.UNSPECIFIED
    platform_id: Optional[str] = None
    display_name: str = ""
    text_index: Optional[int] = None
    text_byte_offset: Optional[int] = None
    text_byte_length: Optional[int] = None
    media_index: Optional[int] = None
    media_x: Optional[float] = None
    media_y: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    extras: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "kind": _enum_val(self.kind),
            "display_name": self.display_name,
        }
        for k in ("platform_id", "text_index", "text_byte_offset", "text_byte_length",
                  "media_index", "media_x", "media_y", "latitude", "longitude"):
            v = getattr(self, k)
            if v is not None:
                d[k] = v
        if self.extras:
            d["extras"] = self.extras
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EntityTag":
        return cls(
            kind=EntityTagKind.from_string(data.get("kind")),
            platform_id=data.get("platform_id"),
            display_name=data.get("display_name", ""),
            text_index=data.get("text_index"),
            text_byte_offset=data.get("text_byte_offset"),
            text_byte_length=data.get("text_byte_length"),
            media_index=data.get("media_index"),
            media_x=data.get("media_x"),
            media_y=data.get("media_y"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            extras=dict(data.get("extras", {})),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "EntityTag":
        return cls.from_dict(json.loads(json_str))


@dataclass
class UserMention:
    handle: str = ""
    platform_user_id: Optional[str] = None
    text_index: Optional[int] = None
    byte_offset: Optional[int] = None
    byte_length: Optional[int] = None
    hidden: bool = False

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"handle": self.handle, "hidden": self.hidden}
        for k in ("platform_user_id", "text_index", "byte_offset", "byte_length"):
            v = getattr(self, k)
            if v is not None:
                d[k] = v
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserMention":
        return cls(
            handle=data.get("handle", ""),
            platform_user_id=data.get("platform_user_id"),
            text_index=data.get("text_index"),
            byte_offset=data.get("byte_offset"),
            byte_length=data.get("byte_length"),
            hidden=data.get("hidden", False),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "UserMention":
        return cls.from_dict(json.loads(json_str))


@dataclass
class PublishBehavior:
    visibility: Visibility = Visibility.UNSPECIFIED
    allow_comments: Optional[bool] = None
    allow_sharing: Optional[bool] = None
    allow_download: Optional[bool] = None
    is_nsfw: Optional[bool] = None
    is_spoiler: Optional[bool] = None
    ai_generated_disclosure: Optional[bool] = None
    allow_duet: Optional[bool] = None
    allow_stitch: Optional[bool] = None
    disclose_branded_content: Optional[bool] = None
    allow_remix: Optional[bool] = None
    share_to_facebook: Optional[bool] = None
    extras: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"visibility": _enum_val(self.visibility)}
        for k in ("allow_comments", "allow_sharing", "allow_download", "is_nsfw",
                  "is_spoiler", "ai_generated_disclosure", "allow_duet", "allow_stitch",
                  "disclose_branded_content", "allow_remix", "share_to_facebook"):
            v = getattr(self, k)
            if v is not None:
                d[k] = v
        if self.extras:
            d["extras"] = self.extras
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PublishBehavior":
        return cls(
            visibility=Visibility.from_string(data.get("visibility")),
            allow_comments=data.get("allow_comments"),
            allow_sharing=data.get("allow_sharing"),
            allow_download=data.get("allow_download"),
            is_nsfw=data.get("is_nsfw"),
            is_spoiler=data.get("is_spoiler"),
            ai_generated_disclosure=data.get("ai_generated_disclosure"),
            allow_duet=data.get("allow_duet"),
            allow_stitch=data.get("allow_stitch"),
            disclose_branded_content=data.get("disclose_branded_content"),
            allow_remix=data.get("allow_remix"),
            share_to_facebook=data.get("share_to_facebook"),
            extras=dict(data.get("extras", {})),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "PublishBehavior":
        return cls.from_dict(json.loads(json_str))


@dataclass
class PublishSchedule:
    scheduled_at: str = ""
    timezone: Optional[str] = None
    save_as_draft: bool = False

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "scheduled_at": self.scheduled_at,
            "save_as_draft": self.save_as_draft,
        }
        if self.timezone is not None:
            d["timezone"] = self.timezone
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PublishSchedule":
        return cls(
            scheduled_at=data.get("scheduled_at", ""),
            timezone=data.get("timezone"),
            save_as_draft=data.get("save_as_draft", False),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "PublishSchedule":
        return cls.from_dict(json.loads(json_str))


@dataclass
class PostPublishAction:
    kind: PostPublishActionKind = PostPublishActionKind.UNSPECIFIED
    comment_text: Optional[str] = None
    targets: List[str] = field(default_factory=list)
    webhook_url: Optional[str] = None
    webhook_bearer: Optional[str] = None
    extras: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "kind": _enum_val(self.kind),
            "targets": self.targets,
        }
        for k in ("comment_text", "webhook_url", "webhook_bearer"):
            v = getattr(self, k)
            if v is not None:
                d[k] = v
        if self.extras:
            d["extras"] = self.extras
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PostPublishAction":
        return cls(
            kind=PostPublishActionKind.from_string(data.get("kind")),
            comment_text=data.get("comment_text"),
            targets=list(data.get("targets", [])),
            webhook_url=data.get("webhook_url"),
            webhook_bearer=data.get("webhook_bearer"),
            extras=dict(data.get("extras", {})),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "PostPublishAction":
        return cls.from_dict(json.loads(json_str))


@dataclass
class UnifiedPublishContent:
    """v2 replacement for AiPubTaskContent. version MUST be 2."""
    version: int = 2
    platform: str = ""
    platform_id: int = 0
    content_type: str = ""
    plan_type: str = ""
    media: List[MediaItem] = field(default_factory=list)
    texts: List[TextBlock] = field(default_factory=list)
    links: List[LinkItem] = field(default_factory=list)
    tags: List[EntityTag] = field(default_factory=list)
    mentions: List[UserMention] = field(default_factory=list)
    platform_extras: Dict[str, str] = field(default_factory=dict)
    behavior: Optional[PublishBehavior] = None
    schedule: Optional[PublishSchedule] = None
    post_publish: List[PostPublishAction] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "version": self.version,
            "platform": self.platform,
            "platform_id": self.platform_id,
            "content_type": self.content_type,
            "plan_type": self.plan_type,
            "media": [m.to_dict() for m in self.media],
            "texts": [t.to_dict() for t in self.texts],
            "links": [l.to_dict() for l in self.links],
            "tags": [t.to_dict() for t in self.tags],
            "mentions": [m.to_dict() for m in self.mentions],
            "post_publish": [a.to_dict() for a in self.post_publish],
        }
        if self.platform_extras:
            d["platform_extras"] = self.platform_extras
        if self.behavior is not None:
            d["behavior"] = self.behavior.to_dict()
        if self.schedule is not None:
            d["schedule"] = self.schedule.to_dict()
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UnifiedPublishContent":
        return cls(
            version=data.get("version", 2),
            platform=data.get("platform", ""),
            platform_id=data.get("platform_id", 0),
            content_type=data.get("content_type", ""),
            plan_type=data.get("plan_type", ""),
            media=[MediaItem.from_dict(m) for m in data.get("media", [])],
            texts=[TextBlock.from_dict(t) for t in data.get("texts", [])],
            links=[LinkItem.from_dict(l) for l in data.get("links", [])],
            tags=[EntityTag.from_dict(t) for t in data.get("tags", [])],
            mentions=[UserMention.from_dict(m) for m in data.get("mentions", [])],
            platform_extras=dict(data.get("platform_extras", {})),
            behavior=PublishBehavior.from_dict(data["behavior"]) if data.get("behavior") else None,
            schedule=PublishSchedule.from_dict(data["schedule"]) if data.get("schedule") else None,
            post_publish=[PostPublishAction.from_dict(a) for a in data.get("post_publish", [])],
        )

    @classmethod
    def from_json(cls, json_str: str) -> "UnifiedPublishContent":
        return cls.from_dict(json.loads(json_str))


# ============================================================
# v2 result reporting (Executor → API)
# ============================================================


@dataclass
class MediaPublishResult:
    media_index: int = 0
    status: MediaStatus = MediaStatus.UNSPECIFIED
    platform_asset_id: Optional[str] = None
    platform_asset_url: Optional[str] = None
    failed_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "media_index": self.media_index,
            "status": _enum_val(self.status),
        }
        for k in ("platform_asset_id", "platform_asset_url", "failed_reason"):
            v = getattr(self, k)
            if v is not None:
                d[k] = v
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MediaPublishResult":
        return cls(
            media_index=data.get("media_index", 0),
            status=MediaStatus.from_string(data.get("status")),
            platform_asset_id=data.get("platform_asset_id"),
            platform_asset_url=data.get("platform_asset_url"),
            failed_reason=data.get("failed_reason"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "MediaPublishResult":
        return cls.from_dict(json.loads(json_str))


@dataclass
class PostPublishActionResult:
    action_index: int = 0
    kind: PostPublishActionKind = PostPublishActionKind.UNSPECIFIED
    succeeded: bool = False
    failed_reason: Optional[str] = None
    platform_artifact_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "action_index": self.action_index,
            "kind": _enum_val(self.kind),
            "succeeded": self.succeeded,
        }
        for k in ("failed_reason", "platform_artifact_id"):
            v = getattr(self, k)
            if v is not None:
                d[k] = v
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PostPublishActionResult":
        return cls(
            action_index=data.get("action_index", 0),
            kind=PostPublishActionKind.from_string(data.get("kind")),
            succeeded=data.get("succeeded", False),
            failed_reason=data.get("failed_reason"),
            platform_artifact_id=data.get("platform_artifact_id"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "PostPublishActionResult":
        return cls.from_dict(json.loads(json_str))


@dataclass
class PublishMetrics:
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    plays: int = 0
    snapshot_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "views": self.views,
            "likes": self.likes,
            "comments": self.comments,
            "shares": self.shares,
            "saves": self.saves,
            "plays": self.plays,
        }
        if self.snapshot_at is not None:
            d["snapshot_at"] = self.snapshot_at
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PublishMetrics":
        return cls(
            views=data.get("views", 0),
            likes=data.get("likes", 0),
            comments=data.get("comments", 0),
            shares=data.get("shares", 0),
            saves=data.get("saves", 0),
            plays=data.get("plays", 0),
            snapshot_at=data.get("snapshot_at"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "PublishMetrics":
        return cls.from_dict(json.loads(json_str))


@dataclass
class UnifiedPublishResult:
    """v2 replacement for ExecutorTaskStatusUpdate. version MUST be 2."""
    version: int = 2
    task_id: int = 0
    status: PublishResultStatus = PublishResultStatus.UNSPECIFIED
    platform_post_id: Optional[str] = None
    platform_post_url: Optional[str] = None
    published_at: Optional[str] = None
    failed_reason: Optional[str] = None
    failed_error_code: Optional[str] = None
    retry_count: int = 0
    next_retry_at: Optional[str] = None
    media_results: List[MediaPublishResult] = field(default_factory=list)
    post_publish_results: List[PostPublishActionResult] = field(default_factory=list)
    initial_metrics: Optional[PublishMetrics] = None
    raw_response_json: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "version": self.version,
            "task_id": self.task_id,
            "status": _enum_val(self.status),
            "retry_count": self.retry_count,
            "media_results": [m.to_dict() for m in self.media_results],
            "post_publish_results": [a.to_dict() for a in self.post_publish_results],
        }
        for k in ("platform_post_id", "platform_post_url", "published_at",
                  "failed_reason", "failed_error_code", "next_retry_at",
                  "raw_response_json"):
            v = getattr(self, k)
            if v is not None:
                d[k] = v
        if self.initial_metrics is not None:
            d["initial_metrics"] = self.initial_metrics.to_dict()
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UnifiedPublishResult":
        return cls(
            version=data.get("version", 2),
            task_id=data.get("task_id", 0),
            status=PublishResultStatus.from_string(data.get("status")),
            platform_post_id=data.get("platform_post_id"),
            platform_post_url=data.get("platform_post_url"),
            published_at=data.get("published_at"),
            failed_reason=data.get("failed_reason"),
            failed_error_code=data.get("failed_error_code"),
            retry_count=data.get("retry_count", 0),
            next_retry_at=data.get("next_retry_at"),
            media_results=[MediaPublishResult.from_dict(m) for m in data.get("media_results", [])],
            post_publish_results=[PostPublishActionResult.from_dict(a) for a in data.get("post_publish_results", [])],
            initial_metrics=PublishMetrics.from_dict(data["initial_metrics"]) if data.get("initial_metrics") else None,
            raw_response_json=data.get("raw_response_json"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "UnifiedPublishResult":
        return cls.from_dict(json.loads(json_str))


# ============================================================
# v2 input — generation specs + UnifiedAiPubInput
# ============================================================


@dataclass
class TextGenerationSpec:
    prompts: List[str] = field(default_factory=list)
    count: int = 1
    target_roles: List[str] = field(default_factory=list)
    model: Optional[str] = None
    extras: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "prompts": self.prompts,
            "count": self.count,
            "target_roles": self.target_roles,
        }
        if self.model is not None:
            d["model"] = self.model
        if self.extras:
            d["extras"] = self.extras
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TextGenerationSpec":
        return cls(
            prompts=list(data.get("prompts", [])),
            count=data.get("count", 1),
            target_roles=list(data.get("target_roles", [])),
            model=data.get("model"),
            extras=dict(data.get("extras", {})),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "TextGenerationSpec":
        return cls.from_dict(json.loads(json_str))


@dataclass
class ImageGenerationSpec:
    """All 15 fields including the 8 recently added (v2.0):
    aspect_ratio, output_format, seed, watermark, provider_hint, mode, safety_tolerance.
    Mirrors aipub.proto ImageGenerationSpec.
    """
    prompts: List[str] = field(default_factory=list)
    count: int = 1
    model: Optional[str] = None
    width_px: int = 0
    height_px: int = 0
    role_hint: MediaRole = MediaRole.UNSPECIFIED
    reference_image_urls: List[str] = field(default_factory=list)
    aspect_ratio: Optional[str] = None
    output_format: Optional[str] = None
    extras: Dict[str, str] = field(default_factory=dict)
    seed: Optional[int] = None
    watermark: Optional[bool] = None
    provider_hint: Optional[str] = None  # "flux" | "seedream" | "openai"
    mode: Optional[str] = None  # "text_to_image" | "image_edit"
    safety_tolerance: Optional[int] = None  # Flux only, 0..6

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "prompts": self.prompts,
            "count": self.count,
            "width_px": self.width_px,
            "height_px": self.height_px,
            "role_hint": _enum_val(self.role_hint),
            "reference_image_urls": self.reference_image_urls,
        }
        for k in ("model", "aspect_ratio", "output_format", "seed",
                  "watermark", "provider_hint", "mode", "safety_tolerance"):
            v = getattr(self, k)
            if v is not None:
                d[k] = v
        if self.extras:
            d["extras"] = self.extras
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ImageGenerationSpec":
        return cls(
            prompts=list(data.get("prompts", [])),
            count=data.get("count", 1),
            model=data.get("model"),
            width_px=data.get("width_px", 0),
            height_px=data.get("height_px", 0),
            role_hint=MediaRole.from_string(data.get("role_hint")),
            reference_image_urls=list(data.get("reference_image_urls", [])),
            aspect_ratio=data.get("aspect_ratio"),
            output_format=data.get("output_format"),
            extras=dict(data.get("extras", {})),
            seed=data.get("seed"),
            watermark=data.get("watermark"),
            provider_hint=data.get("provider_hint"),
            mode=data.get("mode"),
            safety_tolerance=data.get("safety_tolerance"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "ImageGenerationSpec":
        return cls.from_dict(json.loads(json_str))


@dataclass
class VideoGenerationSpec:
    """Carries video-specific engine configs as nested dicts (Vidu, Seedance, etc.).
    Engine sub-message types stay v1 typed (ViduVideoConfig / SeedanceVideoConfig)
    and are stored here as their dict form for forward-compat.
    """
    prompts: List[str] = field(default_factory=list)
    count: int = 1
    model: Optional[str] = None
    role_hint: MediaRole = MediaRole.UNSPECIFIED
    video_config: Optional[Dict[str, Any]] = None
    vidu_config: Optional[Dict[str, Any]] = None
    seedance_config: Optional[Dict[str, Any]] = None
    reference_video: Optional[Dict[str, Any]] = None
    start_image_urls: List[str] = field(default_factory=list)
    end_image_urls: List[str] = field(default_factory=list)
    reference_image_urls: List[str] = field(default_factory=list)
    generation_mode: Optional[str] = None
    extras: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "prompts": self.prompts,
            "count": self.count,
            "role_hint": _enum_val(self.role_hint),
            "start_image_urls": self.start_image_urls,
            "end_image_urls": self.end_image_urls,
            "reference_image_urls": self.reference_image_urls,
        }
        for k in ("model", "video_config", "vidu_config", "seedance_config",
                  "reference_video", "generation_mode"):
            v = getattr(self, k)
            if v is not None:
                d[k] = v
        if self.extras:
            d["extras"] = self.extras
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VideoGenerationSpec":
        return cls(
            prompts=list(data.get("prompts", [])),
            count=data.get("count", 1),
            model=data.get("model"),
            role_hint=MediaRole.from_string(data.get("role_hint")),
            video_config=data.get("video_config"),
            vidu_config=data.get("vidu_config"),
            seedance_config=data.get("seedance_config"),
            reference_video=data.get("reference_video"),
            start_image_urls=list(data.get("start_image_urls", [])),
            end_image_urls=list(data.get("end_image_urls", [])),
            reference_image_urls=list(data.get("reference_image_urls", [])),
            generation_mode=data.get("generation_mode"),
            extras=dict(data.get("extras", {})),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "VideoGenerationSpec":
        return cls.from_dict(json.loads(json_str))


@dataclass
class AccountMediaOverride:
    """Per-account media overrides (replaces v1 account_images)."""
    media: List[MediaItem] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {"media": [m.to_dict() for m in self.media]}

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AccountMediaOverride":
        return cls(media=[MediaItem.from_dict(m) for m in data.get("media", [])])

    @classmethod
    def from_json(cls, json_str: str) -> "AccountMediaOverride":
        return cls.from_dict(json.loads(json_str))


@dataclass
class UnifiedAiPubInput:
    """v2 replacement for AiPubInput. version MUST be 2.
    Three repeated *GenerationSpec lists can coexist in a single plan
    (e.g. FB Post = caption text + carousel images + cover video).
    """
    version: int = 2
    text_generations: List[TextGenerationSpec] = field(default_factory=list)
    image_generations: List[ImageGenerationSpec] = field(default_factory=list)
    video_generations: List[VideoGenerationSpec] = field(default_factory=list)
    initial_media: List[MediaItem] = field(default_factory=list)
    account_media: Dict[str, AccountMediaOverride] = field(default_factory=dict)
    platform_config: Optional[Dict[str, Any]] = None  # oneof; serialized as raw dict
    generation_extras: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "version": self.version,
            "text_generations": [s.to_dict() for s in self.text_generations],
            "image_generations": [s.to_dict() for s in self.image_generations],
            "video_generations": [s.to_dict() for s in self.video_generations],
            "initial_media": [m.to_dict() for m in self.initial_media],
            "account_media": {k: v.to_dict() for k, v in self.account_media.items()},
        }
        if self.platform_config is not None:
            d["platform_config"] = self.platform_config
        if self.generation_extras:
            d["generation_extras"] = self.generation_extras
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UnifiedAiPubInput":
        return cls(
            version=data.get("version", 2),
            text_generations=[TextGenerationSpec.from_dict(s) for s in data.get("text_generations", [])],
            image_generations=[ImageGenerationSpec.from_dict(s) for s in data.get("image_generations", [])],
            video_generations=[VideoGenerationSpec.from_dict(s) for s in data.get("video_generations", [])],
            initial_media=[MediaItem.from_dict(m) for m in data.get("initial_media", [])],
            account_media={
                k: AccountMediaOverride.from_dict(v)
                for k, v in data.get("account_media", {}).items()
            },
            platform_config=data.get("platform_config"),
            generation_extras=dict(data.get("generation_extras", {})),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "UnifiedAiPubInput":
        return cls.from_dict(json.loads(json_str))


# ============================================================
# Generic Agent Task Protocol (from agent_task.proto)
# API -> DB -> Redis wakeup -> Agent Service -> Orchestrator
# ============================================================

@dataclass
class AgentDomainRef:
    """Business-domain reference preserved by agents and interpreted by orchestrators."""
    domain: str = ""
    entity_type: str = ""
    entity_id: str = ""
    slot: str = ""
    on_success: str = ""
    context_json: str = "{}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain": self.domain,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "slot": self.slot,
            "on_success": self.on_success,
            "context_json": self.context_json,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentDomainRef":
        return cls(
            domain=data.get("domain", ""),
            entity_type=data.get("entity_type", ""),
            entity_id=str(data.get("entity_id", "")),
            slot=data.get("slot", ""),
            on_success=data.get("on_success", ""),
            context_json=data.get("context_json", "{}"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "AgentDomainRef":
        return cls.from_dict(json.loads(json_str))


@dataclass
class AgentTaskEnvelope:
    """Generic durable agent task envelope."""
    task_id: str = ""
    agent_type: str = ""
    agent_version: str = ""
    tenant_id: str = ""
    correlation_id: str = ""
    idempotency_key: str = ""
    domain_ref: Optional[AgentDomainRef] = None
    payload_json: str = "{}"
    priority: int = 100
    max_attempts: int = 3
    traceparent: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "agent_type": self.agent_type,
            "agent_version": self.agent_version,
            "tenant_id": self.tenant_id,
            "correlation_id": self.correlation_id,
            "idempotency_key": self.idempotency_key,
            "domain_ref": self.domain_ref.to_dict() if self.domain_ref else None,
            "payload_json": self.payload_json,
            "priority": self.priority,
            "max_attempts": self.max_attempts,
            "traceparent": self.traceparent,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentTaskEnvelope":
        domain_ref = data.get("domain_ref")
        return cls(
            task_id=str(data.get("task_id", "")),
            agent_type=data.get("agent_type", ""),
            agent_version=data.get("agent_version", ""),
            tenant_id=data.get("tenant_id", ""),
            correlation_id=data.get("correlation_id", ""),
            idempotency_key=data.get("idempotency_key", ""),
            domain_ref=AgentDomainRef.from_dict(domain_ref) if domain_ref else None,
            payload_json=data.get("payload_json", "{}"),
            priority=int(data.get("priority", 100)),
            max_attempts=int(data.get("max_attempts", 3)),
            traceparent=data.get("traceparent", ""),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "AgentTaskEnvelope":
        return cls.from_dict(json.loads(json_str))


@dataclass
class AgentTextOutput:
    output_id: str = ""
    role: str = ""
    title: str = ""
    body: str = ""
    format: str = ""
    language: str = ""
    metadata_json: str = "{}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "output_id": self.output_id,
            "role": self.role,
            "title": self.title,
            "body": self.body,
            "format": self.format,
            "language": self.language,
            "metadata_json": self.metadata_json,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentTextOutput":
        return cls(
            output_id=str(data.get("output_id", "")),
            role=data.get("role", ""),
            title=data.get("title", ""),
            body=data.get("body", ""),
            format=data.get("format", ""),
            language=data.get("language", ""),
            metadata_json=data.get("metadata_json", "{}"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "AgentTextOutput":
        return cls.from_dict(json.loads(json_str))


@dataclass
class AgentImageOutput:
    output_id: str = ""
    role: str = ""
    uri: str = ""
    mime_type: str = ""
    width: int = 0
    height: int = 0
    prompt: str = ""
    metadata_json: str = "{}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "output_id": self.output_id,
            "role": self.role,
            "uri": self.uri,
            "mime_type": self.mime_type,
            "width": self.width,
            "height": self.height,
            "prompt": self.prompt,
            "metadata_json": self.metadata_json,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentImageOutput":
        return cls(
            output_id=str(data.get("output_id", "")),
            role=data.get("role", ""),
            uri=data.get("uri", ""),
            mime_type=data.get("mime_type", ""),
            width=int(data.get("width", 0)),
            height=int(data.get("height", 0)),
            prompt=data.get("prompt", ""),
            metadata_json=data.get("metadata_json", "{}"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "AgentImageOutput":
        return cls.from_dict(json.loads(json_str))


@dataclass
class AgentVideoOutput:
    output_id: str = ""
    role: str = ""
    uri: str = ""
    mime_type: str = ""
    width: int = 0
    height: int = 0
    duration_seconds: float = 0.0
    thumbnail_uri: str = ""
    prompt: str = ""
    metadata_json: str = "{}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "output_id": self.output_id,
            "role": self.role,
            "uri": self.uri,
            "mime_type": self.mime_type,
            "width": self.width,
            "height": self.height,
            "duration_seconds": self.duration_seconds,
            "thumbnail_uri": self.thumbnail_uri,
            "prompt": self.prompt,
            "metadata_json": self.metadata_json,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentVideoOutput":
        return cls(
            output_id=str(data.get("output_id", "")),
            role=data.get("role", ""),
            uri=data.get("uri", ""),
            mime_type=data.get("mime_type", ""),
            width=int(data.get("width", 0)),
            height=int(data.get("height", 0)),
            duration_seconds=float(data.get("duration_seconds", 0.0)),
            thumbnail_uri=data.get("thumbnail_uri", ""),
            prompt=data.get("prompt", ""),
            metadata_json=data.get("metadata_json", "{}"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "AgentVideoOutput":
        return cls.from_dict(json.loads(json_str))


@dataclass
class AgentTaskResult:
    task_id: str = ""
    status: str = ""
    texts: List[AgentTextOutput] = field(default_factory=list)
    images: List[AgentImageOutput] = field(default_factory=list)
    videos: List[AgentVideoOutput] = field(default_factory=list)
    result_json: str = "{}"
    error_json: str = "{}"
    metrics_json: str = "{}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "status": self.status,
            "texts": [t.to_dict() for t in self.texts],
            "images": [i.to_dict() for i in self.images],
            "videos": [v.to_dict() for v in self.videos],
            "result_json": self.result_json,
            "error_json": self.error_json,
            "metrics_json": self.metrics_json,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentTaskResult":
        return cls(
            task_id=str(data.get("task_id", "")),
            status=data.get("status", ""),
            texts=[AgentTextOutput.from_dict(t) for t in data.get("texts", [])],
            images=[AgentImageOutput.from_dict(i) for i in data.get("images", [])],
            videos=[AgentVideoOutput.from_dict(v) for v in data.get("videos", [])],
            result_json=data.get("result_json", "{}"),
            error_json=data.get("error_json", "{}"),
            metrics_json=data.get("metrics_json", "{}"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "AgentTaskResult":
        return cls.from_dict(json.loads(json_str))


@dataclass
class AgentTaskEvent:
    event_type: str = ""
    task_id: str = ""
    agent_type: str = ""
    status: str = ""
    domain_ref: Optional[AgentDomainRef] = None
    event_json: str = "{}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "task_id": self.task_id,
            "agent_type": self.agent_type,
            "status": self.status,
            "domain_ref": self.domain_ref.to_dict() if self.domain_ref else None,
            "event_json": self.event_json,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentTaskEvent":
        domain_ref = data.get("domain_ref")
        return cls(
            event_type=data.get("event_type", ""),
            task_id=str(data.get("task_id", "")),
            agent_type=data.get("agent_type", ""),
            status=data.get("status", ""),
            domain_ref=AgentDomainRef.from_dict(domain_ref) if domain_ref else None,
            event_json=data.get("event_json", "{}"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "AgentTaskEvent":
        return cls.from_dict(json.loads(json_str))


# ============================================================
# OpenMontage async professional video protocol
# ============================================================

class _OpenMontageEnum(str, Enum):
    @classmethod
    def from_json(cls, value: Any):
        if isinstance(value, cls):
            return value
        value_str = str(value or "unspecified").lower()
        for member in cls:
            if member.value == value_str:
                return member
        return cls.UNSPECIFIED

    @classmethod
    def from_string(cls, value: Any):
        return cls.from_json(value)

    def to_json(self) -> str:
        return self.value


class OpenMontageProtocolVersion(_OpenMontageEnum):
    UNSPECIFIED = "unspecified"
    V1 = "v1"


class OpenMontageJobStatus(_OpenMontageEnum):
    UNSPECIFIED = "unspecified"
    QUEUED = "queued"
    PREFLIGHT = "preflight"
    AWAITING_APPROVAL = "awaiting_approval"
    RUNNING = "running"
    DEGRADED = "degraded"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    IN_PROGRESS = "in_progress"
    AWAITING_HUMAN = "awaiting_human"


class OpenMontageEventType(_OpenMontageEnum):
    UNSPECIFIED = "unspecified"
    JOB_ACCEPTED = "job_accepted"
    JOB_STATUS_CHANGED = "job_status_changed"
    STAGE_STARTED = "stage_started"
    STAGE_CHECKPOINTED = "stage_checkpointed"
    APPROVAL_REQUIRED = "approval_required"
    APPROVAL_RECORDED = "approval_recorded"
    ARTIFACT_READY = "artifact_ready"
    JOB_COMPLETED = "job_completed"
    JOB_FAILED = "job_failed"
    PREFLIGHT_COMPLETED = "preflight_completed"
    PIPELINE_MANIFEST_READY = "pipeline_manifest_ready"
    TOOL_STARTED = "tool_started"
    TOOL_COMPLETED = "tool_completed"
    TOOL_FAILED = "tool_failed"
    CHECKPOINT_VALIDATED = "checkpoint_validated"
    ARTIFACT_VALIDATED = "artifact_validated"
    PROVIDER_BLOCKED = "provider_blocked"


class OpenMontageInputAssetKind(_OpenMontageEnum):
    UNSPECIFIED = "unspecified"
    REFERENCE_VIDEO = "reference_video"
    SOURCE_VIDEO = "source_video"
    START_FRAME = "start_frame"
    END_FRAME = "end_frame"
    REFERENCE_IMAGE = "reference_image"
    BRAND_ASSET = "brand_asset"
    AUDIO = "audio"
    SUBTITLE = "subtitle"
    NARRATION = "narration"
    MUSIC = "music"
    SFX = "sfx"
    DIAGRAM = "diagram"
    ANIMATION = "animation"
    CODE_SNIPPET = "code_snippet"
    FONT = "font"
    LUT = "lut"


class OpenMontageArtifactKind(_OpenMontageEnum):
    UNSPECIFIED = "unspecified"
    VIDEO = "video"
    IMAGE = "image"
    AUDIO = "audio"
    SUBTITLE = "subtitle"
    JSON = "json"
    REPORT = "report"
    DIRECTORY = "directory"
    NARRATION = "narration"
    MUSIC = "music"
    SFX = "sfx"
    DIAGRAM = "diagram"
    ANIMATION = "animation"
    CODE_SNIPPET = "code_snippet"
    FONT = "font"
    LUT = "lut"
    REVIEW = "review"
    CHECKPOINT = "checkpoint"
    MANIFEST = "manifest"


class OpenMontageErrorCode(_OpenMontageEnum):
    UNSPECIFIED = "unspecified"
    UNSUPPORTED_PROTOCOL_VERSION = "unsupported_protocol_version"
    VALIDATION_ERROR = "validation_error"
    SECRET_MATERIAL_REJECTED = "secret_material_rejected"
    IDEMPOTENCY_CONFLICT = "idempotency_conflict"
    PIPELINE_NOT_FOUND = "pipeline_not_found"
    APPROVAL_REQUIRED = "approval_required"
    APPROVAL_REJECTED = "approval_rejected"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    RENDER_FAILED = "render_failed"
    INTERNAL_ERROR = "internal_error"
    TOOL_NOT_FOUND = "tool_not_found"
    TOOL_VALIDATION_ERROR = "tool_validation_error"
    CHECKPOINT_VALIDATION_ERROR = "checkpoint_validation_error"
    ARTIFACT_VALIDATION_ERROR = "artifact_validation_error"
    RUNTIME_UNAVAILABLE = "runtime_unavailable"
    BUDGET_EXCEEDED = "budget_exceeded"
    LIVE_PROVIDER_NOT_APPROVED = "live_provider_not_approved"


def _omit_none(data: Dict[str, Any]) -> Dict[str, Any]:
    return {key: value for key, value in data.items() if value is not None}


@dataclass
class OpenMontageJobRef:
    job_id: str = ""
    request_id: str = ""
    project_id: str = ""
    correlation_id: str = ""
    idempotency_key: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "request_id": self.request_id,
            "project_id": self.project_id,
            "correlation_id": self.correlation_id,
            "idempotency_key": self.idempotency_key,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenMontageJobRef":
        return cls(
            job_id=data.get("job_id", ""),
            request_id=data.get("request_id", ""),
            project_id=data.get("project_id", ""),
            correlation_id=data.get("correlation_id", ""),
            idempotency_key=data.get("idempotency_key", ""),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "OpenMontageJobRef":
        return cls.from_dict(json.loads(json_str))


@dataclass
class OpenMontageCallbackConfig:
    callback_url: str = ""
    callback_secret_ref: str = ""
    event_types: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "callback_url": self.callback_url,
            "callback_secret_ref": self.callback_secret_ref,
            "event_types": list(self.event_types),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenMontageCallbackConfig":
        return cls(
            callback_url=data.get("callback_url", ""),
            callback_secret_ref=data.get("callback_secret_ref", ""),
            event_types=list(data.get("event_types", [])),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "OpenMontageCallbackConfig":
        return cls.from_dict(json.loads(json_str))


@dataclass
class OpenMontageInputAsset:
    kind: OpenMontageInputAssetKind = OpenMontageInputAssetKind.UNSPECIFIED
    role: str = ""
    uri: str = ""
    mime_type: Optional[str] = None
    width_px: Optional[int] = None
    height_px: Optional[int] = None
    duration_ms: Optional[int] = None
    metadata_json: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return _omit_none({
            "kind": self.kind.value,
            "role": self.role,
            "uri": self.uri,
            "mime_type": self.mime_type,
            "width_px": self.width_px,
            "height_px": self.height_px,
            "duration_ms": self.duration_ms,
            "metadata_json": self.metadata_json,
        })

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenMontageInputAsset":
        return cls(
            kind=OpenMontageInputAssetKind.from_json(data.get("kind")),
            role=data.get("role", ""),
            uri=data.get("uri", ""),
            mime_type=data.get("mime_type"),
            width_px=data.get("width_px"),
            height_px=data.get("height_px"),
            duration_ms=data.get("duration_ms"),
            metadata_json=data.get("metadata_json"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "OpenMontageInputAsset":
        return cls.from_dict(json.loads(json_str))


@dataclass
class OpenMontageSchemaField:
    path: str = ""
    required: bool = False
    json_type: str = ""
    enum_values: List[str] = field(default_factory=list)
    default_json: Optional[str] = None
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return _omit_none({
            "path": self.path,
            "required": self.required,
            "json_type": self.json_type,
            "enum_values": list(self.enum_values),
            "default_json": self.default_json,
            "description": self.description,
        })

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenMontageSchemaField":
        return cls(
            path=data.get("path", ""),
            required=bool(data.get("required", False)),
            json_type=data.get("json_type", ""),
            enum_values=list(data.get("enum_values", [])),
            default_json=data.get("default_json"),
            description=data.get("description"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "OpenMontageSchemaField":
        return cls.from_dict(json.loads(json_str))


@dataclass
class OpenMontageResourceProfile:
    cpu_cores: int = 0
    ram_mb: int = 0
    vram_mb: int = 0
    disk_mb: int = 0
    network_required: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cpu_cores": self.cpu_cores,
            "ram_mb": self.ram_mb,
            "vram_mb": self.vram_mb,
            "disk_mb": self.disk_mb,
            "network_required": self.network_required,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenMontageResourceProfile":
        return cls(
            cpu_cores=int(data.get("cpu_cores", 0)),
            ram_mb=int(data.get("ram_mb", 0)),
            vram_mb=int(data.get("vram_mb", 0)),
            disk_mb=int(data.get("disk_mb", 0)),
            network_required=bool(data.get("network_required", False)),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "OpenMontageResourceProfile":
        return cls.from_dict(json.loads(json_str))


@dataclass
class OpenMontageRetryPolicy:
    max_retries: int = 0
    backoff_seconds: float = 0.0
    retryable_errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_retries": self.max_retries,
            "backoff_seconds": self.backoff_seconds,
            "retryable_errors": list(self.retryable_errors),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenMontageRetryPolicy":
        return cls(
            max_retries=int(data.get("max_retries", 0)),
            backoff_seconds=float(data.get("backoff_seconds", 0.0)),
            retryable_errors=list(data.get("retryable_errors", [])),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "OpenMontageRetryPolicy":
        return cls.from_dict(json.loads(json_str))


@dataclass
class OpenMontageToolContract:
    name: str = ""
    version: str = ""
    tier: str = ""
    capability: str = ""
    provider: str = ""
    stability: str = ""
    status: str = ""
    execution_mode: str = ""
    determinism: str = ""
    runtime: str = ""
    module_path: str = ""
    usage_location: str = ""
    dependencies: List[str] = field(default_factory=list)
    install_instructions: str = ""
    capabilities: List[str] = field(default_factory=list)
    input_fields: List[OpenMontageSchemaField] = field(default_factory=list)
    output_fields: List[OpenMontageSchemaField] = field(default_factory=list)
    input_schema_json: Optional[str] = None
    output_schema_json: Optional[str] = None
    artifact_schema_json: Optional[str] = None
    progress_schema_json: Optional[str] = None
    supports_json: Optional[str] = None
    best_for: List[str] = field(default_factory=list)
    not_good_for: List[str] = field(default_factory=list)
    provider_matrix_json: Optional[str] = None
    resource_profile: Optional[OpenMontageResourceProfile] = None
    retry_policy: Optional[OpenMontageRetryPolicy] = None
    resume_support: str = ""
    side_effects: List[str] = field(default_factory=list)
    fallback: Optional[str] = None
    fallback_tools: List[str] = field(default_factory=list)
    agent_skills: List[str] = field(default_factory=list)
    user_visible_verification: List[str] = field(default_factory=list)
    quality_score: Optional[float] = None
    historical_success_rate: Optional[float] = None
    latency_p50_seconds: Optional[float] = None
    render_engines_json: Optional[str] = None
    render_runtimes_json: Optional[str] = None
    remotion_note: Optional[str] = None
    hyperframes_note: Optional[str] = None
    runtime_governance: Optional[str] = None
    raw_info_json: Optional[str] = None
    related_skills: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return _omit_none({
            "name": self.name,
            "version": self.version,
            "tier": self.tier,
            "capability": self.capability,
            "provider": self.provider,
            "stability": self.stability,
            "status": self.status,
            "execution_mode": self.execution_mode,
            "determinism": self.determinism,
            "runtime": self.runtime,
            "module_path": self.module_path,
            "usage_location": self.usage_location,
            "dependencies": list(self.dependencies),
            "install_instructions": self.install_instructions,
            "capabilities": list(self.capabilities),
            "input_fields": [v.to_dict() for v in self.input_fields],
            "output_fields": [v.to_dict() for v in self.output_fields],
            "input_schema_json": self.input_schema_json,
            "output_schema_json": self.output_schema_json,
            "artifact_schema_json": self.artifact_schema_json,
            "progress_schema_json": self.progress_schema_json,
            "supports_json": self.supports_json,
            "best_for": list(self.best_for),
            "not_good_for": list(self.not_good_for),
            "provider_matrix_json": self.provider_matrix_json,
            "resource_profile": self.resource_profile.to_dict() if self.resource_profile else None,
            "retry_policy": self.retry_policy.to_dict() if self.retry_policy else None,
            "resume_support": self.resume_support,
            "side_effects": list(self.side_effects),
            "fallback": self.fallback,
            "fallback_tools": list(self.fallback_tools),
            "agent_skills": list(self.agent_skills),
            "user_visible_verification": list(self.user_visible_verification),
            "quality_score": self.quality_score,
            "historical_success_rate": self.historical_success_rate,
            "latency_p50_seconds": self.latency_p50_seconds,
            "render_engines_json": self.render_engines_json,
            "render_runtimes_json": self.render_runtimes_json,
            "remotion_note": self.remotion_note,
            "hyperframes_note": self.hyperframes_note,
            "runtime_governance": self.runtime_governance,
            "raw_info_json": self.raw_info_json,
            "related_skills": list(self.related_skills),
        })

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenMontageToolContract":
        rp = data.get("resource_profile")
        retry = data.get("retry_policy")
        return cls(
            name=data.get("name", ""),
            version=data.get("version", ""),
            tier=data.get("tier", ""),
            capability=data.get("capability", ""),
            provider=data.get("provider", ""),
            stability=data.get("stability", ""),
            status=data.get("status", ""),
            execution_mode=data.get("execution_mode", ""),
            determinism=data.get("determinism", ""),
            runtime=data.get("runtime", ""),
            module_path=data.get("module_path", ""),
            usage_location=data.get("usage_location", ""),
            dependencies=list(data.get("dependencies", [])),
            install_instructions=data.get("install_instructions", ""),
            capabilities=list(data.get("capabilities", [])),
            input_fields=[OpenMontageSchemaField.from_dict(v) for v in data.get("input_fields", [])],
            output_fields=[OpenMontageSchemaField.from_dict(v) for v in data.get("output_fields", [])],
            input_schema_json=data.get("input_schema_json"),
            output_schema_json=data.get("output_schema_json"),
            artifact_schema_json=data.get("artifact_schema_json"),
            progress_schema_json=data.get("progress_schema_json"),
            supports_json=data.get("supports_json"),
            best_for=list(data.get("best_for", [])),
            not_good_for=list(data.get("not_good_for", [])),
            provider_matrix_json=data.get("provider_matrix_json"),
            resource_profile=OpenMontageResourceProfile.from_dict(rp) if rp is not None else None,
            retry_policy=OpenMontageRetryPolicy.from_dict(retry) if retry is not None else None,
            resume_support=data.get("resume_support", ""),
            side_effects=list(data.get("side_effects", [])),
            fallback=data.get("fallback"),
            fallback_tools=list(data.get("fallback_tools", [])),
            agent_skills=list(data.get("agent_skills", [])),
            user_visible_verification=list(data.get("user_visible_verification", [])),
            quality_score=data.get("quality_score"),
            historical_success_rate=data.get("historical_success_rate"),
            latency_p50_seconds=data.get("latency_p50_seconds"),
            render_engines_json=data.get("render_engines_json"),
            render_runtimes_json=data.get("render_runtimes_json"),
            remotion_note=data.get("remotion_note"),
            hyperframes_note=data.get("hyperframes_note"),
            runtime_governance=data.get("runtime_governance"),
            raw_info_json=data.get("raw_info_json"),
            related_skills=list(data.get("related_skills", [])),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "OpenMontageToolContract":
        return cls.from_dict(json.loads(json_str))


@dataclass
class OpenMontageToolInvocation:
    invocation_id: str = ""
    stage: str = ""
    tool_name: str = ""
    role: str = ""
    operation: str = ""
    provider: str = ""
    capability: str = ""
    input_json: str = "{}"
    idempotency_key: Optional[str] = None
    max_cost_usd: Optional[float] = None
    dry_run: bool = False
    expected_artifact_roles: List[str] = field(default_factory=list)
    contract_version: Optional[str] = None
    metadata_json: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return _omit_none({
            "invocation_id": self.invocation_id,
            "stage": self.stage,
            "tool_name": self.tool_name,
            "role": self.role,
            "operation": self.operation,
            "provider": self.provider,
            "capability": self.capability,
            "input_json": self.input_json,
            "idempotency_key": self.idempotency_key,
            "max_cost_usd": self.max_cost_usd,
            "dry_run": self.dry_run,
            "expected_artifact_roles": list(self.expected_artifact_roles),
            "contract_version": self.contract_version,
            "metadata_json": self.metadata_json,
        })

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenMontageToolInvocation":
        return cls(
            invocation_id=data.get("invocation_id", ""),
            stage=data.get("stage", ""),
            tool_name=data.get("tool_name", ""),
            role=data.get("role", ""),
            operation=data.get("operation", ""),
            provider=data.get("provider", ""),
            capability=data.get("capability", ""),
            input_json=data.get("input_json", "{}"),
            idempotency_key=data.get("idempotency_key"),
            max_cost_usd=data.get("max_cost_usd"),
            dry_run=bool(data.get("dry_run", False)),
            expected_artifact_roles=list(data.get("expected_artifact_roles", [])),
            contract_version=data.get("contract_version"),
            metadata_json=data.get("metadata_json"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "OpenMontageToolInvocation":
        return cls.from_dict(json.loads(json_str))


@dataclass
class OpenMontageToolResult:
    invocation_id: str = ""
    tool_name: str = ""
    success: bool = False
    data_json: Optional[str] = None
    artifact_uris: List[str] = field(default_factory=list)
    artifacts: List["OpenMontageArtifact"] = field(default_factory=list)
    error: Optional[str] = None
    cost_usd: float = 0.0
    duration_seconds: float = 0.0
    seed: Optional[int] = None
    model: Optional[str] = None
    raw_artifacts_json: Optional[str] = None
    metadata_json: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return _omit_none({
            "invocation_id": self.invocation_id,
            "tool_name": self.tool_name,
            "success": self.success,
            "data_json": self.data_json,
            "artifact_uris": list(self.artifact_uris),
            "artifacts": [v.to_dict() for v in self.artifacts],
            "error": self.error,
            "cost_usd": self.cost_usd,
            "duration_seconds": self.duration_seconds,
            "seed": self.seed,
            "model": self.model,
            "raw_artifacts_json": self.raw_artifacts_json,
            "metadata_json": self.metadata_json,
        })

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenMontageToolResult":
        return cls(
            invocation_id=data.get("invocation_id", ""),
            tool_name=data.get("tool_name", ""),
            success=bool(data.get("success", False)),
            data_json=data.get("data_json"),
            artifact_uris=list(data.get("artifact_uris", [])),
            artifacts=[OpenMontageArtifact.from_dict(v) for v in data.get("artifacts", [])],
            error=data.get("error"),
            cost_usd=float(data.get("cost_usd", 0.0)),
            duration_seconds=float(data.get("duration_seconds", 0.0)),
            seed=data.get("seed"),
            model=data.get("model"),
            raw_artifacts_json=data.get("raw_artifacts_json"),
            metadata_json=data.get("metadata_json"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "OpenMontageToolResult":
        return cls.from_dict(json.loads(json_str))


@dataclass
class OpenMontagePipelineSubStage:
    name: str = ""
    description: Optional[str] = None
    condition: Optional[str] = None
    human_approval_default: Optional[bool] = None
    tools_available: List[str] = field(default_factory=list)
    review_focus: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return _omit_none({
            "name": self.name,
            "description": self.description,
            "condition": self.condition,
            "human_approval_default": self.human_approval_default,
            "tools_available": list(self.tools_available),
            "review_focus": list(self.review_focus),
        })

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenMontagePipelineSubStage":
        return cls(
            name=data.get("name", ""),
            description=data.get("description"),
            condition=data.get("condition"),
            human_approval_default=data.get("human_approval_default"),
            tools_available=list(data.get("tools_available", [])),
            review_focus=list(data.get("review_focus", [])),
        )


@dataclass
class OpenMontagePipelineStage:
    name: str = ""
    agent: Optional[str] = None
    skill: Optional[str] = None
    required_artifacts_in: List[str] = field(default_factory=list)
    optional_artifacts_in: List[str] = field(default_factory=list)
    produces: List[str] = field(default_factory=list)
    preferred_tools: List[str] = field(default_factory=list)
    fallback_tools: List[str] = field(default_factory=list)
    required_tools: List[str] = field(default_factory=list)
    optional_tools: List[str] = field(default_factory=list)
    tools_available: List[str] = field(default_factory=list)
    review_focus: List[str] = field(default_factory=list)
    checkpoint_required: Optional[bool] = None
    human_approval_default: Optional[bool] = None
    success_criteria: List[str] = field(default_factory=list)
    sub_stages: List[OpenMontagePipelineSubStage] = field(default_factory=list)
    metadata_json: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return _omit_none({
            "name": self.name,
            "agent": self.agent,
            "skill": self.skill,
            "required_artifacts_in": list(self.required_artifacts_in),
            "optional_artifacts_in": list(self.optional_artifacts_in),
            "produces": list(self.produces),
            "preferred_tools": list(self.preferred_tools),
            "fallback_tools": list(self.fallback_tools),
            "required_tools": list(self.required_tools),
            "optional_tools": list(self.optional_tools),
            "tools_available": list(self.tools_available),
            "review_focus": list(self.review_focus),
            "checkpoint_required": self.checkpoint_required,
            "human_approval_default": self.human_approval_default,
            "success_criteria": list(self.success_criteria),
            "sub_stages": [v.to_dict() for v in self.sub_stages],
            "metadata_json": self.metadata_json,
        })

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenMontagePipelineStage":
        return cls(
            name=data.get("name", ""),
            agent=data.get("agent"),
            skill=data.get("skill"),
            required_artifacts_in=list(data.get("required_artifacts_in", [])),
            optional_artifacts_in=list(data.get("optional_artifacts_in", [])),
            produces=list(data.get("produces", [])),
            preferred_tools=list(data.get("preferred_tools", [])),
            fallback_tools=list(data.get("fallback_tools", [])),
            required_tools=list(data.get("required_tools", [])),
            optional_tools=list(data.get("optional_tools", [])),
            tools_available=list(data.get("tools_available", [])),
            review_focus=list(data.get("review_focus", [])),
            checkpoint_required=data.get("checkpoint_required"),
            human_approval_default=data.get("human_approval_default"),
            success_criteria=list(data.get("success_criteria", [])),
            sub_stages=[OpenMontagePipelineSubStage.from_dict(v) for v in data.get("sub_stages", [])],
            metadata_json=data.get("metadata_json"),
        )


@dataclass
class OpenMontagePipelineOrchestration:
    mode: Optional[str] = None
    skill: Optional[str] = None
    budget_default_usd: Optional[float] = None
    max_revisions_per_stage: Optional[int] = None
    max_send_backs: Optional[int] = None
    max_wall_time_minutes: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return _omit_none({
            "mode": self.mode,
            "skill": self.skill,
            "budget_default_usd": self.budget_default_usd,
            "max_revisions_per_stage": self.max_revisions_per_stage,
            "max_send_backs": self.max_send_backs,
            "max_wall_time_minutes": self.max_wall_time_minutes,
        })

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenMontagePipelineOrchestration":
        return cls(
            mode=data.get("mode"),
            skill=data.get("skill"),
            budget_default_usd=data.get("budget_default_usd"),
            max_revisions_per_stage=data.get("max_revisions_per_stage"),
            max_send_backs=data.get("max_send_backs"),
            max_wall_time_minutes=data.get("max_wall_time_minutes"),
        )


@dataclass
class OpenMontageExtensionPermissions:
    custom_scripts: Optional[bool] = None
    custom_playbooks: Optional[bool] = None
    custom_skills: Optional[bool] = None
    custom_tools: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        return _omit_none({
            "custom_scripts": self.custom_scripts,
            "custom_playbooks": self.custom_playbooks,
            "custom_skills": self.custom_skills,
            "custom_tools": self.custom_tools,
        })

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenMontageExtensionPermissions":
        return cls(
            custom_scripts=data.get("custom_scripts"),
            custom_playbooks=data.get("custom_playbooks"),
            custom_skills=data.get("custom_skills"),
            custom_tools=data.get("custom_tools"),
        )


@dataclass
class OpenMontageReferenceInputConfig:
    supported: bool = False
    analysis_depth: Optional[str] = None
    analysis_tools: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return _omit_none({
            "supported": self.supported,
            "analysis_depth": self.analysis_depth,
            "analysis_tools": list(self.analysis_tools),
        })

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenMontageReferenceInputConfig":
        return cls(
            supported=bool(data.get("supported", False)),
            analysis_depth=data.get("analysis_depth"),
            analysis_tools=list(data.get("analysis_tools", [])),
        )


@dataclass
class OpenMontagePipelineManifest:
    name: str = ""
    version: str = ""
    description: Optional[str] = None
    category: Optional[str] = None
    stability: Optional[str] = None
    compatible_playbooks: List[str] = field(default_factory=list)
    compatible_playbooks_json: Optional[str] = None
    required_skills: List[str] = field(default_factory=list)
    stages: List[OpenMontagePipelineStage] = field(default_factory=list)
    default_checkpoint_policy: Optional[str] = None
    reference_input: Optional[OpenMontageReferenceInputConfig] = None
    orchestration: Optional[OpenMontagePipelineOrchestration] = None
    extensions: Optional[OpenMontageExtensionPermissions] = None
    metadata_json: Optional[str] = None
    raw_manifest_json: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return _omit_none({
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "category": self.category,
            "stability": self.stability,
            "compatible_playbooks": list(self.compatible_playbooks),
            "compatible_playbooks_json": self.compatible_playbooks_json,
            "required_skills": list(self.required_skills),
            "stages": [v.to_dict() for v in self.stages],
            "default_checkpoint_policy": self.default_checkpoint_policy,
            "reference_input": self.reference_input.to_dict() if self.reference_input else None,
            "orchestration": self.orchestration.to_dict() if self.orchestration else None,
            "extensions": self.extensions.to_dict() if self.extensions else None,
            "metadata_json": self.metadata_json,
            "raw_manifest_json": self.raw_manifest_json,
        })

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenMontagePipelineManifest":
        reference_input = data.get("reference_input")
        orchestration = data.get("orchestration")
        extensions = data.get("extensions")
        return cls(
            name=data.get("name", ""),
            version=data.get("version", ""),
            description=data.get("description"),
            category=data.get("category"),
            stability=data.get("stability"),
            compatible_playbooks=list(data.get("compatible_playbooks", [])),
            compatible_playbooks_json=data.get("compatible_playbooks_json"),
            required_skills=list(data.get("required_skills", [])),
            stages=[OpenMontagePipelineStage.from_dict(v) for v in data.get("stages", [])],
            default_checkpoint_policy=data.get("default_checkpoint_policy"),
            reference_input=OpenMontageReferenceInputConfig.from_dict(reference_input) if reference_input is not None else None,
            orchestration=OpenMontagePipelineOrchestration.from_dict(orchestration) if orchestration is not None else None,
            extensions=OpenMontageExtensionPermissions.from_dict(extensions) if extensions is not None else None,
            metadata_json=data.get("metadata_json"),
            raw_manifest_json=data.get("raw_manifest_json"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "OpenMontagePipelineManifest":
        return cls.from_dict(json.loads(json_str))


@dataclass
class OpenMontageArtifactPayload:
    artifact_name: str = ""
    schema_id: Optional[str] = None
    schema_version: Optional[str] = None
    payload_json: str = "{}"
    validated: bool = False
    schema_fields: List[OpenMontageSchemaField] = field(default_factory=list)
    validation_error: Optional[str] = None
    uri: Optional[str] = None
    role: Optional[str] = None
    metadata_json: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return _omit_none({
            "artifact_name": self.artifact_name,
            "schema_id": self.schema_id,
            "schema_version": self.schema_version,
            "payload_json": self.payload_json,
            "validated": self.validated,
            "schema_fields": [v.to_dict() for v in self.schema_fields],
            "validation_error": self.validation_error,
            "uri": self.uri,
            "role": self.role,
            "metadata_json": self.metadata_json,
        })

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenMontageArtifactPayload":
        return cls(
            artifact_name=data.get("artifact_name", ""),
            schema_id=data.get("schema_id"),
            schema_version=data.get("schema_version"),
            payload_json=data.get("payload_json", "{}"),
            validated=bool(data.get("validated", False)),
            schema_fields=[OpenMontageSchemaField.from_dict(v) for v in data.get("schema_fields", [])],
            validation_error=data.get("validation_error"),
            uri=data.get("uri"),
            role=data.get("role"),
            metadata_json=data.get("metadata_json"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "OpenMontageArtifactPayload":
        return cls.from_dict(json.loads(json_str))


@dataclass
class OpenMontageCheckpoint:
    version: str = ""
    project_id: str = ""
    pipeline_type: str = ""
    stage: str = ""
    status: str = ""
    timestamp: str = ""
    style_playbook: Optional[str] = None
    checkpoint_policy: Optional[str] = None
    human_approval_required: Optional[bool] = None
    human_approved: Optional[bool] = None
    artifacts: List[OpenMontageArtifactPayload] = field(default_factory=list)
    artifacts_json: Optional[str] = None
    review_json: Optional[str] = None
    cost_snapshot_json: Optional[str] = None
    error: Optional[str] = None
    metadata_json: Optional[str] = None
    path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return _omit_none({
            "version": self.version,
            "project_id": self.project_id,
            "pipeline_type": self.pipeline_type,
            "stage": self.stage,
            "status": self.status,
            "timestamp": self.timestamp,
            "style_playbook": self.style_playbook,
            "checkpoint_policy": self.checkpoint_policy,
            "human_approval_required": self.human_approval_required,
            "human_approved": self.human_approved,
            "artifacts": [v.to_dict() for v in self.artifacts],
            "artifacts_json": self.artifacts_json,
            "review_json": self.review_json,
            "cost_snapshot_json": self.cost_snapshot_json,
            "error": self.error,
            "metadata_json": self.metadata_json,
            "path": self.path,
        })

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenMontageCheckpoint":
        return cls(
            version=data.get("version", ""),
            project_id=data.get("project_id", ""),
            pipeline_type=data.get("pipeline_type", ""),
            stage=data.get("stage", ""),
            status=data.get("status", ""),
            timestamp=data.get("timestamp", ""),
            style_playbook=data.get("style_playbook"),
            checkpoint_policy=data.get("checkpoint_policy"),
            human_approval_required=data.get("human_approval_required"),
            human_approved=data.get("human_approved"),
            artifacts=[OpenMontageArtifactPayload.from_dict(v) for v in data.get("artifacts", [])],
            artifacts_json=data.get("artifacts_json"),
            review_json=data.get("review_json"),
            cost_snapshot_json=data.get("cost_snapshot_json"),
            error=data.get("error"),
            metadata_json=data.get("metadata_json"),
            path=data.get("path"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "OpenMontageCheckpoint":
        return cls.from_dict(json.loads(json_str))


@dataclass
class OpenMontageRuntimeAvailability:
    name: str = ""
    available: bool = False
    note: Optional[str] = None
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return _omit_none({
            "name": self.name,
            "available": self.available,
            "note": self.note,
            "warnings": list(self.warnings),
        })

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenMontageRuntimeAvailability":
        return cls(
            name=data.get("name", ""),
            available=bool(data.get("available", False)),
            note=data.get("note"),
            warnings=list(data.get("warnings", [])),
        )


@dataclass
class OpenMontageCapabilitySummary:
    capability: str = ""
    configured: int = 0
    total: int = 0
    available_providers: List[str] = field(default_factory=list)
    unavailable_providers: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "capability": self.capability,
            "configured": self.configured,
            "total": self.total,
            "available_providers": list(self.available_providers),
            "unavailable_providers": list(self.unavailable_providers),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenMontageCapabilitySummary":
        return cls(
            capability=data.get("capability", ""),
            configured=int(data.get("configured", 0)),
            total=int(data.get("total", 0)),
            available_providers=list(data.get("available_providers", [])),
            unavailable_providers=list(data.get("unavailable_providers", [])),
        )


@dataclass
class OpenMontageSetupOffer:
    capability: str = ""
    tool: str = ""
    provider: str = ""
    install_instructions: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "capability": self.capability,
            "tool": self.tool,
            "provider": self.provider,
            "install_instructions": self.install_instructions,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenMontageSetupOffer":
        return cls(
            capability=data.get("capability", ""),
            tool=data.get("tool", ""),
            provider=data.get("provider", ""),
            install_instructions=data.get("install_instructions", ""),
        )


@dataclass
class OpenMontagePreflightSnapshot:
    composition_runtimes: List[OpenMontageRuntimeAvailability] = field(default_factory=list)
    capabilities: List[OpenMontageCapabilitySummary] = field(default_factory=list)
    setup_offers: List[OpenMontageSetupOffer] = field(default_factory=list)
    runtime_warnings: List[str] = field(default_factory=list)
    tools: List[OpenMontageToolContract] = field(default_factory=list)
    pipelines: List[OpenMontagePipelineManifest] = field(default_factory=list)
    captured_at: str = ""
    provider_menu_summary_json: Optional[str] = None
    provider_menu_json: Optional[str] = None
    support_envelope_json: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return _omit_none({
            "composition_runtimes": [v.to_dict() for v in self.composition_runtimes],
            "capabilities": [v.to_dict() for v in self.capabilities],
            "setup_offers": [v.to_dict() for v in self.setup_offers],
            "runtime_warnings": list(self.runtime_warnings),
            "tools": [v.to_dict() for v in self.tools],
            "pipelines": [v.to_dict() for v in self.pipelines],
            "captured_at": self.captured_at,
            "provider_menu_summary_json": self.provider_menu_summary_json,
            "provider_menu_json": self.provider_menu_json,
            "support_envelope_json": self.support_envelope_json,
        })

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenMontagePreflightSnapshot":
        return cls(
            composition_runtimes=[OpenMontageRuntimeAvailability.from_dict(v) for v in data.get("composition_runtimes", [])],
            capabilities=[OpenMontageCapabilitySummary.from_dict(v) for v in data.get("capabilities", [])],
            setup_offers=[OpenMontageSetupOffer.from_dict(v) for v in data.get("setup_offers", [])],
            runtime_warnings=list(data.get("runtime_warnings", [])),
            tools=[OpenMontageToolContract.from_dict(v) for v in data.get("tools", [])],
            pipelines=[OpenMontagePipelineManifest.from_dict(v) for v in data.get("pipelines", [])],
            captured_at=data.get("captured_at", ""),
            provider_menu_summary_json=data.get("provider_menu_summary_json"),
            provider_menu_json=data.get("provider_menu_json"),
            support_envelope_json=data.get("support_envelope_json"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "OpenMontagePreflightSnapshot":
        return cls.from_dict(json.loads(json_str))


@dataclass
class OpenMontageProfessionalVideoRequest:
    version: OpenMontageProtocolVersion = OpenMontageProtocolVersion.UNSPECIFIED
    request_id: str = ""
    idempotency_key: str = ""
    tenant_id: str = ""
    user_id: str = ""
    title: str = ""
    prompt: str = ""
    target_platform: str = ""
    language: str = ""
    duration_seconds: int = 0
    aspect_ratio: str = ""
    audience: Optional[str] = None
    objective: Optional[str] = None
    brand_json: Optional[str] = None
    pipeline: str = ""
    style_playbook: Optional[str] = None
    render_runtime: Optional[str] = None
    quality_tier: str = ""
    approval_policy: str = ""
    budget_limit_usd: float = 0.0
    provider_preferences: Dict[str, str] = field(default_factory=dict)
    assets: List[OpenMontageInputAsset] = field(default_factory=list)
    callback: Optional[OpenMontageCallbackConfig] = None
    metadata_json: Optional[str] = None
    source_script: Optional[str] = None
    source_script_uri: Optional[str] = None
    input_mode: Optional[str] = None
    output_profile: Optional[str] = None
    renderer_family: Optional[str] = None
    delivery_promise_json: Optional[str] = None
    music_plan_json: Optional[str] = None
    voice_selection_json: Optional[str] = None
    tool_invocations: List[OpenMontageToolInvocation] = field(default_factory=list)
    artifact_inputs: List[OpenMontageArtifactPayload] = field(default_factory=list)
    pipeline_manifest: Optional[OpenMontagePipelineManifest] = None
    preflight_policy: Optional[str] = None
    openmontage_request_json: Optional[str] = None
    provider_slots: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return _omit_none({
            "version": self.version.value,
            "request_id": self.request_id,
            "idempotency_key": self.idempotency_key,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "title": self.title,
            "prompt": self.prompt,
            "target_platform": self.target_platform,
            "language": self.language,
            "duration_seconds": self.duration_seconds,
            "aspect_ratio": self.aspect_ratio,
            "audience": self.audience,
            "objective": self.objective,
            "brand_json": self.brand_json,
            "pipeline": self.pipeline,
            "style_playbook": self.style_playbook,
            "render_runtime": self.render_runtime,
            "quality_tier": self.quality_tier,
            "approval_policy": self.approval_policy,
            "budget_limit_usd": self.budget_limit_usd,
            "provider_preferences": dict(self.provider_preferences),
            "assets": [asset.to_dict() for asset in self.assets],
            "callback": self.callback.to_dict() if self.callback else None,
            "metadata_json": self.metadata_json,
            "source_script": self.source_script,
            "source_script_uri": self.source_script_uri,
            "input_mode": self.input_mode,
            "output_profile": self.output_profile,
            "renderer_family": self.renderer_family,
            "delivery_promise_json": self.delivery_promise_json,
            "music_plan_json": self.music_plan_json,
            "voice_selection_json": self.voice_selection_json,
            "tool_invocations": [v.to_dict() for v in self.tool_invocations],
            "artifact_inputs": [v.to_dict() for v in self.artifact_inputs],
            "pipeline_manifest": self.pipeline_manifest.to_dict() if self.pipeline_manifest else None,
            "preflight_policy": self.preflight_policy,
            "openmontage_request_json": self.openmontage_request_json,
            "provider_slots": dict(self.provider_slots),
        })

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenMontageProfessionalVideoRequest":
        callback = data.get("callback")
        pipeline_manifest = data.get("pipeline_manifest")
        return cls(
            version=OpenMontageProtocolVersion.from_json(data.get("version")),
            request_id=data.get("request_id", ""),
            idempotency_key=data.get("idempotency_key", ""),
            tenant_id=data.get("tenant_id", ""),
            user_id=data.get("user_id", ""),
            title=data.get("title", ""),
            prompt=data.get("prompt", ""),
            target_platform=data.get("target_platform", ""),
            language=data.get("language", ""),
            duration_seconds=int(data.get("duration_seconds", 0)),
            aspect_ratio=data.get("aspect_ratio", ""),
            audience=data.get("audience"),
            objective=data.get("objective"),
            brand_json=data.get("brand_json"),
            pipeline=data.get("pipeline", ""),
            style_playbook=data.get("style_playbook"),
            render_runtime=data.get("render_runtime"),
            quality_tier=data.get("quality_tier", ""),
            approval_policy=data.get("approval_policy", ""),
            budget_limit_usd=float(data.get("budget_limit_usd", 0.0)),
            provider_preferences=dict(data.get("provider_preferences", {}) or {}),
            assets=[OpenMontageInputAsset.from_dict(v) for v in data.get("assets", [])],
            callback=OpenMontageCallbackConfig.from_dict(callback) if callback is not None else None,
            metadata_json=data.get("metadata_json"),
            source_script=data.get("source_script"),
            source_script_uri=data.get("source_script_uri"),
            input_mode=data.get("input_mode"),
            output_profile=data.get("output_profile"),
            renderer_family=data.get("renderer_family"),
            delivery_promise_json=data.get("delivery_promise_json"),
            music_plan_json=data.get("music_plan_json"),
            voice_selection_json=data.get("voice_selection_json"),
            tool_invocations=[OpenMontageToolInvocation.from_dict(v) for v in data.get("tool_invocations", [])],
            artifact_inputs=[OpenMontageArtifactPayload.from_dict(v) for v in data.get("artifact_inputs", [])],
            pipeline_manifest=OpenMontagePipelineManifest.from_dict(pipeline_manifest) if pipeline_manifest is not None else None,
            preflight_policy=data.get("preflight_policy"),
            openmontage_request_json=data.get("openmontage_request_json"),
            provider_slots=dict(data.get("provider_slots", {}) or {}),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "OpenMontageProfessionalVideoRequest":
        return cls.from_dict(json.loads(json_str))


@dataclass
class OpenMontageError:
    code: OpenMontageErrorCode = OpenMontageErrorCode.UNSPECIFIED
    message: str = ""
    retryable: bool = False
    detail_json: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return _omit_none({
            "code": self.code.value,
            "message": self.message,
            "retryable": self.retryable,
            "detail_json": self.detail_json,
        })

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenMontageError":
        return cls(
            code=OpenMontageErrorCode.from_json(data.get("code")),
            message=data.get("message", ""),
            retryable=bool(data.get("retryable", False)),
            detail_json=data.get("detail_json"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "OpenMontageError":
        return cls.from_dict(json.loads(json_str))


@dataclass
class OpenMontageSubmitResponse:
    version: OpenMontageProtocolVersion = OpenMontageProtocolVersion.UNSPECIFIED
    job: Optional[OpenMontageJobRef] = None
    status: OpenMontageJobStatus = OpenMontageJobStatus.UNSPECIFIED
    accepted_at: str = ""
    status_url: Optional[str] = None
    next_event_sequence: int = 0
    error: Optional[OpenMontageError] = None

    def to_dict(self) -> Dict[str, Any]:
        return _omit_none({
            "version": self.version.value,
            "job": self.job.to_dict() if self.job else None,
            "status": self.status.value,
            "accepted_at": self.accepted_at,
            "status_url": self.status_url,
            "next_event_sequence": self.next_event_sequence,
            "error": self.error.to_dict() if self.error else None,
        })

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenMontageSubmitResponse":
        job = data.get("job")
        error = data.get("error")
        return cls(
            version=OpenMontageProtocolVersion.from_json(data.get("version")),
            job=OpenMontageJobRef.from_dict(job) if job is not None else None,
            status=OpenMontageJobStatus.from_json(data.get("status")),
            accepted_at=data.get("accepted_at", ""),
            status_url=data.get("status_url"),
            next_event_sequence=int(data.get("next_event_sequence", 0)),
            error=OpenMontageError.from_dict(error) if error is not None else None,
        )

    @classmethod
    def from_json(cls, json_str: str) -> "OpenMontageSubmitResponse":
        return cls.from_dict(json.loads(json_str))


@dataclass
class OpenMontageArtifact:
    artifact_id: str = ""
    kind: OpenMontageArtifactKind = OpenMontageArtifactKind.UNSPECIFIED
    role: str = ""
    uri: str = ""
    mime_type: Optional[str] = None
    width_px: Optional[int] = None
    height_px: Optional[int] = None
    duration_ms: Optional[int] = None
    bytes: Optional[int] = None
    metadata_json: Optional[str] = None
    artifact_name: Optional[str] = None
    path: Optional[str] = None
    source_tool: Optional[str] = None
    scene_id: Optional[str] = None
    payload_json: Optional[str] = None
    schema_id: Optional[str] = None
    validated: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        return _omit_none({
            "artifact_id": self.artifact_id,
            "kind": self.kind.value,
            "role": self.role,
            "uri": self.uri,
            "mime_type": self.mime_type,
            "width_px": self.width_px,
            "height_px": self.height_px,
            "duration_ms": self.duration_ms,
            "bytes": self.bytes,
            "metadata_json": self.metadata_json,
            "artifact_name": self.artifact_name,
            "path": self.path,
            "source_tool": self.source_tool,
            "scene_id": self.scene_id,
            "payload_json": self.payload_json,
            "schema_id": self.schema_id,
            "validated": self.validated,
        })

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenMontageArtifact":
        return cls(
            artifact_id=data.get("artifact_id", ""),
            kind=OpenMontageArtifactKind.from_json(data.get("kind")),
            role=data.get("role", ""),
            uri=data.get("uri", ""),
            mime_type=data.get("mime_type"),
            width_px=data.get("width_px"),
            height_px=data.get("height_px"),
            duration_ms=data.get("duration_ms"),
            bytes=data.get("bytes"),
            metadata_json=data.get("metadata_json"),
            artifact_name=data.get("artifact_name"),
            path=data.get("path"),
            source_tool=data.get("source_tool"),
            scene_id=data.get("scene_id"),
            payload_json=data.get("payload_json"),
            schema_id=data.get("schema_id"),
            validated=data.get("validated"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "OpenMontageArtifact":
        return cls.from_dict(json.loads(json_str))


@dataclass
class OpenMontageStageCheckpoint:
    sequence: int = 0
    stage: str = ""
    status: OpenMontageJobStatus = OpenMontageJobStatus.UNSPECIFIED
    summary: str = ""
    artifact_refs: List[str] = field(default_factory=list)
    cost_snapshot_json: Optional[str] = None
    review_json: Optional[str] = None
    created_at: str = ""
    checkpoint: Optional[OpenMontageCheckpoint] = None
    artifact_payloads: List[OpenMontageArtifactPayload] = field(default_factory=list)
    checkpoint_json: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return _omit_none({
            "sequence": self.sequence,
            "stage": self.stage,
            "status": self.status.value,
            "summary": self.summary,
            "artifact_refs": list(self.artifact_refs),
            "cost_snapshot_json": self.cost_snapshot_json,
            "review_json": self.review_json,
            "created_at": self.created_at,
            "checkpoint": self.checkpoint.to_dict() if self.checkpoint else None,
            "artifact_payloads": [v.to_dict() for v in self.artifact_payloads],
            "checkpoint_json": self.checkpoint_json,
        })

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenMontageStageCheckpoint":
        checkpoint = data.get("checkpoint")
        return cls(
            sequence=int(data.get("sequence", 0)),
            stage=data.get("stage", ""),
            status=OpenMontageJobStatus.from_json(data.get("status")),
            summary=data.get("summary", ""),
            artifact_refs=list(data.get("artifact_refs", [])),
            cost_snapshot_json=data.get("cost_snapshot_json"),
            review_json=data.get("review_json"),
            created_at=data.get("created_at", ""),
            checkpoint=OpenMontageCheckpoint.from_dict(checkpoint) if checkpoint is not None else None,
            artifact_payloads=[OpenMontageArtifactPayload.from_dict(v) for v in data.get("artifact_payloads", [])],
            checkpoint_json=data.get("checkpoint_json"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "OpenMontageStageCheckpoint":
        return cls.from_dict(json.loads(json_str))


@dataclass
class OpenMontageDecision:
    sequence: int = 0
    category: str = ""
    summary: str = ""
    selected_option: Optional[str] = None
    options_json: Optional[str] = None
    confidence: Optional[str] = None
    created_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return _omit_none({
            "sequence": self.sequence,
            "category": self.category,
            "summary": self.summary,
            "selected_option": self.selected_option,
            "options_json": self.options_json,
            "confidence": self.confidence,
            "created_at": self.created_at,
        })

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenMontageDecision":
        return cls(
            sequence=int(data.get("sequence", 0)),
            category=data.get("category", ""),
            summary=data.get("summary", ""),
            selected_option=data.get("selected_option"),
            options_json=data.get("options_json"),
            confidence=data.get("confidence"),
            created_at=data.get("created_at", ""),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "OpenMontageDecision":
        return cls.from_dict(json.loads(json_str))


@dataclass
class OpenMontageApprovalRequest:
    approval_id: str = ""
    stage: str = ""
    decision_category: str = ""
    prompt: str = ""
    options_json: Optional[str] = None
    expires_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return _omit_none({
            "approval_id": self.approval_id,
            "stage": self.stage,
            "decision_category": self.decision_category,
            "prompt": self.prompt,
            "options_json": self.options_json,
            "expires_at": self.expires_at,
        })

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenMontageApprovalRequest":
        return cls(
            approval_id=data.get("approval_id", ""),
            stage=data.get("stage", ""),
            decision_category=data.get("decision_category", ""),
            prompt=data.get("prompt", ""),
            options_json=data.get("options_json"),
            expires_at=data.get("expires_at"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "OpenMontageApprovalRequest":
        return cls.from_dict(json.loads(json_str))


@dataclass
class OpenMontageApprovalDecision:
    job_id: str = ""
    approval_id: str = ""
    actor_id: str = ""
    decision: str = ""
    comment: Optional[str] = None
    decided_at: str = ""
    metadata_json: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return _omit_none({
            "job_id": self.job_id,
            "approval_id": self.approval_id,
            "actor_id": self.actor_id,
            "decision": self.decision,
            "comment": self.comment,
            "decided_at": self.decided_at,
            "metadata_json": self.metadata_json,
        })

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenMontageApprovalDecision":
        return cls(
            job_id=data.get("job_id", ""),
            approval_id=data.get("approval_id", ""),
            actor_id=data.get("actor_id", ""),
            decision=data.get("decision", ""),
            comment=data.get("comment"),
            decided_at=data.get("decided_at", ""),
            metadata_json=data.get("metadata_json"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "OpenMontageApprovalDecision":
        return cls.from_dict(json.loads(json_str))


@dataclass
class OpenMontageJobSnapshot:
    version: OpenMontageProtocolVersion = OpenMontageProtocolVersion.UNSPECIFIED
    job: Optional[OpenMontageJobRef] = None
    status: OpenMontageJobStatus = OpenMontageJobStatus.UNSPECIFIED
    pipeline: str = ""
    current_stage: str = ""
    progress_pct: int = 0
    checkpoints: List[OpenMontageStageCheckpoint] = field(default_factory=list)
    decisions: List[OpenMontageDecision] = field(default_factory=list)
    approvals: List[OpenMontageApprovalRequest] = field(default_factory=list)
    artifacts: List[OpenMontageArtifact] = field(default_factory=list)
    error: Optional[OpenMontageError] = None
    metrics_json: Optional[str] = None
    updated_at: str = ""
    preflight: Optional[OpenMontagePreflightSnapshot] = None
    pipeline_manifest: Optional[OpenMontagePipelineManifest] = None
    artifact_payloads: List[OpenMontageArtifactPayload] = field(default_factory=list)
    tool_results: List[OpenMontageToolResult] = field(default_factory=list)
    full_checkpoints: List[OpenMontageCheckpoint] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return _omit_none({
            "version": self.version.value,
            "job": self.job.to_dict() if self.job else None,
            "status": self.status.value,
            "pipeline": self.pipeline,
            "current_stage": self.current_stage,
            "progress_pct": self.progress_pct,
            "checkpoints": [v.to_dict() for v in self.checkpoints],
            "decisions": [v.to_dict() for v in self.decisions],
            "approvals": [v.to_dict() for v in self.approvals],
            "artifacts": [v.to_dict() for v in self.artifacts],
            "error": self.error.to_dict() if self.error else None,
            "metrics_json": self.metrics_json,
            "updated_at": self.updated_at,
            "preflight": self.preflight.to_dict() if self.preflight else None,
            "pipeline_manifest": self.pipeline_manifest.to_dict() if self.pipeline_manifest else None,
            "artifact_payloads": [v.to_dict() for v in self.artifact_payloads],
            "tool_results": [v.to_dict() for v in self.tool_results],
            "full_checkpoints": [v.to_dict() for v in self.full_checkpoints],
        })

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenMontageJobSnapshot":
        job = data.get("job")
        error = data.get("error")
        preflight = data.get("preflight")
        pipeline_manifest = data.get("pipeline_manifest")
        return cls(
            version=OpenMontageProtocolVersion.from_json(data.get("version")),
            job=OpenMontageJobRef.from_dict(job) if job is not None else None,
            status=OpenMontageJobStatus.from_json(data.get("status")),
            pipeline=data.get("pipeline", ""),
            current_stage=data.get("current_stage", ""),
            progress_pct=int(data.get("progress_pct", 0)),
            checkpoints=[OpenMontageStageCheckpoint.from_dict(v) for v in data.get("checkpoints", [])],
            decisions=[OpenMontageDecision.from_dict(v) for v in data.get("decisions", [])],
            approvals=[OpenMontageApprovalRequest.from_dict(v) for v in data.get("approvals", [])],
            artifacts=[OpenMontageArtifact.from_dict(v) for v in data.get("artifacts", [])],
            error=OpenMontageError.from_dict(error) if error is not None else None,
            metrics_json=data.get("metrics_json"),
            updated_at=data.get("updated_at", ""),
            preflight=OpenMontagePreflightSnapshot.from_dict(preflight) if preflight is not None else None,
            pipeline_manifest=OpenMontagePipelineManifest.from_dict(pipeline_manifest) if pipeline_manifest is not None else None,
            artifact_payloads=[OpenMontageArtifactPayload.from_dict(v) for v in data.get("artifact_payloads", [])],
            tool_results=[OpenMontageToolResult.from_dict(v) for v in data.get("tool_results", [])],
            full_checkpoints=[OpenMontageCheckpoint.from_dict(v) for v in data.get("full_checkpoints", [])],
        )

    @classmethod
    def from_json(cls, json_str: str) -> "OpenMontageJobSnapshot":
        return cls.from_dict(json.loads(json_str))


@dataclass
class OpenMontageJobEvent:
    version: OpenMontageProtocolVersion = OpenMontageProtocolVersion.UNSPECIFIED
    event_id: str = ""
    sequence: int = 0
    job: Optional[OpenMontageJobRef] = None
    event_type: OpenMontageEventType = OpenMontageEventType.UNSPECIFIED
    status: OpenMontageJobStatus = OpenMontageJobStatus.UNSPECIFIED
    stage: str = ""
    progress_pct: int = 0
    checkpoint: Optional[OpenMontageStageCheckpoint] = None
    approval: Optional[OpenMontageApprovalRequest] = None
    artifacts: List[OpenMontageArtifact] = field(default_factory=list)
    error: Optional[OpenMontageError] = None
    event_json: Optional[str] = None
    emitted_at: str = ""
    tool_invocation: Optional[OpenMontageToolInvocation] = None
    tool_result: Optional[OpenMontageToolResult] = None
    artifact_payloads: List[OpenMontageArtifactPayload] = field(default_factory=list)
    checkpoint_full: Optional[OpenMontageCheckpoint] = None
    preflight: Optional[OpenMontagePreflightSnapshot] = None

    def to_dict(self) -> Dict[str, Any]:
        return _omit_none({
            "version": self.version.value,
            "event_id": self.event_id,
            "sequence": self.sequence,
            "job": self.job.to_dict() if self.job else None,
            "event_type": self.event_type.value,
            "status": self.status.value,
            "stage": self.stage,
            "progress_pct": self.progress_pct,
            "checkpoint": self.checkpoint.to_dict() if self.checkpoint else None,
            "approval": self.approval.to_dict() if self.approval else None,
            "artifacts": [v.to_dict() for v in self.artifacts],
            "error": self.error.to_dict() if self.error else None,
            "event_json": self.event_json,
            "emitted_at": self.emitted_at,
            "tool_invocation": self.tool_invocation.to_dict() if self.tool_invocation else None,
            "tool_result": self.tool_result.to_dict() if self.tool_result else None,
            "artifact_payloads": [v.to_dict() for v in self.artifact_payloads],
            "checkpoint_full": self.checkpoint_full.to_dict() if self.checkpoint_full else None,
            "preflight": self.preflight.to_dict() if self.preflight else None,
        })

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenMontageJobEvent":
        job = data.get("job")
        checkpoint = data.get("checkpoint")
        approval = data.get("approval")
        error = data.get("error")
        tool_invocation = data.get("tool_invocation")
        tool_result = data.get("tool_result")
        checkpoint_full = data.get("checkpoint_full")
        preflight = data.get("preflight")
        return cls(
            version=OpenMontageProtocolVersion.from_json(data.get("version")),
            event_id=data.get("event_id", ""),
            sequence=int(data.get("sequence", 0)),
            job=OpenMontageJobRef.from_dict(job) if job is not None else None,
            event_type=OpenMontageEventType.from_json(data.get("event_type")),
            status=OpenMontageJobStatus.from_json(data.get("status")),
            stage=data.get("stage", ""),
            progress_pct=int(data.get("progress_pct", 0)),
            checkpoint=OpenMontageStageCheckpoint.from_dict(checkpoint) if checkpoint is not None else None,
            approval=OpenMontageApprovalRequest.from_dict(approval) if approval is not None else None,
            artifacts=[OpenMontageArtifact.from_dict(v) for v in data.get("artifacts", [])],
            error=OpenMontageError.from_dict(error) if error is not None else None,
            event_json=data.get("event_json"),
            emitted_at=data.get("emitted_at", ""),
            tool_invocation=OpenMontageToolInvocation.from_dict(tool_invocation) if tool_invocation is not None else None,
            tool_result=OpenMontageToolResult.from_dict(tool_result) if tool_result is not None else None,
            artifact_payloads=[OpenMontageArtifactPayload.from_dict(v) for v in data.get("artifact_payloads", [])],
            checkpoint_full=OpenMontageCheckpoint.from_dict(checkpoint_full) if checkpoint_full is not None else None,
            preflight=OpenMontagePreflightSnapshot.from_dict(preflight) if preflight is not None else None,
        )

    @classmethod
    def from_json(cls, json_str: str) -> "OpenMontageJobEvent":
        return cls.from_dict(json.loads(json_str))


@dataclass
class OpenMontageCallbackAck:
    received: bool = False
    event_id: str = ""
    next_expected_sequence: int = 0
    message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return _omit_none({
            "received": self.received,
            "event_id": self.event_id,
            "next_expected_sequence": self.next_expected_sequence,
            "message": self.message,
        })

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenMontageCallbackAck":
        return cls(
            received=bool(data.get("received", False)),
            event_id=data.get("event_id", ""),
            next_expected_sequence=int(data.get("next_expected_sequence", 0)),
            message=data.get("message"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "OpenMontageCallbackAck":
        return cls.from_dict(json.loads(json_str))

class NotificationAction(str, Enum):
    """Activity notification action (NotificationEvent.action_type).

    Consumers MUST tolerate unknown enum values for forward compatibility
    (treat as UNKNOWN). New values are appended; existing values never change.
    """
    UNKNOWN = "unknown"
    LIKE = "like"
    COMMENT = "comment"
    COMMENT_REPLY = "comment_reply"
    MENTION = "mention"
    NEW_FOLLOWER = "new_follower"
    SHARE = "share"
    SYSTEM = "system"


@dataclass
class NotificationEvent:
    """Single notification row scraped from a platform's activity surface.

    Published to NATS subject:  notif.evt.{user_id}
    Stream:                     NOTIF_EVENTS
    Dedup key (Nats-Msg-Id):    f"{platform_name}|{tab}|{actor_user_id}|{object_id}|{date_text}"
    """

    schema_version: int = 1
    notif_id: str = ""
    user_id: int = 0
    social_account_id: int = 0
    device_id: str = ""
    platform_id: int = 0
    platform_name: str = ""
    profile_name: str = ""
    action_type: str = "unknown"
    tab: str = ""
    actor_user_id: str = ""
    actor_username: str = ""
    actor_display_name: str = ""
    actor_avatar_url: str = ""
    object_type: str = ""
    object_id: str = ""
    object_url: str = ""
    preview_text: str = ""
    extra: Dict[str, Any] = field(default_factory=dict)
    occurred_at_text: str = ""
    collected_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "notif_id": self.notif_id,
            "user_id": self.user_id,
            "social_account_id": self.social_account_id,
            "device_id": self.device_id,
            "platform_id": self.platform_id,
            "platform_name": self.platform_name,
            "profile_name": self.profile_name,
            "action_type": self.action_type,
            "tab": self.tab,
            "actor_user_id": self.actor_user_id,
            "actor_username": self.actor_username,
            "actor_display_name": self.actor_display_name,
            "actor_avatar_url": self.actor_avatar_url,
            "object_type": self.object_type,
            "object_id": self.object_id,
            "object_url": self.object_url,
            "preview_text": self.preview_text,
            "extra": dict(self.extra),
            "occurred_at_text": self.occurred_at_text,
            "collected_at": self.collected_at,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NotificationEvent":
        return cls(
            schema_version=data.get("schema_version", 1),
            notif_id=data.get("notif_id", ""),
            user_id=data.get("user_id", 0),
            social_account_id=data.get("social_account_id", 0),
            device_id=data.get("device_id", ""),
            platform_id=data.get("platform_id", 0),
            platform_name=data.get("platform_name", ""),
            profile_name=data.get("profile_name", ""),
            action_type=data.get("action_type", "unknown"),
            tab=data.get("tab", ""),
            actor_user_id=data.get("actor_user_id", ""),
            actor_username=data.get("actor_username", ""),
            actor_display_name=data.get("actor_display_name", ""),
            actor_avatar_url=data.get("actor_avatar_url", ""),
            object_type=data.get("object_type", ""),
            object_id=data.get("object_id", ""),
            object_url=data.get("object_url", ""),
            preview_text=data.get("preview_text", ""),
            extra=dict(data.get("extra", {}) or {}),
            occurred_at_text=data.get("occurred_at_text", ""),
            collected_at=data.get("collected_at", ""),
        )

    @classmethod
    def from_json(cls, s: str) -> "NotificationEvent":
        return cls.from_dict(json.loads(s))


def make_notification_dedup_id(ev: "NotificationEvent") -> str:
    """Stable Nats-Msg-Id for a NotificationEvent.

    Excludes collected_at (drift across cycles). Falls back to a sha256 of
    the preview_text when every identifier field is empty so we never emit
    a constant key like 'tiktok|||' that would collapse unrelated events
    into one dedup bucket.
    """
    import hashlib as _hashlib

    actor = ev.actor_user_id or ev.actor_username or ""
    obj = ev.object_id or ev.object_url or ""
    parts = [
        ev.platform_name or "unknown",
        ev.tab or "",
        actor,
        obj,
        ev.occurred_at_text or "",
    ]
    if not (actor or obj or ev.occurred_at_text):
        digest = _hashlib.sha256((ev.preview_text or "").encode("utf-8")).hexdigest()[:16]
        parts.append(f"contenthash:{digest}")
    return "|".join(parts)
