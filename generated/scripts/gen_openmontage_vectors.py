#!/usr/bin/env python3
"""T10-2 (R-PROTO-02): generate the cross-language OpenMontage golden vectors.

This script is the *single source of truth producer* for
``generated/golden/openmontage_vectors.json`` — a REVIEWED artifact that both
the Rust and Python OpenMontage codecs are checked against. The check catches
Rust<->Python wire-format divergence: each codec must deserialize the golden
JSON and re-serialize to the identical value.

Design (see task T10-2):

  * Build ONE representative instance of every OpenMontage message (32 of them)
    AND one carrier message per OpenMontage enum (6 of them), populated with
    deterministic, *non-default* values for EVERY field.
  * Serialize each via the PYTHON codec (``to_dict``) and emit a canonical,
    sorted-keys, stable JSON map ``{"<Name>": <json>, ...}``.

Why fully populate every field (incl. every ``optional`` and ``map``)?
  The Python codec drops ``None`` optionals (``_omit_none``) while the prost/serde
  Rust codec emits ``Option::None`` as JSON ``null`` (no ``skip_serializing_if``).
  If any optional were left unset, Python would omit it and Rust would emit
  ``null`` for it — a spurious "divergence" that is really just an asymmetry in
  the *fixture*, not in the codecs. By giving every field a concrete non-default
  value, both codecs serialize the same key set and the comparison tests the
  real thing: field *values* and *naming*. (Rust also has no struct-level
  ``#[serde(default)]`` for these messages, so every non-optional field must be
  present in the golden for Rust deserialization to succeed — full population
  satisfies that too.)

Determinism: every value is a fixed literal and the JSON is written with
``sort_keys=True`` + ``indent=2`` + trailing newline, so re-running produces
byte-identical output. Regenerating is a deliberate, reviewed step.

Run:  python generated/scripts/gen_openmontage_vectors.py
"""

from __future__ import annotations

import dataclasses
import json
import os
import sys

# Make ``glance_mind`` importable whether this is run from the repo root or
# from generated/scripts/ — the codec lives in generated/python/.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PY_DIR = os.path.normpath(os.path.join(_THIS_DIR, "..", "python"))
_GOLDEN_PATH = os.path.normpath(
    os.path.join(_THIS_DIR, "..", "golden", "openmontage_vectors.json")
)
if _PY_DIR not in sys.path:
    sys.path.insert(0, _PY_DIR)

import glance_mind as gm  # noqa: E402  (path set up above)


# ---------------------------------------------------------------------------
# Leaf / nested message builders. Each returns a FULLY populated instance
# (every field set to a deterministic non-default value) so that the Python
# and Rust codecs agree on the emitted key set.
# ---------------------------------------------------------------------------


def _job_ref() -> "gm.OpenMontageJobRef":
    return gm.OpenMontageJobRef(
        job_id="job-001",
        request_id="req-001",
        project_id="proj-001",
        correlation_id="corr-001",
        idempotency_key="idem-001",
    )


def _callback_config() -> "gm.OpenMontageCallbackConfig":
    return gm.OpenMontageCallbackConfig(
        callback_url="https://hooks.example/cb",
        callback_secret_ref="secret://cb",
        event_types=["job_completed", "job_failed"],
    )


def _input_asset() -> "gm.OpenMontageInputAsset":
    return gm.OpenMontageInputAsset(
        kind=gm.OpenMontageInputAssetKind.REFERENCE_VIDEO,
        role="reference",
        uri="s3://bucket/reference.mp4",
        mime_type="video/mp4",
        width_px=1920,
        height_px=1080,
        duration_ms=5000,
        metadata_json='{"fps":30}',
    )


def _schema_field() -> "gm.OpenMontageSchemaField":
    return gm.OpenMontageSchemaField(
        path="$.title",
        required=True,
        json_type="string",
        enum_values=["a", "b"],
        default_json='"untitled"',
        description="The title field.",
    )


def _resource_profile() -> "gm.OpenMontageResourceProfile":
    return gm.OpenMontageResourceProfile(
        cpu_cores=4,
        ram_mb=8192,
        vram_mb=4096,
        disk_mb=20480,
        network_required=True,
    )


def _retry_policy() -> "gm.OpenMontageRetryPolicy":
    return gm.OpenMontageRetryPolicy(
        max_retries=3,
        backoff_seconds=2.5,
        retryable_errors=["provider_unavailable", "render_failed"],
    )


