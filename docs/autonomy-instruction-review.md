# Skill 自主性与授权规则审阅

审阅基线：`88f8f81`。以下原文引用来自该基线；文件链接指向修订后的对应规则。范围为安装器白名单中的 11 个活跃 Skill 及相关引用文件。`backup/` 中的 6 个历史 Skill 不进入执行路径，本次保留归档与安装隔离，不将它们重新启用。

## 结论与权限边界

修订 9 个活跃 Skill。主要问题是重复批准、把内部核对当成用户决策、审计与实施范围混淆、多个 Skill 重复接管流程，以及无法满足或缺少执行步骤的完成条件。

本次没有把工具可用、超时、沉默或泛泛的“准备材料”视为外部操作授权。没有取消 Chrome 商店提交、医疗保存目录创建或 Windows 可选修复的明确批准要求。增加了隐私页面公开部署的授权范围说明，收紧了原来“本地准备即可上传”的歧义。常规内部判断和独立工作可继续，但不扩大外部操作权限。

## 高优先级发现

### 1. 扩展发布反复索取已经给过的授权

文件：[扩展发布 Skill](../skills/hn-chrome-extension-publisher/SKILL.md)、[后台提交](../skills/hn-chrome-extension-publisher/references/dashboard-submission.md)。

原文：`After all materials pass local checks, ask whether the user wants ...`；`Do not continue into the dashboard until the user answers.`；引用文件再次要求 `Ask whether authorization covers all of the following`。

影响：用户已经授权特定版本上传和提交，执行到第 7 步或切换引用文件后仍会暂停。重复询问不增加保障，却中断已授权工作。

修改：先核对 publisher/item、版本、包和动作是否在现有明确授权内，只为未覆盖部分请求批准。未获得提交授权时仍停止在提交之前，继续独立的准备和核查。范围或版本变化不复用旧批准。

权限：不扩展；保留逐动作的明确授权，消除重复批准。

### 2. “准备”被误当成上传授权，隐私部署与本地准备混在一起

文件：[后台提交](../skills/hn-chrome-extension-publisher/references/dashboard-submission.md)、[隐私页面](../skills/hn-chrome-extension-publisher/references/privacy-page.md)、[扩展发布 Skill](../skills/hn-chrome-extension-publisher/SKILL.md)。

原文：`If the user authorizes preparation but not final submission, fill and upload`；`Publish it at a stable public HTTPS URL.`；`Commit and publish through the repository's existing Pages workflow.`

影响：仅请求本地素材准备可能触发后台上传或公开部署；反过来，缺少公开部署权限也可能阻止后续打包，尽管二者可独立完成。

修改：把本地准备、后台填写、上传、提交和公开部署分别核对。先准备页面及具体目标，再执行已授权部署；没有授权时只保留对应动作待办，继续本地打包。没有可访问的必需隐私 URL 时，不报告可提交。

权限：收紧授权解释；新仓库创建/发布的明确批准继续保留。

### 3. 医疗采集的固定问卷和“只等待”阻断已有明确请求

文件：[医疗资料采集](../skills/hospital-record-collector/SKILL.md)。

原文：`在进行任何微信界面操作前，先用一条简洁消息要求用户`；`用户未准备好时只等待`；`如果微信中有多个就诊人，询问本次要采集哪一位`。

影响：已经给出类型、时间、患者、目录并说明已登录的用户仍需重复回答；单条金额不清楚或登录待处理可能阻断整个批次和本地整理。

修改：将清单定义为前置条件而非固定问卷，复用范围未变的确认。只询问缺失内容；单条异常仅暂停该条，登录阻塞时仍可做已授权的本地整理。目录不存在仍须批准创建，明确要求创建同一目录即已有批准。

权限：不扩展；保留患者边界、登录由用户完成、禁止下载按钮/外发、不得猜金额、不得覆盖文件。

### 4. 工具名写死造成能力明明存在却无法继续

文件：[医疗资料采集](../skills/hospital-record-collector/SKILL.md)。

原文：`所有桌面和微信界面操作使用 Computer Use 的 node_repl 与 @oai/sky`。

影响：提供其他 Computer Use 接口的环境会被错误判断为无法执行，或诱导调用不存在的 API。

修改：先读取当前可用且已授权的 Computer Use 文档；保留 Sky 作为条件示例，其他环境使用等价状态/截图接口。继续要求每步刷新状态，缺少能力时报告准确限制，不改用未经授权的数据提取方式。

权限：允许等价工具适配，未增加数据访问或外发权限。

### 5. 项目发布要求域名完成，却没有对应执行步骤

文件：[网站发布 Skill](../skills/hn-project-publisher/SKILL.md)、[README 模板](../skills/hn-project-publisher/references/readme-template.md)。

原文：`真实验证 Pages、Cloudflare 域名和作品集页面`；模板要求 `加入自动发布的专属域名`，但主流程没有配置该域名的步骤。

影响：代理可能仅把域名写入 README 就报告完成，或在发现域名不能访问后停工而没有具体下一步。

修改：增加读取既有 DNS/托管配置、准备具体变更、执行已授权配置和验证 HTTPS/实际项目内容/资源路径的步骤。处理 Pages 重定向后的 URL、base path 和二维码；未验证域名标为待配置，不冒充在线演示。

权限：只落实原本要求的域名交付，外部配置仍受目标与动作授权约束；不授予任意 DNS 改动权限。

### 6. 发布流程假设全新仓库、固定分支及全成功交付

文件：[网站发布 Skill](../skills/hn-project-publisher/SKILL.md)、[作品集同步](../skills/hn-project-publisher/references/portfolio-updates.md)。

