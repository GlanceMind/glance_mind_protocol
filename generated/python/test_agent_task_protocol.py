import json

from glance_mind import (
    AgentDomainRef,
    AgentImageOutput,
    AgentTaskEnvelope,
    AgentTaskEvent,
    AgentTaskResult,
    AgentTextOutput,
    AgentVideoOutput,
)


def test_agent_task_envelope_round_trips_json():
    envelope = AgentTaskEnvelope(
        task_id="task-1",
        agent_type="social_seed.workflow",
        agent_version="1",
        tenant_id="tenant-1",
        correlation_id="workflow_run:7",
        idempotency_key="social_seed.workflow:7",
        domain_ref=AgentDomainRef(
            domain="social_seed",
            entity_type="workflow_run",
            entity_id="7",
            slot="primary_package",
            on_success="project_social_seed_package",
            context_json=json.dumps({"source": "test"}),
        ),
        payload_json=json.dumps({"brief": {"product_name": "GlanceMind"}}),
        priority=100,
        max_attempts=3,
        traceparent="00-a0892f3577b34da6a3ce929d0e0e4736-f03067aa0ba902b7-f03067aa0ba902b7-01",
    )

    restored = AgentTaskEnvelope.from_json(envelope.to_json())

    assert restored.task_id == "task-1"
    assert restored.domain_ref is not None
    assert restored.domain_ref.domain == "social_seed"
    assert json.loads(restored.payload_json)["brief"]["product_name"] == "GlanceMind"
    assert json.loads(restored.domain_ref.context_json)["source"] == "test"


def test_agent_task_result_round_trips_text_image_and_video_outputs():
    result = AgentTaskResult(
        task_id="task-1",
        status="succeeded",
        texts=[
            AgentTextOutput(
                output_id="text-1",
                role="xiaohongshu_post",
                title="Title",
                body="Body",
                format="markdown",
                language="zh-CN",
                metadata_json=json.dumps({"platform": "xiaohongshu"}),
            )
        ],
        images=[
            AgentImageOutput(
                output_id="image-1",
                role="cover",
                uri="mock://cover.png",
                mime_type="image/png",
                width=1024,
                height=1024,
                prompt="cover prompt",
                metadata_json=json.dumps({"variant": 1}),
            )
        ],
        videos=[
            AgentVideoOutput(
                output_id="video-1",
                role="primary_video",
                uri="mock://video.mp4",
                mime_type="video/mp4",
                width=1080,
                height=1920,
                duration_seconds=12.5,
                thumbnail_uri="mock://video.jpg",
                prompt="video prompt",
                metadata_json=json.dumps({"model": "mock"}),
            )
        ],
        result_json=json.dumps({"package": {"product_name": "GlanceMind"}}),
        error_json=json.dumps({}),
        metrics_json=json.dumps({"duration_ms": 10}),
    )

    restored = AgentTaskResult.from_json(result.to_json())

    assert restored.status == "succeeded"
    assert restored.texts[0].role == "xiaohongshu_post"
    assert restored.images[0].uri == "mock://cover.png"
    assert restored.videos[0].duration_seconds == 12.5
    assert json.loads(restored.texts[0].metadata_json)["platform"] == "xiaohongshu"
    assert json.loads(restored.result_json)["package"]["product_name"] == "GlanceMind"
    assert json.loads(restored.metrics_json)["duration_ms"] == 10


def test_agent_task_event_round_trips_json():
    event = AgentTaskEvent(
        event_type="agent.task.completed",
        task_id="task-1",
        agent_type="social_seed.workflow",
        status="succeeded",
        domain_ref=AgentDomainRef(domain="social_seed", entity_type="workflow_run", entity_id="7"),
        event_json=json.dumps({"reason": "done"}),
    )

    restored = AgentTaskEvent.from_json(event.to_json())

    assert restored.event_type == "agent.task.completed"
    assert restored.domain_ref is not None
    assert restored.domain_ref.entity_id == "7"
    assert json.loads(restored.event_json)["reason"] == "done"
