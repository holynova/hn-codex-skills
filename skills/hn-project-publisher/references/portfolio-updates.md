# 作品集收录与 Cloudflare 发布

主入口为 `https://xiaosang.cc/`，源码仓库仍叫 `holynova/holynova.github.io`。项目 Worker 与作品集 Worker 各自部署；只推送 GitHub 或完成项目部署均不表示作品集已经更新。

已发布项目先检查现有收录与线上内容。条目、截图和链接均准确且线上与 master 一致时，复用现状并跳过本参考的写入/部署步骤。只修复实际缺口；仓库已正确但线上落后时仅补部署，不制造重复提交。详细判断见 [existing-project-checks.md](existing-project-checks.md)。

执行用户授权范围内的目标。完整发布沿用 GitHub Profile 同步；只要求 xiaosang.cc 时不额外修改 Profile。某个目标受阻，继续另一个独立目标并记录状态。只有验证通过的 HTTPS 地址才能成为可用 Demo。

## 标准元数据

整理 repo name、双语简介、语言、GitHub URL、最终 Cloudflare Demo、真实截图、项目提交时间。保留 repo name 原文，域名使用已核实的 slug。所有公开 Demo（README、二维码、GitHub Homepage、作品集）使用同一地址。

## xiaosang.cc：数据来源与条目更新

1. 核实远端为 `holynova/holynova.github.io`，读取最新 `origin/master` 及工作区状态；有无关改动或分支分歧时使用该提交的干净 checkout 或 detached worktree，不 reset 用户修改，也不新建发布分支。
2. **master 是唯一可编辑作品与部署来源**，数据、截图、Wrangler 配置均在 master 维护。历史 `cloudflare-migration` 分支作档案，不在其上单独维护内容。不得为 Cloudflare 新建其他分支或 GitHub Action/workflow。
3. 阅读当前 `data/repos.json` 和 `js/detail-app.js`。真实结构为顶层 `lastUpdated`、`totalRepos` 与 `categories[]`，每个分类包含 `repos[]`，不得改成扁平列表。
4. 用 `url`（GitHub 仓库 URL）或 `name` 在所有分类查找条目。已有项目原地更新并保留未涉及的属性；新增项目进入已有合适分类，不擅自新增分类或把项目设为精选。

真实条目形状示例（时间与简介按项目实际填写）：

```json
{
  "name": "keyboard_sentence",
  "lang": "JavaScript",
  "desc": {
    "zh": "iOS 键盘响应式模拟器：支持打字动效与视频导出",
    "en": "iOS keyboard adaptive layout simulator with typing animation and video export"
  },
  "url": "https://github.com/holynova/keyboard_sentence",
  "homepage": "https://keyboard-sentence.xiaosang.cc/",
  "screenshot": "screenshots/keyboard_sentence.png",
  "pushed_at": "2026-05-23",
  "commit_time": "2026-05-23T11:31:01+08:00",
  "hidden": false
}
```

`url` 是 Repo，`homepage` 是 Demo；不要使用旧参考中的 `cloudflareUrl`、`github`、`description` 或把 Demo 写进 `url`。保留已有 `stars`、`is_featured` 等属性与其他项目链接。已有明确的历史例外不能因更新一个项目而批量覆盖。

5. 将有效截图同步到 `screenshots/<repo-name>.png`，保持文件格式/扩展名一致，并更新 `screenshot`。新增后按全部分类条目数计算 `totalRepos`；`lastUpdated` 使用执行当天日期。保留既有日期格式。
6. 运行仓库已有检查：

   ```bash
   node scripts/check-demo-links.mjs
   node scripts/verify-data-source.mjs
   git diff --check
   ```

   检查唯一性、总数、所有现有例外与数据来源；不要为通过校验删除旧条目或放宽约束。额外确认新增截图存在且 JSON 可解析。
7. 只提交此次数据与截图，按既有协作流程将改动落入 master 并推送。未经请求不改主站 UI 或刷新整个 GitHub 目录。

## 单独部署作品集

从 **已推送 master 的同一提交**发布。读取该提交 `wrangler.jsonc` 并核实账户/域名绑定；当前仓库配置 Worker 为 `xiaosang-portfolio`，Custom Domain 为 `xiaosang.cc`，assets 为根目录 `.`。不要使用历史 Worker `holynova-github-io`。

遵循仓库 README 的锁定 Wrangler 命令（2026-10-01 核实版本如下；以后以仓库当前约定为准）：

```bash
npx --yes wrangler@4.128.0 deploy --dry-run --config wrangler.jsonc
npx --yes wrangler@4.128.0 deploy --config wrangler.jsonc
```

保留现有 `.assetsignore`、账户、routes 与 bindings。GitHub Actions 的数据校验或 Pages 发布不替代这一步。Cloudflare 固定从 master 同一提交在本地手动发布，不新增独立内容/发布分支、Cloudflare GitHub Action/workflow 或 Workers Builds/Git 集成。

部署后：

- 记录 master SHA 与作品集 Cloudflare deployment/version ID。
- 回读 `https://xiaosang.cc/data/repos.json`，比较该发布提交中的 JSON（可字节比较，或解析比较完整结构），不能只在本地找到条目就宣称线上存在。
- 打开 `https://xiaosang.cc/`，找到项目，确认双语简介、截图，以及 Repo/Demo 分别跳转正确地址；确认线上截图可访问。
- 回归已有代表性项目 Demo，确保本次更新没有使它们退回旧 Pages 地址。

失败时保留本地与 GitHub 成果并报告「作品集已推送但 Cloudflare 未部署/未验证」，不要以备用 Pages 更新冒充主站上线。

## GitHub Profile（范围包含时）

`https://github.com/holynova/` 由 `holynova/holynova` 的根 README 驱动。核实该仓库实际默认分支后，按既有表格形状更新同一项目行，复制缩略图，不重复追加：

```markdown
| 0 | 项目标题 | <img width="320" alt="项目预览" src="./portfolio-<repo>.png"> | 一句话中文简介 | [Demo](https://<project-slug>.xiaosang.cc/) · [Repo](https://github.com/holynova/<repo>) |
```

只提交 README 与对应图片、推送已核实分支，再打开 Profile 验证。Profile 通过 GitHub 渲染，无需 Cloudflare 部署；它的 Demo 同样指向已验证的 Cloudflare 项目地址。