原文：`git add -A`；无条件 `gh repo create ... --push` 与 Pages POST 示例；作品集两次固定 `git push origin master`，而主 Skill 明确支持 main/master。

影响：常规更新可能混入无关改动、在已存在仓库上失败，或向错误分支推送；一个作品集目标受阻可能导致整个发布提前结束。

修改：复用现有仓库和 Pages/Actions 配置，只暂存明确的发布文件；创建示例仅适用于不存在目标且已获授权的情况。按每个仓库核对分支，独立处理两个作品集目标，有限重试部署，分别报告准备/推送/部署/验证/受阻状态。

权限：收紧改动范围；不增加强推、删除或覆盖权限。发布模板仅适用于请求的发布范围，不将局部修复扩大为全流程公开发布。

## 常规流程与重叠问题

### 7. UI 审计直接进入修改，Creation Gate 容易被当作人类批准

文件：[布局排版审计](../skills/hn-ui-layout-typography-audit/SKILL.md)、[工具 UI 打磨](../skills/hn-tool-ui-polisher/SKILL.md)。

原文：`Create or repair the interface`；`Implement polish`；`Before implementing a new interface, confirm all of the following`；`Use hn-tool-ui-polisher as well`。

影响：只请求反馈时可能修改代码；请求实现时又可能停在布局清单等待确认。两个 Skill 同时适用时重复访谈和检查。

修改：明确审计只交付发现与建议；审计并修复则直接继续范围内实施。Creation Gate 是内部设计检查，不是新增批准点。两个 Skill 共用范围、证据和验证；产品里的异步/破坏性操作反馈不是代理执行权限规则。

权限：收紧只读审计边界；保留范围与品牌变更的明确批准。

### 8. 分享卡片核对与验证要求扩大了用户范围

文件：[分享卡片](../skills/hn-share-card/SKILL.md)。

原文：`确认分享范围：结果级或网站级；确认二维码打开的 URL`，但验证步骤要求 `结果级和网站级入口各点击一次`。

影响：只要求结果级卡片也可能被迫补一个网站级入口；“确认”可能变成固定问卷。

修改：从请求和已有实现确定范围/URL，只在实质歧义时澄清；只验证范围内存在的入口。敏感输入、私密数据和参数公开边界不放宽。

权限：不扩展；避免额外功能与隐私范围扩大。

### 9. 统计 Skill 与个人发布约定争夺默认方案，验证流量被白名单排除

文件：[统计 Skill](../skills/hn-web-analytics/SKILL.md)、[验证环境约定](../skills/hn-web-analytics/references/umami-implementation.md)。

原文：发布 Skill 使用统一 Cloud website ID，统计 Skill 默认自托管且每站创建 website；验证要求 `打开 2 个路径并触发 2 个自定义事件`，参考文件又规定 `localhost ... 默认不进正式数据`。

影响：可能重复创建服务、替换既有 ID，或在本地无限等待根本不会进入生产统计的数据；单页工具也可能被迫新增路由/事件。

修改：发布流程复用既有实例与约定 ID，迁移须在明确范围内。验证先确定允许的测试域名/staging 配置，按实际路由/事件检查，有限重试并区分本地检查与后台入库证据。

权限：不扩大生产白名单，不自动迁移服务，不虚报统计完成。

### 10. Windows 验证被交给用户；资产规格可能变成不必要的询问

文件：[Windows 诊断](../skills/hn-windows-stability-doctor/SKILL.md)、[可选修复批准](../skills/hn-windows-stability-doctor/references/codex-preflight.md)、[视觉资产](../skills/hn-visual-asset-pipeline/SKILL.md)。

原文：`Finish with a verification checklist the user can run after the fix`；`Only apply with user approval`；资产步骤只列 `Required sizes, formats, output paths, and naming scheme`。

影响：可自行运行的验证也可能交还用户；已批准的同一环境修复重复询问；可从 manifest/目录推断的导出规格可能被要求用户填写。

修改：优先读取证据并完成安全、已授权的验证，仅把必须重启、物理操作或后续观察的检查交还用户。可选修复批准保持有效且不阻塞只读诊断。资产规格优先从项目推断，可逆导出使用说明过的合理默认值，不自行覆盖未授权文件。

权限：不取消执行策略等可选修复的批准；不增加高风险系统操作权限。

## 保留的有意保障

- `hn-poem` 无输入时请求主题，是缺少创作对象，不是重复确认；有输入时直接创作，未修改。
- `hn-xiaohei-draw` 区分配图建议与直接生成，明确生成请求不等待；保留原创构图、质量校验和禁止覆盖既有资产，未修改。
- 商店登录、验证码、付款及个人法律确认仍由用户完成。
- 医疗采集不得猜测、跨患者或外发资料；新目录创建仍须明确批准。
- Windows 高风险修复依旧需要证据，可选环境修复依旧需要批准。
- 部署、打包、截图及真实浏览器检查是完成证据；没有工具或访问时报告未验证，不凭流程结束宣称通过。

## 验证

- `npm test`：4 项 Node 安装器测试、4 项 Python 发布工具测试通过。
- `npm run check`：11 个活跃 Skill 安装预检通过，归档隔离维持不变。
- Skill frontmatter 与 agents YAML 均可解析；标准 Skill 校验覆盖 11 个入口。
- 发布 Skill 原有 description 中的尖括号占位符改成等义中文，以通过标准描述字段校验；正文命令占位符保留。
- `git diff --check` 通过。检查修改后的入口与引用规则一致；未运行真实商店提交、医疗采集、DNS 变更或系统修复。
- 这些检查验证文件结构和现有程序回归，不等同于证明未来模型在所有场景中都会正确执行。
