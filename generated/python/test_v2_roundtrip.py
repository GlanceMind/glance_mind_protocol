"""TDD test for v2 Python dataclass mirror of aipub.proto v2 schema.

Run:  cd generated/python && python3 -m pytest test_v2_roundtrip.py -v

These tests assert that all v2 enums + dataclasses exist with the
correct fields. Mirrors the Rust tests in generated/rust/src/lib.rs
so wire compatibility stays bidirectional.
"""

import json
import pytest

# RED phase: these imports should fail until we add v2 types to glance_mind.py
from glance_mind import (
    # v2 enums
    MediaKind,
    MediaSource,
    MediaStatus,
    MediaRole,
    TextRole,
    TextSource,
    LinkRole,
    Visibility,
    EntityTagKind,
    PostPublishActionKind,
    PublishResultStatus,
    # v2 messages — input
    UnifiedAiPubInput,
    TextGenerationSpec,
    ImageGenerationSpec,
    VideoGenerationSpec,
    AccountMediaOverride,
    # v2 messages — content
    UnifiedPublishContent,
    MediaItem,
    TextBlock,
    LinkItem,
    EntityTag,
    UserMention,
    PublishBehavior,
    PublishSchedule,
    PostPublishAction,
    # v2 messages — result
    UnifiedPublishResult,
    MediaPublishResult,
    PostPublishActionResult,
    PublishMetrics,
)


# ============================================================
# Enum coverage
# ============================================================


class TestV2Enums:
    def test_media_kind_has_subtitle(self):
        # SUBTITLE was added in v2 for multi-language SRT/VTT tracks
        assert MediaKind.SUBTITLE.value == "subtitle"

    def test_media_role_has_carousel_item(self):
        assert MediaRole.CAROUSEL_ITEM.value == "carousel_item"

    def test_text_role_has_video_scene(self):
        assert TextRole.VIDEO_SCENE.value == "video_scene"

    def test_visibility_values(self):
        assert {v.value for v in Visibility} >= {
            "unspecified", "public", "unlisted", "friends", "private",
        }

    def test_entity_tag_kind_no_user_mention(self):
        # USER_MENTION was intentionally split out into UserMention message
        assert not any(v.value == "user_mention" for v in EntityTagKind)
        assert EntityTagKind.MUSIC.value == "music"

    def test_post_publish_action_kind_values(self):
        expected = {
            "auto_first_comment", "pin_to_profile", "crosspost",
            "share_to_story", "notify_webhook",
        }
        assert {v.value for v in PostPublishActionKind} >= expected

    def test_publish_result_status_includes_partial(self):
        # PARTIAL_SUCCESS is a v2 addition for "primary OK, post_publish action failed"
        assert PublishResultStatus.PARTIAL_SUCCESS.value == "partial_success"


# ============================================================
# ImageGenerationSpec — has all 15 fields after recent extension
# ============================================================


class TestImageGenerationSpec:
    def test_all_15_fields_present(self):
        spec = ImageGenerationSpec(
            prompts=["a cat"],
            count=3,
            model="flux-kontext-pro",
            width_px=0,
            height_px=0,
            role_hint=MediaRole.CAROUSEL_ITEM,
            reference_image_urls=[],
            aspect_ratio="16:9",
            output_format="png",
            extras={},
            seed=42,
            watermark=False,
            provider_hint="flux",
            mode="text_to_image",
            safety_tolerance=2,
        )
        d = spec.to_dict()
        assert d["aspect_ratio"] == "16:9"
        assert d["seed"] == 42
        assert d["provider_hint"] == "flux"
        assert d["safety_tolerance"] == 2

    def test_roundtrip(self):
        spec = ImageGenerationSpec(
            prompts=["a thumbnail"],
            count=1,
            model="seedream-4-5-251128",
            role_hint=MediaRole.PRIMARY,
            mode="image_edit",
            reference_image_urls=["https://x/1.jpg"],
            watermark=True,
        )
        parsed = ImageGenerationSpec.from_json(spec.to_json())
        assert parsed.model == "seedream-4-5-251128"
        assert parsed.mode == "image_edit"
        assert parsed.reference_image_urls == ["https://x/1.jpg"]
        assert parsed.watermark is True


# ============================================================
# UnifiedPublishContent — output side
# ============================================================


