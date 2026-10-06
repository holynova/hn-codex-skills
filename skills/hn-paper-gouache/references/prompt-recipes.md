# 提示词模板与变化方法

使用前按 SKILL.md 实际查看例图。以下是模板，不是已经生成的样图；实际出图后才报告完成。

## 可复用提示词骨架

```text
Create ONE original [aspect ratio] full-bleed illustration of [subject and scene].
Input references: [A/B] are STYLE REFERENCES ONLY; [C, if present] is the subject/composition reference.
Medium: opaque matte gouache in broad painted color shapes on finely textured watercolor paper; subtle paper grain across every color, including white; confidently simplified forms and organically imperfect hand-painted edges.
Shape and light: [lighting]. Build volume with clear light/shadow color planes and crisp [blue / teal / lavender] cast shadows. No black outlines, photoreal rendering, glossy 3D shading, smooth digital gradients, or thick impasto.
Palette: [dominant warm/cool relationship], with [small concentrated accent]. Keep colors clean and readable rather than applying identical blue-green hues to every scene.
Composition: [viewpoint, main focal point, foreground/middle/background relationship, leading shape]. Simplify small details; retain [recognizable landmark features, if relevant].
Atmosphere: [season/weather/time/mood]. Make a fresh composition; do not copy reference subjects or object placement.
Constraints: no text, logo, watermark, frame, collage or inset panel [unless the user explicitly requests one].
```

不要机械填入所有排除项，优先描述所需形状、材质和构图。夜景用平涂深色面、少量暖色窗口表达，避免写实光晕。水面用有方向的色块和少量反光形状，不强迫每个场景都有水。

## 三种应用示例

**新场景：高地小火车。** 风格参考为海岸巴士 + 雪山缆车。橙色短列车穿过高地石桥，仰视近景草坡、桥中景和蓝紫山岭；浅蓝晴空，绿色与蓝色大面，珊瑚色列车成为焦点。保留铁路透视，不复制海岸公路或缆车。

**地标：秋日京都金阁寺。** 风格参考为伏见稻荷 + 秋日划船，需要忠实结构时另用官方景点照片作内容参考。金色楼阁与青绿池水，红枫在边缘形成少量前景；平视中景，保持屋顶层次。不要把鸟居或船复制进画面。

**照片改绘：用户提供的老街。** 风格参考为海岸巴士 + 雨后电车。用户照片负责主要建筑轮廓、街道方向和要求保留的物体；用不透明水粉面、纸纹、蓝紫投影重新解释材质。不擅自添加电车、雨伞或把街道变成海滨。

## 批量变化表

| 图 | 环境 / 主体 | 视角 | 光线季节 | 配色 | 主导线形 |
| --- | --- | --- | --- | --- | --- |
| 1 | 城市电车 | 街面平视 | 雨后 | 紫灰 / 珊瑚 / 黄 | 横向街口 |
| 2 | 沙漠庭院 | 斜俯视 | 午后 | 赭黄 / 靛蓝 | 拱门与棚布 |
| 3 | 河流木船 | 近景俯视 | 秋季 | 橙 / 青绿 | 河道斜线 |
| 4 | 雪山交通 | 高空近景 | 冬日 | 冰蓝白 / 红 | 缆线对角线 |
| 5 | 建筑廊道 | 低位纵深 | 晴日 | 朱红 / 青蓝 | 重复结构 |

这张表展示变化方法，不是每次必须画这五个题材。满足用户主题和一致性要求后，再变化视角、距离、前景、焦点和气候。仅换颜色或交通工具通常不足以形成明显差异。

每张保存完整提示词、实际使用的参考图文件名、主题/视角/配色和输出路径。批量交付核对独立文件数；不用拼图当成多张完成。例图是风格证据，示例提示词不冒充已核实的地标事实或生成结果。
