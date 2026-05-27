import json

from glance_mind import (
    OpenMontageApprovalDecision,
    OpenMontageApprovalRequest,
    OpenMontageArtifact,
    OpenMontageArtifactKind,
    OpenMontageCallbackAck,
    OpenMontageCallbackConfig,
    OpenMontageDecision,
    OpenMontageError,
    OpenMontageErrorCode,
    OpenMontageEventType,
    OpenMontageInputAsset,
    OpenMontageInputAssetKind,
    OpenMontageJobEvent,
    OpenMontageJobRef,
    OpenMontageJobSnapshot,
    OpenMontageJobStatus,
    OpenMontageProfessionalVideoRequest,
    OpenMontageProtocolVersion,
    OpenMontageStageCheckpoint,
    OpenMontageSubmitResponse,
)


def test_professional_video_request_round_trips_without_inline_secrets():
    request = OpenMontageProfessionalVideoRequest(
        version=OpenMontageProtocolVersion.V1,
        request_id="gm-plan-123-task-456",
        idempotency_key="gm-openmontage-123-456",
        tenant_id="tenant-1",
        user_id="42",
        title="Launch video",
        prompt="Create a professional TikTok marketing video for a new AI product.",
        target_platform="tiktok",
        language="zh-CN",
        duration_seconds=30,
        aspect_ratio="9:16",
        pipeline="glancemind-marketing-video",
        style_playbook="product-growth",
        render_runtime="remotion",
        quality_tier="professional",
        approval_policy="auto_except_paid_provider_switch",
        budget_limit_usd=3.0,
        assets=[
            OpenMontageInputAsset(
                kind=OpenMontageInputAssetKind.REFERENCE_IMAGE,
                role="brand_reference",
                uri="https://cdn.example.com/ref.png",
                mime_type="image/png",
            )
        ],
        callback=OpenMontageCallbackConfig(
            callback_url="https://api.example.com/internal/openmontage/callback",
            callback_secret_ref="vault://openmontage/callback",
            event_types=["job.event", "job.completed", "job.failed"],
        ),
        metadata_json=json.dumps({"glancemind_plan_id": 123, "glancemind_task_id": 456}),
    )

    payload = request.to_dict()
    rendered = json.dumps(payload)
    restored = OpenMontageProfessionalVideoRequest.from_json(request.to_json())

    assert payload["version"] == "v1"
    assert payload["assets"][0]["kind"] == "reference_image"
    assert payload["callback"]["callback_secret_ref"] == "vault://openmontage/callback"
    assert restored.version == OpenMontageProtocolVersion.V1
    assert restored.callback is not None
    assert restored.callback.callback_secret_ref == "vault://openmontage/callback"
    assert restored.pipeline == "glancemind-marketing-video"
    assert "callback_secret_ref" in rendered
    assert "vault://openmontage/callback" in rendered
    assert "callback_secret" not in rendered.replace("callback_secret_ref", "")
    assert "secret" not in rendered.replace("callback_secret_ref", "")


