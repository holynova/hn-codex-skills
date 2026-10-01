---
name: hn-project-publisher
description: 发布个人 Web 项目到 Cloudflare Workers 并收录到 xiaosang.cc 作品集。新项目走首次发布流程；已发布项目先检查现状，只补缺失或失效环节，按需更新部署。适用于首次上线、发布检查、更新与 GitHub Pages 迁移。
---

# HN Project Publisher

## 发布目标与范围

默认采用 **Cloudflare Workers Static Assets + Custom Domain**：GitHub 保存源码，项目运行在 `https://<project-slug>.xiaosang.cc/`，作品集入口为 `https://xiaosang.cc/`。不默认创建 Cloudflare Pages 或启用 GitHub Pages。已有 Pages 保留作回退；用户明确要求时才维护双平台发布，仍遵守下方单分支与手动 Cloudflare 发布规则。

**单一分支（强制）**：每个仓库只使用其已核实的一个主分支作为源码与发布来源。项目沿用现有 `main` 或 `master`，作品集使用 `master`；代码、README、Wrangler 配置与作品数据均在各自同一主分支维护。不得为了 Cloudflare 新建 `cloudflare`、`cloudflare-migration`、`deploy`、`gh-pages` 等发布分支，也不得另建长期维护的构建产物分支。

**手动部署（强制）**：在本地从该主分支同一提交构建并执行 `wrangler deploy`。不得为 Cloudflare 发布创建 GitHub Action/workflow，也不得新增 Workers Builds/Git 集成自动部署。GitHub 推送与 Cloudflare 手动部署是独立步骤。

完整发布包含项目上线、GitHub 仓库 Homepage 更新、作品集收录及作品集自身的 Cloudflare 发布。GitHub Profile (`holynova/holynova`) 沿用原有同步流程；用户只指定 xiaosang.cc 时只更新该作品集。仅准备材料、审阅或局部修复时不扩展成完整发布。复用当前与既有授权，不重复确认已经授权的操作；缺少某个外部动作的授权时先准备具体改动，只暂停该动作。

已有账户、域名、tracker 与项目配置优先于默认约定。Chrome 商店发布交给 `hn-chrome-extension-publisher`。

## 先判断项目状态

执行发布动作前，先根据用户说明、仓库历史、release/tag、既有 Pages/Cloudflare 部署及线上内容判断项目是否曾发布。仅有 GitHub 仓库不代表已上线；站点暂时不可达也不代表从未发布。

- **新项目：从未发布过**。执行下方首次发布流程，补齐发布所需配置、材料和收录。
- **已发布项目：曾经上线过，包含仅发布到 GitHub Pages 的项目**。先读取 [references/existing-project-checks.md](references/existing-project-checks.md)，逐项检查并标记「已满足／需补齐／不在范围／受阻」。只执行缺失、失效或本次变更影响的步骤，不从头重走首次发布流程。迁移到 Cloudflare 只补迁移相关环节，复用既有仓库、材料与作品集条目。

历史证据不完整时先继续核实，不能因为缺少本地配置就当新项目初始化。**检查全部满足且没有待发布变更时，报告检查通过即可；不制造提交、不自动递增版本、不重复部署或更新作品集。** 用户另有明确发布要求时按其范围执行。

## 首次发布流程

以下步骤用于新项目；已发布项目仅按检查结果选取必要步骤作为修复方法。

### 1. 核实项目与发布来源

- 检查 Git 状态、remote、实际默认分支、npm/lockfile、框架构建与现有 Wrangler 配置，确定唯一主分支并保护已有修改。只补齐缺失的 Git/npm 元数据。需要隔离工作区时使用该主分支提交的干净 checkout 或 detached worktree，不为发布创建新分支。
- 确认 GitHub owner/repo、Cloudflare account、Worker name、最终域名与可部署目录；仓库名和域名 slug 可不同，如 `keyboard_sentence` → `keyboard-sentence`，复用已存在的映射，检查命名碰撞。
- 读取 [references/cloudflare-publishing.md](references/cloudflare-publishing.md) 完成 Cloudflare 账户、域名绑定与构建检查。纯静态输出可直接发布；SSR/API 项目沿用适配 Workers 的入口与 bindings，不能把服务端源码当静态文件上传。
- GitHub 初始化、版本与推送细节见 [references/github-publishing.md](references/github-publishing.md)。需要发布应用变更时在构建前递增项目版本并在页面显示；仅检查或更新仓库/作品集元数据不自动递增应用版本。保留已有版本机制。

### 2. 准备页面与生产产物

- 在 Header、Nav、Footer 或关于面板提供清晰可见的 GitHub 仓库链接。
- 完整个人项目发布时复用或接入一次统一 Umami 脚本；尊重用户排除统计的要求与已有明确 tracker 配置：

  ```html
  <script defer src="https://cloud.umami.is/script.js" data-website-id="e01c9f78-4607-4e60-b01c-77c8190b12b4"></script>
  ```

