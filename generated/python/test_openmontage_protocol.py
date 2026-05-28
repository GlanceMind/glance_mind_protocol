import json

from glance_mind import (
    OpenMontageApprovalDecision,
    OpenMontageApprovalRequest,
    OpenMontageArtifact,
    OpenMontageArtifactKind,
    OpenMontageArtifactPayload,
    OpenMontageCallbackAck,
    OpenMontageCallbackConfig,
    OpenMontageCapabilitySummary,
    OpenMontageCheckpoint,
    OpenMontageDecision,
    OpenMontageError,
    OpenMontageErrorCode,
    OpenMontageEventType,
    OpenMontageExtensionPermissions,
    OpenMontageInputAsset,
    OpenMontageInputAssetKind,
    OpenMontageJobEvent,
    OpenMontageJobRef,
    OpenMontageJobSnapshot,
    OpenMontageJobStatus,
    OpenMontagePipelineManifest,
    OpenMontagePipelineOrchestration,
    OpenMontagePipelineStage,
    OpenMontagePreflightSnapshot,
    OpenMontageProfessionalVideoRequest,
    OpenMontageProtocolVersion,
    OpenMontageResourceProfile,
    OpenMontageRuntimeAvailability,
    OpenMontageSchemaField,
    OpenMontageSetupOffer,
    OpenMontageStageCheckpoint,
    OpenMontageSubmitResponse,
    OpenMontageToolContract,
    OpenMontageToolInvocation,
    OpenMontageToolResult,
)


GLANCEMIND_TOOL_INPUT_FIELDS = {
    "zhichuang_veo_video": {
        "aspect_ratio", "dry_run", "duration", "idempotency_key", "image_path",
        "image_url", "model", "operation", "output_path", "poll_interval_seconds",
        "prompt", "reference_image_paths", "reference_image_urls",
        "request_timeout_seconds", "resolution", "size", "timeout_seconds",
    },
    "laozhang_gpt_image_2": {
        "dry_run", "idempotency_key", "model", "no_text", "output_format",
        "output_path", "prompt", "quality", "size",
    },
    "doubao_tts": {
        "disable_markdown_filter", "dry_run", "enable_timestamp", "format",
        "metadata_path", "output_path", "poll_interval_seconds", "resource_id",
        "return_usage", "sample_rate", "speech_rate", "text", "timeout_seconds",
        "voice_id",
    },
    "subtitle_gen": {
        "corrections", "format", "highlight_style", "max_chars_per_line",
        "max_words_per_cue", "output_path", "segments",
    },
    "video_compose": {
        "asset_manifest", "audio_path", "codec", "crf", "edit_decisions",
        "input_path", "narration_transcript_path", "operation", "options",
        "output_path", "overlays", "preset", "profile", "proposal_packet",
        "script_path", "script_text", "subtitle_path", "subtitle_style",
    },
    "hyperframes_compose": {
        "asset_manifest", "block_name", "edit_decisions", "fps", "operation",
        "output_path", "playbook", "profile", "quality", "skip_contrast",
        "strict", "workspace_path",
    },
    "deepseek_reviewer": {
        "artifact_text", "dry_run", "round", "stage", "system_prompt",
    },
    "visual_qa": {
        "checks", "expected", "input_path", "operation", "output_dir", "timestamps",
    },
    "audio_probe": {"input_path"},
    "frame_sampler": {
        "count", "format", "input_path", "interval_seconds", "max_frames",
        "output_dir", "quality", "scene_boundaries", "strategy", "timestamps",
    },
}

BASE_TOOL_INFO_FIELDS = {
    "name", "version", "tier", "capability", "provider", "stability", "status",
    "execution_mode", "determinism", "runtime", "module_path", "usage_location",
    "dependencies", "install_instructions", "capabilities", "input_schema",
    "output_schema", "artifact_schema", "supports", "best_for", "not_good_for",
    "provider_matrix", "resource_profile", "resume_support", "side_effects",
    "fallback", "fallback_tools", "agent_skills", "related_skills",
    "user_visible_verification", "quality_score", "historical_success_rate",
    "latency_p50_seconds",
}


