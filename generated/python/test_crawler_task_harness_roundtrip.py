"""Harness contract sample for Campaign -> CrawlerTask JSON.

This test protects the protocol side of
`campaign.tiktok.keyword.mock.v1`: the Python mirror must round-trip the same
CrawlerTask shape that the scheduler emits and the harness records as queue
evidence.
"""

import json

from glance_mind import (
    CrawlerTask,
    CrawlerTaskMeta,
    CrawlerTaskSpec,
    DataType,
    Platform,
    TaskConfig,
    TaskFilters,
    TimeRange,
)


def test_canonical_tiktok_keyword_crawler_task_round_trips_json():
    task = CrawlerTask(
        meta=CrawlerTaskMeta(
            task_id=0,
            campaign_id=34001,
            source="campaign-34001",
            timestamp=1777777777.0,
        ),
        spec=CrawlerTaskSpec(
            platform=Platform.TIKTOK,
            data_type=DataType.VIDEO_COMMENTS,
        ),
        config=TaskConfig(
            keywords=["travel gear review"],
            max_count=50,
            search_offset=0,
            search_limit=10,
            filters=TaskFilters(time_range=TimeRange.LAST_180D, region="US"),
            search_options={
                "tiktok": {
                    "region": "US",
                    "sort_type": "0",
                    "publish_time": "0",
                }
            },
        ),
    )

    wire = json.loads(task.to_json())

    assert wire["meta"]["campaign_id"] == 34001
    assert wire["meta"]["source"] == "campaign-34001"
    assert wire["spec"] == {"platform": "tiktok", "data_type": "video_comments"}
    assert wire["config"]["keywords"] == ["travel gear review"]
    assert wire["config"]["max_count"] == 50
    assert wire["config"]["search_offset"] == 0
    assert wire["config"]["search_limit"] == 10
    assert wire["config"]["filters"] == {"time_range": "last_180d", "region": "US"}
    assert wire["config"]["search_options"]["tiktok"]["sort_type"] == "0"

    restored = CrawlerTask.from_json(task.to_json())

    assert restored.meta.campaign_id == 34001
    assert restored.spec.platform == Platform.TIKTOK
    assert restored.spec.data_type == DataType.VIDEO_COMMENTS
    assert restored.config.keywords == ["travel gear review"]
    assert restored.config.filters.region == "US"
    assert restored.config.search_options["tiktok"]["publish_time"] == "0"
