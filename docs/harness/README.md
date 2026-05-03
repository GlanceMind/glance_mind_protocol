# Protocol Harness

`glance_mind_protocol` owns cross-language wire compatibility. Harness changes
in this repository should prefer `contract_static` checks first.

Use:

- `make validate`
- Python protobuf JSON roundtrip tests under `generated/python/`

Do not run sync/codegen commands unless the proto definition is intentionally
changed in the same task.
