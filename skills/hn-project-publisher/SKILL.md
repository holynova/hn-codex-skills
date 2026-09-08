---
name: hn-project-publisher
description: 端到端初始化、版本化并完整发布个人 Web 项目。涵盖 npm/Git 初始化、页面可见 GitHub 链接与 Umami 埋点检测（项目 ID e01c9f78-4607-4e60-b01c-77c8190b12b4）、简洁中英文 README（各不超过 500 字，含有效内容延迟截图/移动端视口、Repo/Pages 链接、Pages 二维码与 Cloudflare 专属域名 仓库名.xiaosang.cc）、推送到 GitHub、通过 master 或 main 分支发布 GitHub Pages，并同步收录到 GitHub 个人首页与作品集主站。
---

# HN Project Publisher

## Goal

按照以下 7 项完整规范，将本地 Web 项目发布为生产级公开版本：
1. **NPM & Git 初始化**：补齐缺漏的 npm 与 Git 配置，支持 `master` 或 `main` 分支。
2. **页面可见 Repo 链接**：在项目页面显著位置加入 GitHub 开源仓库入口。
3. **Umami 埋点检测**：接入统一 Umami 统计检测流量（项目 ID：`e01c9f78-4607-4e60-b01c-77c8190b12b4`）。
4. **简洁中英文 README（各 $\le 500$ 字）**：包含有效内容真实截图（移动端应用按移动端视口宽度截取）、GitHub Repo 链接、GitHub Pages 链接及扫码访问二维码、以及 Cloudflare 专属域名（`<repo-name>.xiaosang.cc`）。
5. **Push 到 GitHub**：提交代码并推送到 GitHub 远端公开仓库。
6. **开启 GitHub Pages**：使用 `master` 或 `main` 分支（根目录 `/` 或构建目录 `/docs`）发布 Pages 并验证可访问。
7. **同步收录两大作品集**：同步更新 GitHub 个人主页（`https://github.com/holynova/`）与个人作品集主站（`https://holynova.github.io/`）。

## Rules

- **范围与既有授权**：以上是用户要求完整个人项目发布时的流程；若只要求准备材料、审阅或局部修复，完成该范围，不自动推送、发布、接入统计或修改作品集。使用当前请求与既有授权确定发布目标及动作；不重复确认已明确授权且范围未变的操作。缺少某个外部动作的授权时，先准备可审阅的具体改动，只暂停该动作并继续独立工作。
- **单一流程归属**：本 Skill 负责网站发布，Chrome 商店提交由 `hn-chrome-extension-publisher` 负责；辅助 UI、资产和统计 Skill 复用同一范围与已有决定，不追加初始化访谈或重复部署。个人域名、账户与统一 Umami ID 是本流程的默认约定；已有明确项目配置或用户指定目标优先，不默默覆盖。

- **检查先行**：先检查 `package.json`、lockfile、框架配置、`.gitignore`、README、git status 与远端 remotes。
- **保护既有元数据**：只初始化缺漏的 npm 或 Git 状态；已有提交历史与远程配置不要盲目覆盖。
- **分支规范**：支持使用 `master` 或 `main` 分支进行初始化与发布。
- **页面埋点与链接**：完整发布范围内的 Web 项目在根布局接入一次约定的 Umami 埋点，并在 UI 中提供明确的 GitHub 链接；复用既有 tracker，不重复注入。用户明确排除统计时尊重范围并记录。
- **截图与视口规则**：
  - 必须等待页面加载出真实、有效的数据与内容后再截图，严禁使用初始空白、Loading 骨架屏进行截图。
  - 若项目为移动端应用/适配页面，**严禁使用 PC 桌面拉伸宽度截图**，必须采用移动端视口宽度（375px~430px）截图。
- **README 字数与要素**：中英文说明各自不超过 500 字（中文正文 $\le 500$ 汉字，英文正文 $\le 500$ 单词）。必须包含截图、Repo 链接、Pages 链接、扫码二维码图片以及专属域名 `https://<repo-name>.xiaosang.cc`。
- **双作品集同步**：发布完成后，必须更新 GitHub 个人主页（`holynova/holynova`）表格以及作品集主站（`holynova.github.io`）。
- **真实验证**：通过浏览器或 HTTP 请求真实验证 Pages、Cloudflare 域名和作品集页面，不以命令退出码为唯一成功凭据。

## Workflow

1. **项目自省与初始化（Requirement 1）**
   - 检查是否有 `package.json`，无则运行 `npm init -y`，按需配置 scripts 与依赖。
   - 检查 Git 仓库，无则运行 `git init -b master`（或 `git init -b main`）。
   - 补齐 `.gitignore`，排除 `node_modules`、`.env*`、临时构建缓存等。

2. **页面增强：Repo 链接与 Umami 埋点（Requirements 2 & 3）**
   - **GitHub Repo 链接**：在前端页面的 Header、Nav、Footer 或关于面板中添加清晰可见的 GitHub 图标/链接（例如 `<a href="https://github.com/holynova/<repo>" ...>GitHub</a>`）。
   - **Umami 埋点**：在 `index.html`（或根 layout）的 `<head>` 区域注入统一统计脚本：
     ```html
     <script defer src="https://cloud.umami.is/script.js" data-website-id="e01c9f78-4607-4e60-b01c-77c8190b12b4"></script>
     ```

