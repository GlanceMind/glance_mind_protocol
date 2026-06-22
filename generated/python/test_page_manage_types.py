"""Python bindings for the page_manage plan type.

Pins the Python mirror of the proto page_manage additions:

  * PlanType.PAGE_MANAGE == "page_manage" (+ listed in PlanType.ALL)
  * AiTaskType.PAGE_MANAGE == "page_manage" (+ listed in AiTaskType.ALL)

page_manage is an enqueue-time ORCHESTRATION plan: the scheduler expands
one page_manage plan into existing child task types (account_grooming +
batch_text), each scheduled independently. There is intentionally NO new
content dataclass and NO ExecutorPublishTask routing — the executor never
sees a page_manage task, only the standard children.

Proto source: proto/aipub.proto PlanType (:45) + AiTaskType (:105).

Run:
    cd generated/python && python3 -m pytest test_page_manage_types.py -v
"""

from __future__ import annotations

from glance_mind import AiTaskType, PlanType


class TestPlanTypeConstant:
    def test_page_manage_constant(self):
        assert PlanType.PAGE_MANAGE == "page_manage"

    def test_page_manage_in_all(self):
        assert "page_manage" in PlanType.ALL

    def test_page_manage_is_not_reddit(self):
        assert PlanType.PAGE_MANAGE not in PlanType.REDDIT_PLAN_TYPES

    def test_existing_constants_unchanged(self):
        """Adding page_manage must not perturb the existing plan types."""
        assert PlanType.BATCH_TEXT == "batch_text"
        assert PlanType.ACCOUNT_GROOMING == "account_grooming"
        assert PlanType.REDDIT_LINK == "reddit_link"
        # The pre-existing six remain, in order, ahead of page_manage.
        assert PlanType.ALL[:6] == [
            "batch_text",
            "single_video",
            "account_grooming",
            "reddit_text",
            "reddit_image",
            "reddit_link",
        ]


class TestAiTaskTypeConstant:
    def test_page_manage_constant(self):
        assert AiTaskType.PAGE_MANAGE == "page_manage"

    def test_page_manage_in_all(self):
        assert "page_manage" in AiTaskType.ALL

    def test_existing_constants_unchanged(self):
        assert AiTaskType.CONTENT_GEN == "content_gen"
        assert AiTaskType.ACCOUNT_GROOMING == "account_grooming"
        assert AiTaskType.ALL[:5] == [
            "content_gen",
            "video_gen",
            "image_gen",
            "combined",
            "account_grooming",
        ]


class TestNoExecutorTaskRouting:
    """page_manage is plan-level only; the executor contract must NOT gain a
    page_manage task shape (children are standard account_grooming/batch_text).
    """

    def test_no_page_manage_content_dataclass(self):
        import glance_mind

        assert not hasattr(glance_mind, "PageManageTaskContent"), (
            "page_manage must not introduce an executor task content type — "
            "it expands into existing child task types at enqueue time."
        )
