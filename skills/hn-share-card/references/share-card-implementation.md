# 分享卡片实现参考

本文件用于实际编写或迁移分享卡片时加载。它描述通用契约，不替代项目已有的视觉设计和组件约定。

## 推荐数据契约

```ts
type ShareCardPayload = {
  scope: "result" | "site";
  title: string;
  subtitle?: string;
  description: string;
  result?: {
    summary?: string;
    facts?: Array<{ label: string; value: string }>;
    tags?: string[];
    source?: string;
    date?: string;
    status?: string;
  };
  brand: {
    name: string;
    label?: string;
    accent?: string;
  };
  url: string;
  qrUrl: string;
  logoUrl?: string;
  fileName?: string;
};
```

所有字段在进入渲染器前归一化。缺失值使用明确 fallback，不要让 `undefined`、`[object Object]` 或过长的自由文本直接出现在图片上。用稳定 `result_id` 关联事件，但不要把原始搜索词当作 ID。

## 目标 URL 规则

按以下优先级选择二维码目标：

1. 已存在、可公开访问的结果详情页，例如 `/result/stable-id/`。
2. 首页或结果页加短小、可复现、经过编码的筛选参数。
3. 如果结果只存在于浏览器内存且公开内容很短，才考虑 compact query；先确认不会产生隐私泄露、URL 过长或分享失效。
4. 私密、用户生成或很长的结果需要后端短链/分享快照，并设置过期策略；静态站不要伪装成有持久化能力。

可以为 QR 目标加入 `utm_source=share_card&utm_medium=qr`，但应保留原有路径、语言和结果 ID。不要让 `utm` 变成 canonical URL，也不要把完整用户输入编码到 UTM。

## Canvas 绘制顺序

用固定坐标系和动态高度，保证同一 payload 在不同 viewport 生成同一张图：

1. 等待 `document.fonts.ready`；设定固定宽度（常用 1080）和足够的安全边距。
2. 绘制背景、品牌色块、边框和卡片底板。
3. 绘制品牌标识与标题，先测量文字再换行。
4. 绘制结果摘要、facts、标签和状态；为 `status` 保留原始语义，例如“有争议”“待核实”。
5. 生成二维码到独立 canvas，再绘制到卡片；二维码周围保留 quiet zone，使用高对比度颜色。
6. 绘制目标地址的短版 fallback 和底部品牌信息。
7. `canvas.toBlob(resolve, "image/png")` 生成文件，并用稳定 slug 命名。

中文换行不能只依赖空格。优先使用 `Intl.Segmenter("zh-CN", { granularity: "word" })`，不可用时逐字符 fallback；避免让 `，。！？；：` 出现在行首，避免 `（《「` 出现在行尾。标题、摘要、facts 都要有最大行数，超出时使用省略号或明确的“查看完整结果”。

## 二维码

优先使用项目已有的 QR 库（例如已安装的 `qrcode`），在浏览器本地生成 QR canvas；不要依赖第三方二维码图片 URL。示意：

```ts
const qrCanvas = document.createElement("canvas");
await QRCode.toCanvas(qrCanvas, payload.qrUrl, {
  width: 180,
  margin: 1,
  color: { dark: "#1f1b17", light: "#fffdf7" },
});
context.drawImage(qrCanvas, qrX, qrY, qrSize, qrSize);
```

生成后用二维码扫描器或解码工具验证，不要只肉眼判断“看起来像二维码”。目标 URL 变化时重新生成，不要复用旧 canvas。

## 预览与操作模板

可以用 `<dialog>` 作为跨框架的最小结构；若项目已有 modal，保留其 focus trap 和样式：

```html
<dialog data-share-dialog>
  <div class="share-card-preview">
    <canvas data-share-canvas aria-label="分享卡预览"></canvas>
  </div>
  <div class="share-card-actions">
    <button data-share-download type="button">下载 PNG</button>
    <button data-share-native type="button" hidden>系统分享</button>
    <button data-share-copy type="button">复制链接</button>
  </div>
  <p data-share-status aria-live="polite"></p>
</dialog>
```

操作逻辑应保持以下回退顺序：

```ts
const file = new File([blob], fileName, { type: "image/png" });

if (navigator.share && navigator.canShare?.({ files: [file] })) {
  await navigator.share({ title, text: description, url, files: [file] });
} else {
  const anchor = document.createElement("a");
  anchor.href = URL.createObjectURL(file);
  anchor.download = file.name;
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  window.setTimeout(() => URL.revokeObjectURL(anchor.href), 1000);
}
```

用户取消 `navigator.share()` 时不显示成系统错误；恢复为“可以下载图片或复制链接”。浏览器不支持 `navigator.canShare` 时不要盲目显示图片系统分享按钮。

## 安全与兼容性

- Canvas 绘制文本比 `innerHTML` 更适合处理用户结果；如果必须用 DOM-to-image，使用 `textContent`，不拼接原始 HTML。
- 外部图片可能使 canvas 变成 tainted，导致 `toBlob()` 失败；优先同源 logo，或设置 `crossOrigin="anonymous"` 并确认 CDN 发送 `Access-Control-Allow-Origin`。
- 字体未加载会导致测量和截图不一致；等待字体并准备 system font fallback。
- 生成卡片时暂时隐藏的 canvas 仍需在 DOM 中有可计算尺寸；不要在 `display:none` 下依赖布局测量。
- 文件下载的 Object URL 释放不能早于浏览器消费下载动作；移动端多等一个事件循环或约 1 秒更稳。
- 分享卡是公开传播物，默认不加入邮箱、手机号、内部 ID、管理 URL、私有 API 响应或完整用户输入。
- 若图片里展示来源或统计数字，保留日期/时间范围，避免把时间敏感的“最火”写成无日期的官方排名。

## 验收矩阵

| 场景 | 必测结果 |
| --- | --- |
| 结果级入口 | 标题、摘要、关键字段、二维码指向该结果 |
| 网站级入口 | 项目介绍、站点 URL、二维码指向首页 |
| 长中文/英文标题 | 换行自然，无裁切、重叠和行首标点 |
| 空 logo/空字段 | 有 fallback，卡片仍可生成 |
| 桌面下载 | PNG 存在、1080 宽、内容完整 |
| iOS/Android 浏览器 | 能力支持时系统分享，否则下载/复制 fallback |
| 二维码扫描 | URL 可打开，结果/语言状态不丢失 |
| 生成失败/CORS | 显示错误，复制链接仍可用 |
| analytics 已接入 | 事件只含稳定低敏感字段 |
