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

// ===========================================================================
// T10-2 (R-PROTO-02): cross-language golden-vector oracle.
//
// The golden file `generated/golden/openmontage_vectors.json` is produced by
// the PYTHON codec (`generated/scripts/gen_openmontage_vectors.py`) and is the
// reviewed shared oracle. This test is the cross-language parity check: for
// every entry, DESERIALIZE the golden JSON via the RUST codec, RE-SERIALIZE
// via the Rust codec, and assert it equals the golden JSON after
// canonicalization (parse both to `serde_json::Value`, which compares values
// order-independently but is strictly value-sensitive). If Rust serializes any
// field differently than the Python-produced golden, this reddens.
//
// Entries are enumerated DYNAMICALLY from the JSON map keys. The key->type
// dispatch below is a `match` (unavoidable in a statically typed language),
// but it is exhaustive: any golden key with no arm fails the test loudly, so
// no message can silently be skipped.
// ===========================================================================

use glance_mind_protocol::glance_mind::{
    OpenMontageApprovalDecision, OpenMontageApprovalRequest, OpenMontageArtifact,
    OpenMontageArtifactPayload, OpenMontageCallbackAck, OpenMontageCallbackConfig,
    OpenMontageCapabilitySummary, OpenMontageCheckpoint, OpenMontageDecision, OpenMontageError,
    OpenMontageExtensionPermissions, OpenMontageInputAsset, OpenMontageJobEvent, OpenMontageJobRef,
    OpenMontageJobSnapshot, OpenMontagePipelineManifest, OpenMontagePipelineOrchestration,
    OpenMontagePipelineStage, OpenMontagePipelineSubStage, OpenMontagePreflightSnapshot,
    OpenMontageProfessionalVideoRequest, OpenMontageReferenceInputConfig,
    OpenMontageResourceProfile, OpenMontageRetryPolicy, OpenMontageRuntimeAvailability,
    OpenMontageSchemaField, OpenMontageSetupOffer, OpenMontageStageCheckpoint,
    OpenMontageSubmitResponse, OpenMontageToolContract, OpenMontageToolInvocation,
    OpenMontageToolResult,
};

/// Reserved (non-message) key in the golden file: maps each `Enum_*` entry to
/// the carrier message type used to serialize it.
const ENUM_CARRIERS_KEY: &str = "__enum_carriers__";

/// Load + parse the committed golden file. Path is resolved relative to the
/// crate manifest dir (`generated/rust/`) so it works regardless of CWD:
/// `generated/rust/` -> `generated/golden/openmontage_vectors.json`.
fn load_golden() -> serde_json::Map<String, serde_json::Value> {
    let path = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("..")
        .join("golden")
        .join("openmontage_vectors.json");
    let raw = std::fs::read_to_string(&path).unwrap_or_else(|e| {
        panic!(
            "golden vector file not found at {}: {e}; regenerate it with \
             `python generated/scripts/gen_openmontage_vectors.py`",
            path.display()
        )
    });
    let value: serde_json::Value =
        serde_json::from_str(&raw).expect("golden vector file is not valid JSON");
    value
        .as_object()
        .expect("golden vector file root must be a JSON object")
        .clone()
}

