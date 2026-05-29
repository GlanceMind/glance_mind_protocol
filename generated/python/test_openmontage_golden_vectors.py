# ASSERTION-CHANGE-JUSTIFIED: purely additive — extends the module docstring,
# adds imports (json/os/gm + golden path), and (below) appends a NEW
# test_matches_golden_vectors for T10-2. The existing T10-1
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
