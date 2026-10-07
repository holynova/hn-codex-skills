# 生图提示词模板

每张图单独生成。根据正文内容替换变量，不要把多张图拼在一起。

```text
Generate one standalone 16:9 horizontal Chinese article illustration.

Visual DNA:
Pure white background. Minimalist black hand-drawn line art. Slightly wobbly pen lines. Lots of empty white space. Sparse red/orange/blue handwritten Chinese annotations. Clean absurd product-sketch feeling. No gradients, no shadows, no paper texture, no complex background, no commercial vector style, no PPT infographic look, no cute mascot poster, no children's illustration, no realistic UI.

Recurring IP character required:
Yoyo (悠悠), a cute chibi character with extremely short, fat, and chubby 2-head-height proportions (chibi look). Her giant round head takes up 50% of her entire height, with no neck and super short, thick stubby limbs. She has solid medium-dark gray bob-cut hair with a small gray sprout stem sticking straight up at the very top of her head. She has a round face with two vertical black oval dot eyes spaced close together, plain white/light gray cheeks with three tiny dark gray freckles on each cheek, and NO mouth, NO nose, and NO ears (blank face look). She wears a loose, bell-shaped light-medium gray cloak-like poncho dress with the white uppercase text 'YOYO' printed clearly on the chest, and short stubby legs with chunky soft-light-gray boots. She holds light-gray star wands. Yoyo must perform the core conceptual action, not decorate the scene. Make Yoyo curious, cute, and actively exploring or interacting with the system elements.

Theme:
{正文配图主题}

Structure type:
{结构类型：Workflow / 系统局部 / 前后对比 / 角色状态 / 概念隐喻 / 方法分层 / 地图路线 / 小漫画分镜}

Core idea:
{这张图要表达的核心意思}

Composition:
{具体画面：小黑在哪里、正在做什么、主要物件是什么、信息如何流动}

Suggested elements:
{元素1} / {元素2} / {元素3} / {元素4}

Chinese handwritten labels:
{标注词1} / {标注词2} / {标注词3} / {标注词4} / {可选标注词5}

Color use:
Black for main line art, outlines, and text. Medium-dark gray for Yoyo's hair. Light-medium gray for Yoyo's dress. Soft-light gray for Yoyo's boots and wands. Orange only for main flow/path/arrows. Light blue only for system states or secondary notes. Red only for key warnings/problems/results. Keep background pure white. Colors must be flat and clean.

Constraints:
One image explains only one core structure. Keep the main subject around 40%-60% of the canvas. Preserve at least 35% blank white space. Use at most 5-8 short handwritten Chinese labels. Do not write a title in the top-left corner. Do not write the structure type on the image. Do not make it a formal diagram, course slide, or dense explainer. Do not copy prior examples or reuse known case compositions unless explicitly requested; invent a fresh visual metaphor for this specific article. It should be clear but not instructional, interesting but not childish, strange but clean.
```

## 图像编辑提示

去掉左上角标题：

```text
Edit the provided image. Remove only the handwritten title "{要删除的文字}" and its underline from the top-left corner. Fill that area with the same clean white background, matching the surrounding blank paper. Preserve everything else exactly: characters, labels, paths, line style, composition, aspect ratio, and image quality. Do not add any new text or objects.
```

增强怪诞感：

```text
Regenerate this illustration with the same core meaning and simple layout, but make Yoyo more central to the conceptual action. Yoyo should be doing the curious exploration work that explains the idea, not standing beside the diagram. Keep it clean, sparse, hand-drawn, and cute.
```
