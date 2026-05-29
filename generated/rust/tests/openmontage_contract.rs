//! T10-1 (R-PROTO-01): exhaustive OpenMontage enum round-trip contract.
//!
//! For every variant of all 6 OpenMontage enums, assert that the
//! hand-maintained string codec round-trips
//! (`Enum::from_json_str(&v.to_json_str()) == Some(v)`) and that the wire
//! form is a lowercase snake_case token (matches `^[a-z0-9_]+$`).
//!
//! Variants are enumerated PROGRAMMATICALLY, not hand-picked: prost 0.13
//! generates `TryFrom<i32>` for each proto enum (it no longer emits the
//! deprecated `from_i32`), so `(0..64).filter_map(|i| Enum::try_from(i).ok())`
//! collects every declared variant. The collected count is asserted against
//! the spec count so a dropped (or silently added) variant reddens the test.

use glance_mind_protocol::glance_mind::{
    OpenMontageArtifactKind, OpenMontageErrorCode, OpenMontageEventType, OpenMontageInputAssetKind,
    OpenMontageJobStatus, OpenMontageProtocolVersion,
};

/// Collect every variant of a prost enum by probing `TryFrom<i32>` over a
/// range that comfortably covers all current and near-future tags.
fn collect_variants<T>() -> Vec<T>
where
    T: TryFrom<i32>,
{
    (0..64).filter_map(|i| T::try_from(i).ok()).collect()
}

/// A lowercase snake_case wire token: only `[a-z0-9_]`, and non-empty.
fn is_lower_snake(s: &str) -> bool {
    !s.is_empty()
        && s.chars()
            .all(|c| c.is_ascii_lowercase() || c.is_ascii_digit() || c == '_')
}

#[test]
fn all_enum_variants_roundtrip_as_strings() {
    // Each closure exercises one enum: round-trips every collected variant,
    // checks the wire form is lower snake_case, and returns how many
    // variants it saw. The macro keeps the per-enum body identical so no
    // enum can accidentally be tested differently from the others.
    macro_rules! check_enum {
        ($ty:ty, $expected:expr) => {{
            let variants = collect_variants::<$ty>();
            assert_eq!(
                variants.len(),
                $expected,
                "{}: expected {} variants but collected {} via TryFrom<i32> \
                 (a variant was added or dropped)",
                stringify!($ty),
                $expected,
                variants.len()
            );
            for v in &variants {
                let wire = v.to_json_str();
                assert!(
                    is_lower_snake(wire),
                    "{}::{:?} serializes to {:?}, which is not lowercase snake_case \
                     (must match ^[a-z0-9_]+$)",
                    stringify!($ty),
                    v,
                    wire
                );
                let back = <$ty>::from_json_str(wire);
                assert_eq!(
                    back,
                    Some(*v),
                    "{}::{:?} did not round-trip: to_json_str()={:?} \
                     parsed back to {:?}",
                    stringify!($ty),
                    v,
                    wire,
                    back
                );
            }
            variants.len()
        }};
    }

    let n_version = check_enum!(OpenMontageProtocolVersion, 2);
    let n_status = check_enum!(OpenMontageJobStatus, 11);
    let n_event = check_enum!(OpenMontageEventType, 18);
    let n_input = check_enum!(OpenMontageInputAssetKind, 17);
    let n_artifact = check_enum!(OpenMontageArtifactKind, 19);
    let n_error = check_enum!(OpenMontageErrorCode, 18);

    // Total exercised: 2 + 11 + 18 + 17 + 19 + 18 = 85.
    let total = n_version + n_status + n_event + n_input + n_artifact + n_error;
    assert_eq!(
        total, 85,
        "expected 85 total OpenMontage enum variants exercised, got {total}"
    );
}
