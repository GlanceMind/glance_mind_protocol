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
    DB CHECK: ('batch_text', 'single_video', 'account_grooming')
    """
    BATCH_TEXT = "batch_text"
    SINGLE_VIDEO = "single_video"
    ACCOUNT_GROOMING = "account_grooming"
    ALL = [BATCH_TEXT, SINGLE_VIDEO, ACCOUNT_GROOMING]


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
    
    def get_grooming_content(self) -> Optional[AccountGroomingTaskContent]:
        """Parse content as AccountGroomingTaskContent"""
        if not self.is_account_grooming():
            return None
        return AccountGroomingTaskContent.from_dict(self.content)
    
    def get_publish_content(self) -> Optional[AiPubTaskContent]:
        """Parse content as AiPubTaskContent"""
        if self.is_account_grooming():
            return None
        return AiPubTaskContent.from_dict(self.content)
    
    def validate(self) -> bool:
        if not self.task_id or not self.platform or not self.profile_name:
            return False
        if self.is_account_grooming():
            gc = self.get_grooming_content()
            return gc is not None and bool(gc.generated_name)
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
