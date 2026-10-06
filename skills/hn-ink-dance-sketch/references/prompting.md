# 提示词与修正

## 共享风格块

下面的英文模板方便向图像工具传递约束，可按用户语言等义改写。方括号是必须填入的规格，不是直接传给工具的文本。

```text
Create ONE original standalone full-body dance artwork.
Visual references: the attached examples are ONLY references for the ink mark-making,
paper and degree of simplification. Do not copy their character, pose or costume.
Subject: [dance type, adult dancer, distinctive garment silhouette and footwear].
Action: [support point, torso direction, arm and leg relationships, gaze].
Composition: [portrait or landscape; subject placement, dominant axis, ample blank margins].
Style: a sparse spontaneous observational Chinese ink gesture sketch;
economical unfinished contours, irregular thin-to-thick calligraphic black lines,
broken dry-brush strokes, a handful of dark anchors, simplified expressive face.
Suggest folds only where they explain the motion. Pale warm ivory fibrous paper,
subtle low-contrast texture, large untouched negative space.
Keep anatomy and weight-bearing coherent, but allow loose incomplete marks.
No photorealism, polished vector contours, dense ornament, gray volume shading,
stage scenery, decorative border, writing, seal or watermark.
[Subject-specific exclusions that prevent drift into the wrong costume or dance.]
```

不要把所有例图中的衣服、头饰和飘带写进共享风格块。飘带是主体属性，不能成为每张的必选项。

## 三个填好的主体规格

**芭蕾：** adult female ballet dancer, plain sleeveless leotard, short stiff tutu, tights and pointe shoes, simple bun; left-facing arabesque, one straight supporting leg on pointe, rear leg extended horizontally, arms reaching at different heights; airy stretched silhouette; no long skirt, ornate headdress or flowing ribbons.

**蒙古舞：** adult male Mongolian dancer in a knee-length cross-fastened deel, broad sash, loose trousers, tall boots and simple cap; vigorous wide bent-knee stance with open arms, slightly forward torso; substantial straight sleeves and visible boots; strong economical strokes, no floor-length skirt or fantasy accessories.

**现代舞：** adult short-haired contemporary dancer in a loose plain tank and cropped wide trousers, barefoot; seated on one hip, one palm on the ground, other arm reaching diagonally upward, legs arranged in readable folded and extended directions; compact low silhouette with generous blank space above; no skirt, ribbons or jewelry.

## 常见偏差与有针对性的修正

| 偏差 | 下一轮修改 |
| --- | --- |
| 五张像同一个人换手势 | 换短裙/长裙/长袍/裤装等结构，并改变站立、低蹲、地面动作和视角 |
| 都是古风长裙与飘带 | 从主体规格删去 fantasy dancer / flowing costume，写清真实衣服结构，必要时明确 no ribbons |
| 变成精致服装插画 | 减少脸部线条、花纹、首饰和衣褶；要求现场速写、未闭合轮廓，而非 polished illustration |
| 线条像矢量描边 | 要求断笔、飞白、轻重不均与少量急转；删去 clean line art |
| 像水墨渲染画 | 删去 wash、shading、atmospheric background；强调轮廓线与留白，不靠灰色塑造体积 |
| 动作失衡或肢体含糊 | 明确支撑点与肩胯方向，简化遮挡；保留松线但重新建立姿态 |
| 纸张抢戏 | 降低纸纹对比、去除污渍和暗角；保持暖米白空白背景 |

检查的是图像结果，不是提示词里有没有写到某个关键词。不要因使用了模板就宣布风格匹配成功。
