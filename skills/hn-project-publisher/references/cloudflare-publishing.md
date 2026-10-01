# Cloudflare Workers 发布

适用于个人项目的 Workers Static Assets 发布。默认每个项目一个 Worker、一个 `*.xiaosang.cc` Custom Domain；作品集是另一个独立 Worker。这里的 Cloudflare 指 Workers，不是 Cloudflare Pages。

已发布项目先按 [existing-project-checks.md](existing-project-checks.md) 检查；下方构建与部署仅在实际缺口或待发布变更需要时执行。有效 Worker、域名与配置直接复用，不因调用本技能重新部署。

**唯一源码分支 + 本地手动部署**：每个仓库沿用一个主分支（项目现有 main/master，作品集 master），源码与 Wrangler 配置在同一分支维护。不得为 Cloudflare 新建发布分支或 GitHub Action/workflow，不新增 Workers Builds/Git 集成。所有 Cloudflare 发布均在本地从该主分支同一提交执行 Wrangler。

## 1. 账户、Worker 与域名

先读取现有 `wrangler.jsonc`、`wrangler.toml` 或框架生成配置、package scripts、remote 与线上地址。复用项目锁定的 Wrangler 版本；无现有工具时安装并锁定当前稳定 Wrangler 4，或选择经验证的精确版本。后文 `npx wrangler` 指该已确定版本。

```bash
npx wrangler --version
npx wrangler whoami
```

确认当前账户拥有 `xiaosang.cc` zone 及所需 Worker/域名权限。配置多个账户时选择并记录已核实的 account_id，不从别的项目盲抄。交互登录缺失时使用 `wrangler login`；凭据只由登录或环境提供，不写入代码或输出。

先查现有 Worker、Custom Domains/Routes 与该主机的 DNS 绑定，可使用已认证 Cloudflare 工具、控制台或 API（`GET /accounts/{account_id}/workers/domains`）。同名 Worker 或域名指向其他项目时先解决目标冲突，不能直接覆盖。不要由一条 A/CNAME 或历史记录推断当前 Worker。

域名使用已有映射；新项目可将 repo 名小写、下划线/点等转成连字符，并检查有效 DNS label、长度与碰撞。`keyboard_sentence` → `keyboard-sentence.xiaosang.cc` 是现有映射示例。保留原仓库名称。

Custom Domain 要求账户内有效 Cloudflare zone。绑定会管理对应 DNS 与证书；不要再添加指向 GitHub Pages 或 `workers.dev` 的 CNAME。已有 CNAME 会阻止创建 Custom Domain：先核实旧用途，仅在已授权的迁移中移除该条冲突记录，并保留回退信息。

## 2. 构建与配置

| 项目 | assets.directory | 路由与构建 |
| --- | --- | --- |
| 纯 HTML/CSS/JS | 公开静态目录；必要时 `.` | 根路径 `/`，审查 `.assetsignore` |
| Vite/React/Vue | 通常 `./dist` | `base: '/'`；有客户端 history 路由才启用 SPA fallback |
| 静态导出/多页项目 | 实际 `out/`、`build/`、`docs/` 等 | 保留页面结构，按需 `404-page` |
| SSR/API | 框架 Workers adapter 的产物 | 保留 `main`、bindings、secrets 和运行时配置，不能仅上传源目录 |

生产输出必须含入口与全部运行资源。Vite 等不再默认 `/<repo>/` base，不强制输出/提交 `docs/`。哈希路由或普通多页网站不必启用 SPA。

新建的纯静态配置示例；替换 slug、目录、日期及经核实的账户，已有配置则局部修改，不覆盖 bindings/routes：

```jsonc
{
  "$schema": "./node_modules/wrangler/config-schema.json",
  "name": "project-slug",
  "compatibility_date": "2026-10-01",
  "workers_dev": false,
  "assets": { "directory": "./dist" },
  "routes": [
    { "pattern": "project-slug.xiaosang.cc", "custom_domain": true }
  ]
}
```

新 Worker 的 compatibility_date 使用执行当天日期，已有项目不无故升级。`pattern` 是裸主机名，不含 `https://`、路径或 `/*`。纯静态站不需要虚构 `main` 或 ASSETS binding；有 Worker 代码时才按运行时需要配置。