def test_professional_video_request_round_trips_without_inline_secrets():
    tool_invocation = OpenMontageToolInvocation(
        invocation_id="assets-zhichuang-1",
        stage="assets",
        tool_name="zhichuang_veo_video",
        role="motion_background",
        operation="text_to_video",
        provider="zhichuang",
        capability="video_generation",
        input_json=json.dumps({
            field: "example" for field in GLANCEMIND_TOOL_INPUT_FIELDS["zhichuang_veo_video"]
        }),
        idempotency_key="gm-openmontage-123-456-video-1",
        max_cost_usd=0.5,
        expected_artifact_roles=["scene_video"],
    )
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
        source_script="30-second launch script",
        input_mode="marketing_script",
        output_profile="tiktok",
        renderer_family="product-reveal",
        delivery_promise_json=json.dumps({"promise_type": "motion_led", "motion_required": True}),
        provider_slots={"video_provider": "zhichuang_veo_video", "tts_provider": "doubao_tts"},
        tool_invocations=[tool_invocation],
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
    assert restored.input_mode == "marketing_script"
    assert restored.provider_slots["video_provider"] == "zhichuang_veo_video"
    assert json.loads(restored.tool_invocations[0].input_json)["prompt"] == "example"
    assert "callback_secret_ref" in rendered
    assert "vault://openmontage/callback" in rendered
    assert "callback_secret" not in rendered.replace("callback_secret_ref", "")
    assert "secret" not in rendered.replace("callback_secret_ref", "")


def test_openmontage_tool_contract_covers_internal_base_tool_fields_and_provider_inputs():
    contracts = []
    for tool_name, input_fields in GLANCEMIND_TOOL_INPUT_FIELDS.items():
        input_schema = {"type": "object", "properties": {field: {} for field in sorted(input_fields)}}
        contract = OpenMontageToolContract(
            name=tool_name,
            version="0.1.0",
            tier="generate",
            capability="video_generation",
            provider="openmontage",
            stability="beta",
            status="available",
            execution_mode="sync",
            determinism="stochastic",
            runtime="api",
            module_path=f"tools.example.{tool_name}",
            usage_location=f"tools/example/{tool_name}.py",
            dependencies=["env:EXAMPLE_API_KEY"],
            install_instructions="Set EXAMPLE_API_KEY.",
            capabilities=["example"],
            input_fields=[
                OpenMontageSchemaField(path=field, required=field in {"prompt", "operation", "input_path"}, json_type="string")
                for field in sorted(input_fields)
            ],
            output_fields=[OpenMontageSchemaField(path="output", required=False, json_type="string")],
            input_schema_json=json.dumps(input_schema, sort_keys=True),
            output_schema_json=json.dumps({"type": "object", "properties": {"output": {}}}),
            artifact_schema_json=json.dumps({"type": "array", "items": {"type": "string"}}),
            supports_json=json.dumps({"dry_run": True}),
            best_for=["professional video pipeline"],
            not_good_for=["offline"],
            provider_matrix_json=json.dumps({"provider": "openmontage"}),
            resource_profile=OpenMontageResourceProfile(cpu_cores=1, ram_mb=256, disk_mb=50, network_required=True),
            resume_support="none",
            side_effects=["writes artifact"],
            fallback_tools=["video_compose"],
            agent_skills=["ai-video-gen"],
            related_skills=["ai-video-gen"],
            user_visible_verification=["inspect output"],
            raw_info_json=json.dumps({field: True for field in BASE_TOOL_INFO_FIELDS}),
        )
        contracts.append(contract)

    restored = [OpenMontageToolContract.from_json(contract.to_json()) for contract in contracts]

    for contract in restored:
        expected = GLANCEMIND_TOOL_INPUT_FIELDS[contract.name]
        assert {field.path for field in contract.input_fields} == expected
        assert set(json.loads(contract.input_schema_json)["properties"]) == expected
        assert set(json.loads(contract.raw_info_json)) == BASE_TOOL_INFO_FIELDS


