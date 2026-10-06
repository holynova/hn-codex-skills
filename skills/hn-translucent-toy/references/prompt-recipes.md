# 提示词配方

使用前已查看 SKILL.md 规定的基础例图。按本次主题挑选实际参考图，并将每张图的角色内容与风格作用分开说明。以下公共段是材质与人物锚点；数量、背景、构图、角色身份由用户请求决定。

## 公共风格锚点

```text
Use case: stylized-concept.
Create a premium 3D designer collectible toy character poster.
The attached examples are style and material references, not identities,
poses, palettes or props that must be copied.
The person is visibly a sculpted cartoon vinyl figure: slightly enlarged
head and eyes, simplified smooth nose and lips, graphic eyebrows, chunky
sculpted hair, satin vinyl skin without photographic pores or skin texture.
Use mature heroic proportions, approximately a 1:6 head-to-body ratio
unless the user specifies another toy proportion.
The uniform or armor is structurally rigid: thick injection-molded shells,
rounded edges, layered plates, rivets, buckles, jointed gloves and a few
assembly seams. Combine frosted colored translucent resin with selected
clear plastic components; show subtle inner structure through the shells,
physical wall thickness, darker overlapping layers and controlled refraction.
Use large readable color blocks, small contrasting fasteners, and sparse
pictogram decals or neon inlays. Keep the silhouette distinctive.
Default composition: one character, portrait 2:3, softly textured warm-white
studio background, clean breathing space and soft product-photography light.
Avoid real human skin, soft gauze dresses, flowing transparent organza,
opaque shiny metal substituted for translucent plastic, excessive decals,
brand logos and unrequested lettering.
```

## 加上本次角色规格

```text
Character: [role, stylized face, molded hairstyle, expression].
Uniform silhouette: [era/profession, specific stiff shell or layered armor].
Materials: [where frosted translucent shells, clear components and opaque joints go].
Palette: [dominant colors, contrasting small accents, neutral inner structure].
Equipment: [role-appropriate prop, held plausibly with jointed gloves].
Pose and framing: [front/three-quarter/back, full-body or mid-thigh portrait].
Reference roles: [which attached image anchors face/material/silhouette].
```

## 角色变化示例

这些规格可以替换内容；它们不会覆盖用户的角色和配色要求。

- **历史制服**：靛蓝硬壳短制服、柠檬黄模压绳饰、乳白肩片、少量粉色灯线；高帽军官一手扶仪仗刀柄。参考骠骑兵，保留制服结构，换脸与时代细节。
- **圆厚重甲**：薄荷绿磨砂透明护胸与圆肩甲、炭黑关节内壳、橙色卡扣；持透明盾牌的卡通骑士。参考薄荷骑士，突出内外层。
- **专业特勤**：奶油黄硬壳制服、红色护肩、钴蓝扣件、透明琥珀导航板；戴刚性护目镜的航空军官。参考飞行军官，保持设备与人体比例合理。
- **背面视角**：冰蓝分片透明背甲、灰色内部框架、红色固定点；戴透明护面罩的极地巡逻员回头看。参考极地巡逻员，防止背甲变成柔软塑料雨衣。
- **球罩轮廓**：青绿装甲、橙色机械扣件、乳白关节、清透球形头罩；潜水卫兵手持专业设备。参考潜水卫兵，球罩是厚壳配件而非人物整体玻璃化。

## 两种常见偏差的定向修正

- 人物变写实：加强 “sculpted cartoon vinyl face, simplified features, molded hair, no photographic skin detail”；参考一张基础例图的头部与整体造型。不要只增加柔焦。
- 衣服变柔软：明确 “rigid injection-molded uniform shell, fixed geometric silhouette, hard panel edges, layered armor plates”；减少披风、纱、缎带、丝绸等主服装描述。透明材质属于壳体，不意味着服装应柔软。