#[test]
fn matches_golden_vectors() {
    let golden = load_golden();

    // Pull the enum-carrier metadata: which message type carries each Enum_*.
    let carriers = golden
        .get(ENUM_CARRIERS_KEY)
        .and_then(|v| v.as_object())
        .expect("golden file missing __enum_carriers__ metadata object")
        .clone();

    // Re-serialize `$golden_value` through type `$ty` and assert the parsed
    // result equals the golden value. `$key` names the entry for diagnostics.
    macro_rules! check_roundtrip {
        ($ty:ty, $key:expr, $golden_value:expr) => {{
            let parsed: $ty = serde_json::from_value($golden_value.clone()).unwrap_or_else(|e| {
                panic!(
                    "golden entry {} failed to DESERIALIZE via Rust codec as {}: {e}",
                    $key,
                    stringify!($ty)
                )
            });
            let regenerated =
                serde_json::to_value(&parsed).expect("Rust re-serialization to Value failed");
            // Apples-to-apples: both are serde_json::Value, so comparison is
            // key-order independent yet strictly value-sensitive.
            if regenerated != *$golden_value {
                panic!(
                    "golden mismatch for {} (type {}): Rust re-serialization differs from the \
                     committed (Python-produced) golden.\n  golden:      {}\n  regenerated: {}",
                    $key,
                    stringify!($ty),
                    $golden_value,
                    regenerated
                );
            }
        }};
    }

    // Dispatch a single entry to the right concrete type. `type_name` is the
    // message type to deserialize into (for enum carriers this is the carrier
    // type, resolved from metadata; for messages it is the entry key itself).
    macro_rules! dispatch {
        ($type_name:expr, $key:expr, $value:expr) => {
            match $type_name {
                "OpenMontageJobRef" => check_roundtrip!(OpenMontageJobRef, $key, $value),
                "OpenMontageCallbackConfig" => {
                    check_roundtrip!(OpenMontageCallbackConfig, $key, $value)
                }
                "OpenMontageInputAsset" => check_roundtrip!(OpenMontageInputAsset, $key, $value),
                "OpenMontageSchemaField" => check_roundtrip!(OpenMontageSchemaField, $key, $value),
                "OpenMontageResourceProfile" => {
                    check_roundtrip!(OpenMontageResourceProfile, $key, $value)
                }
                "OpenMontageRetryPolicy" => check_roundtrip!(OpenMontageRetryPolicy, $key, $value),
                "OpenMontageToolContract" => {
                    check_roundtrip!(OpenMontageToolContract, $key, $value)
                }
                "OpenMontageToolInvocation" => {
                    check_roundtrip!(OpenMontageToolInvocation, $key, $value)
                }
                "OpenMontageToolResult" => check_roundtrip!(OpenMontageToolResult, $key, $value),
                "OpenMontagePipelineSubStage" => {
                    check_roundtrip!(OpenMontagePipelineSubStage, $key, $value)
                }
                "OpenMontagePipelineStage" => {
                    check_roundtrip!(OpenMontagePipelineStage, $key, $value)
                }
                "OpenMontagePipelineOrchestration" => {
                    check_roundtrip!(OpenMontagePipelineOrchestration, $key, $value)
                }
                "OpenMontageExtensionPermissions" => {
                    check_roundtrip!(OpenMontageExtensionPermissions, $key, $value)
                }
                "OpenMontageReferenceInputConfig" => {
                    check_roundtrip!(OpenMontageReferenceInputConfig, $key, $value)
                }
                "OpenMontagePipelineManifest" => {
                    check_roundtrip!(OpenMontagePipelineManifest, $key, $value)
                }
                "OpenMontageArtifactPayload" => {
                    check_roundtrip!(OpenMontageArtifactPayload, $key, $value)
                }
                "OpenMontageCheckpoint" => check_roundtrip!(OpenMontageCheckpoint, $key, $value),
                "OpenMontageRuntimeAvailability" => {
                    check_roundtrip!(OpenMontageRuntimeAvailability, $key, $value)
                }
                "OpenMontageCapabilitySummary" => {
                    check_roundtrip!(OpenMontageCapabilitySummary, $key, $value)
                }
                "OpenMontageSetupOffer" => check_roundtrip!(OpenMontageSetupOffer, $key, $value),
                "OpenMontagePreflightSnapshot" => {
                    check_roundtrip!(OpenMontagePreflightSnapshot, $key, $value)
                }
                "OpenMontageProfessionalVideoRequest" => {
                    check_roundtrip!(OpenMontageProfessionalVideoRequest, $key, $value)
                }
                "OpenMontageError" => check_roundtrip!(OpenMontageError, $key, $value),
                "OpenMontageSubmitResponse" => {
                    check_roundtrip!(OpenMontageSubmitResponse, $key, $value)
                }
                "OpenMontageArtifact" => check_roundtrip!(OpenMontageArtifact, $key, $value),
                "OpenMontageStageCheckpoint" => {
                    check_roundtrip!(OpenMontageStageCheckpoint, $key, $value)
                }
                "OpenMontageDecision" => check_roundtrip!(OpenMontageDecision, $key, $value),
                "OpenMontageApprovalRequest" => {
                    check_roundtrip!(OpenMontageApprovalRequest, $key, $value)
                }
                "OpenMontageApprovalDecision" => {
                    check_roundtrip!(OpenMontageApprovalDecision, $key, $value)
                }
                "OpenMontageJobSnapshot" => check_roundtrip!(OpenMontageJobSnapshot, $key, $value),
                "OpenMontageJobEvent" => check_roundtrip!(OpenMontageJobEvent, $key, $value),
                "OpenMontageCallbackAck" => check_roundtrip!(OpenMontageCallbackAck, $key, $value),
                other => panic!(
                    "golden entry {} maps to unhandled type {:?}; add a dispatch arm \
                     (the test must cover every golden vector, not a subset)",
                    $key, other
                ),
            }
        };
    }

    let mut n_enum = 0usize;
    let mut n_msg = 0usize;

    for (key, value) in &golden {
        if key == ENUM_CARRIERS_KEY {
            continue;
        }
        if key.starts_with("Enum_") {
            // Enum carrier: resolve the carrier message type from metadata.
            let carrier = carriers
                .get(key)
                .and_then(|v| v.as_str())
                .unwrap_or_else(|| panic!("no __enum_carriers__ entry for {key}"));
            dispatch!(carrier, key.as_str(), value);
            n_enum += 1;
        } else {
            dispatch!(key.as_str(), key.as_str(), value);
            n_msg += 1;
        }
    }

    // 6 enum carriers + 32 messages = 38 vectors. Asserting the counts ensures
    // the golden wasn't truncated and that we actually exercised every entry.
    assert_eq!(
        n_enum, 6,
        "expected 6 enum-carrier golden vectors, exercised {n_enum}"
    );
    assert_eq!(
        n_msg, 32,
        "expected 32 message golden vectors, exercised {n_msg}"
    );
}
