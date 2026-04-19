"""Phase 4 Round 3 Task 4 — Python bindings for Reddit plan types.

Pins the Python mirror of the proto Reddit additions so the worker
side (aipub_v2_upgrade.ensure_unified) has types to target:

  * PlanType.REDDIT_TEXT / REDDIT_IMAGE / REDDIT_LINK
  * RedditPublishContent dataclass with full field set
  * ExecutorPublishTask.get_reddit_content() + is_reddit() helpers
  * validate() works for Reddit tasks

Proto source: proto/aipub.proto:567 (RedditPublishContent) + :45-53
(PlanType enum).

Run:
    cd generated/python && python3 -m pytest test_reddit_types.py -v
"""

from __future__ import annotations

import pytest

from glance_mind import (
    ExecutorPublishTask,
    PlanType,
    RedditPublishContent,
)


class TestPlanTypeConstants:
    def test_reddit_text_constant(self):
        assert PlanType.REDDIT_TEXT == "reddit_text"

    def test_reddit_image_constant(self):
        assert PlanType.REDDIT_IMAGE == "reddit_image"

    def test_reddit_link_constant(self):
        assert PlanType.REDDIT_LINK == "reddit_link"

    def test_reddit_constants_in_all(self):
        for value in ("reddit_text", "reddit_image", "reddit_link"):
            assert value in PlanType.ALL, f"{value} must be listed in PlanType.ALL"

    def test_existing_constants_unchanged(self):
        """Pre-existing non-reddit constants must not change."""
        assert PlanType.BATCH_TEXT == "batch_text"
        assert PlanType.SINGLE_VIDEO == "single_video"
        assert PlanType.ACCOUNT_GROOMING == "account_grooming"


class TestRedditPublishContentRoundtrip:
    def test_minimal_text_post_roundtrip(self):
        rc = RedditPublishContent(
            subreddit="r/test",
            reddit_post_type="TEXT",
            title="Hello",
            body="Body text",
        )
        d = rc.to_dict()
        assert d["subreddit"] == "r/test"
        assert d["reddit_post_type"] == "TEXT"
        assert d["title"] == "Hello"
        assert d["body"] == "Body text"

        parsed = RedditPublishContent.from_dict(d)
        assert parsed == rc

    def test_image_post_with_flags(self):
        rc = RedditPublishContent(
            subreddit="r/aww",
            reddit_post_type="IMAGE",
            title="Cute",
            image_urls=["https://i.example/1.jpg", "https://i.example/2.jpg"],
            flair_text="Photo",
            is_nsfw=False,
            is_spoiler=False,
            use_markdown=False,
            is_brand_affiliate=True,
        )
        d = rc.to_dict()
        assert d["image_urls"] == ["https://i.example/1.jpg", "https://i.example/2.jpg"]
        assert d["flair_text"] == "Photo"
        assert d["is_brand_affiliate"] is True
        parsed = RedditPublishContent.from_dict(d)
        assert parsed == rc

    def test_link_post(self):
        rc = RedditPublishContent(
            subreddit="r/programming",
            reddit_post_type="LINK",
            title="Great blog",
            link_url="https://example.com/blog",
            body=None,
        )
        d = rc.to_dict()
        assert d["link_url"] == "https://example.com/blog"
        # optional body should be elided when None to stay proto-clean
        assert "body" not in d or d.get("body") is None

    def test_empty_optional_fields_omitted(self):
        """to_dict should leave Optional fields out when unset so the
        wire bytes match protobuf json_name = None convention."""
        rc = RedditPublishContent(
            subreddit="r/x",
            reddit_post_type="TEXT",
            title="t",
        )
        d = rc.to_dict()
        for optional_key in ("body", "link_url", "flair_text"):
            assert optional_key not in d or d[optional_key] is None, (
                f"Unset optional field {optional_key!r} must be omitted from dict"
            )

    def test_default_flags_are_false(self):
        rc = RedditPublishContent(
            subreddit="r/x", reddit_post_type="TEXT", title="t"
        )
        assert rc.is_nsfw is False
        assert rc.is_spoiler is False
        assert rc.use_markdown is False
        assert rc.is_brand_affiliate is False

    def test_image_urls_default_empty_list(self):
        rc = RedditPublishContent(
            subreddit="r/x", reddit_post_type="TEXT", title="t"
        )
        assert rc.image_urls == []


