# Image Provider Parameter Matrix

**Status:** Active — single source of truth for image provider passthrough.
**Consumers:** `glance_mind_scheduler/src/image_providers/*`,
`glance_mind_scheduler/tests/image_providers_live_test.rs`,
`glance_mind_rust/crates/api/src/service/image_generation_validation.rs`,
`glance_mind_front/src/components/aipub/ImageGenerationConfig.tsx`.

> **Strong rule.** Any change here MUST be accompanied by:
>
> 1. A matching update to the affected provider client in `image_providers/`
> 2. A matching update to `ExpectMatrix::*()` fixtures
> 3. A successful **live** run of the affected route(s) (Phase 8.2 / `image_smoke_test`)
>
> Any new provider parameter starts as a documented row here, then gets
> wired through validation -> client -> fixture -> live test, in that order.

---

## Table A — Provider HTTP field mapping (4 columns × 8 routes)

The 4 columns are the four provider-mode combinations we currently ship.
Pro vs Max for Flux and 4.0 vs 4.5 for SeeDream share the **same** column —
they differ only in the `model` string (see Table B).

> **Important — `extra_body` is a Python SDK convention.** OpenAI's Python
> client offers an `extra_body=` kwarg that gets **flattened into the
> top-level JSON body** before transport. When we hit LaoZhang directly with
> raw HTTP, we MUST put Flux knobs at the **top level** of the body / form,
> not nested inside an `"extra_body": { ... }` object. Sending the wrapped
> shape causes LaoZhang to silently fall back to model defaults (e.g. it
> returned 1024×1024 instead of the requested `aspect_ratio=16:9` until we
> fixed this).

| `ImageGenRequest` field           | Flux T2I (json, top-level)     | Flux Edit (multipart, top-level)   | SeeDream T2I (json)         | SeeDream Edit (json)        |
| --------------------------------- | ------------------------------ | ---------------------------------- | --------------------------- | --------------------------- |
| `prompt`                          | `top.prompt`                   | `form.prompt`                      | `top.prompt`                | `top.prompt`                |
| `model_key`                       | `top.model`                    | `form.model`                       | `top.model`                 | `top.model`                 |
| `reference_image_urls` (>=1, edit required) | —                    | `form.image` (downloaded + stitched bytes when N>1) | —                | `top.image` (string for N=1, JSON array for N>=2; truncated at 10) |
| `width_px` / `height_px`          | — (Flux uses `aspect_ratio`)   | `form.size = "{w}x{h}"`            | `top.size = "{w}x{h}"`      | `top.size = "{w}x{h}"`      |
| `aspect_ratio`                    | `top.aspect_ratio` (clamped to `[3:7, 7:3]`, downgrade to `1:1`) | `form.aspect_ratio` | — (advisory; emit WARN if no width/height set) | — (advisory) |
| size **default** when none set    | `1:1`                          | `1024x1024`                        | `2K`                        | `2K`                        |
| `seed`                            | `top.seed`                     | `form.seed`                        | — (silently dropped + WARN) | — (silently dropped + WARN) |
| `output_format` (`jpeg` / `png`)  | `top.output_format`            | `form.output_format`               | — (default `jpeg`)          | — (default `jpeg`)          |
| `safety_tolerance`                | `top.safety_tolerance` (default 2, clamped to 6) | `form.safety_tolerance` | — (silently dropped + WARN) | — (silently dropped + WARN) |
| `extras["prompt_upsampling"]`     | `top.prompt_upsampling` (coerced to bool) | `form.prompt_upsampling` | — (ignored)                  | — (ignored)                  |
| `watermark` (bool)                | — (ignored)                    | — (ignored)                        | `top.watermark`             | `top.watermark`             |
| `extras["sequential_image_generation"]` | — (ignored)              | — (ignored)                        | `top.sequential_image_generation` (default `disabled`) | `top.sequential_image_generation` |
| `response_format`                 | hard-coded `"url"`             | hard-coded `"url"`                 | hard-coded `"url"`          | hard-coded `"url"`          |
| `n` / `count`                     | `top.n = 1` (count loops in scheduler) | `form.n = 1`               | `top.n` not set; provider returns 1 | same                |
| `extras` other keys (whitelist)   | flattened into top-level for `prompt_upsampling`, `guidance_scale`, `negative_prompt` | same (multipart fields) | merged into top-level for `sequential_image_generation`, `stream`, `negative_prompt` | same |
| **NEVER appears**                 | `extra_body`                   | `extra_body`                       | n/a                         | n/a                         |
| HTTP method + path                | `POST /v1/images/generations`  | `POST /v1/images/edits`            | `POST /v1/images/generations` | `POST /v1/images/generations` |
| HTTP `Content-Type`               | `application/json`             | `multipart/form-data`              | `application/json`          | `application/json`          |
| HTTP `Authorization`              | `Bearer ${LAOZHANG_API_KEY}`   | `Bearer ${LAOZHANG_API_KEY}`       | `Bearer ${LAOZHANG_API_KEY}` | `Bearer ${LAOZHANG_API_KEY}` |

