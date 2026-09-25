# HN Codex Skills

> 个人精选 Codex Skills 体系 · 高频工程与创作工作流沉淀

本仓库用于沉淀个人的高频工程发版、界面打磨、内容创作与系统诊断工作流，避免每次与 AI 对话时重复说明复杂规则。内置安装脚本，支持通过 `npx` 一键分发到任意环境的 Codex 中。

---

## 📦 现收录技能目录 (Curated Bundled Skills)

经过架构重构与职责收敛，本仓库精选并维护 **12 个核心高频技能**（其余重叠/历史流程已安全隔离至 `backup/` 文件夹中）：

### 🚀 发布与交付 (Publishing & Releasing)
- **`hn-project-publisher`**：**全流程 Web 项目发布总控**。涵盖 NPM/Git 初始化、页面显式 Repo 链接、Umami 流量埋点（固定项目 ID `e01c9f78-4607-4e60-b01c-77c8190b12b4`）、简洁中英文 README（各 $\le 500$ 字，含移动端有效内容延迟截图、Pages 扫码二维码、Cloudflare 专属域名 `<repo-name>.xiaosang.cc`）、推送 GitHub、GitHub Pages 双分支部署及同步收录两大作品集。
- **`hn-chrome-extension-publisher`**：**Chrome 网上应用店扩展发布专属**。包含 Manifest V3 审计、商店素材尺寸与隐私政策审查、过滤敏感密钥自动打包 ZIP、生成 SHA256 校验和并指导商店开发者后台提审。

### 🎨 界面打磨与视觉资产 (UI & Visual Assets)
- **`hn-ui-layout-typography-audit`**：**UI 布局与排版审计**。基于对比、重复、对齐、亲密性四大设计原则，走查字号阶梯、4px/8px 间距网格、色彩对比度与无障碍规范。
- **`hn-tool-ui-polisher`**：**工具界面可用性打磨**。针对紧凑型小应用/独立工具，审查表单控件对齐、按钮分组、交互状态流转（Loading/Error/Success）与移动端自适应。
- **`hn-visual-asset-pipeline`**：**产品视觉资产流水线**。规范化生成并批量整理 Favicon、多尺寸 App 图标、README 题图、透明底 PNG 与商店宣传图。

### ✍️ 内容创作与艺术表达 (Creative & Content)
- **`hn-xiaohei-draw`**：**“宇航员小黑”IP 正文配图系统**。生成具有 Ian 风格白底手绘线稿、红橙蓝局部重点标注、可爱宇航员小黑角色的中文技术与方法论配图。
- **`hn-poem`**：**现代汉语短诗生成体系**。采用“低相关并置”理论，一次创作四首分别采用错搭替换、强制等同、重新解释与能力越权的陌生化短诗。
- **`rubber-stamp-art`**：**橡皮图章与木刻版画创作**。根据文字、诗词、地标或用户图片生成宣纸质感、矿物印泥配色与手工刻痕风格的印章艺术提示词。

### 📊 数据埋点与交互分享 (Analytics & Sharing)
- **`hn-web-analytics`**：**集中式 Umami 统计接入**。为多个静态站点、Astro、React、Vue 前端统一埋入隐私友好的 PV、UV 与自定义事件统计代码。
- **`hn-share-card`**：**精美结果分享卡片**。为 Web 工具生成带有二维码与关键成果的 Canvas 分享图片，支持一键下载 PNG 与系统原生分享回退。

### 🛠️ 系统诊断与日常自动化 (Diagnostics & Automation)
- **`hn-windows-stability-doctor`**：**Windows 稳定性与崩溃诊断**。快速诊断蓝屏（BSOD）、异常死机、WHEA 硬件报错、驱动崩溃与内存/磁盘健康。
- **`hospital-record-collector`**：**医疗票据与病历自动化采集**。配合微信岳阳医院服务，按时间范围自动截取电子发票与门诊病历截图并归档。

---

## ⚡ 安装方式 (Installation)

### 1. 全量安装 (Install All Bundled Skills)
直接通过 npx 将所有 12 个精选技能安装到本地 Codex（默认路径为 `~/.codex/skills`）：

```bash
npx github:holynova/hn-codex-skills install
```

如需强制覆盖本地已有同名目录，添加 `--force` 参数：
```bash
npx github:holynova/hn-codex-skills install --force
```

### 2. 单项按需安装 (Install a Specific Skill)
指定技能名称单独安装：

```bash
# 安装 Web 项目全流程发布总控技能
npx github:holynova/hn-codex-skills install hn-project-publisher

# 安装 Chrome 扩展发布技能
npx github:holynova/hn-codex-skills install hn-chrome-extension-publisher

# 安装 UI 排版与版式走查技能
npx github:holynova/hn-codex-skills install hn-ui-layout-typography-audit

# 安装工具界面打磨技能
npx github:holynova/hn-codex-skills install hn-tool-ui-polisher

# 安装视觉资产生成流水线
npx github:holynova/hn-codex-skills install hn-visual-asset-pipeline

# 安装“宇航员小黑”IP 正文配图技能
npx github:holynova/hn-codex-skills install hn-xiaohei-draw

# 安装现代汉语短诗生成技能
npx github:holynova/hn-codex-skills install hn-poem

# 安装橡皮图章与木刻版画创作技能
npx github:holynova/hn-codex-skills install rubber-stamp-art

# 安装 Umami 数据统计接入技能
npx github:holynova/hn-codex-skills install hn-web-analytics

# 安装分享卡片生成技能
npx github:holynova/hn-codex-skills install hn-share-card

# 安装 Windows 稳定性诊断技能
npx github:holynova/hn-codex-skills install hn-windows-stability-doctor

# 安装岳阳医院票据采集技能
npx github:holynova/hn-codex-skills install hospital-record-collector
```

### 3. 指定自定义安装目录 (Custom Install Path)
```bash
npx github:holynova/hn-codex-skills install --path /custom/skills/dir
```

---

## 📂 仓库目录结构 (Directory Structure)

```text
hn-codex-skills/
├── bin/
│   └── install.mjs        # npx 自动化安装器 CLI
├── skills/                # 12 个当前正式发布的活跃技能
│   ├── hn-chrome-extension-publisher/
│   ├── hn-project-publisher/
│   ├── hn-ui-layout-typography-audit/
│   └── ...
├── backup/                # 归档隔离的 6 个重叠/历史技能（严禁外部安装）
│   ├── hn-frontend-project-shipper/
│   ├── hn-agent-workflow-productizer/
│   ├── hn-data-to-github-pages-gallery/
│   └── ...
├── tests/                 # 自动化测试套件
└── README.md
```

---

## 🛡️ 安全与隔离说明 (Archived Skills Notice)

为保证工作流的单一性与可预测性，本仓库已将此前功能重叠的 6 个技能（如 `hn-frontend-project-shipper`、`hn-data-to-github-pages-gallery` 等）移入 `backup/` 文件夹中归档。
- 安装脚本已启用白名单校验，**严禁外部用户安装任何已归档技能**；
- 若尝试安装归档技能，系统将直接报错拦截，保障工作流的干净纯粹。