def _tool_contract() -> "gm.OpenMontageToolContract":
    return gm.OpenMontageToolContract(
        name="video_compose",
        version="1.2.3",
        tier="core",
        capability="video_post",
        provider="ffmpeg",
        stability="production",
        status="available",
        execution_mode="local",
        determinism="deterministic",
        runtime="LOCAL",
        module_path="tools.video.video_compose",
        usage_location="tools/video/video_compose.py",
        dependencies=["ffmpeg"],
        install_instructions="brew install ffmpeg",
        capabilities=["concat", "trim"],
        input_fields=[_schema_field()],
        output_fields=[_schema_field()],
        input_schema_json='{"type":"object"}',
        output_schema_json='{"type":"object"}',
        artifact_schema_json='{"type":"array"}',
        progress_schema_json='{"type":"number"}',
        supports_json='{"subtitle_burn":true}',
        best_for=["cuts", "concat"],
        not_good_for=["3d"],
        provider_matrix_json='{"ffmpeg":"ok"}',
        resource_profile=_resource_profile(),
        retry_policy=_retry_policy(),
        resume_support="checkpoint",
        side_effects=["writes_disk"],
        fallback="video_stitch",
        fallback_tools=["video_stitch", "video_trimmer"],
        agent_skills=["ffmpeg"],
        user_visible_verification=["play the output"],
        quality_score=0.95,
        historical_success_rate=0.99,
        latency_p50_seconds=12.5,
        render_engines_json='["ffmpeg","remotion"]',
        render_runtimes_json='["ffmpeg"]',
        remotion_note="needs node",
        hyperframes_note="needs node22",
        runtime_governance="locked_at_proposal",
        raw_info_json='{"k":"v"}',
        related_skills=["remotion"],
    )


def _tool_invocation() -> "gm.OpenMontageToolInvocation":
    return gm.OpenMontageToolInvocation(
        invocation_id="inv-001",
        stage="compose",
        tool_name="video_compose",
        role="primary",
        operation="render",
        provider="ffmpeg",
        capability="video_post",
        input_json='{"cuts":[]}',
        idempotency_key="inv-idem-001",
        max_cost_usd=1.5,
        dry_run=True,
        expected_artifact_roles=["final"],
        contract_version="1.2.3",
        metadata_json='{"attempt":1}',
    )


def _artifact() -> "gm.OpenMontageArtifact":
    return gm.OpenMontageArtifact(
        artifact_id="art-001",
        kind=gm.OpenMontageArtifactKind.VIDEO,
        role="final",
        uri="s3://bucket/final.mp4",
        mime_type="video/mp4",
        width_px=1920,
        height_px=1080,
        duration_ms=60000,
        bytes=1048576,
        metadata_json='{"codec":"h264"}',
        artifact_name="final.mp4",
        path="renders/final.mp4",
        source_tool="video_compose",
        scene_id="scene-1",
        payload_json='{"ok":true}',
        schema_id="render_report",
        validated=True,
    )


def _tool_result() -> "gm.OpenMontageToolResult":
    return gm.OpenMontageToolResult(
        invocation_id="inv-001",
        tool_name="video_compose",
        success=True,
        data_json='{"output":"final.mp4"}',
        artifact_uris=["s3://bucket/final.mp4"],
        artifacts=[_artifact()],
        error="none",
        cost_usd=1.25,
        duration_seconds=12.5,
        seed=42,
        model="ffmpeg-6",
        raw_artifacts_json='[{"uri":"s3://bucket/final.mp4"}]',
        metadata_json='{"attempt":1}',
    )


def _pipeline_sub_stage() -> "gm.OpenMontagePipelineSubStage":
    return gm.OpenMontagePipelineSubStage(
        name="sub-1",
        description="A sub stage.",
        condition="always",
        human_approval_default=True,
        tools_available=["video_compose"],
        review_focus=["timing"],
    )