- 自定义域名运行在根路径 `/`，移除旧 Pages 的 `/<repo>/` base、硬编码资源前缀及生产环境旧链接。沿用 `dist/`、`build/`、`docs/` 或静态目录，不为 Cloudflare 强制改成 `docs/`。需要双平台时分别构建对应 base。
- 将 Worker 配置与部署命令保存到项目；检查静态上传边界，根目录部署时使用 `.assetsignore`。运行项目原有检查、生产构建与 Wrangler dry-run，并测试真实页面、资源和路由。

### 3. 截图、二维码与 README

- 启动生产预览，等到真实数据、Canvas 或核心组件渲染完成后截图。移动应用使用 375–430px 宽视口，不使用桌面拉伸截图。保存仓库内的截图，如 `assets/screenshot.png`。
- 二维码编码最终 Cloudflare HTTPS 地址，与 README、仓库 Homepage 和作品集 Demo 保持一致：

  ```bash
  npx qrcode -o assets/qr.png "https://<project-slug>.xiaosang.cc/"
  ```

- 按 [references/readme-template.md](references/readme-template.md) 编写简洁中英文说明（中文 ≤500 汉字，英文 ≤500 单词），包含真实截图、Repo、Cloudflare Demo、二维码、本地运行及发布命令。未验证的地址先标为待验证。
- 从技能目录运行校验器，参数路径指向项目；不要假设项目已复制技能脚本：

  ```bash
  node <skill-dir>/scripts/validate_release_readme.mjs <project-dir>/README.md <repo-url> <cloudflare-url> 500 500
  node <skill-dir>/scripts/validate_release_version.mjs <project-dir>/package.json <deployable-file-or-dir> <previous-version>
  ```

  README 校验仅检查链接文本、图片文件存在与字数；二维码实际内容、截图有效性和线上状态仍需验证。没有历史版本时省略版本校验的最后一项。

### 4. 发布并验证项目

- 只提交本次明确文件，推送到已核实的唯一主分支；复用正确远端。代码与部署配置一并在该分支维护，不使用 Cloudflare 专用分支或 Action。仅在授权包含创建公开仓库且没有目标仓库时使用 `gh repo create`。
- 从对应提交的生产产物执行 `wrangler deploy --config <config>`，记录源码 SHA、Worker、Cloudflare deployment/version ID 与域名。Git push、dry-run 和上传成功均不能替代线上验证。
- 验证自定义域名的 HTTPS、当前内容/版本、关键 JS/CSS/图片、路由刷新和核心功能；重试有上限，TLS 失败不可用 `curl -k` 算成功。
- 项目验证后，将 GitHub Homepage 设置为该 Cloudflare 地址。若之前因域名未就绪标注为待验证，更新 README 后提交推送；生产产物含 README 时同步重建部署。

### 5. 收录并发布作品集

读取 [references/portfolio-updates.md](references/portfolio-updates.md)。先验证项目，再将同一 Demo 地址与截图写入作品集；按仓库 URL/name 更新现有条目，避免重复。

`holynova/holynova.github.io` 的 **`master` 是唯一作品数据来源**，当前配置的 Worker 为 **`xiaosang-portfolio`**。保留真实的 `categories[].repos[]` 结构，使用 `url` 存 GitHub Repo、`homepage` 存 Cloudflare Demo。运行作品集检查后提交推送，再从同一提交 **单独部署作品集 Worker**。

回读 `https://xiaosang.cc/data/repos.json` 与发布提交比较，打开作品卡片检查截图及 Repo/Demo 跳转。仅推送作品集仓库或等待 GitHub Pages 不算 xiaosang.cc 已更新。

### 6. 交付状态

先报告「首次发布」或「已发布项目检查补齐」，再按实际结果报告，不使用默认全成功模板。已发布项目明确列出检查已满足项、实际补齐项及按需部署的目标；已满足并复用的项目标为「已检查，复用」，不写成此次重新生成或发布：

```text
Project: GitHub URL / source branch + commit / app version
Cloudflare: Worker / custom domain / deployment ID / HTTPS and UI checks
Assets: screenshot viewport / QR target / README and version validation
GitHub metadata: Homepage / visible Repo link / Umami status
Portfolio: master commit / xiaosang-portfolio deployment / live JSON + card checks
GitHub Profile: updated + verified / outside scope / pending
Remaining: prepared / pushed / deployed / verified / blocked items
```

项目 Worker 与作品集 Worker 分别报告；任何必需环节受阻都保留已完成成果并明确指出，不回退改写 Demo 为未验证地址。
