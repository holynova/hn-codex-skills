---
name: hn-project-publisher
description: 端到端初始化、版本化并完整发布个人 Web 项目。涵盖 npm/Git 初始化、页面可见 GitHub 链接与 Umami 埋点检测（项目 ID e01c9f78-4607-4e60-b01c-77c8190b12b4）、简洁中英文 README（各不超过 500 字，含有效内容延迟截图/移动端视口、Repo/Pages 链接、Pages 二维码与 Cloudflare 专属域名 <repo-name>.xiaosang.cc）、推送到 GitHub、通过 master 或 main 分支发布 GitHub Pages，并同步收录到 GitHub 个人首页与作品集主站。
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

- **检查先行**：先检查 `package.json`、lockfile、框架配置、`.gitignore`、README、git status 与远端 remotes。
- **保护既有元数据**：只初始化缺漏的 npm 或 Git 状态；已有提交历史与远程配置不要盲目覆盖。
- **分支规范**：支持使用 `master` 或 `main` 分支进行初始化与发布。
- **页面埋点与链接**：每个发布的 Web 项目必须在 `<head>` 中嵌入指定 Umami 埋点，且在 UI 中必须提供明确的 GitHub 链接。
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
   - 暂存并提交本地修改：`git add -A && git commit -m "feat: complete public release"`。
   - 创建或关联 GitHub 仓库并推送：
     ```bash
     gh repo create holynova/<repo> --public --source=. --remote=origin --push
     ```

6. **启用并配置 GitHub Pages（Requirement 6）**
   - 调用 GitHub API 启用 Pages（分支为 `master` 或 `main`，路径为 `/` 或 `/docs`）：
     ```bash
     gh api --method POST repos/holynova/<repo>/pages -f 'source[branch]=master' -f 'source[path]=/'
     ```
   - 设置仓库 Homepage 为 Pages 网址：
     ```bash
     gh repo edit holynova/<repo> --homepage "https://holynova.github.io/<repo>/"
     ```
   - 轮询等待 Pages 构建完成并验证 HTTP 访问状态。

7. **同步收录两大作品集（Requirement 7）**
   - 阅读并执行 [references/portfolio-updates.md](references/portfolio-updates.md)：
     1. **GitHub Profile (`https://github.com/holynova/`)**：更新 `holynova/holynova` 仓库根目录 `README.md` 的作品列表表格，并复制缩略图。
     2. **个人作品集主站 (`https://holynova.github.io/`)**：更新 `holynova.github.io` 仓库中的 `data/repos.json`，同步截图到 `screenshots/<repo>.png`，提交推送部署。
   - 验证两大主页上该项目均可正常展示与跳转。

8. **交付汇报**
   - 报告发布结果：版本号、GitHub 仓库地址、GitHub Pages 地址、Cloudflare 专属域名、README 验证状态、Umami 埋点确认、截图与二维码状态、两大作品集收录状态。

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