def test_pipeline_checkpoint_preflight_and_tool_result_round_trip_internal_shapes():
    proposal_stage = OpenMontagePipelineStage(
        name="proposal",
        skill="pipelines/glancemind-marketing-video/proposal-director",
        produces=["proposal_packet", "decision_log", "show_bible"],
        tools_available=["video_compose", "hyperframes_compose"],
        review_focus=["render_runtime_selection presents Remotion and HyperFrames"],
        checkpoint_required=True,
        human_approval_default=True,
        success_criteria=["Schema-valid proposal_packet with selected concept"],
    )
    manifest = OpenMontagePipelineManifest(
        name="glancemind-marketing-video",
        version="0.1",
        description="Native GlanceMind marketing-video workflow",
        category="generated",
        stability="beta",
        compatible_playbooks_json=json.dumps({
            "recommended": ["clean-professional", "product-growth"],
            "also_works": ["minimalist-diagram"],
            "custom_allowed": True,
        }),
        required_skills=["pipelines/glancemind-marketing-video/executive-producer"],
        stages=[proposal_stage],
        default_checkpoint_policy="guided",
        orchestration=OpenMontagePipelineOrchestration(
            mode="executive-producer",
            skill="pipelines/glancemind-marketing-video/executive-producer",
            budget_default_usd=3.0,
            max_revisions_per_stage=3,
            max_send_backs=3,
            max_wall_time_minutes=25,
        ),
        extensions=OpenMontageExtensionPermissions(
            custom_scripts=True,
            custom_playbooks=True,
            custom_skills=True,
            custom_tools=False,
        ),
    )
    artifact_payload = OpenMontageArtifactPayload(
        artifact_name="proposal_packet",
        schema_id="openmontage/artifacts/proposal_packet",
        schema_version="1.0",
        payload_json=json.dumps({
            "version": "1.0",
            "concept_options": [],
            "selected_concept": {},
            "production_plan": {"pipeline": "glancemind-marketing-video", "stages": [], "render_runtime": "remotion"},
            "cost_estimate": {"total_estimated_usd": 1.0, "line_items": [], "budget_verdict": "within_budget"},
            "approval": {"status": "pending"},
        }),
        validated=True,
        schema_fields=[
            OpenMontageSchemaField(path="production_plan.render_runtime", required=True, json_type="string", enum_values=["remotion", "hyperframes", "ffmpeg"])
        ],
    )
    checkpoint = OpenMontageCheckpoint(
        version="1.0",
        project_id="gm-plan-123-task-456",
        pipeline_type="glancemind-marketing-video",
        stage="proposal",
        status="awaiting_human",
        timestamp="2026-05-27T09:00:00Z",
        checkpoint_policy="guided",
        human_approval_required=True,
        human_approved=False,
        artifacts=[artifact_payload],
        artifacts_json=json.dumps({"proposal_packet": json.loads(artifact_payload.payload_json)}),
        cost_snapshot_json=json.dumps({"total_spent_usd": 0.0, "budget_remaining_usd": 3.0}),
    )
    preflight = OpenMontagePreflightSnapshot(
        composition_runtimes=[
            OpenMontageRuntimeAvailability(name="ffmpeg", available=True),
            OpenMontageRuntimeAvailability(name="remotion", available=True),
            OpenMontageRuntimeAvailability(name="hyperframes", available=False, warnings=["node < 22"]),
        ],
        capabilities=[
            OpenMontageCapabilitySummary(
                capability="video_generation",
                configured=1,
                total=3,
                available_providers=["zhichuang"],
                unavailable_providers=["seedance"],
            )
        ],
        setup_offers=[
            OpenMontageSetupOffer(
                capability="video_generation",
                tool="seedance_video",
                provider="seedance",
                install_instructions="Set SEEDANCE_API_KEY.",
            )
        ],
        tools=[
            OpenMontageToolContract(
                name="video_compose",
                input_fields=[OpenMontageSchemaField(path="operation", required=True, json_type="string")],
            )
        ],
        pipelines=[manifest],
        captured_at="2026-05-27T08:59:00Z",
    )
    snapshot = OpenMontageJobSnapshot(
        version=OpenMontageProtocolVersion.V1,
        job=OpenMontageJobRef(job_id="omx_job_1", request_id="req-1"),
        status=OpenMontageJobStatus.AWAITING_HUMAN,
        pipeline="glancemind-marketing-video",
        current_stage="proposal",
        progress_pct=20,
        preflight=preflight,
        pipeline_manifest=manifest,
        artifact_payloads=[artifact_payload],
        tool_results=[
            OpenMontageToolResult(
                invocation_id="compose-1",
                tool_name="video_compose",
                success=True,
                data_json=json.dumps({"output": "final.mp4"}),
                artifact_uris=["projects/example/renders/final.mp4"],
            )
        ],
        full_checkpoints=[checkpoint],
        updated_at="2026-05-27T09:01:00Z",
    )

    restored = OpenMontageJobSnapshot.from_json(snapshot.to_json())

    assert restored.status == OpenMontageJobStatus.AWAITING_HUMAN
    assert restored.pipeline_manifest.stages[0].checkpoint_required is True
    assert restored.full_checkpoints[0].status == "awaiting_human"
    assert restored.preflight.composition_runtimes[2].warnings == ["node < 22"]
    assert json.loads(restored.artifact_payloads[0].payload_json)["production_plan"]["render_runtime"] == "remotion"


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
