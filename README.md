# GlanceMind Protocol

集中管理 GlanceMind 系统中各工程之间的数据协议定义。

## 概述

本工程使用 **Protocol Buffers** 定义跨工程数据协议，并生成 Rust 和 Python 代码。
所有服务之间使用 **JSON** 格式进行数据交互（protobuf 结构 + JSON 序列化）。

### 协议类型

1. **Queue 协议** (Scheduler <-> Agent)
   - 通过 Redis Queue 传递的任务消息格式
   - 定义在 `proto/crawler_task.proto`

2. **REST 协议** (API <-> Executor)
   - REST API 请求/响应数据格式
   - 定义在 `proto/device_comments.proto`
   - 优化结构：campaign 配置提取，comments 作为数组

3. **Agent Task 协议** (API / Scheduler / Agent Service / Orchestrator)
   - 通用异步 agent 任务 envelope、事件和结果格式
   - 定义在 `proto/agent_task.proto`
   - `AgentTaskResult.texts` / `images` / `videos` 是 agent 的三类标准输出
   - `result_json` 保留为业务域兼容载荷，例如 social seed package 或 AIPub domain result

## 目录结构

```
glance_mind_protocol/
├── proto/                      # Protocol Buffers 定义
│   ├── common.proto            # 共享类型定义 (Platform, DataType, etc.)
│   ├── crawler_task.proto      # Scheduler -> Agent 队列消息
│   ├── agent_task.proto        # 通用异步 Agent Task 协议
│   └── device_comments.proto   # API -> Executor REST 响应
├── generated/
│   ├── rust/                   # 生成的 Rust 代码 (prost)
│   │   ├── Cargo.toml
│   │   ├── build.rs
│   │   └── src/lib.rs
│   └── python/                 # 生成的 Python 代码 (dataclasses)
│       ├── __init__.py
│       └── glance_mind.py
├── Makefile
└── README.md
```

## 使用方法

### 生成代码

```bash
# 生成所有语言的代码
make generate-all

# 仅生成 Rust 代码
make generate-rust

# 验证 Python 代码
make generate-python
```

### 验证 Proto 文件

```bash
make validate
```

### 同步到各工程

```bash
make sync
```

## 集成方式

### Rust (Scheduler / API)

```toml
# Cargo.toml
[dependencies]
glance_mind_protocol = { path = "../glance_mind_protocol/generated/rust" }
```

```rust
use glance_mind_protocol::{CrawlerTask, Platform, DataType};

// Serialize to JSON
let json = serde_json::to_string(&task)?;

// Deserialize from JSON
let task: CrawlerTask = serde_json::from_str(&json)?;
```

### Python (Agent / Executor)

```python
from protocol_gen import CrawlerTask, Platform, DataType

# Parse from dict/JSON
task = CrawlerTask.from_dict(data)
task = CrawlerTask.from_json(json_string)

# Serialize to dict/JSON
data = task.to_dict()
json_str = task.to_json()
```

## 协议详情

### CrawlerTask (Scheduler -> Agent)

```json
{
  "meta": {
    "task_id": 123,
    "source": "campaign-456",
    "timestamp": 1234567890.0
  },
  "spec": {
    "platform": "tiktok",
    "data_type": "video_comments"
  },
  "config": {
    "keywords": ["keyword1", "keyword2"],
    "max_count": 50,
    "search_offset": 0,
    "search_limit": 20,
    "filters": {
      "time_range": "last_180d",
      "region": "US"
    }
  }
}
```

### DeviceCommentsResponse (API -> Executor)

优化后的结构，campaign 配置只返回一次：

```json
{
  "campaign": {
    "campaign_id": 123,
    "auto_like": true,
    "auto_follow": false,
    "auto_dm": true,
    "auto_reply_comments": true,
    "auto_reply_post": false,
    "profile_name": "profile_1"
  },
  "comments": [
    {
      "id": 1,
      "comment_id": "comment_abc",
      "content_id": "video_xyz",
      "platform": "tiktok",
      "content": "Great video!",
      "status": "pending",
      "user_nickname": "user1",
      "suggested_reply": "Thanks!",
      "created_at": "2026-01-21T12:00:00Z"
    }
  ],
  "pagination": {
    "total": 100,
    "page": 1,
    "per_page": 20,
    "total_pages": 5
  }
}
```

## 枚举值映射

| 枚举 | 值 | 说明 |
|-----|---|------|
| Platform | reddit, tiktok, facebook, instagram, twitter, youtube | 平台 |
| DataType | video_content, video_metadata, video_comments, keyword_search | 数据类型 |
| TimeRange | all_time, last_24h, last_7d, last_30d, last_180d | 时间范围 |
| CommentStatus | pending, processing, completed | 评论状态 |

## 版本

当前版本: 1.0.0

协议变更请遵循语义化版本规范。