def _pipeline_stage() -> "gm.OpenMontagePipelineStage":
    return gm.OpenMontagePipelineStage(
        name="compose",
        agent="composer",
        skill="skills/pipelines/x/compose-director.md",
        required_artifacts_in=["edit_decisions"],
        optional_artifacts_in=["music"],
        produces=["render_report"],
        preferred_tools=["video_compose"],
        fallback_tools=["video_stitch"],
        required_tools=["video_compose"],
        optional_tools=["audio_mixer"],
        tools_available=["video_compose", "audio_mixer"],
        review_focus=["encoding"],
        checkpoint_required=True,
        human_approval_default=False,
        success_criteria=["final.mp4 exists"],
        sub_stages=[_pipeline_sub_stage()],
        metadata_json='{"order":6}',
    )


def _pipeline_orchestration() -> "gm.OpenMontagePipelineOrchestration":
    return gm.OpenMontagePipelineOrchestration(
        mode="autonomous",
        skill="skills/meta/orchestrator.md",
        budget_default_usd=10.0,
        max_revisions_per_stage=2,
        max_send_backs=1,
        max_wall_time_minutes=30,
    )


def _extension_permissions() -> "gm.OpenMontageExtensionPermissions":
    return gm.OpenMontageExtensionPermissions(
        custom_scripts=True,
        custom_playbooks=True,
        custom_skills=False,
        custom_tools=False,
    )


def _reference_input_config() -> "gm.OpenMontageReferenceInputConfig":
    return gm.OpenMontageReferenceInputConfig(
        supported=True,
        analysis_depth="deep",
        analysis_tools=["video_analyzer", "transcriber"],
    )


def _pipeline_manifest() -> "gm.OpenMontagePipelineManifest":
    return gm.OpenMontagePipelineManifest(
        name="animated-explainer",
        version="1.0.0",
        description="Topic to fully generated explainer.",
        category="explainer",
        stability="production",
        compatible_playbooks=["flat-motion-graphics"],
        compatible_playbooks_json='["flat-motion-graphics"]',
        required_skills=["reviewer"],
        stages=[_pipeline_stage()],
        default_checkpoint_policy="creative_stages",
        reference_input=_reference_input_config(),
        orchestration=_pipeline_orchestration(),
        extensions=_extension_permissions(),
        metadata_json='{"v":1}',
        raw_manifest_json='{"name":"animated-explainer"}',
    )


def _artifact_payload() -> "gm.OpenMontageArtifactPayload":
    return gm.OpenMontageArtifactPayload(
        artifact_name="script",
        schema_id="script.schema.json",
        schema_version="1.0.0",
        payload_json='{"sections":[]}',
        validated=True,
        schema_fields=[_schema_field()],
        validation_error="none",
        uri="artifacts/script.json",
        role="script",
        metadata_json='{"stage":"script"}',
    )


def _checkpoint() -> "gm.OpenMontageCheckpoint":
    return gm.OpenMontageCheckpoint(
        version="1.0.0",
        project_id="proj-001",
        pipeline_type="animated-explainer",
        stage="script",
        status="completed",
        timestamp="2026-01-01T00:00:00Z",
        style_playbook="flat-motion-graphics",
        checkpoint_policy="creative_stages",
        human_approval_required=True,
        human_approved=True,
        artifacts=[_artifact_payload()],
        artifacts_json='[{"artifact_name":"script"}]',
        review_json='{"findings":[]}',
        cost_snapshot_json='{"usd":1.0}',
        error="none",
        metadata_json='{"k":"v"}',
        path="pipelines/proj-001/checkpoint_script.json",
    )


def _runtime_availability() -> "gm.OpenMontageRuntimeAvailability":
    return gm.OpenMontageRuntimeAvailability(
        name="remotion",
        available=True,
        note="node present",
        warnings=["slow first render"],
    )


def _capability_summary() -> "gm.OpenMontageCapabilitySummary":
    return gm.OpenMontageCapabilitySummary(
        capability="tts",
        configured=1,
        total=3,
        available_providers=["elevenlabs"],
        unavailable_providers=["openai", "piper"],
    )


def _setup_offer() -> "gm.OpenMontageSetupOffer":
    return gm.OpenMontageSetupOffer(
        capability="video_generation",
        tool="kling_video",
        provider="kling",
        install_instructions="set FAL_KEY",
    )


def _preflight_snapshot() -> "gm.OpenMontagePreflightSnapshot":
    return gm.OpenMontagePreflightSnapshot(
        composition_runtimes=[_runtime_availability()],
        capabilities=[_capability_summary()],
        setup_offers=[_setup_offer()],
        runtime_warnings=["hyperframes: npm package not resolvable"],
        tools=[_tool_contract()],
        pipelines=[_pipeline_manifest()],
        captured_at="2026-01-01T00:00:00Z",
        provider_menu_summary_json='{"composition_runtimes":{}}',
        provider_menu_json='{"capabilities":[]}',
        support_envelope_json='{"tools":[]}',
    )