class TestUnifiedPublishContent:
    def test_minimal_video_post(self):
        content = UnifiedPublishContent(
            version=2,
            platform="tiktok",
            platform_id=2,
            content_type="video",
            plan_type="single_video",
            media=[
                MediaItem(
                    kind=MediaKind.VIDEO,
                    source=MediaSource.AI_GENERATED,
                    status=MediaStatus.READY,
                    role=MediaRole.PRIMARY,
                    order=0,
                    url="https://oss.example.com/video.mp4",
                    ai_task_id=123,
                )
            ],
            texts=[
                TextBlock(role=TextRole.TITLE, value="hello", source=TextSource.AI_GENERATED, order=0),
            ],
        )
        d = content.to_dict()
        assert d["version"] == 2
        assert d["media"][0]["url"] == "https://oss.example.com/video.mp4"
        assert d["texts"][0]["role"] == "title"

        parsed = UnifiedPublishContent.from_json(content.to_json())
        assert parsed.media[0].kind == MediaKind.VIDEO
        assert parsed.texts[0].role == TextRole.TITLE

    def test_carousel_with_subtitle(self):
        # v2 supports SUBTITLE media bound to a parent video via parent_media_index
        content = UnifiedPublishContent(
            version=2,
            platform="instagram",
            platform_id=4,
            content_type="reel",
            plan_type="single_video",
            media=[
                MediaItem(
                    kind=MediaKind.VIDEO,
                    source=MediaSource.AI_GENERATED,
                    status=MediaStatus.READY,
                    role=MediaRole.PRIMARY,
                    order=0,
                    url="https://oss/v.mp4",
                ),
                MediaItem(
                    kind=MediaKind.SUBTITLE,
                    source=MediaSource.USER_UPLOADED,
                    status=MediaStatus.READY,
                    role=MediaRole.UNSPECIFIED,
                    order=0,
                    url="https://oss/cap.srt",
                    language="en",
                    parent_media_index=0,
                ),
            ],
        )
        parsed = UnifiedPublishContent.from_json(content.to_json())
        assert parsed.media[1].kind == MediaKind.SUBTITLE
        assert parsed.media[1].language == "en"
        assert parsed.media[1].parent_media_index == 0


# ============================================================
# UnifiedPublishResult — replaces v1 ExecutorTaskStatusUpdate
# ============================================================


class TestUnifiedPublishResult:
    def test_succeeded_with_metrics(self):
        result = UnifiedPublishResult(
            version=2,
            task_id=999,
            status=PublishResultStatus.SUCCEEDED,
            platform_post_id="t3_xxx",
            platform_post_url="https://reddit.com/r/foo/comments/xxx",
            published_at="2026-04-19T12:00:00Z",
            initial_metrics=PublishMetrics(views=100, likes=10),
        )
        parsed = UnifiedPublishResult.from_json(result.to_json())
        assert parsed.status == PublishResultStatus.SUCCEEDED
        assert parsed.initial_metrics.views == 100

    def test_partial_success_with_post_publish_results(self):
        result = UnifiedPublishResult(
            version=2,
            task_id=1000,
            status=PublishResultStatus.PARTIAL_SUCCESS,
            platform_post_id="ig_yyy",
            post_publish_results=[
                PostPublishActionResult(
                    action_index=0,
                    kind=PostPublishActionKind.AUTO_FIRST_COMMENT,
                    succeeded=False,
                    failed_reason="rate limited",
                ),
            ],
        )
        parsed = UnifiedPublishResult.from_json(result.to_json())
        assert parsed.status == PublishResultStatus.PARTIAL_SUCCESS
        assert parsed.post_publish_results[0].succeeded is False


# ============================================================
# UnifiedAiPubInput — input side, three repeated spec lists
# ============================================================


class TestUnifiedAiPubInput:
    def test_three_specs_coexist(self):
        inp = UnifiedAiPubInput(
            version=2,
            text_generations=[
                TextGenerationSpec(
                    prompts=["caption"],
                    count=1,
                    target_roles=["CAPTION"],
                    model="gpt-4o",
                ),
            ],
            image_generations=[
                ImageGenerationSpec(
                    prompts=["thumbnail"],
                    count=1,
                    model="flux-kontext-pro",
                    role_hint=MediaRole.COVER,
                ),
            ],
            video_generations=[],
        )
        parsed = UnifiedAiPubInput.from_json(inp.to_json())
        assert len(parsed.text_generations) == 1
        assert len(parsed.image_generations) == 1
        assert len(parsed.video_generations) == 0


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
