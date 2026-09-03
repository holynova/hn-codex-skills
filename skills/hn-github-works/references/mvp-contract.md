# MVP 产品契约

## 推荐目录边界

沿用现有项目结构；绿地项目可采用以下职责分离：

```text
portfolio.config.json       # 可提交的扫描与导出配置，不含 token
data/generated.json         # 扫描生成，可安全重建
data/curation.json          # 人工校对，扫描不得覆盖
screenshots/                # 已接受的项目截图
.portfolio-cache/           # API/探测缓存，应加入 .gitignore
dist/                       # 静态站导出，可安全重建
```

不要把凭据存入以上文件。覆盖 `generated.json`、截图或 `dist/` 时使用同目录临时文件与原子替换。

## 核心数据对象

### repository

```json
{
  "id": "github:123456",
  "owner": "example",
  "name": "project",
  "fullName": "example/project",
  "url": "https://github.com/example/project",
  "description": "GitHub 原始描述",
  "readme": { "sourcePath": "README.md", "summary": "...", "status": "generated|manual|needs_review" },
  "primaryLanguage": "TypeScript",
  "topics": ["cli"],
  "fork": false,
  "archived": false,
  "updatedAt": "2026-01-01T00:00:00Z",
  "scannedAt": "2026-01-02T00:00:00Z"
}
```

### deployment

```json
{
  "repositoryId": "github:123456",
  "url": "https://example.github.io/project/",
  "source": "pages_api|homepage|convention|manual",
  "status": "verified|unreachable|invalid_url|skipped",
  "httpStatus": 200,
  "checkedAt": "2026-01-02T00:00:00Z",
  "error": null
}
```

### screenshot

```json
{
  "repositoryId": "github:123456",
  "deploymentUrl": "https://example.github.io/project/",
  "path": "screenshots/github-123456.webp",
  "status": "captured|failed|manual|skipped",
  "capturedAt": "2026-01-02T00:00:00Z",
  "error": null
}
```

### tag

```json
{
  "repositoryId": "github:123456",
  "value": "TypeScript",
  "kind": "language|topic|framework|category",
  "source": "github|package|readme|manual",
  "confidence": 1
}
```

### curation

```json
{
  "repositoryId": "github:123456",
  "approved": true,
  "hidden": false,
  "pinned": true,
  "order": 10,
  "title": "人工标题",
  "summary": "人工校对后的摘要",
  "category": "开发工具",
  "tags": ["CLI", "TypeScript"],
  "deploymentUrl": null,
  "screenshotPath": null
}
```

人工值覆盖自动值；`null` 表示没有人工覆盖，不表示删除自动值。需要显式清空时定义单独的清空语义并补测试。

## 状态与恢复

| 环节 | 必须保留的状态 | 恢复方式 |
| --- | --- | --- |
| GitHub 扫描 | 成功、跳过原因、限流、请求失败 | 缓存成功项，只重试失败项 |
| 部署验证 | verified、unreachable、invalid_url、skipped | 按 URL 或仓库重试 |
| 截图 | captured、failed、manual、skipped | 重试失败项或人工覆盖 |
| 摘要/分类 | generated、manual、needs_review | 人工校对优先 |
| 静态导出 | 成功或构建错误 | 保留上一次完整 dist，原子替换 |

批处理允许部分成功。最终报告应列出总数、成功数、跳过数、失败数、缓存命中数和每类失败原因。

## 权限与网络边界

- 默认仅读取公开 GitHub 元数据；私有仓库必须由用户明确授权。
- token 只从环境变量、系统凭据或已登录 CLI 读取，日志只显示是否存在及权限不足错误。
- 截图与页面探测默认拒绝 `localhost`、环回、RFC 1918 私网、链路本地、metadata 地址、非 HTTP(S) 协议及带嵌入式凭据的 URL。
- 解析每次重定向后的主机并再次执行网络边界检查，防止公开 URL 跳转到内网。
- 不执行仓库中的脚本来“修复”历史项目；只检查公开部署或用户明确允许启动的本地项目。
- 不自动写 GitHub 仓库设置、不推送、不发布、不删除远端资源。

## 最小验收矩阵

1. 多页仓库结果能完整扫描，fork 和 archived 默认被排除且可配置。
2. 标准 README 404 时能找到根目录 `README*`；没有 README 时记录明确跳过或降级原因。
3. 缓存命中不会发出重复请求；TTL 为 0 时可强制刷新。
4. 遇到速率限制时读取重置时间并有界等待或停止，不进行无限重试。
5. homepage 存在但不可访问时不会标记为 verified，也不会进入默认截图队列。
6. 私网 URL、危险重定向和路径穿越截图文件名被拒绝。
7. 单个截图失败不影响其他项目，并可仅重试失败项。
8. 自动摘要与标签保留来源；人工标题、摘要、标签、隐藏和置顶在重扫后不丢失。
9. 无仓库、无部署、无截图、全被筛选和部分失败都有可理解的 CLI 与页面状态。
10. 静态站不含 token、本机绝对路径或未转义的 README HTML，桌面端和移动端核心浏览可用。
