---
name: hn-flowing-pen-art
description: 根据主题、文字或参考照片创作旧纸深蓝墨色、随形排线与流动线场的钢笔画。适用于复古钢笔插画、象征主义线描、风云旋涡排线及此风格的系列作品；不用于普通速写、木刻印章或网点海报。
---

# 流线钢笔画

将任意主题转成有体积、有线条节奏的钢笔插画。默认深蓝墨与暖旧纸；风格来自线条组织，而非复古滤镜。用户指定颜色、背景、题材与比例时，以其要求为准。

## 例图是必需输入

五张例图是本 skill 的核心工作资源，不是可省略的装饰：

1. 先读 [例图索引与视觉分析](references/examples.md)。
2. 每次任务生成前，用可用的图片查看工具打开至少两张例图：一张匹配当前主体，一张提供不同构图。多图任务可在开始时集中查看。
3. 实际作图时，至少选一张已查看例图，作为 **style reference only** 传入生成工具；工具允许时通常选两张。按当前工具文档使用路径或会话图片机制。用户参考照片另标为主体/结构参考，避免角色混淆。
4. 所有相对路径从本 skill 所在目录解析，不能依赖作者机器的路径或旧会话。
5. 若例图缺失、无法查看或工具无法接收图片参考，说明限制，先恢复资源或选择支持图片参考的工具；不要声称完成本 skill 的视觉匹配。用户接受限制时可交付文字提示词，但须标注未完成视觉验证。

| 例图 | 必需随包文件 | 可借鉴的线条与构图 |
|---|---|---|
| 守潮人 | [01-tide-keeper.webp](references/images/01-tide-keeper.webp) | 小人物、大环境；海浪与风云的长弧排线 |
| 蛾之梦 | [02-moth-dreamer.webp](references/images/02-moth-dreamer.webp) | 近景侧脸；纸色留白与密集发丝对比 |
| 林间白鹿 | [03-white-stag.webp](references/images/03-white-stag.webp) | 横向动物场景；枝干框景，疏密建立主体 |
| 螺旋之城 | [04-spiral-city.webp](references/images/04-spiral-city.webp) | 俯视空间；屋瓦、石阶、拱桥的分面排线 |
| 贝壳与飞鸟 | [05-shell-atlas.webp](references/images/05-shell-atlas.webp) | 静物变形；壳体、书页与飞鸟形成走势 |

## 风格语法

- **纸与墨**：柔和麦黄、赭米色旧纸，纤维与斑驳轻微；墨为近黑深蓝。默认只有纸与一种墨色，不以水彩色块替代排线。
- **轮廓**：细而有力度，允许断笔、轻微抖动与线宽变化。避免所有物体都有等粗闭合描边。
- **体积**：排线随表面转折。面颊用短弧，衣褶用折线束，岩石/屋顶用不同方向的直线面，贝壳用沿曲率展开的弧线。
- **明暗**：用线距、长度与叠加控制。亮部保留完整纸色，暗部加密但保留线间隙；交叉排线用于局部加深，不铺满全图。
- **流动**：选一条主走势，令风、云、水、发丝、植物或布料形成连续长弧线场。线束在对象边缘停顿、转向或断开，不能像均匀条纹滤镜一样穿过所有主体。
- **节奏**：长弧与短直线、疏处与密处交替。焦点清楚，细节有层级，旧纸质感退到墨线之后。
- **气质**：复古书籍插图、诗性与轻微象征主义。人物、动物、建筑、静物均可；天使、女性、灯塔、旋涡都不是必选元素。

## 作图流程

1. 根据用户主题确定主体、情绪、画幅。未指定时自行选择，不为常规艺术选择反复询问。
2. 查看和选择例图，提取线条组织，不复制人物身份、物件组合或具体布局。
3. 选择焦点与主走势，分配亮部、暗部和安静区域。写清视角、主体尺度、空间层次与排线方向。
4. 使用可用的图像生成工具创作真正的位图。Codex 内置 image_gen 可用时优先使用；不默认改用需 API key 的 CLI，不用 SVG/CSS 模拟替代成图。
5. 每个作品独立生成。系列保持纸、墨与排线语言一致，让主题、视角、主体尺度、线场形态或画幅产生变化；除非用户要求同构图，避免只替换中心人物的道具。五张系列通常选择至少三种构图，横竖幅只是可选手段。
6. 查看成图并按下方验收。偏离时针对具体问题调整；工具持续失败则如实报告，不把提示词当已生成作品。
7. 多图交付保存每张最终图，保留主题、例图选择和完整提示词的对应关系。按需打包，报告保存位置，不覆盖用户原图。

## 提示词骨架

在以下英文风格核心后追加当前画面说明；用户请求提示词时可同时提供中文版本。它是可调整骨架，不是固定题材模板。

> Create one original fountain-pen illustration. Attached image(s) are STYLE REFERENCES ONLY: borrow the ink, paper, contour hatching and rhythmic line organization, not their subjects or layout. Deep midnight-blue ink on warm softly aged ochre paper. Fine hand-drawn parallel contour hatching follows the volume of each surface; short angular line bundles describe hard planes and fabric folds. Long curved line fields describe environmental movement. Build shadows through line density and local overlaps; preserve untouched paper for highlights and breathing space. Broken irregular strokes, restrained line-weight variation, clear focal hierarchy, sculptural forms, poetic antique book-illustration atmosphere. Subtle paper texture. No watercolor washes, gradients, uniform digital stripe overlay, large flat black fills, text, signature, border, collage or watermark.

接着写：

- **Scene/subject**：明确当前主题，不沿用例图物件。
- **Composition**：画幅、视角、焦点尺度与空间层次。
- **Line choreography**：主运动方向，各材质排线如何分工。
- **Light and negative space**：哪些区域疏、哪些密，哪里保留纸色。
- **Input roles**：每张例图的风格角色；有用户图片时说明需保留的结构。
- **User constraints**：准确记录数量、文案、背景、比例等；用户要求文字时移除默认 no text，保留原文。

具体应用示例见 [提示词示例](references/prompts.md)，按需阅读、替换其中主题和构图，不把示例当题材白名单。

## 视觉验收

- 放大后能看清有方向的钢笔线，不是灰色噪点、涂抹或滤镜条纹。
- 排线随体积转折，环境线场与主体边界协调。
- 明部是纸，深色主要由密线构成；纸纹没有压过墨线。
- 一眼能找到焦点，背景不会吞没人脸、动物轮廓或主要建筑。
- 人物肢体、动物结构、建筑透视可读；超现实变形有明确过渡。
- 系列变化出现在构图与线条走势，同时仍属于同一套视觉语言。
