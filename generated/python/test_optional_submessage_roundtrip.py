"""Round-trip tests for non-OpenMontage messages that embed an all-optional
sub-message which serializes (via _omit_none) to an empty dict ``{}``.

A truthiness guard (``if data.get("x"):``) in from_dict treats a present-but-empty
``{}`` as falsy and reads it back as ``None``, so ``from_dict(to_dict(x)) != x``.
The correct guard is presence (``is not None``): "key absent" (None) vs
"key present but empty" ({}). This is the same defect class fixed for the
OpenMontage messages in commit 61db8c8; these tests cover the remaining
non-OpenMontage parents (TaskConfig.filters, AiPubInput.default_images/account_images).
"""

import glance_mind as gm


def _roundtrips(obj):
    return type(obj).from_dict(obj.to_dict()) == obj


def test_taskconfig_empty_filters_roundtrips():
    obj = gm.TaskConfig(filters=gm.TaskFilters())  # all-None TaskFilters -> {}
    rt = gm.TaskConfig.from_dict(obj.to_dict())
    assert rt == obj, f"empty filters lost on round-trip: filters={rt.filters!r}"


def test_aipubinput_empty_default_images_roundtrips():
    obj = gm.AiPubInput(default_images=gm.AiPubImageConfig())  # all-None -> {}
    rt = gm.AiPubInput.from_dict(obj.to_dict())
    assert rt == obj, f"empty default_images lost on round-trip: {rt.default_images!r}"


def test_aipubinput_empty_account_images_roundtrips():
    obj = gm.AiPubInput(account_images={})  # present-but-empty map
    rt = gm.AiPubInput.from_dict(obj.to_dict())
    assert rt == obj, f"empty account_images lost on round-trip: {rt.account_images!r}"


def test_absent_submessages_stay_none():
    # Regression guard: the is-not-None fix must NOT turn genuinely-absent
    # optional sub-messages into empty instances (absent stays None).
    assert gm.TaskConfig.from_dict(gm.TaskConfig().to_dict()).filters is None
    assert gm.AiPubInput.from_dict(gm.AiPubInput().to_dict()).default_images is None
    assert gm.AiPubInput.from_dict(gm.AiPubInput().to_dict()).account_images is None