def _error() -> "gm.OpenMontageError":
    return gm.OpenMontageError(
        code=gm.OpenMontageErrorCode.VALIDATION_ERROR,
        message="validation failed",
        retryable=False,
        detail_json='{"field":"title"}',
    )


def _stage_checkpoint() -> "gm.OpenMontageStageCheckpoint":
    return gm.OpenMontageStageCheckpoint(
        sequence=3,
        stage="script",
        status=gm.OpenMontageJobStatus.COMPLETED,
        summary="script complete",
        artifact_refs=["script"],
        cost_snapshot_json='{"usd":1.0}',
        review_json='{"findings":[]}',
        created_at="2026-01-01T00:00:00Z",
        checkpoint=_checkpoint(),
        artifact_payloads=[_artifact_payload()],
        checkpoint_json='{"stage":"script"}',
    )


def _decision() -> "gm.OpenMontageDecision":
    return gm.OpenMontageDecision(
        sequence=2,
        category="render_runtime_selection",
        summary="chose remotion",
        selected_option="remotion",
        options_json='["remotion","ffmpeg"]',
        confidence="high",
        created_at="2026-01-01T00:00:00Z",
    )


def _approval_request() -> "gm.OpenMontageApprovalRequest":
    return gm.OpenMontageApprovalRequest(
        approval_id="appr-001",
        stage="scene_plan",
        decision_category="scene_plan_approval",
        prompt="approve the scene plan?",
        options_json='["approve","revise"]',
        expires_at="2026-01-02T00:00:00Z",
    )


# ---------------------------------------------------------------------------
# Top-level message builders.
# ---------------------------------------------------------------------------


def _submit_response() -> "gm.OpenMontageSubmitResponse":
    return gm.OpenMontageSubmitResponse(
        version=gm.OpenMontageProtocolVersion.V1,
        job=_job_ref(),
        status=gm.OpenMontageJobStatus.QUEUED,
        accepted_at="2026-01-01T00:00:00Z",
        status_url="https://api.example/jobs/job-001",
        next_event_sequence=1,
        error=_error(),
    )


def _approval_decision() -> "gm.OpenMontageApprovalDecision":
    return gm.OpenMontageApprovalDecision(
        job_id="job-001",
        approval_id="appr-001",
        actor_id="user-001",
        decision="approve",
        comment="looks good",
        decided_at="2026-01-01T00:05:00Z",
        metadata_json='{"channel":"ui"}',
    )


def _professional_video_request() -> "gm.OpenMontageProfessionalVideoRequest":
    return gm.OpenMontageProfessionalVideoRequest(
        version=gm.OpenMontageProtocolVersion.V1,
        request_id="req-001",
        idempotency_key="idem-001",
        tenant_id="tenant-001",
        user_id="user-001",
        title="Black Holes",
        prompt="Explain black holes in 60s.",
        target_platform="youtube_shorts",
        language="en",
        duration_seconds=60,
        aspect_ratio="9:16",
        audience="general",
        objective="educate",
        brand_json='{"primary":"#000000"}',
        pipeline="animated-explainer",
        style_playbook="flat-motion-graphics",
        render_runtime="remotion",
        quality_tier="premium",
        approval_policy="creative_stages",
        budget_limit_usd=25.0,
        provider_preferences={"image_generation": "flux", "tts": "elevenlabs"},
        assets=[_input_asset()],
        callback=_callback_config(),
        metadata_json='{"source":"api"}',
        source_script="Once upon a time...",
        source_script_uri="s3://bucket/script.txt",
        input_mode="prompt",
        output_profile="1080p",
        renderer_family="remotion",
        delivery_promise_json='{"motion":true}',
        music_plan_json='{"source":"library"}',
        voice_selection_json='{"voice":"rachel"}',
        tool_invocations=[_tool_invocation()],
        artifact_inputs=[_artifact_payload()],
        pipeline_manifest=_pipeline_manifest(),
        preflight_policy="required",
        openmontage_request_json='{"raw":true}',
        provider_slots={"video_generation": "kling"},
    )


