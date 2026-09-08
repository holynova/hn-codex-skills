---
name: hn-web-analytics
description: 为多个静态站点、Astro、React、Vue、Next.js 或其他前端网站接入集中式、隐私友好的 PV、UV、来源、设备、地域和自定义事件统计后台。用于用户要求增加网站访问统计、埋点、分析面板、跨站点数据汇总、分享/搜索/下载行为统计，或排查统计脚本未生效时。
---

# HN 网站数据统计

## 目标与默认方案

为一组网站建立一个集中式 Umami v3 统计实例，并在每个生产站点的根布局只接入一次 tracker。默认优先自托管 Umami + PostgreSQL：数据由用户控制、无 Cookie、脚本轻量，且一个后台可以管理多个 website；如果用户不想维护服务器，再改用 Umami Cloud。

统计后台要回答三类问题：

- **流量**：PV、UV（Umami 的匿名 unique visitors）、访问次数、跳出率、平均停留时间。
- **来源**：入口页、路径、来源站、UTM、设备、浏览器、操作系统、国家/地区。
- **产品行为**：搜索提交、结果打开、复制、下载、分享卡片打开/下载/系统分享等自定义事件。

详细字段、事件命名和部署建议见 [references/umami-implementation.md](references/umami-implementation.md)。

## 工作流

### 1. 盘点站点与目标

先检查当前项目的框架、根布局、部署域名、环境变量、是否是 SPA、是否已有 Google Analytics/Plausible/Umami，以及用户希望统计的关键动作。列出生产域名和预览域名，默认只把生产域名纳入正式统计。

不要把“UV”解释成可识别的真实用户数；它是统计系统按匿名标识计算的 unique visitors。不要采集搜索原文、姓名、邮箱、token、完整 URL 中的敏感 query 或其他个人数据。

### 2. 选择与配置 Umami

- 自托管时准备一个稳定的 `https://stats.example.com`，使用官方 Docker/PostgreSQL 方案，并单独保存管理员凭据、数据库凭据和备份策略。
- 在 Umami 中为每个生产站点创建一个 website，记录 `websiteId`、hostname 白名单和部署环境；不要在仓库提交管理员 token 或数据库密码。
- 如果已有集中式 Umami，不重复创建实例，先核对版本、数据保留、时区、权限和域名过滤。`hn-project-publisher` 的统一 Cloud website ID 属于其个人发布约定；该流程内复用它及既有实例，不因本 Skill 的自托管默认值而另建服务或替换 ID。用户明确要求迁移时再按迁移范围执行。
- 若用户只想快速试用，使用 Umami Cloud，但把 API key 留在服务端或 CI secret 中。

### 3. 接入根布局

在 Astro layout、React/Vite 根组件、Next.js layout、Vue/Nuxt app shell 或静态 HTML 的 `<head>` 中加入一次 tracker。推荐模式如下，替换为真实地址和 ID：

```html
<script
  defer
  src="https://stats.example.com/script.js"
  data-website-id="WEBSITE_UUID"
  data-domains="example.com,www.example.com"
></script>
```

脚本只加载一次；SPA 交给 Umami 监听 History API 自动记录导航，不要在每个 route effect 中再次手动发送 pageview。若项目有 CSP、广告拦截、路径前缀或自定义域名，按项目配置补充 `connect-src`、`script-src`、`data-host-url` 或反向代理。

### 4. 设计并加入事件

只为能影响产品判断的动作埋点，事件名使用稳定的 `snake_case` 或 `kebab-case`，不要把搜索原文作为 event name 或 event data。常用事件：

```js
umami.track("search_submit", { surface: "catalog", result_count: 12 });
umami.track("result_open", { result_id: "stable-id", position: 3 });
umami.track("copy_result", { result_id: "stable-id" });
umami.track("share_card_download", { result_id: "stable-id", format: "png" });
```

优先使用 `data-umami-event` 属性处理静态按钮，使用 `umami.track()` 处理动态结果。事件 data 只保留低敏感、低基数、可聚合字段；不要发送大段正文、用户输入、原始 URL query 或个人标识。

### 5. 验证数据链路

按以下顺序验证。先确定测试环境与 hostname 过滤：本地验证使用已有 staging website 或已授权的测试配置，不直接等待被生产白名单排除的 localhost 流量入库，也不为测试自动放开生产过滤。缺少后台访问时完成本地构建和请求检查，明确后台入库尚未验证；继续独立工作，不虚报端到端成功。

1. `npm run build` 或项目等价构建通过，tracker 位于最终 HTML/JS 的正确根布局。
2. 使用真实浏览器访问生产样式的本地站点，确认 tracker 请求返回 2xx，且无 CSP、CORS、404 或重复加载。
3. 在允许的测试域名中打开实际存在的路径并触发已实现的事件；有两个路径和两类事件时各验证两个，不为凑数量新增路由或埋点。查看对应 dashboard 的 PV/UV 和事件；若有限重试后仍未出现，检查请求、域名过滤和服务状态并报告未验证项，不无限等待。
4. 在 SPA 中前进、后退、刷新，确认导航不会产生重复 pageview。
5. 用桌面和窄移动端各验证一次；如果站点有分享卡片，同时验证 `share_card_open`、`share_card_download` 等事件。
6. 记录统计实例地址、website 列表、事件字典、验证时间和任何广告拦截/隐私限制。

### 6. 可选：读取自定义报表

只有在用户确实需要把多站点汇总到自己的门户时才调用 Umami API。API 请求必须在服务端、脚本或受保护的 CI 中完成；浏览器端不能暴露 Umami 管理 token。默认使用 dashboard，不为了显示一个 PV 卡片而重复实现统计后台。

## 完成标准

- 每个生产站点有明确的 website ID 和 hostname 过滤。
- tracker 在根布局加载一次，SPA 无重复 pageview。
- Umami 后台能看到 PV、UV 和至少一个事件；来源/设备等基础报表可用。
- 事件字典稳定、低敏感，没有搜索原文和个人数据泄露。
- 本地构建、真实浏览器请求、桌面/窄移动端均已验证。
- 报告中明确说明“已接入并验证”与“仅配置、尚未线上验证”的边界。
