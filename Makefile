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

# Sync generated code to consumer projects
sync: generate-all
	@echo "Syncing to Scheduler (inline version)..."
	@mkdir -p ../glance_mind_worker/glance_mind_scheduler/src/protocol_gen
	@cp generated/rust/src/lib_inline.rs ../glance_mind_worker/glance_mind_scheduler/src/protocol_gen/mod.rs
	@echo "Syncing to Agent (Python)..."
	@mkdir -p ../glance_mind_worker/glance_mind_agent/src/protocol_gen
	@cp generated/python/glance_mind.py ../glance_mind_worker/glance_mind_agent/src/protocol_gen/
	@cp generated/python/__init__.py ../glance_mind_worker/glance_mind_agent/src/protocol_gen/
	@echo "Syncing to Agent-RS (Rust)..."
	@mkdir -p ../glance_mind_agent_rs/src/protocol_gen
	@cp generated/rust/src/lib_inline.rs ../glance_mind_agent_rs/src/protocol_gen/mod.rs
	@echo "Syncing to Executor..."
	@mkdir -p ../glance_mind_worker/glance_mind_executor/protocol_gen
	@cp generated/python/glance_mind.py ../glance_mind_worker/glance_mind_executor/protocol_gen/
	@cp generated/python/__init__.py ../glance_mind_worker/glance_mind_executor/protocol_gen/
	@echo "Syncing to Rust API (inline version)..."
	@mkdir -p ../glance_mind_rust/crates/api/src/protocol_gen
	@cp generated/rust/src/lib_inline.rs ../glance_mind_rust/crates/api/src/protocol_gen/mod.rs
	@echo "✓ Code synced to all projects"

# Sync only (without regenerating)
sync-only:
	@echo "Syncing existing generated code..."
	@mkdir -p ../glance_mind_worker/glance_mind_scheduler/src/protocol_gen
	@cp generated/rust/src/lib_inline.rs ../glance_mind_worker/glance_mind_scheduler/src/protocol_gen/mod.rs
	@mkdir -p ../glance_mind_worker/glance_mind_agent/src/protocol_gen
	@cp generated/python/glance_mind.py ../glance_mind_worker/glance_mind_agent/src/protocol_gen/
	@cp generated/python/__init__.py ../glance_mind_worker/glance_mind_agent/src/protocol_gen/
	@mkdir -p ../glance_mind_agent_rs/src/protocol_gen
	@cp generated/rust/src/lib_inline.rs ../glance_mind_agent_rs/src/protocol_gen/mod.rs
	@mkdir -p ../glance_mind_worker/glance_mind_executor/protocol_gen
	@cp generated/python/glance_mind.py ../glance_mind_worker/glance_mind_executor/protocol_gen/
	@cp generated/python/__init__.py ../glance_mind_worker/glance_mind_executor/protocol_gen/
	@mkdir -p ../glance_mind_rust/crates/api/src/protocol_gen
	@cp generated/rust/src/lib_inline.rs ../glance_mind_rust/crates/api/src/protocol_gen/mod.rs
	@echo "✓ Code synced"

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