**Blacklist** (rejected at API validation, stripped at client level): `api_key`,
`authorization`, `base_url`, `n`, `response_format`. These cannot be set via
`extras` — defense in depth so a malformed plan can never pin a wrong API key
or override response shape.

---

## Table B — Routes (model × mode = live test enumeration)

These rows drive `glance_mind_scheduler/tests/image_providers_live_test.rs`
and `cargo run --bin image_smoke_test`. Adding a row = adding a `Route` enum
variant + an `ExpectMatrix` fixture + a `#[ignore]` test.

| # | model_key                | mode             | provider | unit price | refs | notes |
|---|--------------------------|------------------|----------|------------|------|-------|
| 1 | `flux-kontext-pro`       | text_to_image    | Flux     | $0.035     | 0    | default cheap baseline |
| 2 | `flux-kontext-pro`       | image_edit       | Flux     | $0.035     | 1    | single-ref edit path |
| 3 | `flux-kontext-max`       | text_to_image    | Flux     | $0.07      | 0    | Max-tier T2I |
| 4 | `flux-kontext-max`       | image_edit       | Flux     | $0.07      | 2    | **multi-ref stitch path** |
| 5 | `seedream-4-0-250828`    | text_to_image    | SeeDream | $0.035     | 0    | |
| 6 | `seedream-4-0-250828`    | image_edit       | SeeDream | $0.035     | 1    | |
| 7 | `seedream-4-5-251128`    | text_to_image    | SeeDream | $0.045     | 0    | newer model |
| 8 | `seedream-4-5-251128`    | image_edit       | SeeDream | $0.045     | 5    | **multi-ref array path** |
|   | **TOTAL**                |                  |          | **$0.37 / full run** | | |

`LIVE_PROVIDERS` env filters which rows run:

- `LIVE_PROVIDERS=seedream-4-0-250828` → rows 5+6 only (~$0.07)
- `LIVE_PROVIDERS=flux-kontext-pro,seedream-4-0-250828` → rows 1, 2, 5, 6 (~$0.14)
- unset → all 8 rows (~$0.37)

---

## Persistence flow

After every successful provider call, the scheduler invokes
`OssUploader::persist_image()` with:

- `temp_url` from `ImageGenResponse.upstream_url`
- path scheme `aipub/images/user_{user_id}/plan_{plan_id}/{ts}_{ai_task_id}_var_{i}_{uuid8}.{ext}`
- `Content-Type` resolved from upstream response header, falling back to the
  `output_format` hint (jpeg/png/webp), final fallback `image/png`
- one immediate retry on transient failure
- on hard failure, returns Err → scheduler falls back to the upstream URL
  (logs WARN with 10-minute expiry caveat)

Only the resulting OSS permanent URL ever lands in `aipub_task.content.image_urls`.
