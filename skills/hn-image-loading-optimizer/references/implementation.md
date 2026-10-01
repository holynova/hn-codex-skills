# 可迁移实现与参数

本参考区分原项目经验与增强实现，目标项目已有框架组件时直接补生命周期与失败状态，不重复安装控制器。

## 三层图片契约

```js
const item = {
  id: "stable-id",
  width: 1122,
  height: 1402,
  thumbnail: "/images/thumbnails/item.webp",
  detail: "/images/detail_webp/item.webp",
  original: "/images/item.png",
  alt: "作品名称与必要描述",
};
```

上述仅展示字段，不要求改变既有数据模型。已有 URL/base path、中文/空格文件名、CDN 参数应由对应 URL/路由工具解析；简单 .png 字符替换只适用于已验证的同目录 PNG 数据。避免同 stem 的 jpg/png 输出撞名。

Sharp 参数来源：缩略图 `resize({ width: 400, withoutEnlargement: true }).webp({ quality: 82, effort: 4 })`；详情 `webp({ quality: 85, effort: 4 })`。详情可按显示宽×DPR设置上限，但这是目标项目新增取舍，源案例没有缩尺寸。可以按需增加 srcset/sizes，不能声称源案例已经实现。

## 解码后升级控制器

[../assets/progressive-image.mjs](../assets/progressive-image.mjs) 提供原生 DOM 参考：监听器先安装，再设置 src；兼容缓存 complete；支持 decode 时等待成功；失败保留预览；关闭/切项使旧结果失效；原图回退默认关闭，避免失败时自动下载 MB 图片。

```js
import { createProgressiveImageController } from "./progressive-image.mjs";

const controller = createProgressiveImageController(document.querySelector("#detail-image"));

async function openItem(item) {
  const state = await controller.show({
    thumbnail: item.thumbnail,
    detail: item.detail,
    original: item.original,
    alt: item.alt,
    allowOriginalFallback: false,
  });
  if (state.status === "preview" && state.error) {
    // Display a non-blocking retry indication while keeping the thumbnail.
    console.warn("High-resolution image unavailable", state.error);
  }
}

function closeDetail() {
  controller.invalidate();
  document.querySelector("#detail-dialog").close();
}
```

引用资源应复制到目标项目真实模块目录，并按框架调整调用。保留占位布局、缩略图自己的 load/error 状态与交互，本控制器不负责弹窗 UI、thumbnail 失败占位或网络超时。每个视图一个控制器；销毁/切换数据集也调用 invalidate。

token 只抑制过期写入，不取消请求。需要节省快速翻页带宽时增加限并发/延迟高清请求或支持取消的 fetch+Blob 方案；后者必须处理 CORS、内存与 Object URL 生命周期。正常浏览优先详情 WebP，原始 PNG 留给下载/打印；允许回退原图时只尝试一次。

## 有界失败与滚动回退

列表图片回退用明确阶段（thumb → 可选 detail/original → placeholder），最后清除 error handler，不能比较绝对 img.src 和相对字符串决定重试。placeholder 失败时用文字/背景停止，不能循环再赋 src。确保错误状态停止骨架动画。

图片懒加载沿用浏览器；列表增量加载沿用分页。IntersectionObserver 不支持时显示「加载更多」按钮；末尾隐藏按钮、observer disconnect，过滤后重置结果。不要把 sentinel 调用与滚动处理叠成两个重复追加入口。

`content-visibility` 与 contain-intrinsic-size 应用在合适卡片边界，并按真实高度调整估计值，验证滚动与辅助技术可见性。混合横/竖图可用元数据计算 aspect-ratio；不是强制裁成4:5。加载反馈与 opacity/transform 动画适配 prefers-reduced-motion。

## 依赖与缓存边界

辅助模块按需 import/加载单个 Promise；请求失败后移除 rejected 条目，允许用户重试。已存在 eager script 时不能宣称按需加载达成。图片同 URL 复用依赖浏览器/HTTP 缓存响应，不需给每张图片建常驻 Image；若建立应用缓存必须有界。

资源内容发生变化时沿用哈希文件名或既有版本策略；不要给每次请求加时间戳破坏缓存，也不要对会覆盖的同名图片无条件设置长期 immutable。原项目没有自定义 Cache-Control 证据，不能归纳成它已实现的技巧。

## API 依据

- [HTMLImageElement.decode](https://developer.mozilla.org/en-US/docs/Web/API/HTMLImageElement/decode)：成功解码后再呈现，不以 decoding 属性代替 Promise。
- [原生懒加载](https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/Lazy_loading)：图片请求按接近视口延后，实际预取阈值由浏览器决定。
- [content-visibility](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/content-visibility)：控制渲染工作，不替代网络调度。
