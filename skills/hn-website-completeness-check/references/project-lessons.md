# 从个人项目提炼的检查经验

2026-10-01 阅读的实例只用来说明检查方法，不是对这些网站做完整生产审计。除rubber-stamp固定提交、作品集master和GitHub About外，以下网页来自本地项目快照，可能落后线上；使用技能时必须核实目标项目的真实来源和部署。

- **rubber-stamp**：[main f3d47486 的 index.html](https://github.com/holynova/rubber-stamp/blob/f3d47486ebcd097c45e8067153cfac4a6063178c/index.html) 有单字「印」品牌标识、meta description、缩略/详情图片分层、分享卡/二维码/原图下载；head中没有favicon引用，页面没有可见项目Repo入口。logo、favicon、Repo链接、分享不是一项的替代物。README中的手账等功能描述也应与该分支实际功能核对，不能因为文案看起来完整就判定合理。
- **print-atlas 本地快照**：根index.html声明 `rel="icon" href="data:,"`，这只有空favicon标签；导航/页尾有项目Repo，README含真实截图、Cloudflare主入口和Pages镜像。这说明「有link标签」不足以判图标通过，主入口和镜像应有明确区分。设计过的PRESS / ATLAS字标可作为logo，不必强制生成位图品牌。
- **my-design-system 本地快照**：页头有Repo入口，README含截图与Pages二维码。独立代码、仓库README和二维码需要一起核对；在Cloudflare迁移场景下判断是否仍指旧主入口，不能一概把所有Pages镜像删掉。
- **brand-etymology 本地构建快照**：根index.html含description/theme-color，但canonical指向localhost。它是本地产物，不能据此直接宣布线上SEO错误；应检查实际生产输出。GitHub description和Homepage独立于这个文件，不能由本地head推断远端元数据。
- **xiaosang.cc 作品集**：[master首页](https://github.com/holynova/holynova.github.io/blob/master/index.html) 引用favicon.png与作者头像，卡片通过data/repos.json给Repo/Demo；首页作者Profile不是子项目页面Repo入口的替代。源码数据、截图和线上Worker的更新分别核实。
- **GitHub About读取**：本次读取rubber-stamp、print-atlas和brand-etymology的Homepage均仍为github.io地址；这提示代码/README已使用Cloudflare也不代表About同步。只能在核实最终主入口后判断是否需改，不能由一个旧地址自动推断项目未部署。

仓库已有的hn-share-card、hn-visual-asset-pipeline、hn-web-analytics与hn-project-publisher分别提供分享卡、视觉资源、统计与发布实现。新检查技能只确定缺口并路由，不复制整套实现或扩张用户范围。
