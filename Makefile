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

# Sync generated code to all consumer projects.
#
# Each consumer vendors its own copy of this crate to keep its repo
# self-contained (no cross-repo Cargo path-dep, no special Docker/CI
# vendoring, no access tokens required). Run this after modifying any
# .proto file.
#
# Consumers:
#   - glance_mind_rust    vendor/glance_mind_protocol/           (Rust)
#   - glance_mind_worker  glance_mind_scheduler/vendor/...       (Rust)
#   - glance_mind_worker  glance_mind_executor/protocol_gen/     (Python)
RUST_CONSUMERS := \
	../glance_mind_rust/vendor/glance_mind_protocol \
	../glance_mind_worker/glance_mind_scheduler/vendor/glance_mind_protocol

sync: generate-all sync-rust sync-python
	@echo ""
	@echo "✓ Synced protocol to all consumer projects."
	@echo "  Run 'cargo build' in each Rust consumer to regenerate types."

# Sync generated Rust crate (proto/ + generated/rust/) into every consumer
sync-rust:
	@for dest in $(RUST_CONSUMERS); do \
		echo "Syncing Rust protocol crate to $$dest ..."; \
		mkdir -p $$dest/generated; \
		rsync -a --delete --exclude=target --exclude=Cargo.lock \
			generated/rust/ $$dest/generated/rust/; \
		rsync -a --delete proto/ $$dest/proto/; \
	done
	@echo "✓ Rust protocol crate synced to consumers"

# Sync generated Python code to Executor
sync-python:
	@echo "Syncing Python types to Executor..."
	@mkdir -p ../glance_mind_worker/glance_mind_executor/protocol_gen
	@cp generated/python/glance_mind.py ../glance_mind_worker/glance_mind_executor/protocol_gen/
	@cp generated/python/__init__.py ../glance_mind_worker/glance_mind_executor/protocol_gen/
	@echo "✓ Python code synced to executor"

# Sync without regenerating (use when generated/ is already up to date)
sync-only: sync-rust sync-python
	@echo "✓ Synced existing generated code to consumers"

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
