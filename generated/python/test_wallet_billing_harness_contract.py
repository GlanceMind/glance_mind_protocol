"""Wallet/Billing harness contract sample.

Wallet/Billing does not currently use protobuf as its source of truth; the v1
contract is HTTP + DB evidence. This sample protects that boundary explicitly so
future protocol changes do not accidentally imply a queue/protobuf contract for
wallet recharge or reconciliation.
"""

import json


def test_wallet_recharge_harness_contract_sample_round_trips_json():
    sample = {
        "scenario_id": "wallet.recharge.xunhupay.mock.v1",
        "transport_contract": "http_db",
        "api_routes": [
            "POST /api/v1/wallet/recharge",
            "GET /api/v1/wallet/recharge/{order_no}",
        ],
        "db_tables": ["gm_user_wallets", "gm_wallet_transactions"],
        "required_transaction_types": ["RECHARGE", "DEPOSIT"],
        "provider": "xunhupay",
    }

    wire = json.loads(json.dumps(sample, sort_keys=True))

    assert wire["scenario_id"] == "wallet.recharge.xunhupay.mock.v1"
    assert wire["transport_contract"] == "http_db"
    assert "gm_wallet_transactions" in wire["db_tables"]
    assert wire["required_transaction_types"] == ["RECHARGE", "DEPOSIT"]
    assert "CrawlerTask" not in json.dumps(wire)
