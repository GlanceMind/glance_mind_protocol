# ASSERTION-CHANGE-JUSTIFIED: purely additive — extends the module docstring,
# adds imports (json/os/gm + golden path + hypothesis), and appends NEW tests:
# test_matches_golden_vectors (T10-2) and the T10-3 property tests
# (test_property_* at the bottom). The existing T10-1
# test_all_enum_variants_roundtrip and all its assertions are left byte-for-byte
# intact; no existing assertion is weakened, skipped, or removed.
"""OpenMontage codec contract tests (Python side).

T10-1 (R-PROTO-01): exhaustive enum round-trip — for every variant of all 6
OpenMontage enums, assert the hand-maintained string codec round-trips
(``Enum.from_json(v.to_json()) == v``) and that the JSON wire form is a
lowercase snake_case token (matches ``^[a-z0-9_]+$``). The Python enums are
``(str, Enum)`` subclasses (see ``_OpenMontageEnum`` in ``glance_mind.py``), so
each enum is iterable and every variant is enumerated PROGRAMMATICALLY via
``for v in Enum``. The per-enum count is asserted against the spec count so a
dropped (or silently added) variant reddens the test.

T10-2 (R-PROTO-02): cross-language golden vectors — assert this codec
round-trips every entry in the committed golden file
(``generated/golden/openmontage_vectors.json``). The golden is produced by the
PYTHON codec (see ``generated/scripts/gen_openmontage_vectors.py``) and is the
shared oracle the RUST codec is also checked against; the Python side here
guards determinism and that the committed golden has not been hand-corrupted.
"""

import json
import os
import re

import glance_mind as gm
from glance_mind import (
    OpenMontageArtifactKind,
    OpenMontageErrorCode,
    OpenMontageEventType,
    OpenMontageInputAssetKind,
    OpenMontageJobStatus,
    OpenMontageProtocolVersion,
)

# Path to the committed golden oracle, relative to this test file
# (generated/python/ -> generated/golden/).
_GOLDEN_PATH = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "golden", "openmontage_vectors.json")
)

# Expected variant counts per enum (incl. UNSPECIFIED), matching
# proto/openmontage.proto and the Rust codec.
_EXPECTED_COUNTS = [
    (OpenMontageProtocolVersion, 2),
    (OpenMontageJobStatus, 11),
    (OpenMontageEventType, 18),
    (OpenMontageInputAssetKind, 17),
    (OpenMontageArtifactKind, 19),
    (OpenMontageErrorCode, 18),
]

_LOWER_SNAKE = re.compile(r"[a-z0-9_]+")


def test_all_enum_variants_roundtrip():
    total = 0
    for enum_cls, expected in _EXPECTED_COUNTS:
        variants = list(enum_cls)
        assert len(variants) == expected, (
            f"{enum_cls.__name__}: expected {expected} variants but found "
            f"{len(variants)} (a variant was added or dropped)"
        )
        for v in variants:
            wire = v.to_json()
            assert isinstance(wire, str), (
                f"{enum_cls.__name__}.{v.name}.to_json() returned non-str {wire!r}"
            )
            assert _LOWER_SNAKE.fullmatch(wire), (
                f"{enum_cls.__name__}.{v.name} serializes to {wire!r}, which is "
                f"not lowercase snake_case (must match ^[a-z0-9_]+$)"
            )
            back = enum_cls.from_json(wire)
            assert back == v, (
                f"{enum_cls.__name__}.{v.name} did not round-trip: "
                f"to_json()={wire!r} parsed back to {back!r}"
            )
        total += len(variants)

    # Total exercised: 2 + 11 + 18 + 17 + 19 + 18 = 85.
    assert total == 85, (
        f"expected 85 total OpenMontage enum variants exercised, got {total}"
    )


# ---------------------------------------------------------------------------
# T10-2 (R-PROTO-02): cross-language golden-vector oracle.
# ---------------------------------------------------------------------------

# Reserved (non-message) key in the golden file: maps each ``Enum_*`` entry to
# the message type used to carry it. Skipped by the message loop.
_ENUM_CARRIERS_KEY = "__enum_carriers__"


