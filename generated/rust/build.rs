use std::io::Result;

fn main() -> Result<()> {
    // Configure prost-build with serde support
    let mut config = prost_build::Config::new();
    
    // Add serde derives to all generated types (messages only, not enums)
    config.type_attribute("glance_mind.CrawlerTask", "#[derive(serde::Serialize, serde::Deserialize)]");
    config.type_attribute("glance_mind.CrawlerTaskMeta", "#[derive(serde::Serialize, serde::Deserialize)]");
    config.type_attribute("glance_mind.CrawlerTaskSpec", "#[derive(serde::Serialize, serde::Deserialize)]");
    config.type_attribute("glance_mind.TaskConfig", "#[derive(serde::Serialize, serde::Deserialize)]");
    config.type_attribute("glance_mind.TaskFilters", "#[derive(serde::Serialize, serde::Deserialize)]");
    config.type_attribute("glance_mind.DeviceCommentsQuery", "#[derive(serde::Serialize, serde::Deserialize)]");
    config.type_attribute("glance_mind.DeviceCommentsResponse", "#[derive(serde::Serialize, serde::Deserialize)]");
    config.type_attribute("glance_mind.CampaignConfig", "#[derive(serde::Serialize, serde::Deserialize)]");
    config.type_attribute("glance_mind.CommentData", "#[derive(serde::Serialize, serde::Deserialize)]");
    config.type_attribute("glance_mind.Pagination", "#[derive(serde::Serialize, serde::Deserialize)]");
    config.type_attribute("glance_mind.UpdateCommentStatusRequest", "#[derive(serde::Serialize, serde::Deserialize)]");
    config.type_attribute("glance_mind.UpdateCommentStatusResponse", "#[derive(serde::Serialize, serde::Deserialize)]");
    
    // DM types (from dm.proto)
    config.type_attribute("glance_mind.DmMessage", "#[derive(serde::Serialize, serde::Deserialize)]");
    config.type_attribute("glance_mind.ConversationMeta", "#[derive(serde::Serialize, serde::Deserialize)]");
    config.type_attribute("glance_mind.DmEvent", "#[derive(serde::Serialize, serde::Deserialize)]");
    config.type_attribute("glance_mind.ReplyCommand", "#[derive(serde::Serialize, serde::Deserialize)]");
    config.type_attribute("glance_mind.DeviceHeartbeat", "#[derive(serde::Serialize, serde::Deserialize)]");
    
    // Generate code from proto files
    config.compile_protos(
        &[
            "../../proto/common.proto",
            "../../proto/crawler_task.proto",
            "../../proto/device_comments.proto",
            "../../proto/dm.proto",
        ],
        &["../../proto/"],
    )?;
    
    Ok(())
}
