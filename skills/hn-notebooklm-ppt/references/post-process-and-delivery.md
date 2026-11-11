# 校对修补、画质无损化提取与极速 Web/PDF 交付

NotebookLM 产出的 PDF 在内容和交付工程上各有典型陷阱：既容易出现个别同音人名/日期/口径幻觉，又常常因为 PDF 体积大、CDN 行为与二次重采样而在网页端变得极慢、极糊。本章完整还原 `v2.0.0 → v2.1.0` 的实战方案。

---

## 1. 下载校验与非破坏性 PDF 矢量校对

### 基礎校验
- 下载使用临时文件 `*.part.pdf`，确认字节前缀为 `b'%PDF-'` 且页数 `> 0` 后再原子替换（`os.replace`）到 `assets/slides/<id>.pdf`。
- 始终在被 `.gitignore` 排除的 `work/` 目录保留一份未改动的原件（如 `work/<id>-original.pdf` 或 `work/<id>-uncompressed.pdf`）。

### 矢量叠层修补（保留原始漫画插画）
当仅有个别封面归属、同音人名、年份数字或尾页统计口径需要修正时，**不要整本重生成**，而是在 `original` PDF 上用 `pypdf` + `reportlab` 合并矢量修正层：
- 按页面实际 `mediabox` 尺寸计算缩放比例（常见设计基准如 `sx = width / 1280`, `sy = height / 714`）。
- 注册系统 CJK 字体（如 macOS `STHeiti Medium.ttc` 或跨平台 Noto Sans CJK），先绘制与局部背景色完全匹配的纯色矩形盖住错字，再绘制锐利矢量中文。
- 页脚可统一补一条极细的来源与校对说明。
- 因为修正层是纯矢量文字与色块，原页底下的高清插画 100% 无损保留。

---

## 2. Web 阅读器延迟陷阱与预拆静态 WebP 架构

### 为什么在线渲染 PDF.js 会成为性能灾难？
1. **CDN / 边缘网关剥离 `HTTP 206 Range`**：Cloudflare 等部分边缘缓存或 Worker 资源路由在默认配置下可能忽略字节范围请求（Range），导致 PDF.js 的按页流式加载失效，被迫把整本 **~8–10 MB** PDF 全部拉下来才能显示第 1 页。
2. **重型运行时开销**：`pdf.min.mjs` + `pdf.worker.min.mjs` 合计约 **1.7 MB**，再加上首次 Canvas 光栅化阻塞，在 4G 移动网络下打开第一页幻灯片往往需要 **9–22 秒**。

### 正确架构：构建期预拆 WebP + 浏览器原生 `<img>`
- **浏览用静态 WebP**：构建站点时把每套 PDF 拆为内容寻址的 `/static/<16位hash>/1.webp .. N.webp`（单页约 `150–310 KB`，均值约 `200 KB`），首屏加载从 9–22 秒降到 **~200–600 ms（提速 30x–50x）**。
- **PDF 专供下载与兜底**：原优化 PDF 仍部署到 `/assets/slides/<id>.pdf`，专门服务顶部「↓ 下载」按钮（以及无 WebP 元数据时才按需动态 `import` PDF.js 回退）。
- **缓存策略严格分离**：
  - `/static/<16位hex>/...` 的内容寻址 WebP 设置 `Cache-Control: public, max-age=31536000, immutable`；
  - 固定路径的 `/assets/slides/<id>.pdf` 与 HTML 页面**严禁设置长期 `immutable`**，保持可再验证（revalidate），确保后续矢量校对覆盖 PDF 后用户能立刻下载到新版。

---

## 3. 清晰度生命线：Solution 1（杜绝二次重采样）

### 致命误区
NotebookLM 导出的每页 PPT 本质上是固定分辨率（常见约 `1376×768`）的位图。如果简单使用 `pdftoppm -scale-to 1376 -png` 重新渲染整本 PDF，Poppler 会把已经栅格化的位图再走一遍缩放采样，实测造成 **~20 dB 清晰度损失**，细黑漫画轮廓发虚、小字边缘发糊。

### 正确的混合无损直出管线（`build_slides.py` 核心逻辑）

对每页 PDF 先用 `has_vector_overlay(pub_page)` 自动分流：

```python
def has_vector_overlay(pub_page):
    if pub_page.extract_text().strip():
        return True
    if len(pub_page.images) != 1:
        return True
    contents = pub_page.get_contents()
    if contents is None:
        return False
    if hasattr(contents, 'get_data'):
        return len(contents.get_data()) > 200
    return sum(len(s.get_object().get_data()) for s in contents) > 200
```

1. **分支 A：无矢量叠层的纯图页（绝大多数页面）**：
   - **直接提取 `pub_page.images[0].data`**（原始内嵌图像字节），绝不经过 `pdftoppm` 重渲染！
   - 若 `work/<id>-uncompressed.pdf` 存在且对应页也只有 1 张图，计算两者缩略到 `64×36` 后的 `macro_hot_tiles`（RGB 均值差 `> 12` 的像素块数 `<= 5`）。若一致，说明该页未经过其他人工整页涂改，直接取**未压缩原始流 `uncomp_page.images[0].data`**，彻底消除二次 JPEG 压缩块效应。
