# 证据与检查步骤

## 静态检查

从实际路由/根布局/metadata配置和生产输出搜索，不只找项目中任意一份HTML：

```bash
rg -n 'rel=.icon|favicon|apple-touch-icon|og:|twitter:|canonical|description|viewport' <actual-source-files>
rg -n 'github.com|share-card|navigator.share|canShare|toBlob|QRCode' <actual-source-files>
gh repo view OWNER/REPO --json name,url,description,homepageUrl,defaultBranchRef
```

参数替换为已核实仓库与入口文件。阅读根 README 及语言版，核实截图与说明不是废弃版本。React/Next/Astro 等跟踪metadata组件、路由和构建输出；关键词不出现不能直接判定缺失。

远端元数据和本地package各自检查；default_branch只核实，不在检查中修改。只读检查不触发init、版本升级、提交、push或生产部署。

## 页面与资源

有可运行环境时用项目现有方法预览；如果构建会写输出，标清本地验证动作，保护已有产物。检查线上时记录URL/时间/版本，不把本地正确当线上通过。

从最终页面获取资源URL，按真实base解析favicon、logo、OG图和截图。检查HTTP状态、重定向目标、Content-Type、真实文件格式与内容；SVG/favicon小尺寸也看清晰度。空data URI不是品牌资源；内联SVG图标需看内容，不要求必须外部PNG。

桌面及窄移动端各看一遍；验证页面Repo入口、核心路径、弹窗关闭与键盘、空结果/失败状态。只有源码可用就报告静态检查与待浏览器验证。

## 分享

打开真实入口，确认内容来自当前网站/结果，等待生成，下载并打开PNG验证可读、完整、尺寸合适。解码二维码，访问其地址确认详情定位；不能仅与二维码图片文件名比较。

复制链接检查成功或明确可手动复制回退。Web Share检查能力检测、HTTPS与用户点击触发，不要求每个浏览器支持；取消应恢复状态。验证到系统分享弹窗即可，不替用户选联系人/发送。[Web Share API依据](https://developer.mozilla.org/en-US/docs/Web/API/Navigator/share)

OG检查生产初始HTML中字段与图片URL，必要时查看服务端不同详情路由；源码里存在一个og:image不证明平台爬虫实际显示。声明/资源通过与平台抓取实测分别记载。[Open Graph基础字段](https://ogp.me/)

## 发布与作品集

核对README/二维码/GitHub About与Homepage/站内卡片/作品集Data中URL。Cloudflare自定义域使用根路径，迁移前旧Pages路径不能无检查直接保留。明确镜像保留标注即可，不把它误作主入口。

个人作品集当前约定：holynova/holynova.github.io 的master维护data/repos.json，url为Repo、homepage为Demo，Cloudflare Worker单独部署。查询线上JSON与页面确认条目；发现缺口仅报告或按修复授权执行，不在网站检查中自动跑完整publisher流程。

## 输出发现

每项输出状态、依据、影响、最小修复与优先级；说明源码、产物、本地浏览器、线上验证做到了哪层。未知项列待验证，不粗暴扣分凑总分。复用已有合格材料，只对缺口及本次变更相关项复验。
