"""T10-1 (R-PROTO-01): exhaustive OpenMontage enum round-trip contract (Python).

For every variant of all 6 OpenMontage enums, assert the hand-maintained
string codec round-trips (``Enum.from_json(v.to_json()) == v``) and that the
JSON wire form is a lowercase snake_case token (matches ``^[a-z0-9_]+$``).

The Python enums are ``(str, Enum)`` subclasses (see ``_OpenMontageEnum`` in
``glance_mind.py``), so each enum is iterable and every variant is enumerated
PROGRAMMATICALLY via ``for v in Enum``. The per-enum count is asserted against
the spec count so a dropped (or silently added) variant reddens the test.
"""

import re

from glance_mind import (
    OpenMontageArtifactKind,
    OpenMontageErrorCode,
    OpenMontageEventType,
    OpenMontageInputAssetKind,
    OpenMontageJobStatus,
    OpenMontageProtocolVersion,
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
