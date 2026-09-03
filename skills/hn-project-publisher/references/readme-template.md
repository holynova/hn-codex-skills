# Bilingual README Template

保持 README 简洁、结构清晰。中文与英文部分各自不超过 500 字（中文正文 $\le 500$ 汉字，英文正文 $\le 500$ 单词）。

必须包含：
1. **项目有效内容截图**：页面完全加载出真实、有效的内容后再截图，严禁加载中/白屏截取；若为移动端应用，必须使用移动端视口宽度（375px~430px）截图，禁止按 PC 桌面端拉伸宽度截取。
2. **GitHub Repo 链接**
3. **GitHub Pages 在线访问链接**
4. **手机扫码访问二维码**：生成并包含二维码图片（如 `assets/qr.png`），方便手机直接扫码打开 Pages。
5. **Cloudflare 专属域名**：加入自动发布的专属域名 `https://<repo-name>.xiaosang.cc`。

````markdown
# Project Name / 项目名

中文：简要说明项目功能、核心特性与解决的问题（不超过 500 字）。

English: Concise summary of what the project does, key highlights, and how it works (under 500 words).

![Project screenshot](./assets/screenshot.png)

## 在线体验 / Live Demo

- **GitHub Pages**：[https://OWNER.github.io/REPO/](https://OWNER.github.io/REPO/)
- **Cloudflare 专属域名**：[https://REPO.xiaosang.cc](https://REPO.xiaosang.cc)
- **开源仓库 / GitHub Repo**：[https://github.com/OWNER/REPO](https://github.com/OWNER/REPO)

### 手机扫码访问 / Mobile QR Code

<img src="./assets/qr.png" width="180" alt="手机扫码访问在线体验">

## 本地运行 / Run locally

```bash
npm install
npm run dev
```
````

### 二维码生成快捷指令
在项目根目录下使用 `npx qrcode` 即可快速生成：
```bash
mkdir -p assets
npx qrcode -o assets/qr.png "https://OWNER.github.io/REPO/"
```