2. **分支 B：含矢量校对叠层的页面**：
   - 必须光栅化合并矢量文字，使用 Poppler **2x 超采样**（`pdftoppm -scale-to 2752`），再用 `Image.Resampling.LANCZOS` 缩回页面目标像素尺寸（如 `1376×768`），使修补上去的中文矢量字同样锐利无锯齿。
3. **锐利 WebP 编码**：
   - 优先调用 `cwebp -quiet -q 90 -m 4 -sharp_yuv <tmp.ppm> -o <out.webp>`；`-sharp_yuv` 对细黑线稿和高饱和红黄漫画色块的色度边缘保真度远胜普通 YUV 转换。仅在环境缺少 `cwebp` 时回退到 Pillow `quality=90, method=4`。
4. **配方级内容寻址缓存**：
   - 缓存键由 `sha256(pdf_bytes + RECIPE_TAG)[:16]` 计算（例如 `RECIPE_TAG = b'slides-v2:uncomp-q90-sharp'`），并在 `.cache-index.json` 记录 `recipe`、`size`、`mtime_ns`。升级编码参数只需更改 `RECIPE_TAG`，自动淘汰旧缓存。

---

## 4. 可下载 PDF 的体积优化（保留原件与回退）

若直接下载的原始 PDF 偏大（如 20–40 MB），可生成一份 Web 下载用优化版，但需守住三条底线：
1. 原件先备份到 `work/<id>-uncompressed.pdf`（以后提取 WebP 与做矢量修补优先基于它）。
2. 用 `pdftoppm -scale-to <max(w,h)> -png` 渲染后以 `JPEG quality=95, subsampling=0` 写入新 PDF，保留原 `mediabox` 宽高。
3. 核对输出 PDF 页数与原版严格一致，且**仅当体积确实小于原版时才替换**；否则还原原版。

---

## 5. Solution 4：比例自适应全屏与前端阅读体验

### 视口比例 CSS（消除黑边过宽与小屏挤压）
不要只用 `max-width / max-height` 让浏览器随意缩窄图片，显式结合 `100dvh` 与幻灯片宽高比（16:9 实测约为 `1.791667`）最大化填充可用舞台：

```css
.slide-img {
  width: min(96%, calc((100dvh - 56px) * 0.96 * 1.791667));
  max-width: 96%;
  max-height: 96%;
  height: auto;
  display: block;
  border-radius: 4px;
  cursor: pointer;
}
.slide-viewer:fullscreen .slide-img,
.slide-viewer:-webkit-full-screen .slide-img,
.slide-viewer.is-fullscreen .slide-img {
  width: min(98%, calc((100dvh - 52px) * 0.98 * 1.791667));
  max-width: 98%;
  max-height: 98%;
}
```

### 阅读器交互与竞态保护 Checklist
- **无闪烁翻页与预加载**：
  - 切换第 `N` 页时，先调用 `preloadSlideImg(N)`（内部使用 `new Image()`、`im.decoding = 'async'` 与 `im.decode()`），待解码完成后核对 `token === slideRenderToken && slideViewer?.open` 再赋给 visible `<img>`，同时异步预加载 `N+1` 与 `N+2`。
  - 缓存 `Map` 设置上限（如 45 张）做简单 FIFO/LRU 淘汰，避免翻多套后内存膨胀。
- **双模式全屏（兼容移动端 Safari）**：优先尝试 `requestFullscreen` / `webkitRequestFullscreen`，失败或不支持时回退到切换 `.is-fullscreen` 类（`position: fixed; inset: 0; z-index: 999999`）。
- **无障碍与多端翻页**：
  - 键盘：`ArrowLeft/Up/PageUp` 上一页，`ArrowRight/Down/PageDown/Space` 下一页，`Home/End` 首尾页，`Escape` 退出。
  - 点击热区：图片左侧 40% 区域上一页，右侧 60% 区域下一页。
  - 移动端手势：监听 `touchstart`/`touchend`，水平滑动距离 `> 40px` 且大于垂直位移时翻页。
- **篇末连看引导**：末页弹出 End Card，提供同专题内上一篇/下一篇幻灯片一键连看（目录未加载时异步拉取并原地刷新按钮）及「重看」。
- **渐进显露浮动入口**：主操作按钮随页面滚动离开视口后，侧边目录自动滑出「看 PPT」快捷按钮，避免页面顶部堆砌重复 CTA。

---

## 6. 章节配图与发布前校验

- **封面与正文插图**：从幻灯片选取封面（`第 0 页`）与均匀分布的故事页（如共 7 张），若经人工筛选则固化到 `pages.json`（`reviewed: true`, `samples: [...]`），避免重建时覆盖人工挑选的好图；再派生封面（`480w / 768w / 960w`）与正文插图（`640w / 1080w`）多尺寸 WebP。
- **静态构建校验**：遍历 `dist/**/*.html` 验证站内所有链接与资源存在、确认所有 PDF 含 `%PDF-` 头、确认无 `state/`、`work/`、`config.json`、`transcript.*`、`.env` 泄漏进 `dist/`、确认单文件体积满足宿主上限（如 `< 25 MiB`）。
- **线上验证闭环**：部署后用真实 HTTPS 请求逐一抽检或批量校验首页、专题页、搜索索引、单篇页面、WebP 幻灯片、插图与可下载 PDF 的状态码和内容摘要，全部通过才记为 `publication_status = verified`。
