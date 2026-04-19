# GlanceMind Protocol Makefile
# Generates and manages protocol definitions for cross-service communication
# Protocol definitions are in proto/*.proto (Protocol Buffers)

.PHONY: all generate-all generate-rust generate-python validate sync clean help

# Default target
all: generate-all

# Generate code for all languages
generate-all: generate-rust generate-python
	@echo "✓ All code generated successfully"

# Generate Rust code (uses prost-build via cargo build)
generate-rust:
	@echo "Generating Rust code..."
	@cd generated/rust && cargo build --quiet
	@echo "✓ Rust code generated and verified"

# Generate Python code (note: Python code is manually maintained for better JSON compat)
generate-python:
	@echo "Verifying Python code..."
	@cd generated/python && python3 -c "from glance_mind import *; print('Import OK')"
	@echo "✓ Python code verified"

# Validate proto files syntax
validate:
	@echo "Validating proto files..."
	@protoc -I=proto --descriptor_set_out=/dev/null proto/*.proto
	@echo "✓ All proto files valid"

# Sync generated PYTHON code to consumer projects.
#
# v2 cutover: Rust consumers now use Cargo path-dep on this crate
# (`glance_mind_protocol = { path = "../glance_mind_protocol/generated/rust" }`)
# so they auto-pick up prost-generated types via cargo build. Only Python
# still needs explicit sync (manually maintained — no Python codegen).
sync: generate-all
	@echo "Syncing Python types to Executor..."
	@mkdir -p ../glance_mind_worker/glance_mind_executor/protocol_gen
	@cp generated/python/glance_mind.py ../glance_mind_worker/glance_mind_executor/protocol_gen/
	@cp generated/python/__init__.py ../glance_mind_worker/glance_mind_executor/protocol_gen/
	@echo "✓ Python code synced to executor"
	@echo ""
	@echo "Note: Rust consumers (api / scheduler / agent_rs) auto-pick up"
	@echo "      types via Cargo path-dep on this crate — no copy needed."
	@echo "      Run 'cargo build' in each consumer to regenerate."

# Sync Python only (without regenerating)
sync-only:
	@echo "Syncing existing Python code..."
	@mkdir -p ../glance_mind_worker/glance_mind_executor/protocol_gen
	@cp generated/python/glance_mind.py ../glance_mind_worker/glance_mind_executor/protocol_gen/
	@cp generated/python/__init__.py ../glance_mind_worker/glance_mind_executor/protocol_gen/
	@echo "✓ Python code synced"

# Clean generated files (be careful!)
clean:
	@echo "Cleaning Rust build artifacts..."
	@cd generated/rust && cargo clean
	@echo "✓ Cleaned"

# Show help
help:
	@echo "GlanceMind Protocol Makefile (Protocol Buffers)"
	@echo ""
	@echo "Usage:"
	@echo "  make              - Generate all code (default)"
	@echo "  make generate-all - Generate Rust and Python code"
	@echo "  make generate-rust   - Generate/verify Rust code"
	@echo "  make generate-python - Verify Python code"
	@echo "  make validate     - Validate proto files syntax"
	@echo "  make sync         - Regenerate and sync to consumer projects"
	@echo "  make sync-only    - Sync existing code without regenerating"
	@echo "  make clean        - Remove build artifacts"
	@echo "  make help         - Show this help message"
	@echo ""
	@echo "Project structure:"
	@echo "  proto/            - Protocol Buffers definitions"
	@echo "    common.proto    - Shared types (Platform, DataType, etc.)"
	@echo "    crawler_task.proto    - Scheduler <-> Agent queue messages"
	@echo "    device_comments.proto - API <-> Executor REST responses"
	@echo "    aipub.proto     - AI Publish types (AiPubInput, AiPubImageConfig)"
	@echo "    dm.proto        - DM group control (NATS JetStream messages)"
	@echo "    patrol.proto    - Patrol stats types (NATS JetStream messages)"
	@echo "  generated/rust/   - Generated Rust code (prost)"
	@echo "  generated/python/ - Generated Python code (dataclasses)"
