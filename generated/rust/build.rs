use std::io::Result;

fn main() -> Result<()> {
    let mut config = prost_build::Config::new();

    // Apply serde derives to MESSAGE types only.
    // Enums are excluded because lib.rs has manual `impl Serialize/Deserialize`
    // for Platform / DataType / TimeRange / CommentStatus that emit
    // lowercase string variants ("tiktok") instead of prost's default
    // SCREAMING_SNAKE_CASE int repr.
    //
    // Auto-generated message list extracted from `rg "^message" proto/*.proto`.
    // Adding a new message in proto: append it here.
    let messages = [
        // common.proto: (no top-level messages)
        // crawler_task.proto
        "CrawlerTask",
        "CrawlerTaskMeta",
        "CrawlerTaskSpec",
        "TaskConfig",
        "TaskFilters",
        // device_comments.proto
        "DeviceCommentsQuery",
        "DeviceCommentsResponse",
        "CampaignConfig",
        "CommentData",
        "Pagination",
        "UpdateCommentStatusRequest",
        "UpdateCommentStatusResponse",
        // dm.proto
        "DmMessage",
        "ConversationMeta",
        "DmEvent",
        "ReplyCommand",
        "DeviceHeartbeat",
        // patrol.proto
        "AccountStats",
        "AccountPatrolStats",
        "PatrolReport",
        "PatrolConfig",
        // aipub.proto v1 (kept for legacy migration / executor compat)
        "AiPubImageConfig",
        "ReferenceVideoConfig",
        "VideoGenerationConfig",
        "ViduVideoConfig",
        "SeedanceVideoConfig",
        "AiTaskInput",
        "AiTaskResult",
        "ContentVariation",
        "AiPubTaskContent",
        "RedditPostConfig",
        "AiPubInput",
        "UploadTaskMessage",
        "UploadTaskMeta",
        "RedditPublishContent",
        "ExecutorPublishTask",
        "AccountGroomingTaskContent",
        "ExecutorTaskStatusUpdate",
        // aipub.proto v2 — unified content schema
        "MediaItem",
        "TextBlock",
        "LinkItem",
        "EntityTag",
        "UserMention",
        "PublishBehavior",
        "PublishSchedule",
        "PostPublishAction",
        "UnifiedPublishContent",
        "MediaPublishResult",
        "PostPublishActionResult",
        "PublishMetrics",
        "UnifiedPublishResult",
        "TextGenerationSpec",
        "ImageGenerationSpec",
        "VideoGenerationSpec",
        "UnifiedAiPubInput",
        "AccountMediaOverride",
    ];
    for m in messages {
        config.type_attribute(
            format!(".glance_mind.{}", m),
            "#[derive(serde::Serialize, serde::Deserialize)]",
        );
    }

    // Generate code from proto files. v2 cutover adds aipub.proto +
    // patrol.proto to the prost pipeline (previously hand-mirrored in
    // the now-deleted lib_inline.rs).
    config.compile_protos(
        &[
            "../../proto/common.proto",
            "../../proto/crawler_task.proto",
            "../../proto/device_comments.proto",
            "../../proto/dm.proto",
            "../../proto/aipub.proto",
            "../../proto/patrol.proto",
        ],
        &["../../proto/"],
    )?;

    Ok(())
}
