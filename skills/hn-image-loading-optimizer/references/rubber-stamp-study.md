# rubber-stamp 图片优化代码研究

阅读日期：2026-10-01。基线：[holynova/rubber-stamp main 提交 f3d47486](https://github.com/holynova/rubber-stamp/tree/f3d47486ebcd097c45e8067153cfac4a6063178c)。以下是该提交代码与 GitHub tree 文件大小的检查，不是生产网络性能实测。

## 完整资产核对

从 data.js 的 11 个分类提取 296 个唯一 output；每个原图均有对应 thumbnail/detail WebP，没有缺失。体积取固定提交的 Git blob size，仅统计被数据引用的资产，不包括备份和截图。

| 层级 | 文件数 | 合计 | 平均每张 |
| --- | --- | --- | --- |
| PNG 原图 | 296 | 815.57 MiB | 2821.42 KiB |
| thumbnail WebP | 296 | 10.52 MiB | 36.39 KiB |
| detail WebP | 296 | 90.71 MiB | 313.81 KiB |

相对同组原图，缩略资产字节少约 98.71%，详情资产少约 88.88%。这是资产体积比例，不代表首屏速度同比提升，也不保证其他项目得到相同结果。页面注释中的 98.8% 与 ~280KB 不是本次实测值。

## 资产生成与复用

1. **提前生成缩略图**：Sharp 按 400px 宽、等比例高度、withoutEnlargement、WebP quality 82/effort 4 转换，不在浏览器逐张处理 MB 图。[generate_thumbnails.js:33–54](https://github.com/holynova/rubber-stamp/blob/f3d47486ebcd097c45e8067153cfac4a6063178c/scripts/generate_thumbnails.js#L33-L54)
2. **生成独立高清压缩层**：detail WebP quality 85/effort 4；没有 resize，保留输入像素尺寸，和原始 PNG 分离。[generate_detail_webp.js:18–58](https://github.com/holynova/rubber-stamp/blob/f3d47486ebcd097c45e8067153cfac4a6063178c/scripts/generate_detail_webp.js#L18-L58)
3. **保留目录层级与稳定映射**：缩略/详情插入各自目录并把 PNG 扩展名替成 WebP，缺少路径时返回轻量 placeholder.svg。[index.html:1557–1565](https://github.com/holynova/rubber-stamp/blob/f3d47486ebcd097c45e8067153cfac4a6063178c/index.html#L1557-L1565)
4. **详情增量生成**：从 data.js 提取 output、Set 去重，只处理引用的 PNG；目标比源新且大于 1000 字节时跳过，统计原/新字节。缩略脚本递归扫描时排除 thumbnails、隐藏和 backup 路径，处理是串行 await。[详情生成](https://github.com/holynova/rubber-stamp/blob/f3d47486ebcd097c45e8067153cfac4a6063178c/scripts/generate_detail_webp.js#L9-L75)、[缩略扫描](https://github.com/holynova/rubber-stamp/blob/f3d47486ebcd097c45e8067153cfac4a6063178c/scripts/generate_thumbnails.js#L8-L21)
5. **源素材标准化与验收**：特定城市图片裁到 1122×1402，PNG compressionLevel 8；finalize 脚本记尺寸/字节，制作 240×300 联系表预览并查尺寸/最低字节。裁切改变艺术内容，属于该项目生产流程，不能作为通用加载优化自动套用。[crop_world_cities.js:129–134](https://github.com/holynova/rubber-stamp/blob/f3d47486ebcd097c45e8067153cfac4a6063178c/scripts/crop_world_cities.js#L129-L134)、[finalize_gallery.py:18–49](https://github.com/holynova/rubber-stamp/blob/f3d47486ebcd097c45e8067153cfac4a6063178c/finalize_gallery.py#L18-L49)

## 列表、请求与布局

6. **列表只用缩略层**：renderCardHtml 设置 thumbUrl，不正常加载所有原图。[index.html:1825–1844](https://github.com/holynova/rubber-stamp/blob/f3d47486ebcd097c45e8067153cfac4a6063178c/index.html#L1825-L1844)
7. **首屏与后续区别调度**：前 4 张 eager + fetchpriority high，其余 lazy + decoding async。4 是源项目参数，不是所有布局都应预取 4 张。[同上](https://github.com/holynova/rubber-stamp/blob/f3d47486ebcd097c45e8067153cfac4a6063178c/index.html#L1825-L1844)
8. **12 张一批追加 DOM**：初始只 appendNextFeedChunk，滚动才继续；insertAdjacentHTML 追加而非每次重建整个列表。[index.html:1819–1875](https://github.com/holynova/rubber-stamp/blob/f3d47486ebcd097c45e8067153cfac4a6063178c/index.html#L1819-L1875)
9. **提前触发追加**：IntersectionObserver 观察列表哨兵，rootMargin 300px 0px；重设先 disconnect 旧 observer，末批隐藏哨兵。[index.html:1877–1890](https://github.com/holynova/rubber-stamp/blob/f3d47486ebcd097c45e8067153cfac4a6063178c/index.html#L1877-L1890)
10. **离屏跳过布局/绘制工作**：卡片 content-visibility auto + contain-intrinsic-size 200px 320px；不等于虚拟化，也不直接替代图片请求懒加载。[index.html:277–288](https://github.com/holynova/rubber-stamp/blob/f3d47486ebcd097c45e8067153cfac4a6063178c/index.html#L277-L288)
11. **固定占位与渐进反馈**：媒体框 aspect-ratio 4/5，图片 width/height 400/500；骨架背景先占位，加载后淡入、停止 shimmer，降低跳动与等待感。[CSS:296–327](https://github.com/holynova/rubber-stamp/blob/f3d47486ebcd097c45e8067153cfac4a6063178c/index.html#L296-L327)、[加载回调](https://github.com/holynova/rubber-stamp/blob/f3d47486ebcd097c45e8067153cfac4a6063178c/index.html#L1835-L1844)
12. **避免无效重渲染**：切相同分类且已有结果时提前 return；搜索输入 100ms 防抖；筛选/分类切换重新清空并渲染第一批。[index.html:1892–1953](https://github.com/holynova/rubber-stamp/blob/f3d47486ebcd097c45e8067153cfac4a6063178c/index.html#L1892-L1953)

## 详情与连续浏览

13. **先显示当前缩略图**：打开详情立即赋 thumbUrl，复用已访问 URL 的浏览器资源缓存，不主动模糊化图片。[index.html:2009–2027](https://github.com/holynova/rubber-stamp/blob/f3d47486ebcd097c45e8067153cfac4a6063178c/index.html#L2009-L2027)
14. **后台加载、先解码再切换**：new Image 请求 detail WebP，await decode 后才给主图赋高清 URL；目标是避免解码等待带来的空白，实际表现仍需浏览器验证。[index.html:2028–2049](https://github.com/holynova/rubber-stamp/blob/f3d47486ebcd097c45e8067153cfac4a6063178c/index.html#L2028-L2049)
15. **防旧响应覆盖新图片**：每次 ++currentHiresToken，swap 核对 token 与 modal index；快速滑动时旧结果丢弃。[index.html:2019–2035](https://github.com/holynova/rubber-stamp/blob/f3d47486ebcd097c45e8067153cfac4a6063178c/index.html#L2019-L2035)
16. **兼容解码 API 与格式失败**：无 decode 用 onload；详情 WebP 失败回退原图。这是源实现的意图，后文指出其失败分支问题。[index.html:2036–2049](https://github.com/holynova/rubber-stamp/blob/f3d47486ebcd097c45e8067153cfac4a6063178c/index.html#L2036-L2049)
17. **只预取相邻轻量图**：前后 slide 与预取 Image 都使用缩略 URL，不预加载两张大原图。同 URL 的额外 Image 请求通常依赖浏览器复用，源码没有自己的图片 LRU 缓存。[index.html:1979–2006](https://github.com/holynova/rubber-stamp/blob/f3d47486ebcd097c45e8067153cfac4a6063178c/index.html#L1979-L2006)
18. **只复用三个轮播位置**：前/当前/后 img，不为全部图片创建 slide；transform translate3d 和有限 will-change 移动轨道，动画结束重置中心并换内容。不是每张都开 GPU 图层。[HTML:1367–1377](https://github.com/holynova/rubber-stamp/blob/f3d47486ebcd097c45e8067153cfac4a6063178c/index.html#L1367-L1377)、[CSS:536–574](https://github.com/holynova/rubber-stamp/blob/f3d47486ebcd097c45e8067153cfac4a6063178c/index.html#L536-L574)、[finishSlide](https://github.com/holynova/rubber-stamp/blob/f3d47486ebcd097c45e8067153cfac4a6063178c/index.html#L2063-L2082)

## 分享、下载与辅助成本

19. **分享预览与输出分开**：分享弹窗用缩略图，保存海报才加载原图并按 naturalWidth/Height 计算画布尺寸；原图失败尝试缩略图。不会在打开分享弹窗时先请求 PNG。[预览](https://github.com/holynova/rubber-stamp/blob/f3d47486ebcd097c45e8067153cfac4a6063178c/index.html#L2169-L2187)、[导出加载](https://github.com/holynova/rubber-stamp/blob/f3d47486ebcd097c45e8067153cfac4a6063178c/index.html#L2254-L2288)
20. **原图下载按操作触发**：单图 fetch 原图，收藏批量下载逐张 await fetch，进度/禁用按钮防重复提交，ZIP 完成后下载，不在列表初始化下载所有 PNG。串行仍会累计 ZIP 数据。[index.html:1685–1763](https://github.com/holynova/rubber-stamp/blob/f3d47486ebcd097c45e8067153cfac4a6063178c/index.html#L1685-L1763)
21. **Blob 输出与临时 URL 清理**：Canvas toBlob/下载 createObjectURL，下载后 revoke，避免持续留住 URL 引用；源码立即 revoke 的时机需要浏览器确认。[ZIP](https://github.com/holynova/rubber-stamp/blob/f3d47486ebcd097c45e8067153cfac4a6063178c/index.html#L1718-L1731)、[海报](https://github.com/holynova/rubber-stamp/blob/f3d47486ebcd097c45e8067153cfac4a6063178c/index.html#L2389-L2402)
22. **辅助依赖单次按需加载**：loadScriptOnce 用 Map 缓存 Promise，二维码库到分享/导出时才加载。JSZip 虽也有该条件分支，但 HTML 仍 eager 引入 jszip.min.js，因此不能声称 ZIP 库已经延迟加载。[loader](https://github.com/holynova/rubber-stamp/blob/f3d47486ebcd097c45e8067153cfac4a6063178c/index.html#L1537-L1552)、[eager JSZip](https://github.com/holynova/rubber-stamp/blob/f3d47486ebcd097c45e8067153cfac4a6063178c/index.html#L1485-L1487)、[QRCode](https://github.com/holynova/rubber-stamp/blob/f3d47486ebcd097c45e8067153cfac4a6063178c/index.html#L2206-L2225)
23. **少加载无关资产**：系统字体栈无额外字体下载；Worker .assetsignore 排除备份、联系表、生成源文件。上传排除减少发布体积，不代表所有剩余文件会被浏览器下载；Workers 配置不证明自定义缓存策略。[字体](https://github.com/holynova/rubber-stamp/blob/f3d47486ebcd097c45e8067153cfac4a6063178c/index.html#L51-L59)、[.assetsignore](https://github.com/holynova/rubber-stamp/blob/f3d47486ebcd097c45e8067153cfac4a6063178c/.assetsignore)
24. **有可重复测量入口**：measure_perf 在 430×932 冷缓存环境启动 Chrome/CDP，测 FCP、DCL、load、资源字节/数与 DOM，默认 3 次取平均。它没有采集 LCP/CLS，也没有网络节流或详情切换验证；本次没有运行其浏览器基准。[measure_perf.js](https://github.com/holynova/rubber-stamp/blob/f3d47486ebcd097c45e8067153cfac4a6063178c/scripts/measure_perf.js#L136-L230)

## 迁移时必须修正的边界

- 列表 onerror 比较的是 img.src 绝对 URL 与 x.output 相对路径，判断可能永远不相等，原图也失败时可能反复赋同 URL。要用显式 fallback stage、统一绝对 URL，且终止于稳定占位；不要照抄这个 handler。
- 详情原图 decode 失败仍 catch(swapToHires)，可能把失败原图替换到已正常缩略图上；无 decode 分支保留 onerror 后再设原图也可能循环。新实现只在成功解码后替换、回退有界、最终保留缩略图。
- closeNoteDetail 没有让 token 失效，隐藏窗口仍可能被旧任务写入；新实现关闭/卸载也 invalidate。token 没有 AbortController，不会阻止旧请求消耗带宽。
- 前 4 high 可能过多；400px 在大卡片/高 DPR 上可能不足；统一 4/5 并不适合混合宽高比。都需按项目测量。
- 没有 IntersectionObserver 时初始 12 张以后没有自动追加回退；长滚动 DOM 仍不断增加，非完整窗口化。content-visibility 不自动减少网络请求或节点数。
- 缩略脚本每次重建全部目标，详情 mtime+字节判断不覆盖编码参数变化。不要把两个生成器都说成完整增量缓存。
- loadScriptOnce 缓存 rejected Promise 后无法重试；辅助库是否真正 lazy 要看 HTML。详情预取与 DOM 相邻图使用同 URL，不保证零次额外请求。
- 原图导出与缩略回退都失败时源代码仍 resolve，后续 drawImage 可能失败。需要明确拒绝并保留错误/重试状态。大量 ZIP 的串行请求不限制最终占用。
- measure_perf 用 transferSize || encodedBodySize，会将真实零传输的缓存项以 encoded 体积计入；总字节未计完整文档，固定 3.5 秒不代表所有资源结束，跨源 TAO 限制会影响数字。应分开网络传输、压缩体积与缓存命中，报告测量窗口。

## 来源中未实现，不得归为既有技巧

没有 srcset/sizes 多尺寸选择、AVIF 协商、Service Worker、图片 LRU、请求 AbortController、网络 Save-Data 自适应、完整列表虚拟化或图片 CDN 变换规则。需要时可建议，但明确属于新增方案。上述源码问题是静态分析发现，本次没有故障注入到上游站点。