3. **构建与 Pages 静态产物准备（Requirement 6 准备）**
   - 纯静态项目：直接部署根目录（`master:/` 或 `main:/`）。
   - 带构建流程的项目（如 Vite/React/Vue）：配置 public base 为 `/<repo>/`，输出到 `docs/` 并纳入版本管理；或配置 GitHub Actions。

4. **截图、二维码与双语 README（Requirement 4）**
   - **有效内容截图**：启动本地服务，等待动态数据、Canvas 或核心组件完全渲染后截图。如果是移动端应用，设置浏览器视口宽度为 390px（如 iPhone 视口）截图。保存至 `assets/screenshot.png`。
   - **二维码生成**：使用 `npx qrcode -o assets/qr.png "https://holynova.github.io/<repo>/"` 生成 Pages 访问二维码。
   - **撰写 README**：中英文各不超过 500 字，按 [references/readme-template.md](references/readme-template.md) 编写，包含：
     - 项目中英文标题与核心介绍
     - 有效内容预览截图
     - 在线体验链接（GitHub Pages 与 Cloudflare 专属域 `https://<repo-name>.xiaosang.cc`）
     - GitHub Repo 开源仓库链接
     - 手机扫码访问二维码图片（`<img src="./assets/qr.png" width="180">`）
     - 本地运行指南
   - **运行校验脚本**：
     ```bash
     node scripts/validate_release_readme.mjs README.md <repo-url> <pages-url> 500 500 "https://<repo-name>.xiaosang.cc"
     ```

5. **推送到 GitHub（Requirement 5）**
   - 先检查 diff，只暂存本次发布涉及的明确文件，再提交；不要用 `git add -A` 混入用户已有或无关修改。
   - 已有远端时核对目标并复用，只推送本次发布分支，不重建仓库或改写历史。以下创建示例仅用于尚无目标仓库且创建公开仓库在授权范围内的情况：
     ```bash
     gh repo create holynova/<repo> --public --source=. --remote=origin --push
     ```

6. **启用并配置 GitHub Pages（Requirement 6）**
   - 先读取现有 Pages 配置，复用已确定的分支或 Actions 发布方式；只在尚未启用且授权覆盖时创建。以下示例中的 `master` 必须替换为实际发布分支，路径采用已准备的 `/` 或 `/docs`，不要把示例值覆盖到已有配置：
     ```bash
     gh api --method POST repos/holynova/<repo>/pages -f 'source[branch]=master' -f 'source[path]=/'
     ```
   - 设置仓库 Homepage 为 Pages 网址：
     ```bash
     gh repo edit holynova/<repo> --homepage "https://holynova.github.io/<repo>/"
     ```
   - 有限重试检查 Pages 构建与 HTTP 状态；构建失败先检查日志，权限或服务阻塞则保留成果并报告，不无限轮询，也不把命令成功当成站点已上线。
   - **专属域名**：读取现有 Cloudflare/DNS 与站点域名配置，先检查约定的域名是否已正确指向本项目。缺少配置时准备具体 DNS/托管变更，在目标与动作已获授权且工具可用时执行，保留无关记录；否则报告域名配置待处理并继续独立发布工作。验证 HTTPS、实际项目内容及资源路径，而非仅检查域名返回 200。若自定义域名使 Pages 重定向，核对 base path、README 和二维码在最终地址仍可用。未验证的域名只能标注为待配置/待验证，不能宣称已自动发布。

7. **同步收录两大作品集（Requirement 7）**
   - 阅读并执行 [references/portfolio-updates.md](references/portfolio-updates.md)：
     1. **GitHub Profile (`https://github.com/holynova/`)**：更新 `holynova/holynova` 仓库根目录 `README.md` 的作品列表表格，并复制缩略图。
     2. **个人作品集主站 (`https://holynova.github.io/`)**：更新 `holynova.github.io` 仓库中的 `data/repos.json`，同步截图到 `screenshots/<repo>.png`，提交推送部署。
   - 验证两大主页上该项目均可正常展示与跳转。

8. **交付汇报**
   - 按实际结果报告版本号、GitHub、Pages、Cloudflare 域名、README 校验、Umami、截图、二维码和两大作品集状态。区分已准备、已推送、已部署、已验证、待授权和受阻；任一范围内必需项未完成时明确列出，不能套用全成功模板。未要求的步骤标为不在范围。

## Output

```text
Published:
- Repository: https://github.com/holynova/<repo>
- GitHub Pages: https://holynova.github.io/<repo>/
- Cloudflare Domain: https://<repo>.xiaosang.cc
- Branch/Source: master:/ (or main:/)

Verified:
- NPM & Git: initialized and clean
- Page Repo Link: verified in UI
- Umami Tracking: present (ID: e01c9f78-4607-4e60-b01c-77c8190b12b4)
- Screenshot: captured with valid rendered content (viewport verified)
- QR Code: generated and rendered in README
- README Validation: passed (Chinese <= 500 chars, English <= 500 words)

Portfolios:
- GitHub Profile (holynova/holynova): updated & verified
- Portfolio Site (holynova.github.io): updated & verified
```
