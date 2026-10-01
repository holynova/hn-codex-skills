# Bilingual README Template

中文正文 ≤500 汉字，英文正文 ≤500 单词。README 必须包含真实内容截图、GitHub Repo、最终 Cloudflare HTTPS Demo、编码同一 Demo 地址的二维码，以及适用于实际项目的本地运行与发布命令。

新项目使用模板准备材料；已发布项目检查现有 README、截图与二维码，只修缺失、失效或本次变更影响的部分，不重写已合格文案或重新生成仍有效的图片。

截图等待数据/Canvas/组件渲染完成；移动应用采用 375–430px 宽视口。未验证地址仅在草稿中标为待配置/待验证，上线验证后再作为可用入口。默认不要求 GitHub Pages 链接。

下方 OWNER、REPO、PROJECT-SLUG 与项目名需替换为实际值；运行命令按项目 scripts 调整。

````markdown
# Project Name / 项目名

中文：简要说明项目功能、核心特性与解决的问题。

English: Concise summary of the project and its key features.

![Project screenshot](./assets/screenshot.png)

## 在线体验 / Live Demo

- [Cloudflare Demo](https://PROJECT-SLUG.xiaosang.cc/)
- [GitHub Repo](https://github.com/OWNER/REPO)

<img src="./assets/qr.png" width="180" alt="扫码访问 Cloudflare 在线体验">

## 本地运行 / Run locally

```bash
npm install
npm run dev
```

## 发布 / Deploy

```bash
npm run deploy
```

Cloudflare Workers · Custom Domain: `PROJECT-SLUG.xiaosang.cc`

源码与部署配置使用同一个主分支；在本地手动发布，不创建 Cloudflare 专用分支或 GitHub Action。
````

生成二维码与校验（从项目目录执行，skill-dir 是实际技能位置）：

```bash
mkdir -p assets
npx qrcode -o assets/qr.png "https://PROJECT-SLUG.xiaosang.cc/"
node <skill-dir>/scripts/validate_release_readme.mjs README.md "https://github.com/OWNER/REPO" "https://PROJECT-SLUG.xiaosang.cc/" 500 500
```

校验器检查链接文本、截图/二维码文件存在及字数，不检查图片内容、二维码编码与线上可达性，这些仍需独立验证。保留旧调用兼容：最后可传额外的公开 URL，只有传入才要求 README 包含它；新流程不传 Pages URL。
