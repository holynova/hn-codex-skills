# Umami 实现参考

本文件只在实际接入、排错或需要自定义报表时读取。默认方案是 Umami v3；执行前仍应核对当前实例版本和官方文档。

## 方案边界

| 决策 | 默认做法 | 原因 |
| --- | --- | --- |
| 统计平台 | 一个 Umami 实例管理多个 website | 适合一组静态站和前端工具，共用 dashboard 与权限 |
| 部署 | 自托管 Umami + PostgreSQL | 数据留在自己的基础设施，避免每个项目各自维护一套统计后端 |
| 快速试用 | Umami Cloud | 省去服务器和数据库维护，但依赖托管服务与配额 |
| 数据范围 | PV、UV、访问次数、跳出率、停留时间、来源、路径、设备和自定义事件 | 覆盖基础产品判断，不复制完整广告追踪体系 |
| 用户身份 | 匿名 unique visitor/session | 不把 UV 包装成真实身份识别，也不主动收集姓名、邮箱或搜索原文 |
| 自定义总览 | 先用 Umami dashboard；跨站汇总再用受保护 API | 避免为简单需求造一个新的后台前端 |

## 站点清单

建议在项目或私有运维记录中维护如下表，不要把密码和 API key 放入公开仓库：

```text
| project | production hostnames | website id | environment | events | last verified |
|---------|----------------------|------------|-------------|--------|---------------|
| catalog | example.com,www.example.com | UUID | production | search_submit,result_open | 2026-08-01 |
```

预览域名、localhost 和临时部署默认不进正式数据；如果必须测试，使用单独的 staging website 或临时 domain allowlist。

## 集成模板

静态 HTML、Astro、React/Vite 等项目通常可以把下列脚本放在根 layout 的 `<head>`：

```html
<script
  defer
  src="https://stats.example.com/script.js"
  data-website-id="WEBSITE_UUID"
  data-domains="example.com,www.example.com"
></script>
```

如果 tracker 由自定义域名或反向代理提供，核对脚本实际地址和事件上报地址；不要让 script 成功加载但 `send` 请求仍指向错误主机。Next.js 使用框架推荐的 Script 组件，且只在 root layout 渲染一次。

### SPA 规则

Umami tracker 会观察 History API 和 `popstate`。因此：

- 不要在 React `useEffect`、Vue `onMounted` 或路由 watcher 中无条件调用 `umami.track()` 记录 pageview。
- 检查 hash routing 是否需要保留 hash；如果 URL 可能含敏感内容，排除 query/hash 或在应用侧传递干净路径。
- 对于手动控制 pageview 的场景，明确设置 `data-auto-track="false"`，再在受控的 route-change 处调用一次，不要混用两套机制。

## 事件字典

事件名要代表动作，不要代表用户输入内容。推荐字段如下：

| 事件 | 低敏感字段 | 不要发送 |
| --- | --- | --- |
| `search_submit` | `surface`, `result_count`, `filter_count` | 搜索原文、完整 query string |
| `result_open` | `result_id`, `position`, `surface` | 结果中可能含个人信息的长文本 |
| `copy_result` | `result_id`, `surface` | 剪贴板内容 |
| `download_result` | `result_id`, `format` | 用户生成的文件原文 |
| `share_card_open` | `result_id`, `scope` (`result`/`site`) | 私密结果内容 |
| `share_card_download` | `result_id`, `format` (`png`) | 图片二进制、分享者身份 |
| `share_card_native` | `result_id`, `has_file` | 联系人、系统分享目标 |
| `share_link_copy` | `result_id`, `scope` | 完整私有链接 |

HTML 静态按钮可以使用：

```html
<button
  data-umami-event="share_card_open"
  data-umami-event-scope="result"
  data-umami-event-result_id="stable-id"
>
  分享卡
</button>
```

动态组件使用：

```js
window.umami?.track("result_open", {
  result_id: result.id,
  position: index + 1,
  surface: "catalog",
});
```

## 自定义报表 API

Umami v3 的网站统计接口包括 `/api/websites/:websiteId/stats`、`/pageviews`、`/metrics` 和事件统计接口。典型返回字段包含 `pageviews`、`visitors`、`visits`、`bounces` 和 `totaltime`。

服务端读取示意：

```js
const response = await fetch(
  `${UMAMI_URL}/api/websites/${websiteId}/stats?startAt=${startAt}&endAt=${endAt}`,
  { headers: { Authorization: `Bearer ${process.env.UMAMI_TOKEN}` } },
);
if (!response.ok) throw new Error(`Umami request failed: ${response.status}`);
const stats = await response.json();
```

不要把 `UMAMI_TOKEN`、管理员密码或 Cloud API key 编译进浏览器 bundle。若网页需要展示数据，增加自己的服务端代理、最小权限接口、缓存和速率限制，并只返回必要的聚合字段。

## 排错清单

1. 查看最终 HTML，确认 script 只出现一次、`data-website-id` 非空且不是 staging ID。
2. 浏览器 Network 过滤 `script.js` 和 `/api/send`，检查状态码、请求主机、CSP 和 blocked by client。
3. 检查网站 hostname allowlist、时区和 Umami 实例时间；不要用浏览器 console 中的“脚本加载成功”替代事件入库验证。
4. SPA 只做一次路径切换，分别对比 dashboard 的 pageview 增量，排除重复 route effect。
5. 事件验证既要看 dashboard 事件数，也要检查 event data 字段是否符合低敏感契约。
6. 如果启用广告拦截器或隐私浏览器，记录它对采样结果的影响；不要以一台浏览器的 PV 作为绝对访问量。

## 官方参考

- [Umami Introduction](https://docs.umami.is/docs)
- [Collect data](https://docs.umami.is/docs/collect-data)
- [Tracker configuration](https://docs.umami.is/docs/tracker-configuration)
- [Track single-page apps](https://docs.umami.is/docs/guides/track-single-page-apps)
- [Tracker functions](https://docs.umami.is/docs/tracker-functions)
- [Website statistics API](https://docs.umami.is/docs/api/website-stats)
