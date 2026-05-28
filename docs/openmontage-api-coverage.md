# OpenMontage API Coverage Matrix

This document records the field-by-field compatibility audit between
`proto/openmontage.proto` and the current OpenMontage internal API surface.

Sources compared:

- OpenMontage tool contract: `tools/base_tool.py::BaseTool.get_info()`
- GlanceMind marketing pipeline: `pipeline_defs/glancemind-marketing-video.yaml`
- Checkpoint contract: `schemas/checkpoints/checkpoint.schema.json`
- Artifact contracts: `schemas/artifacts/*.schema.json`
- Provider tools used by the GlanceMind pipeline:
  `zhichuang_veo_video`, `laozhang_gpt_image_2`, `doubao_tts`,
  `subtitle_gen`, `video_compose`, `hyperframes_compose`,
  `deepseek_reviewer`, `visual_qa`, `audio_probe`, and `frame_sampler`

## Coverage Strategy

OpenMontage exposes JSON-schema-driven tools and artifacts. To avoid making the
protocol brittle every time a provider adds a parameter, the protocol now covers
the internal API in two layers:

- Typed envelope fields for stable orchestration concepts: jobs, events,
  approvals, preflight, tool contracts, tool invocations/results, pipeline
  manifests, checkpoints, and artifacts.
- Lossless JSON/schema fields for provider- and artifact-specific payloads:
  `input_schema_json`, `output_schema_json`, `artifact_schema_json`,
  `input_json`, `data_json`, `payload_json`, `raw_info_json`, and
  `OpenMontageSchemaField.path`.

That means every current internal field can either be represented as a typed
field or preserved losslessly in a JSON payload with its schema path.

## BaseTool.get_info Coverage

| OpenMontage field | Protocol field |
| --- | --- |
| `name` | `OpenMontageToolContract.name` |
| `version` | `OpenMontageToolContract.version` |
| `tier` | `OpenMontageToolContract.tier` |
| `capability` | `OpenMontageToolContract.capability` |
| `provider` | `OpenMontageToolContract.provider` |
| `stability` | `OpenMontageToolContract.stability` |
| `status` | `OpenMontageToolContract.status` |
| `execution_mode` | `OpenMontageToolContract.execution_mode` |
| `determinism` | `OpenMontageToolContract.determinism` |
| `runtime` | `OpenMontageToolContract.runtime` |
| `module_path` | `OpenMontageToolContract.module_path` |
| `usage_location` | `OpenMontageToolContract.usage_location` |
| `dependencies` | `OpenMontageToolContract.dependencies` |
| `install_instructions` | `OpenMontageToolContract.install_instructions` |
| `capabilities` | `OpenMontageToolContract.capabilities` |
| `input_schema` | `OpenMontageToolContract.input_schema_json` + `input_fields` |
| `output_schema` | `OpenMontageToolContract.output_schema_json` + `output_fields` |
| `artifact_schema` | `OpenMontageToolContract.artifact_schema_json` |
| `supports` | `OpenMontageToolContract.supports_json` |
| `best_for` | `OpenMontageToolContract.best_for` |
| `not_good_for` | `OpenMontageToolContract.not_good_for` |
| `provider_matrix` | `OpenMontageToolContract.provider_matrix_json` |
| `resource_profile.*` | `OpenMontageResourceProfile` |
| `resume_support` | `OpenMontageToolContract.resume_support` |
| `side_effects` | `OpenMontageToolContract.side_effects` |
| `fallback` | `OpenMontageToolContract.fallback` |
| `fallback_tools` | `OpenMontageToolContract.fallback_tools` |
| `agent_skills` | `OpenMontageToolContract.agent_skills` |
| `related_skills` | `OpenMontageToolContract.related_skills` |
| `user_visible_verification` | `OpenMontageToolContract.user_visible_verification` |
| `quality_score` | `OpenMontageToolContract.quality_score` |
| `historical_success_rate` | `OpenMontageToolContract.historical_success_rate` |
| `latency_p50_seconds` | `OpenMontageToolContract.latency_p50_seconds` |
| provider-specific extras | `OpenMontageToolContract.raw_info_json` |

## Tool Input Coverage

Each field below is covered by both:

- `OpenMontageToolContract.input_fields[].path` and `input_schema_json`
- `OpenMontageToolInvocation.input_json`

