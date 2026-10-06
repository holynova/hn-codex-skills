# 配色与提示词配方

## 基础配方

将括号内容替换为具体场景，不把占位词原样交给生成工具。

> Create one original multicolor woodcut-style fine-art print of [subject and distinguishing structures], seen from [viewpoint]. Arrange [foreground, main subject, distant shapes] with [composition and depth]. Use broad flat interlocking ink blocks, hand-carved angular edges and directional gouge marks, subtle dry-ink grain and small unprinted flecks on ivory paper. Build [clouds / snow / reflections / foam / steam] with reserved paper-white shapes. Palette: [deep anchor ink], [two or three main inks], [light ink], [small accent]. Fine structural details remain carved shapes rather than photographic shading. [Format] with a clean narrow ivory paper margin. No smooth gradients, glossy 3D surfaces, photographic realism, vector-perfect outlines, excessive distress, text, signature or watermark.

不必逐字复用整个英文骨架；它表达墨块、刀痕、留白和构图的关系。人物与地标细节要落实成可画出的形状，避免“梦幻、震撼、高级”这类不指向具体画面的词堆叠。

## 配色角色

| 氛围 | 深色锚点 | 主墨色 | 浅色与点睛 | 纸白用途 |
| --- | --- | --- | --- | --- |
| 青绿山河 | 深松绿 | 青绿、薄荷青 | 嫩黄绿、浅赭 | 云海、山路 |
| 砖红街景 | 蓝灰或深棕 | 砖红、赭黄 | 浅蓝灰、梧桐金 | 天光、路面 |
| 秋枫寺院 | 墨绿 | 金黄、枫红 | 湖蓝、浅青 | 天际、池水光 |
| 紫暮山谷 | 深靛 | 灰紫、青蓝 | 珊瑚橙、淡杏 | 雪峰、薄云 |
| 节庆烟火 | 深绿或深棕 | 朱红、橙赭 | 米黄、冷青灰 | 蒸汽、灯火间隙 |
| 海浪与月夜 | 深靛 | 群青、青蓝 | 灰紫、淡金 | 浪花、月下水光 |

## 三个可迁移场景

- **山谷小火车**：高处斜俯视，暗色针叶林压住近景，赭红列车沿弯曲铁路进入中景，冷蓝雪峰和纸白云海在后；青蓝、墨绿与列车红形成主次。避免把画面画成旅游海报，默认不加标题。
- **雨后旧城咖啡馆**：街角三分之四视点，赭红石墙、深紫树影与淡杏天色，纸白湿路倒影通向远处门洞；桌椅和路人用少量刻线交代。保留木刻硬边，不能用水彩渗色替代刀痕。
- **冬日节庆院落**：半开木门形成近景框景，中景有人端热食，朱红灯笼与深绿屋檐相互映衬，大片米白蒸汽和积雪留纸；动作简洁可辨，不添加臆造可读文字。

原有8幅作品的准确生成提示词保存在[examples.json](examples.json)，用于追溯例图；新主题应重写场景与构图，不能仅替换地名。
