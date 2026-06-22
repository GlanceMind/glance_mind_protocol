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

from glance_mind import (
    AccountGroomingTaskContent,
    AiTaskType,
    ContentType,
    LinkItem,
    PageManagePlanContent,
    PlanType,
    PublishSchedule,
    UnifiedPublishContent,
)


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


class TestGroomingRichFields:
    """AccountGroomingTaskContent gained page-decoration fields (cover photo,
    links, About fields, profile_url) so a page_manage profile child can fully
    decorate a managed Page. All optional ⇒ partial updates."""

    def test_rich_fields_roundtrip(self):
        g = AccountGroomingTaskContent(
            generated_bio="hi",
            cover_url="c.png",
            cover_prompt="sunset",
            profile_url="https://www.facebook.com/profile.php?id=100082341853837",
            links=[LinkItem(url="https://glancemind.com", label="Site")],
            about_fields={"work": "10y retail"},
        )
        d = g.to_dict()
        assert d["cover_url"] == "c.png"
        assert d["cover_prompt"] == "sunset"
        assert d["profile_url"].endswith("100082341853837")
        assert d["links"][0]["url"] == "https://glancemind.com"
        assert d["about_fields"]["work"] == "10y retail"

        r = AccountGroomingTaskContent.from_dict(d)
        assert r.profile_url == g.profile_url
        assert r.cover_url == "c.png"
        assert r.links[0].url == "https://glancemind.com"
        assert r.about_fields == {"work": "10y retail"}

    def test_partial_update_elides_unset_fields(self):
        # Only bio set ⇒ no cover/links/about keys leak into the wire dict.
        d = AccountGroomingTaskContent(generated_bio="x").to_dict()
        assert d == {"generated_name": "", "generated_bio": "x"}

    def test_backward_compatible_with_legacy_4_field_payload(self):
        # A pre-extension payload (name/avatar/bio only) still parses, with the
        # new fields defaulting empty.
        r = AccountGroomingTaskContent.from_dict(
            {"generated_name": "n", "avatar_url": "a.png", "generated_bio": "b"}
        )
        assert r.generated_name == "n"
        assert r.avatar_url == "a.png"
        assert r.cover_url is None
        assert r.links == []
        assert r.about_fields == {}
        assert r.profile_url is None


class TestPageManagePlanContent:
    """The legacy inline page_manage plan shape (profile + posts). Carries an
    application-level expand() helper on the Python mirror (not wire data)."""

    _PAGE = "https://www.facebook.com/profile.php?id=100082341853837"

    def _plan(self):
        return PageManagePlanContent(
            profile_url=self._PAGE,
            profile=AccountGroomingTaskContent(generated_bio="hi", cover_url="c.png"),
            posts=[
                UnifiedPublishContent(
                    version=2, platform="facebook", content_type="post",
                    plan_type="batch_text",
                    schedule=PublishSchedule(scheduled_at="2026-06-23T13:00:00+08:00"),
                )
            ],
        )

    def test_roundtrip(self):
        r = PageManagePlanContent.from_dict(self._plan().to_dict())
        assert r.profile_url == self._PAGE
        assert r.profile.cover_url == "c.png"
        assert len(r.posts) == 1

    def test_expand_profile_and_post_with_targeting_and_schedule(self):
        children = self._plan().expand()
        assert len(children) == 2

        prof = children[0]
        assert prof["plan_type"] == PlanType.ACCOUNT_GROOMING
        assert prof["content_type"] == ContentType.PROFILE
        assert prof["content"]["profile_url"].endswith("100082341853837")
        assert prof["scheduled_at"] is None

        post = children[1]
        assert post["plan_type"] == "batch_text"
        assert post["content_type"] == "post"
        assert post["scheduled_at"] == "2026-06-23T13:00:00+08:00"
        # profile_url propagated into the post's platform_extras for targeting.
        assert post["content"]["platform_extras"]["profile_url"].endswith(
            "100082341853837"
        )

    def test_expand_empty_plan_is_empty(self):
        assert PageManagePlanContent().expand() == []