| Tool | Current input fields |
| --- | --- |
| `zhichuang_veo_video` | `aspect_ratio`, `dry_run`, `duration`, `idempotency_key`, `image_path`, `image_url`, `model`, `operation`, `output_path`, `poll_interval_seconds`, `prompt`, `reference_image_paths`, `reference_image_urls`, `request_timeout_seconds`, `resolution`, `size`, `timeout_seconds` |
| `laozhang_gpt_image_2` | `dry_run`, `idempotency_key`, `model`, `no_text`, `output_format`, `output_path`, `prompt`, `quality`, `size` |
| `doubao_tts` | `disable_markdown_filter`, `dry_run`, `enable_timestamp`, `format`, `metadata_path`, `output_path`, `poll_interval_seconds`, `resource_id`, `return_usage`, `sample_rate`, `speech_rate`, `text`, `timeout_seconds`, `voice_id` |
| `subtitle_gen` | `corrections`, `format`, `highlight_style`, `max_chars_per_line`, `max_words_per_cue`, `output_path`, `segments` |
| `video_compose` | `asset_manifest`, `audio_path`, `codec`, `crf`, `edit_decisions`, `input_path`, `narration_transcript_path`, `operation`, `options`, `output_path`, `overlays`, `preset`, `profile`, `proposal_packet`, `script_path`, `script_text`, `subtitle_path`, `subtitle_style` |
| `hyperframes_compose` | `asset_manifest`, `block_name`, `edit_decisions`, `fps`, `operation`, `output_path`, `playbook`, `profile`, `quality`, `skip_contrast`, `strict`, `workspace_path` |
| `deepseek_reviewer` | `artifact_text`, `dry_run`, `round`, `stage`, `system_prompt` |
| `visual_qa` | `checks`, `expected`, `input_path`, `operation`, `output_dir`, `timestamps` |
| `audio_probe` | `input_path` |
| `frame_sampler` | `count`, `format`, `input_path`, `interval_seconds`, `max_frames`, `output_dir`, `quality`, `scene_boundaries`, `strategy`, `timestamps` |

## Pipeline Manifest Coverage

| OpenMontage manifest field | Protocol field |
| --- | --- |
| `name` | `OpenMontagePipelineManifest.name` |
| `version` | `OpenMontagePipelineManifest.version` |
| `description` | `OpenMontagePipelineManifest.description` |
| `category` | `OpenMontagePipelineManifest.category` |
| `stability` | `OpenMontagePipelineManifest.stability` |
| `compatible_playbooks` | `compatible_playbooks` or `compatible_playbooks_json` |
| `required_skills` | `OpenMontagePipelineManifest.required_skills` |
| `stages[].name` | `OpenMontagePipelineStage.name` |
| `stages[].agent` | `OpenMontagePipelineStage.agent` |
| `stages[].skill` | `OpenMontagePipelineStage.skill` |
| `stages[].required_artifacts_in` | `OpenMontagePipelineStage.required_artifacts_in` |
| `stages[].optional_artifacts_in` | `OpenMontagePipelineStage.optional_artifacts_in` |
| `stages[].produces` | `OpenMontagePipelineStage.produces` |
| `stages[].preferred_tools` | `OpenMontagePipelineStage.preferred_tools` |
| `stages[].fallback_tools` | `OpenMontagePipelineStage.fallback_tools` |
| `stages[].required_tools` | `OpenMontagePipelineStage.required_tools` |
| `stages[].optional_tools` | `OpenMontagePipelineStage.optional_tools` |
| `stages[].tools_available` | `OpenMontagePipelineStage.tools_available` |
| `stages[].review_focus` | `OpenMontagePipelineStage.review_focus` |
| `stages[].checkpoint_required` | `OpenMontagePipelineStage.checkpoint_required` |
| `stages[].human_approval_default` | `OpenMontagePipelineStage.human_approval_default` |
| `stages[].success_criteria` | `OpenMontagePipelineStage.success_criteria` |
| `stages[].sub_stages.*` | `OpenMontagePipelineSubStage` |
| `default_checkpoint_policy` | `OpenMontagePipelineManifest.default_checkpoint_policy` |
| `reference_input.*` | `OpenMontageReferenceInputConfig` |
| `orchestration.*` | `OpenMontagePipelineOrchestration` |
| `extensions.*` | `OpenMontageExtensionPermissions` |
| `metadata` | `OpenMontagePipelineManifest.metadata_json` |
| full source manifest | `OpenMontagePipelineManifest.raw_manifest_json` |