def test_job_snapshot_carries_checkpoint_decision_approval_and_final_artifact():
    snapshot = OpenMontageJobSnapshot(
        version=OpenMontageProtocolVersion.V1,
        job=OpenMontageJobRef(
            job_id="omx_job_1",
            request_id="gm-plan-123-task-456",
            project_id="gm-plan-123-task-456",
            correlation_id="corr-1",
            idempotency_key="idem-1",
        ),
        status=OpenMontageJobStatus.COMPLETED,
        pipeline="glancemind-marketing-video",
        current_stage="publish",
        progress_pct=100,
        checkpoints=[
            OpenMontageStageCheckpoint(
                sequence=4,
                stage="compose",
                status=OpenMontageJobStatus.COMPLETED,
                summary="Final render passed QA",
                artifact_refs=["artifact-final-video"],
                cost_snapshot_json=json.dumps({"spent_usd": 1.25}),
                created_at="2026-05-27T10:00:00Z",
            )
        ],
        decisions=[
            OpenMontageDecision(
                sequence=1,
                category="render_runtime_selection",
                summary="Remotion selected for caption-heavy marketing video",
                selected_option="remotion",
                options_json=json.dumps(["remotion", "hyperframes"]),
                confidence="high",
                created_at="2026-05-27T09:00:00Z",
            )
        ],
        approvals=[
            OpenMontageApprovalRequest(
                approval_id="approval-1",
                stage="proposal",
                decision_category="provider_plan",
                prompt="Approve proposal and provider budget.",
                options_json=json.dumps({"approve": True}),
                expires_at="2026-05-28T09:00:00Z",
            )
        ],
        artifacts=[
            OpenMontageArtifact(
                artifact_id="artifact-final-video",
                kind=OpenMontageArtifactKind.VIDEO,
                role="primary_video",
                uri="oss://bucket/openmontage/final.mp4",
                mime_type="video/mp4",
                width_px=1080,
                height_px=1920,
                duration_ms=30000,
            )
        ],
        updated_at="2026-05-27T10:01:00Z",
    )

    restored = OpenMontageJobSnapshot.from_json(snapshot.to_json())

    assert restored.status == OpenMontageJobStatus.COMPLETED
    assert restored.checkpoints[0].stage == "compose"
    assert restored.decisions[0].selected_option == "remotion"
    assert restored.approvals[0].approval_id == "approval-1"
    assert restored.artifacts[0].role == "primary_video"
    assert json.loads(restored.decisions[0].options_json) == ["remotion", "hyperframes"]
    assert restored.to_dict()["status"] == "completed"


def test_ordered_event_and_callback_ack_round_trip():
    event = OpenMontageJobEvent(
        version=OpenMontageProtocolVersion.V1,
        event_id="evt-7",
        sequence=7,
        job=OpenMontageJobRef(job_id="omx_job_1", request_id="req-1"),
        event_type=OpenMontageEventType.JOB_COMPLETED,
        status=OpenMontageJobStatus.COMPLETED,
        stage="publish",
        progress_pct=100,
        artifacts=[
            OpenMontageArtifact(
                artifact_id="artifact-1",
                kind=OpenMontageArtifactKind.VIDEO,
                role="primary_video",
                uri="https://oss.example.com/final.mp4",
            )
        ],
        emitted_at="2026-05-27T10:03:00Z",
    )
    ack = OpenMontageCallbackAck(
        received=True,
        event_id="evt-7",
        next_expected_sequence=8,
        message="ok",
    )

    restored_event = OpenMontageJobEvent.from_json(event.to_json())
    restored_ack = OpenMontageCallbackAck.from_json(ack.to_json())

    assert restored_event.sequence == 7
    assert restored_event.event_type == OpenMontageEventType.JOB_COMPLETED
    assert restored_event.status == OpenMontageJobStatus.COMPLETED
    assert restored_event.to_dict()["event_type"] == "job_completed"
    assert restored_ack.received is True
    assert restored_ack.next_expected_sequence == 8


def test_error_and_approval_decision_round_trip():
    response = OpenMontageSubmitResponse(
        version=OpenMontageProtocolVersion.V1,
        job=OpenMontageJobRef(job_id="omx_job_1", request_id="req-1"),
        status=OpenMontageJobStatus.FAILED,
        accepted_at="2026-05-27T10:04:00Z",
        next_event_sequence=3,
        error=OpenMontageError(
            code=OpenMontageErrorCode.IDEMPOTENCY_CONFLICT,
            message="idempotency key was reused with a different request body",
            retryable=False,
            detail_json=json.dumps({"field": "idempotency_key"}),
        ),
    )
    decision = OpenMontageApprovalDecision(
        job_id="omx_job_1",
        approval_id="approval-1",
        actor_id="user-42",
        decision="approve",
        comment="Approved professional video proposal.",
        decided_at="2026-05-27T09:30:00Z",
    )

    restored_response = OpenMontageSubmitResponse.from_json(response.to_json())
    restored_decision = OpenMontageApprovalDecision.from_json(decision.to_json())

    assert restored_response.error is not None
    assert restored_response.error.code == OpenMontageErrorCode.IDEMPOTENCY_CONFLICT
    assert restored_response.error.to_dict()["code"] == "idempotency_conflict"
    assert restored_decision.decision == "approve"