class TestExecutorPublishTaskRedditWiring:
    def _reddit_task_dict(self, plan_type: str = "reddit_text") -> dict:
        return {
            "task_id": 101,
            "plan_id": 10,
            "social_account_id": 42,
            "platform": "reddit",
            "platform_id": 1,
            "content_type": "post",
            "plan_type": plan_type,
            "profile_name": "reddit_profile_1",
            "content": {
                "subreddit": "r/test",
                "reddit_post_type": "TEXT",
                "title": "Hello from E2E",
                "body": "body content",
                "is_nsfw": False,
            },
            "created_at": "2026-04-20T00:00:00Z",
        }

    def test_is_reddit_returns_true_for_reddit_plan_types(self):
        for pt in ("reddit_text", "reddit_image", "reddit_link"):
            task = ExecutorPublishTask.from_dict(self._reddit_task_dict(pt))
            assert task.is_reddit() is True, f"{pt} must be reddit"
        task = ExecutorPublishTask.from_dict(
            {**self._reddit_task_dict(), "plan_type": "single_video"}
        )
        assert task.is_reddit() is False

    def test_get_reddit_content_returns_parsed_object(self):
        task = ExecutorPublishTask.from_dict(self._reddit_task_dict())
        rc = task.get_reddit_content()
        assert rc is not None
        assert rc.subreddit == "r/test"
        assert rc.reddit_post_type == "TEXT"
        assert rc.title == "Hello from E2E"
        assert rc.body == "body content"

    def test_get_reddit_content_returns_none_for_non_reddit(self):
        task = ExecutorPublishTask.from_dict(
            {**self._reddit_task_dict(), "plan_type": "single_video"}
        )
        assert task.get_reddit_content() is None

    def test_get_publish_content_returns_none_for_reddit(self):
        """AiPubTaskContent must not swallow reddit payload shape."""
        task = ExecutorPublishTask.from_dict(self._reddit_task_dict())
        assert task.get_publish_content() is None

    def test_validate_requires_title(self):
        task = ExecutorPublishTask.from_dict(self._reddit_task_dict())
        assert task.validate() is True

        bad = self._reddit_task_dict()
        bad["content"]["title"] = ""
        task_bad = ExecutorPublishTask.from_dict(bad)
        assert task_bad.validate() is False

    def test_validate_requires_subreddit(self):
        bad = self._reddit_task_dict()
        bad["content"]["subreddit"] = ""
        assert ExecutorPublishTask.from_dict(bad).validate() is False

    def test_validate_link_post_requires_link_url(self):
        link_task = self._reddit_task_dict(plan_type="reddit_link")
        link_task["content"]["reddit_post_type"] = "LINK"
        link_task["content"]["link_url"] = ""
        assert ExecutorPublishTask.from_dict(link_task).validate() is False

        link_task["content"]["link_url"] = "https://example.com"
        assert ExecutorPublishTask.from_dict(link_task).validate() is True

    def test_validate_image_post_requires_at_least_one_image(self):
        image_task = self._reddit_task_dict(plan_type="reddit_image")
        image_task["content"]["reddit_post_type"] = "IMAGE"
        image_task["content"]["image_urls"] = []
        assert ExecutorPublishTask.from_dict(image_task).validate() is False

        image_task["content"]["image_urls"] = ["https://i.example/a.jpg"]
        assert ExecutorPublishTask.from_dict(image_task).validate() is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