def _job_snapshot() -> "gm.OpenMontageJobSnapshot":
    return gm.OpenMontageJobSnapshot(
        version=gm.OpenMontageProtocolVersion.V1,
        job=_job_ref(),
        status=gm.OpenMontageJobStatus.RUNNING,
        pipeline="animated-explainer",
        current_stage="assets",
        progress_pct=42,
        checkpoints=[_stage_checkpoint()],
        decisions=[_decision()],
        approvals=[_approval_request()],
        artifacts=[_artifact()],
        error=_error(),
        metrics_json='{"frames":1800}',
        updated_at="2026-01-01T00:10:00Z",
        preflight=_preflight_snapshot(),
        pipeline_manifest=_pipeline_manifest(),
        artifact_payloads=[_artifact_payload()],
        tool_results=[_tool_result()],
        full_checkpoints=[_checkpoint()],
    )


def _job_event() -> "gm.OpenMontageJobEvent":
    return gm.OpenMontageJobEvent(
        version=gm.OpenMontageProtocolVersion.V1,
        event_id="evt-001",
        sequence=5,
        job=_job_ref(),
        event_type=gm.OpenMontageEventType.ARTIFACT_READY,
        status=gm.OpenMontageJobStatus.RUNNING,
        stage="assets",
        progress_pct=42,
        checkpoint=_stage_checkpoint(),
        approval=_approval_request(),
        artifacts=[_artifact()],
        error=_error(),
        event_json='{"raw":true}',
        emitted_at="2026-01-01T00:10:00Z",
        tool_invocation=_tool_invocation(),
        tool_result=_tool_result(),
        artifact_payloads=[_artifact_payload()],
        checkpoint_full=_checkpoint(),
        preflight=_preflight_snapshot(),
    )


def _callback_ack() -> "gm.OpenMontageCallbackAck":
    return gm.OpenMontageCallbackAck(
        received=True,
        event_id="evt-001",
        next_expected_sequence=6,
        message="ok",
    )


# ---------------------------------------------------------------------------
# Vector assembly.
# ---------------------------------------------------------------------------

# Every OpenMontage message, fully populated. Keys are the Rust/Python type
# names (sans the ``OpenMontage`` prefix is NOT stripped — we keep the full
# name so both codecs can map the key to a concrete type unambiguously).
_MESSAGE_BUILDERS = {
    "OpenMontageJobRef": _job_ref,
    "OpenMontageCallbackConfig": _callback_config,
    "OpenMontageInputAsset": _input_asset,
    "OpenMontageSchemaField": _schema_field,
    "OpenMontageResourceProfile": _resource_profile,
    "OpenMontageRetryPolicy": _retry_policy,
    "OpenMontageToolContract": _tool_contract,
    "OpenMontageToolInvocation": _tool_invocation,
    "OpenMontageToolResult": _tool_result,
    "OpenMontagePipelineSubStage": _pipeline_sub_stage,
    "OpenMontagePipelineStage": _pipeline_stage,
    "OpenMontagePipelineOrchestration": _pipeline_orchestration,
    "OpenMontageExtensionPermissions": _extension_permissions,
    "OpenMontageReferenceInputConfig": _reference_input_config,
    "OpenMontagePipelineManifest": _pipeline_manifest,
    "OpenMontageArtifactPayload": _artifact_payload,
    "OpenMontageCheckpoint": _checkpoint,
    "OpenMontageRuntimeAvailability": _runtime_availability,
    "OpenMontageCapabilitySummary": _capability_summary,
    "OpenMontageSetupOffer": _setup_offer,
    "OpenMontagePreflightSnapshot": _preflight_snapshot,
    "OpenMontageProfessionalVideoRequest": _professional_video_request,
    "OpenMontageError": _error,
    "OpenMontageSubmitResponse": _submit_response,
    "OpenMontageArtifact": _artifact,
    "OpenMontageStageCheckpoint": _stage_checkpoint,
    "OpenMontageDecision": _decision,
    "OpenMontageApprovalRequest": _approval_request,
    "OpenMontageApprovalDecision": _approval_decision,
    "OpenMontageJobSnapshot": _job_snapshot,
    "OpenMontageJobEvent": _job_event,
    "OpenMontageCallbackAck": _callback_ack,
}