def _load_golden():
    assert os.path.exists(_GOLDEN_PATH), (
        f"golden vector file not found at {_GOLDEN_PATH}; regenerate it with "
        f"`python generated/scripts/gen_openmontage_vectors.py`"
    )
    with open(_GOLDEN_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def _codec_for(entry_key, golden):
    """Resolve the Python codec class for a golden entry key.

    Message entries are keyed by their exact type name. Enum carrier entries
    (``Enum_<EnumName>``) are mapped to a carrier message type via the
    reserved ``__enum_carriers__`` metadata block in the golden file, so the
    mapping is not hard-coded here.
    """
    if entry_key.startswith("Enum_"):
        carriers = golden[_ENUM_CARRIERS_KEY]
        type_name = carriers[entry_key]
    else:
        type_name = entry_key
    cls = getattr(gm, type_name, None)
    assert cls is not None, f"no Python codec class named {type_name!r} for golden entry {entry_key!r}"
    return cls


def test_matches_golden_vectors():
    """Python codec must round-trip every committed golden vector.

    For each entry: deserialize the golden JSON via the Python codec
    (``from_dict``), re-serialize (``to_dict``), and assert the re-serialized
    value equals the golden value. Comparison is on parsed JSON values (dicts),
    so it is key-order independent but strictly value-sensitive — a changed
    field value reddens it. Entries are enumerated DYNAMICALLY from the golden
    map (no hard-coded subset).
    """
    golden = _load_golden()

    entry_keys = [k for k in golden if k != _ENUM_CARRIERS_KEY]
    # 6 enum carriers + 32 messages = 38 vectors.
    assert len(entry_keys) == 38, (
        f"expected 38 golden vectors (6 enum carriers + 32 messages), found "
        f"{len(entry_keys)}: {sorted(entry_keys)}"
    )

    for key in entry_keys:
        cls = _codec_for(key, golden)
        golden_value = golden[key]
        # Deserialize via the codec, then re-serialize.
        instance = cls.from_dict(golden_value)
        regenerated = instance.to_dict()
        # Canonicalize both sides to parsed JSON (round-trip through json so any
        # tuple/list or int/float normalization the codec applies is reflected
        # symmetrically), then compare as values.
        golden_canon = json.loads(json.dumps(golden_value, sort_keys=True))
        regen_canon = json.loads(json.dumps(regenerated, sort_keys=True))
        assert regen_canon == golden_canon, (
            f"golden mismatch for {key}: Python re-serialization differs from "
            f"the committed golden.\n  golden:      {json.dumps(golden_canon, sort_keys=True)}\n"
            f"  regenerated: {json.dumps(regen_canon, sort_keys=True)}"
        )


# ---------------------------------------------------------------------------
# T10-3 (R-PROTO-03): property-based round-trip for the 5 core OpenMontage
# messages.
#
# T10-2 above proves EXAMPLE round-trip (one fully populated golden instance per
# message). This section proves the property `decode(encode(x)) == x` for
# ARBITRARY hypothesis-generated instances of the 5 core messages:
#
#   * OpenMontageProfessionalVideoRequest  (submit boundary; maps + nested lists)
#   * OpenMontageJobSnapshot               (full job state; deep nesting)
#   * OpenMontageJobEvent                  (streamed event; deep nesting)
#   * OpenMontageToolContract              (43 fields; many optionals)
#   * OpenMontagePipelineManifest          (nested stages/sub-stages)
#
# "encode"/"decode" is the Python codec: both the dict codec
# (``from_dict(to_dict(x))``) and, for the top-level messages, the JSON-text
# codec (``from_json(to_json(x))``) are asserted equal to ``x`` (dataclass
# structural ``==``).
#
# Strategy design (genuine variation, NOT a fixed value):
#   * strings: empty, ASCII, JSON-hostile chars (quote/backslash/newline/control)
#     AND unicode — so json escaping is exercised, not just identifiers;
#   * optionals: generated present AND absent (``st.none() | inner``);
#   * collections (list, dict): generated empty AND non-empty (size 0..N);
#   * floats: FINITE only (``allow_nan=False, allow_infinity=False``) — ``NaN``
#     breaks ``==`` (and the dataclass round-trip is dict->dict, so ``nan`` would
#     spuriously fail), and JSON has no real NaN/Inf. This is type/domain
#     correctness, not strategy-narrowing to dodge a bug;
#   * ints: ``from_dict`` coerces double fields with ``float(...)`` and int
#     fields with ``int(...)``; the dataclass types are respected (ints for int
#     fields, floats for float fields) so the coercions are identities. uint64
#     fields (``seed``, ``bytes``, ``sequence``) span the full 0..2**64-1 range
#     to exercise large-magnitude fidelity;
#   * enums: ``st.sampled_from(list(EnumCls))`` — every declared variant
#     (incl. UNSPECIFIED) is a candidate.
#
# If any property fails it is a REAL codec round-trip bug; hypothesis prints the
# shrunk falsifying example. Per T10-3 separation-of-duties, the test author
# surfaces it and does NOT patch the production codec
# (``glance_mind.py``) or narrow the strategy to dodge it.
#
# ===========================================================================
# DONE_WITH_CONCERNS — REAL Python codec round-trip bug found by T10-3.
# ===========================================================================
# Status today (commit time):
#   * GREEN  : test_property_tool_contract_roundtrips
#              (its whole nested tree has at least one non-optional field per
#               sub-message, so no sub-message ever serializes to ``{}``).
#   * FAILING (real bug, NOT dodged): the other 4 core messages — PVR,
#              JobSnapshot, JobEvent, PipelineManifest.
#
# Root cause (in glance_mind.py, the production codec — NOT touched here):
#   A nested OPTIONAL sub-message whose every field is itself optional/None
#   serializes via ``_omit_none`` to an EMPTY dict ``{}``. The parent's
#   ``from_dict`` then reconstructs it with a truthiness guard
#   (``Cls.from_dict(v) if v else None``); ``{}`` is falsy, so the sub-message
#   is read back as ``None``. Thus an all-None ``OpenMontageExtensionPermissions``
#   or ``OpenMontagePipelineOrchestration`` does NOT round-trip — it collapses to
#   ``None`` — violating ``decode(encode(x)) == x``.
#
#   Minimal falsifying example (hypothesis-shrunk):
#       OpenMontagePipelineManifest(
#           name='', version='', ...,
#           extensions=OpenMontageExtensionPermissions(custom_scripts=None,
#               custom_playbooks=None, custom_skills=None, custom_tools=None))
#       -> round-trips to ...extensions=None  (NOT equal)
#
#   Affected embedded messages: OpenMontageExtensionPermissions (4 optional
#   bools) and OpenMontagePipelineOrchestration (all 6 optional). PVR /
#   JobSnapshot / JobEvent inherit the bug transitively via PipelineManifest
#   (directly, or via PreflightSnapshot.pipelines[]).
#
# Per the T10-3 anti-gaming + separation-of-duties contract, the fix belongs to
# a SEPARATE codec fixer (e.g. make `from_dict` distinguish "absent" from
# "present-but-empty", or have these sub-messages emit a non-empty dict). These
# 4 tests are left as honest FAILING evidence (they are NOT wired into the CI
# `harness-contract` gate yet — that is task T10-10 — so they do not break CI),
# and they will pass once the codec is fixed. They are deliberately NOT skipped,
# NOT xfail-marked, and their strategies are NOT narrowed to avoid the all-None
# sub-message, because doing any of those would mask the defect.
# ---------------------------------------------------------------------------

from hypothesis import HealthCheck, given, settings  # noqa: E402
from hypothesis import strategies as st  # noqa: E402

# Bound on generated collection sizes: small enough that the deeply-nested
# messages (Snapshot/Event embed PreflightSnapshot -> lists of ToolContract +
# PipelineManifest) stay fast, large enough to exercise empty AND multi-element.
_MAX_LIST = 3
_MAX_MAP = 3

# A common settings profile for the (necessarily heavier) nested-message
# properties: keep example count modest and silence the "data generation too
# slow" health check, which can trip on the deep nesting without indicating a
# real problem.
_PROP_SETTINGS = settings(
    max_examples=200,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


def _text():
    """Genuinely varied text: plain tokens, JSON-hostile literals, unicode,
    arbitrary BMP+astral codepoints, and the empty string."""
    return st.one_of(
        st.text(alphabet="abcDEF012_./:-", max_size=12),
        st.sampled_from(['"', "\\", 'line1\nline2\t"q"\\', "emoji-\U0001f600-☃", ""]),
        st.text(max_size=8),  # arbitrary unicode incl. control chars
    )


def _opt_text():
    return st.none() | _text()


def _list_text():
    return st.lists(_text(), max_size=_MAX_LIST)


def _map_text():
    # Keys are simple tokens (distinctness), values fully varied.
    return st.dictionaries(
        st.text(alphabet="abcdef0123456789_", min_size=1, max_size=8),
        _text(),
        max_size=_MAX_MAP,
    )


def _finite_float():
    return st.floats(allow_nan=False, allow_infinity=False)


def _opt_finite_float():
    return st.none() | _finite_float()


_U32 = st.integers(min_value=0, max_value=2**32 - 1)
_U64 = st.integers(min_value=0, max_value=2**64 - 1)


def _opt_u32():
    return st.none() | _U32


def _opt_u64():
    return st.none() | _U64


def _opt_bool():
    return st.none() | st.booleans()


def _enum(cls):
    return st.sampled_from(list(cls))


# --- leaf / nested message strategies (mirrors gen_openmontage_vectors.py) ---


@st.composite
def _st_job_ref(draw):
    return gm.OpenMontageJobRef(
        job_id=draw(_text()),
        request_id=draw(_text()),
        project_id=draw(_text()),
        correlation_id=draw(_text()),
        idempotency_key=draw(_text()),
    )


@st.composite
def _st_callback_config(draw):
    return gm.OpenMontageCallbackConfig(
        callback_url=draw(_text()),
        callback_secret_ref=draw(_text()),
        event_types=draw(_list_text()),
    )


@st.composite
def _st_input_asset(draw):
    return gm.OpenMontageInputAsset(
        kind=draw(_enum(gm.OpenMontageInputAssetKind)),
        role=draw(_text()),
        uri=draw(_text()),
        mime_type=draw(_opt_text()),
        width_px=draw(_opt_u32()),
        height_px=draw(_opt_u32()),
        duration_ms=draw(_opt_u32()),
        metadata_json=draw(_opt_text()),
    )


@st.composite
def _st_schema_field(draw):
    return gm.OpenMontageSchemaField(
        path=draw(_text()),
        required=draw(st.booleans()),
        json_type=draw(_text()),
        enum_values=draw(_list_text()),
        default_json=draw(_opt_text()),
        description=draw(_opt_text()),
    )


@st.composite
def _st_resource_profile(draw):
    return gm.OpenMontageResourceProfile(
        cpu_cores=draw(_U32),
        ram_mb=draw(_U32),
        vram_mb=draw(_U32),
        disk_mb=draw(_U32),
        network_required=draw(st.booleans()),
    )


@st.composite
def _st_retry_policy(draw):
    return gm.OpenMontageRetryPolicy(
        max_retries=draw(_U32),
        backoff_seconds=draw(_finite_float()),
        retryable_errors=draw(_list_text()),
    )


@st.composite
def _st_tool_invocation(draw):
    return gm.OpenMontageToolInvocation(
        invocation_id=draw(_text()),
        stage=draw(_text()),
        tool_name=draw(_text()),
        role=draw(_text()),
        operation=draw(_text()),
        provider=draw(_text()),
        capability=draw(_text()),
        input_json=draw(_text()),
        idempotency_key=draw(_opt_text()),
        max_cost_usd=draw(_opt_finite_float()),
        dry_run=draw(st.booleans()),
        expected_artifact_roles=draw(_list_text()),
        contract_version=draw(_opt_text()),
        metadata_json=draw(_opt_text()),
    )


@st.composite
def _st_artifact(draw):
    return gm.OpenMontageArtifact(
        artifact_id=draw(_text()),
        kind=draw(_enum(gm.OpenMontageArtifactKind)),
        role=draw(_text()),
        uri=draw(_text()),
        mime_type=draw(_opt_text()),
        width_px=draw(_opt_u32()),
        height_px=draw(_opt_u32()),
        duration_ms=draw(_opt_u32()),
        bytes=draw(_opt_u64()),
        metadata_json=draw(_opt_text()),
        artifact_name=draw(_opt_text()),
        path=draw(_opt_text()),
        source_tool=draw(_opt_text()),
        scene_id=draw(_opt_text()),
        payload_json=draw(_opt_text()),
        schema_id=draw(_opt_text()),
        validated=draw(_opt_bool()),
    )


@st.composite
def _st_tool_result(draw):
    return gm.OpenMontageToolResult(
        invocation_id=draw(_text()),
        tool_name=draw(_text()),
        success=draw(st.booleans()),
        data_json=draw(_opt_text()),
        artifact_uris=draw(_list_text()),
        artifacts=draw(st.lists(_st_artifact(), max_size=_MAX_LIST)),
        error=draw(_opt_text()),
        cost_usd=draw(_finite_float()),
        duration_seconds=draw(_finite_float()),
        seed=draw(_opt_u64()),
        model=draw(_opt_text()),
        raw_artifacts_json=draw(_opt_text()),
        metadata_json=draw(_opt_text()),
    )


@st.composite
def _st_artifact_payload(draw):
    return gm.OpenMontageArtifactPayload(
        artifact_name=draw(_text()),
        schema_id=draw(_opt_text()),
        schema_version=draw(_opt_text()),
        payload_json=draw(_text()),
        validated=draw(st.booleans()),
        schema_fields=draw(st.lists(_st_schema_field(), max_size=_MAX_LIST)),
        validation_error=draw(_opt_text()),
        uri=draw(_opt_text()),
        role=draw(_opt_text()),
        metadata_json=draw(_opt_text()),
    )


@st.composite
def _st_checkpoint(draw):
    return gm.OpenMontageCheckpoint(
        version=draw(_text()),
        project_id=draw(_text()),
        pipeline_type=draw(_text()),
        stage=draw(_text()),
        status=draw(_text()),
        timestamp=draw(_text()),
        style_playbook=draw(_opt_text()),
        checkpoint_policy=draw(_opt_text()),
        human_approval_required=draw(_opt_bool()),
        human_approved=draw(_opt_bool()),
        artifacts=draw(st.lists(_st_artifact_payload(), max_size=_MAX_LIST)),
        artifacts_json=draw(_opt_text()),
        review_json=draw(_opt_text()),
        cost_snapshot_json=draw(_opt_text()),
        error=draw(_opt_text()),
        metadata_json=draw(_opt_text()),
        path=draw(_opt_text()),
    )


@st.composite
def _st_stage_checkpoint(draw):
    return gm.OpenMontageStageCheckpoint(
        sequence=draw(_U64),
        stage=draw(_text()),
        status=draw(_enum(gm.OpenMontageJobStatus)),
        summary=draw(_text()),
        artifact_refs=draw(_list_text()),
        cost_snapshot_json=draw(_opt_text()),
        review_json=draw(_opt_text()),
        created_at=draw(_text()),
        checkpoint=draw(st.none() | _st_checkpoint()),
        artifact_payloads=draw(st.lists(_st_artifact_payload(), max_size=_MAX_LIST)),
        checkpoint_json=draw(_opt_text()),
    )


@st.composite
def _st_decision(draw):
    return gm.OpenMontageDecision(
        sequence=draw(_U64),
        category=draw(_text()),
        summary=draw(_text()),
        selected_option=draw(_opt_text()),
        options_json=draw(_opt_text()),
        confidence=draw(_opt_text()),
        created_at=draw(_text()),
    )


@st.composite
def _st_approval_request(draw):
    return gm.OpenMontageApprovalRequest(
        approval_id=draw(_text()),
        stage=draw(_text()),
        decision_category=draw(_text()),
        prompt=draw(_text()),
        options_json=draw(_opt_text()),
        expires_at=draw(_opt_text()),
    )


@st.composite
def _st_error(draw):
    return gm.OpenMontageError(
        code=draw(_enum(gm.OpenMontageErrorCode)),
        message=draw(_text()),
        retryable=draw(st.booleans()),
        detail_json=draw(_opt_text()),
    )


@st.composite
def _st_runtime_availability(draw):
    return gm.OpenMontageRuntimeAvailability(
        name=draw(_text()),
        available=draw(st.booleans()),
        note=draw(_opt_text()),
        warnings=draw(_list_text()),
    )


@st.composite
def _st_capability_summary(draw):
    return gm.OpenMontageCapabilitySummary(
        capability=draw(_text()),
        configured=draw(_U32),
        total=draw(_U32),
        available_providers=draw(_list_text()),
        unavailable_providers=draw(_list_text()),
    )


@st.composite
def _st_setup_offer(draw):
    return gm.OpenMontageSetupOffer(
        capability=draw(_text()),
        tool=draw(_text()),
        provider=draw(_text()),
        install_instructions=draw(_text()),
    )


@st.composite
def _st_pipeline_sub_stage(draw):
    return gm.OpenMontagePipelineSubStage(
        name=draw(_text()),
        description=draw(_opt_text()),
        condition=draw(_opt_text()),
        human_approval_default=draw(_opt_bool()),
        tools_available=draw(_list_text()),
        review_focus=draw(_list_text()),
    )


@st.composite
def _st_pipeline_stage(draw):
    return gm.OpenMontagePipelineStage(
        name=draw(_text()),
        agent=draw(_opt_text()),
        skill=draw(_opt_text()),
        required_artifacts_in=draw(_list_text()),
        optional_artifacts_in=draw(_list_text()),
        produces=draw(_list_text()),
        preferred_tools=draw(_list_text()),
        fallback_tools=draw(_list_text()),
        required_tools=draw(_list_text()),
        optional_tools=draw(_list_text()),
        tools_available=draw(_list_text()),
        review_focus=draw(_list_text()),
        checkpoint_required=draw(_opt_bool()),
        human_approval_default=draw(_opt_bool()),
        success_criteria=draw(_list_text()),
        sub_stages=draw(st.lists(_st_pipeline_sub_stage(), max_size=_MAX_LIST)),
        metadata_json=draw(_opt_text()),
    )


@st.composite
def _st_pipeline_orchestration(draw):
    return gm.OpenMontagePipelineOrchestration(
        mode=draw(_opt_text()),
        skill=draw(_opt_text()),
        budget_default_usd=draw(_opt_finite_float()),
        max_revisions_per_stage=draw(_opt_u32()),
        max_send_backs=draw(_opt_u32()),
        max_wall_time_minutes=draw(_opt_u32()),
    )


@st.composite
def _st_extension_permissions(draw):
    return gm.OpenMontageExtensionPermissions(
        custom_scripts=draw(_opt_bool()),
        custom_playbooks=draw(_opt_bool()),
        custom_skills=draw(_opt_bool()),
        custom_tools=draw(_opt_bool()),
    )


@st.composite
def _st_reference_input_config(draw):
    return gm.OpenMontageReferenceInputConfig(
        supported=draw(st.booleans()),
        analysis_depth=draw(_opt_text()),
        analysis_tools=draw(_list_text()),
    )


@st.composite
def _st_tool_contract(draw):
    return gm.OpenMontageToolContract(
        name=draw(_text()),
        version=draw(_text()),
        tier=draw(_text()),
        capability=draw(_text()),
        provider=draw(_text()),
        stability=draw(_text()),
        status=draw(_text()),
        execution_mode=draw(_text()),
        determinism=draw(_text()),
        runtime=draw(_text()),
        module_path=draw(_text()),
        usage_location=draw(_text()),
        dependencies=draw(_list_text()),
        install_instructions=draw(_text()),
        capabilities=draw(_list_text()),
        input_fields=draw(st.lists(_st_schema_field(), max_size=_MAX_LIST)),
        output_fields=draw(st.lists(_st_schema_field(), max_size=_MAX_LIST)),
        input_schema_json=draw(_opt_text()),
        output_schema_json=draw(_opt_text()),
        artifact_schema_json=draw(_opt_text()),
        progress_schema_json=draw(_opt_text()),
        supports_json=draw(_opt_text()),
        best_for=draw(_list_text()),
        not_good_for=draw(_list_text()),
        provider_matrix_json=draw(_opt_text()),
        resource_profile=draw(st.none() | _st_resource_profile()),
        retry_policy=draw(st.none() | _st_retry_policy()),
        resume_support=draw(_text()),
        side_effects=draw(_list_text()),
        fallback=draw(_opt_text()),
        fallback_tools=draw(_list_text()),
        agent_skills=draw(_list_text()),
        user_visible_verification=draw(_list_text()),
        quality_score=draw(_opt_finite_float()),
        historical_success_rate=draw(_opt_finite_float()),
        latency_p50_seconds=draw(_opt_finite_float()),
        render_engines_json=draw(_opt_text()),
        render_runtimes_json=draw(_opt_text()),
        remotion_note=draw(_opt_text()),
        hyperframes_note=draw(_opt_text()),
        runtime_governance=draw(_opt_text()),
        raw_info_json=draw(_opt_text()),
        related_skills=draw(_list_text()),
    )


@st.composite
def _st_pipeline_manifest(draw):
    return gm.OpenMontagePipelineManifest(
        name=draw(_text()),
        version=draw(_text()),
        description=draw(_opt_text()),
        category=draw(_opt_text()),
        stability=draw(_opt_text()),
        compatible_playbooks=draw(_list_text()),
        compatible_playbooks_json=draw(_opt_text()),
        required_skills=draw(_list_text()),
        stages=draw(st.lists(_st_pipeline_stage(), max_size=_MAX_LIST)),
        default_checkpoint_policy=draw(_opt_text()),
        reference_input=draw(st.none() | _st_reference_input_config()),
        orchestration=draw(st.none() | _st_pipeline_orchestration()),
        extensions=draw(st.none() | _st_extension_permissions()),
        metadata_json=draw(_opt_text()),
        raw_manifest_json=draw(_opt_text()),
    )


@st.composite
def _st_preflight_snapshot(draw):
    return gm.OpenMontagePreflightSnapshot(
        composition_runtimes=draw(st.lists(_st_runtime_availability(), max_size=_MAX_LIST)),
        capabilities=draw(st.lists(_st_capability_summary(), max_size=_MAX_LIST)),
        setup_offers=draw(st.lists(_st_setup_offer(), max_size=_MAX_LIST)),
        runtime_warnings=draw(_list_text()),
        tools=draw(st.lists(_st_tool_contract(), max_size=_MAX_LIST)),
        pipelines=draw(st.lists(_st_pipeline_manifest(), max_size=_MAX_LIST)),
        captured_at=draw(_text()),
        provider_menu_summary_json=draw(_opt_text()),
        provider_menu_json=draw(_opt_text()),
        support_envelope_json=draw(_opt_text()),
    )


# --- the 5 core message strategies ---


@st.composite
def _st_professional_video_request(draw):
    return gm.OpenMontageProfessionalVideoRequest(
        version=draw(_enum(gm.OpenMontageProtocolVersion)),
        request_id=draw(_text()),
        idempotency_key=draw(_text()),
        tenant_id=draw(_text()),
        user_id=draw(_text()),
        title=draw(_text()),
        prompt=draw(_text()),
        target_platform=draw(_text()),
        language=draw(_text()),
        duration_seconds=draw(_U32),
        aspect_ratio=draw(_text()),
        audience=draw(_opt_text()),
        objective=draw(_opt_text()),
        brand_json=draw(_opt_text()),
        pipeline=draw(_text()),
        style_playbook=draw(_opt_text()),
        render_runtime=draw(_opt_text()),
        quality_tier=draw(_text()),
        approval_policy=draw(_text()),
        budget_limit_usd=draw(_finite_float()),
        provider_preferences=draw(_map_text()),
        assets=draw(st.lists(_st_input_asset(), max_size=_MAX_LIST)),
        callback=draw(st.none() | _st_callback_config()),
        metadata_json=draw(_opt_text()),
        source_script=draw(_opt_text()),
        source_script_uri=draw(_opt_text()),
        input_mode=draw(_opt_text()),
        output_profile=draw(_opt_text()),
        renderer_family=draw(_opt_text()),
        delivery_promise_json=draw(_opt_text()),
        music_plan_json=draw(_opt_text()),
        voice_selection_json=draw(_opt_text()),
        tool_invocations=draw(st.lists(_st_tool_invocation(), max_size=_MAX_LIST)),
        artifact_inputs=draw(st.lists(_st_artifact_payload(), max_size=_MAX_LIST)),
        pipeline_manifest=draw(st.none() | _st_pipeline_manifest()),
        preflight_policy=draw(_opt_text()),
        openmontage_request_json=draw(_opt_text()),
        provider_slots=draw(_map_text()),
    )


@st.composite
def _st_job_snapshot(draw):
    return gm.OpenMontageJobSnapshot(
        version=draw(_enum(gm.OpenMontageProtocolVersion)),
        job=draw(st.none() | _st_job_ref()),
        status=draw(_enum(gm.OpenMontageJobStatus)),
        pipeline=draw(_text()),
        current_stage=draw(_text()),
        progress_pct=draw(_U32),
        checkpoints=draw(st.lists(_st_stage_checkpoint(), max_size=_MAX_LIST)),
        decisions=draw(st.lists(_st_decision(), max_size=_MAX_LIST)),
        approvals=draw(st.lists(_st_approval_request(), max_size=_MAX_LIST)),
        artifacts=draw(st.lists(_st_artifact(), max_size=_MAX_LIST)),
        error=draw(st.none() | _st_error()),
        metrics_json=draw(_opt_text()),
        updated_at=draw(_text()),
        preflight=draw(st.none() | _st_preflight_snapshot()),
        pipeline_manifest=draw(st.none() | _st_pipeline_manifest()),
        artifact_payloads=draw(st.lists(_st_artifact_payload(), max_size=_MAX_LIST)),
        tool_results=draw(st.lists(_st_tool_result(), max_size=_MAX_LIST)),
        full_checkpoints=draw(st.lists(_st_checkpoint(), max_size=_MAX_LIST)),
    )


@st.composite
def _st_job_event(draw):
    return gm.OpenMontageJobEvent(
        version=draw(_enum(gm.OpenMontageProtocolVersion)),
        event_id=draw(_text()),
        sequence=draw(_U64),
        job=draw(st.none() | _st_job_ref()),
        event_type=draw(_enum(gm.OpenMontageEventType)),
        status=draw(_enum(gm.OpenMontageJobStatus)),
        stage=draw(_text()),
        progress_pct=draw(_U32),
        checkpoint=draw(st.none() | _st_stage_checkpoint()),
        approval=draw(st.none() | _st_approval_request()),
        artifacts=draw(st.lists(_st_artifact(), max_size=_MAX_LIST)),
        error=draw(st.none() | _st_error()),
        event_json=draw(_opt_text()),
        emitted_at=draw(_text()),
        tool_invocation=draw(st.none() | _st_tool_invocation()),
        tool_result=draw(st.none() | _st_tool_result()),
        artifact_payloads=draw(st.lists(_st_artifact_payload(), max_size=_MAX_LIST)),
        checkpoint_full=draw(st.none() | _st_checkpoint()),
        preflight=draw(st.none() | _st_preflight_snapshot()),
    )


def _assert_roundtrip(instance, cls):
    """The property: both the dict codec and the JSON-text codec must round-trip
    ``instance`` to an equal value (dataclass structural ``==``)."""
    via_dict = cls.from_dict(instance.to_dict())
    assert via_dict == instance, (
        f"dict round-trip mismatch for {cls.__name__}: "
        f"from_dict(to_dict(x)) != x\n  original:   {instance!r}\n  round-trip: {via_dict!r}"
    )
    via_json = cls.from_json(instance.to_json())
    assert via_json == instance, (
        f"json round-trip mismatch for {cls.__name__}: "
        f"from_json(to_json(x)) != x\n  original:   {instance!r}\n  round-trip: {via_json!r}"
    )


@_PROP_SETTINGS
@given(x=_st_professional_video_request())
def test_property_professional_video_request_roundtrips(x):
    _assert_roundtrip(x, gm.OpenMontageProfessionalVideoRequest)


@_PROP_SETTINGS
@given(x=_st_job_snapshot())
def test_property_job_snapshot_roundtrips(x):
    _assert_roundtrip(x, gm.OpenMontageJobSnapshot)


@_PROP_SETTINGS
@given(x=_st_job_event())
def test_property_job_event_roundtrips(x):
    _assert_roundtrip(x, gm.OpenMontageJobEvent)


@_PROP_SETTINGS
@given(x=_st_tool_contract())
def test_property_tool_contract_roundtrips(x):
    _assert_roundtrip(x, gm.OpenMontageToolContract)


@_PROP_SETTINGS
@given(x=_st_pipeline_manifest())
def test_property_pipeline_manifest_roundtrips(x):
    _assert_roundtrip(x, gm.OpenMontagePipelineManifest)


# ---------------------------------------------------------------------------
# T10-4 (R-PROTO-04): unknown-enum behavior at BOTH layers (Python side).
#
# Unlike the Rust codec, the Python codec COERCES an unknown enum token to
# UNSPECIFIED at BOTH layers (it is a forward-compatible reader):
#
#   * BARE codec (``Enum.from_json``): an unknown token -> ``Enum.UNSPECIFIED``
#     (the ``return cls.UNSPECIFIED`` fallback in ``_OpenMontageEnum``).
#   * MESSAGE layer (``Message.from_json``/``from_dict``): an unknown ``status``
#     or ``event_type`` string yields a struct with that enum = UNSPECIFIED and
#     NO error raised.
#
# The companion RUST codec instead REJECTS an unknown token on the message layer
# (``serde_json::from_str`` returns an "unknown variant" ``Err``); see
# tests/openmontage_contract.rs. That intentional Rust-rejects / Python-coerces
# divergence is recorded in docs/openmontage-api-coverage.md.
# ---------------------------------------------------------------------------


def test_unknown_enum_bare_codec_coerces_to_unspecified():
    # Strict on the Rust side; coercing on the Python side. Exercised on 2 of
    # the 6 enums (JobStatus + EventType); all six share ``_OpenMontageEnum``.
    assert OpenMontageJobStatus.from_json("bogus") is OpenMontageJobStatus.UNSPECIFIED, (
        "bare OpenMontageJobStatus.from_json must coerce an unknown token to UNSPECIFIED"
    )
    assert (
        OpenMontageEventType.from_json("not_a_real_event")
        is OpenMontageEventType.UNSPECIFIED
    ), "bare OpenMontageEventType.from_json must coerce an unknown token to UNSPECIFIED"
    # Sanity: a KNOWN token still parses to its own member (guards against a
    # degenerate codec that maps EVERYTHING to UNSPECIFIED).
    assert OpenMontageJobStatus.from_json("running") is OpenMontageJobStatus.RUNNING, (
        "a known token must still parse to its own member on the bare codec"
    )


def test_unknown_enum_message_layer_coerces_to_unspecified():
    # An unknown enum token anywhere in a message is silently coerced to
    # UNSPECIFIED (no error). This is the Python side of the documented
    # Rust-rejects / Python-coerces divergence.

    # (a) unknown ``status`` token.
    ev = gm.OpenMontageJobEvent.from_json(
        '{"version":"v1","status":"bogus_status"}'
    )
    assert ev.status is OpenMontageJobStatus.UNSPECIFIED, (
        "an unknown `status` token must coerce to UNSPECIFIED, "
        f"got {ev.status!r}"
    )

    # (b) unknown ``event_type`` token.
    ev = gm.OpenMontageJobEvent.from_json(
        '{"version":"v1","event_type":"teleportation_completed"}'
    )
    assert ev.event_type is OpenMontageEventType.UNSPECIFIED, (
        "an unknown `event_type` token must coerce to UNSPECIFIED, "
        f"got {ev.event_type!r}"
    )

    # Control: known tokens parse to their own members (so the coercions above
    # are caused by the unknown token, not by a codec that ignores the field).
    ev = gm.OpenMontageJobEvent.from_json(
        '{"version":"v1","status":"running","event_type":"job_status_changed"}'
    )
    assert ev.status is OpenMontageJobStatus.RUNNING
    assert ev.event_type is OpenMontageEventType.JOB_STATUS_CHANGED


# ---------------------------------------------------------------------------
# T10-5 (R-PROTO-05): unknown-field tolerance + omit-vs-null optional parity
# (Python side).
#
#   * Forward-compat: a message dict carrying an EXTRA unknown key is IGNORED.
#     ``from_dict`` reads each known field via ``data.get(...)`` and never
#     inspects unrecognized keys, so a field a newer peer added is dropped.
#   * Omit-vs-null: an optional field may arrive as an OMITTED key or as an
#     explicit ``None``. Both forms must deserialize to the SAME value
#     (``None``) and round-trip identically. Cosmetic wire-form difference; both
#     sides read both forms (recorded in docs/openmontage-api-coverage.md).
# ---------------------------------------------------------------------------


def test_unknown_field_is_ignored():
    # Extra unknown key on a leaf message.
    asset = gm.OpenMontageInputAsset.from_dict(
        {"kind": "audio", "role": "narration", "uri": "u", "future_field": 123}
    )
    assert asset.kind is OpenMontageInputAssetKind.AUDIO
    assert asset.role == "narration"

    # Extra unknown key on a top-level message too.
    req = gm.OpenMontageProfessionalVideoRequest.from_dict(
        {"version": "v1", "request_id": "r1", "future_field": {"nested": [1, 2, 3]}}
    )
    assert req.request_id == "r1"
    assert req.version is OpenMontageProtocolVersion.V1
    # The dropped key must NOT reappear on re-serialization.
    assert "future_field" not in req.to_dict(), (
        "an ignored unknown key must not be echoed back out by to_dict()"
    )


def test_optional_omit_vs_null_yield_same_value():
    # ``OpenMontageInputAsset.mime_type`` is optional.
    # Form A: key omitted entirely.
    omitted = gm.OpenMontageInputAsset.from_dict(
        {"kind": "audio", "role": "r", "uri": "u"}
    )
    # Form B: key present but explicitly null.
    explicit_null = gm.OpenMontageInputAsset.from_dict(
        {"kind": "audio", "role": "r", "uri": "u", "mime_type": None}
    )

    # Both forms collapse to the same absent value...
    assert omitted.mime_type is None, "omitted optional must be None"
    assert explicit_null.mime_type is None, "explicit-null optional must also be None"
    # ...and produce structurally identical messages (dataclass ``==``).
    assert omitted == explicit_null, (
        "omit-vs-null optional must deserialize to the SAME value"
    )

    # Round-trip consistency: re-serializing either form yields the canonical
    # wire form (which OMITS the None optional via ``_omit_none``), and
    # re-parsing it lands back on the same value.
    reserialized = omitted.to_dict()
    assert "mime_type" not in reserialized, (
        "a None optional must be omitted from the canonical wire form"
    )
    assert gm.OpenMontageInputAsset.from_dict(reserialized) == omitted, (
        "round-trip must be stable for the absent optional"
    )


# ---------------------------------------------------------------------------
# T10-6 (R-PROTO-06): ``version`` default + string emission (Python side).
#
# ``version`` is an ``OpenMontageProtocolVersion`` (a ``(str, Enum)``); it MUST
# serialize as its lowercase STRING token — ``"v1"`` for ``V1`` and
# ``"unspecified"`` for the defaulted/UNSPECIFIED value — NEVER the int ``1``.
# Asserted on two messages that carry ``version`` (ProfessionalVideoRequest +
# JobEvent).
# ---------------------------------------------------------------------------


def test_version_serializes_as_string_token_not_int():
    # --- version = V1 -> "v1" ---
    for ctx, msg in (
        (
            "ProfessionalVideoRequest",
            gm.OpenMontageProfessionalVideoRequest(version=OpenMontageProtocolVersion.V1),
        ),
        ("JobEvent", gm.OpenMontageJobEvent(version=OpenMontageProtocolVersion.V1)),
    ):
        v = msg.to_dict()["version"]
        assert v == "v1", f"{ctx}(V1): version must serialize to 'v1', got {v!r}"
        assert isinstance(v, str) and not isinstance(v, bool), (
            f"{ctx}(V1): version must be a string, got {type(v).__name__}"
        )
        assert v != 1, f"{ctx}(V1): version must NOT be the int 1"
        # In the JSON text it appears as the quoted string, never the bare int.
        text = msg.to_json()
        assert '"version": "v1"' in text, (
            f"{ctx}(V1): JSON must contain '\"version\": \"v1\"', got: {text}"
        )

    # --- defaulted / UNSPECIFIED -> "unspecified" ---
    for ctx, msg in (
        ("ProfessionalVideoRequest", gm.OpenMontageProfessionalVideoRequest()),
        ("JobEvent", gm.OpenMontageJobEvent()),
    ):
        # The dataclass default is UNSPECIFIED.
        assert msg.version is OpenMontageProtocolVersion.UNSPECIFIED, (
            f"{ctx}: default version must be UNSPECIFIED"
        )
        v = msg.to_dict()["version"]
        assert v == "unspecified", (
            f"{ctx}(default): version must serialize to 'unspecified', got {v!r}"
        )
        assert isinstance(v, str), f"{ctx}(default): version must be a string"