## Checkpoint Coverage

| OpenMontage checkpoint field | Protocol field |
| --- | --- |
| `version` | `OpenMontageCheckpoint.version` |
| `project_id` | `OpenMontageCheckpoint.project_id` |
| `pipeline_type` | `OpenMontageCheckpoint.pipeline_type` |
| `stage` | `OpenMontageCheckpoint.stage` |
| `status` | `OpenMontageCheckpoint.status` |
| `timestamp` | `OpenMontageCheckpoint.timestamp` |
| `style_playbook` | `OpenMontageCheckpoint.style_playbook` |
| `checkpoint_policy` | `OpenMontageCheckpoint.checkpoint_policy` |
| `human_approval_required` | `OpenMontageCheckpoint.human_approval_required` |
| `human_approved` | `OpenMontageCheckpoint.human_approved` |
| `artifacts` | `OpenMontageCheckpoint.artifacts` + `artifacts_json` |
| `review` | `OpenMontageCheckpoint.review_json` |
| `cost_snapshot` | `OpenMontageCheckpoint.cost_snapshot_json` |
| `error` | `OpenMontageCheckpoint.error` |
| `metadata` | `OpenMontageCheckpoint.metadata_json` |

## Artifact Coverage

Every artifact schema is transported by `OpenMontageArtifactPayload`:

- `artifact_name`: schema/artifact key, such as `proposal_packet`
- `schema_id` and `schema_version`: schema identity
- `payload_json`: full artifact JSON, preserving all nested fields
- `schema_fields`: flattened field paths such as
  `production_plan.render_runtime` or `checks.provider_boundary.providers[].status`
- `validated` and `validation_error`: result of local OpenMontage schema validation

The audited artifact top-level fields are:

| Artifact | Top-level fields |
| --- | --- |
| `action_timeline` | `version`, `fps`, `scenes`, `metadata` |
| `asset_manifest` | `version`, `assets`, `total_cost_usd`, `metadata` |
| `brief` | `version`, `title`, `hook`, `key_points`, `core_message`, `cta`, `tone`, `style`, `target_audience`, `target_platform`, `target_duration_seconds`, `reference_material`, `angle_options`, `selected_angle`, `metadata` |
| `cost_log` | `version`, `budget_total_usd`, `budget_reserved_usd`, `budget_spent_usd`, `entries`, `metadata` |
| `decision_log` | `version`, `project_id`, `decisions` |
| `edit_decisions` | `version`, `cuts`, `overlays`, `audio`, `subtitles`, `music`, `transitions`, `renderer_family`, `render_runtime`, `slideshow_risk_score`, `metadata` |
| `final_review` | `version`, `output_path`, `status`, `checks`, `issues_found`, `recommended_action`, `metadata` |
| `proposal_packet` | `version`, `concept_options`, `selected_concept`, `production_plan`, `cost_estimate`, `approval`, `metadata` |
| `publish_log` | `version`, `entries`, `metadata` |
| `render_report` | `version`, `outputs`, `render_time_seconds`, `warnings`, `verification_notes`, `render_grammar`, `slideshow_risk_score`, `decision_log_ref`, `final_review_ref`, `metadata` |
| `research_brief` | `version`, `topic`, `research_date`, `landscape`, `trending`, `data_points`, `audience_insights`, `expert_voices`, `angles_discovered`, `visual_references`, `sources`, `research_summary`, `metadata` |
| `review` | `version`, `stage`, `decision`, `round`, `findings`, `metadata` |
| `scene_plan` | `version`, `style_playbook`, `scenes`, `metadata` |
| `script` | `version`, `title`, `total_duration_seconds`, `sections`, `metadata` |
| `source_media_review` | `version`, `files`, `summary`, `planning_implications`, `metadata` |
| `video_analysis_brief` | `version`, `source`, `content_analysis`, `structure_analysis`, `style_profile`, `narration_transcript`, `replication_guidance`, `keyframes` |

Character-animation artifacts (`character_design`, `rig_plan`, `pose_library`,
`action_timeline`, and `character_qa_report`) are covered by the same
`OpenMontageArtifactPayload` mechanism.