# One carrier message per enum, exercising a representative non-UNSPECIFIED
# variant of that enum *inside a real message*. Keyed ``Enum_<EnumName>`` so
# the cross-language tests can map each entry to a concrete carrier message
# type. The value is (carrier_type_name, builder).
#
# IMPORTANT: each carrier reuses the carrier type's FULLY POPULATED message
# builder and overrides ONLY the enum field (via dataclasses.replace). This is
# deliberate: the Python codec omits ``None`` optionals while the Rust prost/
# serde codec emits them as JSON ``null`` (no ``skip_serializing_if`` and no
# struct-level ``#[serde(default)]`` on these messages). A carrier with unset
# optionals would therefore produce a different key set on each side — a
# *fixture* asymmetry that would masquerade as a codec divergence. Fully
# populating keeps the comparison apples-to-apples so it tests the enum's wire
# token (and field values), not optional-omission policy.
_ENUM_CARRIERS = {
    "Enum_OpenMontageProtocolVersion": (
        "OpenMontageSubmitResponse",
        lambda: dataclasses.replace(
            _submit_response(), version=gm.OpenMontageProtocolVersion.V1
        ),
    ),
    "Enum_OpenMontageJobStatus": (
        "OpenMontageStageCheckpoint",
        lambda: dataclasses.replace(
            _stage_checkpoint(), status=gm.OpenMontageJobStatus.AWAITING_HUMAN
        ),
    ),
    "Enum_OpenMontageEventType": (
        "OpenMontageJobEvent",
        lambda: dataclasses.replace(
            _job_event(), event_type=gm.OpenMontageEventType.PROVIDER_BLOCKED
        ),
    ),
    "Enum_OpenMontageInputAssetKind": (
        "OpenMontageInputAsset",
        lambda: dataclasses.replace(
            _input_asset(), kind=gm.OpenMontageInputAssetKind.LUT
        ),
    ),
    "Enum_OpenMontageArtifactKind": (
        "OpenMontageArtifact",
        lambda: dataclasses.replace(
            _artifact(), kind=gm.OpenMontageArtifactKind.MANIFEST
        ),
    ),
    "Enum_OpenMontageErrorCode": (
        "OpenMontageError",
        lambda: dataclasses.replace(
            _error(), code=gm.OpenMontageErrorCode.LIVE_PROVIDER_NOT_APPROVED
        ),
    ),
}


def build_vectors() -> dict:
    """Build the full ``{name: json_value}`` golden map via the Python codec."""
    vectors: dict = {}

    # Carrier-message-per-enum entries first (deterministic key order does not
    # matter for the file because we sort keys on write, but build in a stable
    # order anyway).
    for key, (_carrier_type, builder) in _ENUM_CARRIERS.items():
        vectors[key] = builder().to_dict()

    for name, builder in _MESSAGE_BUILDERS.items():
        vectors[name] = builder().to_dict()

    return vectors


def enum_carrier_types() -> dict:
    """Map each ``Enum_*`` golden key to its carrier message type name.

    Emitted into the golden file under a reserved ``__enum_carriers__`` key so
    the cross-language tests know which message type to deserialize each enum
    carrier entry into without hard-coding the mapping in two languages.
    """
    return {key: carrier for key, (carrier, _b) in _ENUM_CARRIERS.items()}


def main() -> int:
    vectors = build_vectors()

    # Sanity: 6 enum carriers + 32 messages = 38 entries.
    n_enum = sum(1 for k in vectors if k.startswith("Enum_"))
    n_msg = sum(1 for k in vectors if not k.startswith("Enum_"))
    assert n_enum == 6, f"expected 6 enum carriers, built {n_enum}"
    assert n_msg == 32, f"expected 32 messages, built {n_msg}"

    payload = dict(vectors)
    # Reserved metadata key (not a message); tells the consumers which carrier
    # type each Enum_* entry uses. Underscore-prefixed so it sorts and is
    # trivially skippable by the test loops.
    payload["__enum_carriers__"] = enum_carrier_types()

    os.makedirs(os.path.dirname(_GOLDEN_PATH), exist_ok=True)
    with open(_GOLDEN_PATH, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, sort_keys=True, indent=2, ensure_ascii=True)
        fh.write("\n")

    print(f"wrote {_GOLDEN_PATH}")
    print(f"  enum carriers: {n_enum}")
    print(f"  messages:      {n_msg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