客户端 history 路由的 SPA 在 assets 中增加 `"not_found_handling": "single-page-application"`。有 API 时核实导航与 `run_worker_first` 行为，避免将 API 请求回退为 HTML。

根目录上传时，在 **assets.directory 根目录**放 `.assetsignore`；`.gitignore` 不等于静态上传边界。以下是起点，按实际运行资源调整：

```gitignore
.git/
.github/
node_modules/
.wrangler/
.env
.env.*
.dev.vars
.dev.vars.*
work/
tests/
scripts/
README.md
package.json
package-lock.json
pnpm-lock.yaml
yarn.lock
wrangler.jsonc
wrangler.toml
.gitignore
.assetsignore
```

不能因示例而排除浏览器实际依赖的 scripts/ 或数据。优先使用只含公开文件的产物目录；所有被纳入 assets 的文件均可能公开访问。

## 3. 本地检查与可重复发布

需要构建时使用现有 lockfile/包管理器安装，按实际缺口准备 Repo 链接与 Umami，仅在发布应用变更时更新版本，再构建；纯静态项目省略不存在的构建命令。配置脚本可采用：

```json
{
  "scripts": {
    "deploy:check": "wrangler deploy --dry-run --config wrangler.jsonc",
    "deploy": "npm run build && wrangler deploy --config wrangler.jsonc"
  }
}
```

已有脚本优先；静态无 build 项目将 deploy 改为直接 `wrangler deploy`。

```bash
npx wrangler deploy --dry-run --config wrangler.jsonc
npx wrangler dev --config wrangler.jsonc
```

dry-run 检查打包/配置，不会验证线上 DNS、证书和实际功能。通过本地 Worker/生产预览测试首页、关键操作、资源及深层路由刷新；核实资产文件类型、数量与大小是否符合当前账户限制，不把历史迁移时的配额当恒定值。

## 4. 部署与上线检查

从唯一主分支已提交的同一提交构建并在本地部署，记录主分支、源码 SHA、项目版本、Worker 和部署 ID：

```bash
npx wrangler deploy --config wrangler.jsonc
curl -fLsS --max-time 30 "https://<project-slug>.xiaosang.cc/"
```

不得创建 Cloudflare 专用分支、GitHub Action/workflow 或 Workers Builds/Git 集成，不能用自动部署替代本地 Wrangler 发布。检查已有 workflow/自动构建是否会覆盖本次手动部署；若存在冲突，记录并在迁移授权范围内处理，不另建分支或 Action 绕过冲突。已有测试、数据校验与历史 Pages workflow 不因本规则自动删除。

核实 Custom Domain 指向目标 Worker，再验证 HTTPS、当前版本/独有内容、主要 JS/CSS/图片的响应和 Content-Type、浏览器核心功能及深层路由。SPA 的缺失资源可能返回 HTML，200 不是完整验证。

证书传播可有限重试（例如最多 6 次、间隔 10 秒）。仍失败则报告「已部署，域名/TLS 待就绪」，不要无限轮询、禁用证书校验或将故障地址加入作品集。部署失败检查具体错误并修复可处理项，权限或额度受阻时保留产物与配置，不改投未要求的平台。

项目验证成功后更新仓库 Homepage，然后执行 [portfolio-updates.md](portfolio-updates.md)；作品集需要自己的独立部署。

## 参考与证据

2026-10-01 核实的作品集 [master 配置](https://github.com/holynova/holynova.github.io/blob/master/wrangler.jsonc) 使用 `xiaosang-portfolio`、`assets.directory: '.'`、`xiaosang.cc` Custom Domain；[README](https://github.com/holynova/holynova.github.io/blob/master/README.md) 明确手动发布。现有本地项目也展示根目录与 dist 两类配置；部分配置未进入远端仓库，不能推断 Git push 已部署。

- [Workers Static Assets](https://developers.cloudflare.com/workers/static-assets/)
- [资产配置与 .assetsignore](https://developers.cloudflare.com/workers/static-assets/binding/)
- [Custom Domains 与 DNS/证书](https://developers.cloudflare.com/workers/configuration/routing/custom-domains/)
- [SPA 路由](https://developers.cloudflare.com/workers/static-assets/routing/single-page-application/)

执行时以项目当前配置、线上绑定和官方文档为准，不复制历史 Worker 名到新项目。
