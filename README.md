# HN Codex Skills

> 个人精选 Codex Skills 体系 · 高频工程与创作工作流沉淀

本仓库用于沉淀个人的高频工程发版、界面打磨、内容创作与系统诊断工作流，避免每次与 AI 对话时重复说明复杂规则。内置安装脚本，支持通过 `npx` 一键分发到任意环境的 Codex 中。

---

## 📦 现收录技能目录 (Curated Bundled Skills)

经过架构重构与职责收敛，本仓库精选并维护 **19 个核心高频技能**（其余重叠/历史流程已安全隔离至 `backup/` 文件夹中）：

### 🚀 发布与交付 (Publishing & Releasing)
- **`hn-project-publisher`**：**Web 项目首次发布与发布检查**。新项目走完整首次发布；已发布项目先检查现状，仅补缺失、失效或本次变更影响的环节，无缺口和待发布变更时无需重新发布。涵盖 npm/Git 与版本管理、页面 Repo 链接和 Umami 埋点、简洁中英文 README（各 ≤500 字，含真实截图与 Cloudflare Demo 二维码）、推送 GitHub、Cloudflare Workers Static Assets 独立域名部署（`<project-slug>.xiaosang.cc`），以及收录并单独发布 [xiaosang.cc 作品集](https://xiaosang.cc/)。每个仓库只使用一个主分支，本地手动部署 Cloudflare，不创建专用发布分支或 GitHub Action；默认保留旧 GitHub Pages 作回退，完整发布沿用 GitHub 个人主页同步。
- **`hn-chrome-extension-publisher`**：**Chrome 网上应用店扩展发布专属**。包含 Manifest V3 审计、商店素材尺寸与隐私政策审查、过滤敏感密钥自动打包 ZIP、生成 SHA256 校验和并指导商店开发者后台提审。

### 🎨 界面打磨与视觉资产 (UI & Visual Assets)
- **`hn-ui-layout-typography-audit`**：**UI 布局与排版审计**。基于对比、重复、对齐、亲密性四大设计原则，走查字号阶梯、4px/8px 间距网格、色彩对比度与无障碍规范。
- **`hn-website-completeness-check`**：**网站查缺补漏**。检查 favicon、可见项目 GitHub 链接、README/仓库介绍、分享卡片、icon/logo，并按需检查元数据、移动端、交互状态、图片性能和发布收录。区分检查与修复，已有项目只补缺口。
- **`hn-image-loading-optimizer`**：**图片密集网站加载优化**。从 rubber-stamp 提炼三层图片资产、解码后无感切换、过期响应隔离、首屏优先级、懒加载与分批渲染、导出按需加载，并附源码证据、验证方法与可复用控制器。
- **`hn-tool-ui-polisher`**：**工具界面可用性打磨**。针对紧凑型小应用/独立工具，审查表单控件对齐、按钮分组、交互状态流转（Loading/Error/Success）与移动端自适应。
- **`hn-visual-asset-pipeline`**：**产品视觉资产流水线**。规范化生成并批量整理 Favicon、多尺寸 App 图标、README 题图、透明底 PNG 与商店宣传图。

### ✍️ 内容创作与艺术表达 (Creative & Content)
- **[`hn-ink-dance-sketch`](skills/hn-ink-dance-sketch/SKILL.md)**：**墨线舞蹈速写**。疏放书写性墨线、暖纸留白、少量浓墨锚点；内置 [6 张必读例图](skills/hn-ink-dance-sketch/references/examples.md)，并通过舞种、服装轮廓、重心与视角变化避免系列雷同。
- **`hn-xiaohei-draw`**：**“宇航员小黑”IP 正文配图系统**。生成具有 Ian 风格白底手绘线稿、红橙蓝局部重点标注、可爱宇航员小黑角色的中文技术与方法论配图。
- **`hn-poem`**：**现代汉语短诗生成体系**。采用“低相关并置”理论，一次创作四首分别采用错搭替换、强制等同、重新解释与能力越权的陌生化短诗。
- **`rubber-stamp-art`**：**橡皮图章与木刻版画创作**。根据文字、诗词、地标或用户图片生成宣纸质感、矿物印泥配色与手工刻痕风格的印章艺术提示词。
- **[`hn-paper-gouache`](skills/hn-paper-gouache/SKILL.md)**：**纸纹平涂水粉插画**。抽象明亮色块、不透明水粉、纸纹和手绘边缘，用于城市、地标与自然场景；内置 [6 张完整必读例图](skills/hn-paper-gouache/references/visual-examples.md)，先看图再生成，支持配色、季节与构图多样性。安装器拒绝缺例图的文字版包。

- **`hn-color-woodcut`**：**套色木刻 · 山河入版**。附带必须查看的8张风格例图与总览，提炼平涂套色、手刻刀痕、纸白留空与景深构图，支持山河、城市、庭院、生活、节庆和海浪等题材。

- **[`hn-flowing-pen-art`](skills/hn-flowing-pen-art/SKILL.md)**：**流线钢笔画创作**。将任意主题转成暖旧纸、深蓝墨色、随形排线与流动线场的诗性插画；内置[五张必需例图与分析](skills/hn-flowing-pen-art/references/examples.md)，生成前必须查看至少两张，并将至少一张作为风格参考输入。支持人物、动物、建筑、风景、静物和构图多变的系列。

- **[`hn-translucent-toy`](skills/hn-translucent-toy/SKILL.md)**：**半透明制服与盔甲玩具生图**。提炼卡通收藏玩具人物、硬挺模压制服、厚壳半透明树脂与鲜亮撞色；内置6张必需例图，生成前必须看图校准，支持多角色、多配色系列。

### 📊 数据埋点与交互分享 (Analytics & Sharing)
- **`hn-web-analytics`**：**集中式 Umami 统计接入**。为多个静态站点、Astro、React、Vue 前端统一埋入隐私友好的 PV、UV 与自定义事件统计代码。
- **`hn-share-card`**：**精美结果分享卡片**。为 Web 工具生成带有二维码与关键成果的 Canvas 分享图片，支持一键下载 PNG 与系统原生分享回退。

### 🛠️ 系统诊断与日常自动化 (Diagnostics & Automation)
- **`hn-windows-stability-doctor`**：**Windows 稳定性与崩溃诊断**。快速诊断蓝屏（BSOD）、异常死机、WHEA 硬件报错、驱动崩溃与内存/磁盘健康。
- **`hospital-record-collector`**：**医疗票据与病历自动化采集**。配合微信岳阳医院服务，按时间范围自动截取电子发票与门诊病历截图并归档。

---

## ⚡ 安装方式 (Installation)

### 1. 全量安装 (Install All Bundled Skills)
直接通过 npx 将所有 19 个精选技能安装到本地 Codex（默认路径为 `~/.codex/skills`）：

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

# 安装网站查缺补漏技能
npx github:holynova/hn-codex-skills install hn-website-completeness-check

# 安装图片加载优化技能
npx github:holynova/hn-codex-skills install hn-image-loading-optimizer

# 安装工具界面打磨技能
npx github:holynova/hn-codex-skills install hn-tool-ui-polisher

# 安装视觉资产生成流水线
npx github:holynova/hn-codex-skills install hn-visual-asset-pipeline

# 安装“宇航员小黑”IP 正文配图技能
npx github:holynova/hn-codex-skills install hn-xiaohei-draw

# 安装现代汉语短诗生成技能
npx github:holynova/hn-codex-skills install hn-poem

# 安装墨线舞蹈速写技能（包含必读例图）
npx github:holynova/hn-codex-skills install hn-ink-dance-sketch

# 安装半透明制服与盔甲玩具生图技能（包含必需例图）
npx github:holynova/hn-codex-skills install hn-translucent-toy

# 安装橡皮图章与木刻版画创作技能
npx github:holynova/hn-codex-skills install rubber-stamp-art

# 安装纸纹平涂水粉插画技能（包含必读例图）
npx github:holynova/hn-codex-skills install hn-paper-gouache

# 安装套色木刻作图技能（含必备例图）
npx github:holynova/hn-codex-skills install hn-color-woodcut

# 安装流线钢笔画技能（含五张必需例图）
npx github:holynova/hn-codex-skills install hn-flowing-pen-art

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
├── skills/                # 19 个当前正式发布的活跃技能
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
