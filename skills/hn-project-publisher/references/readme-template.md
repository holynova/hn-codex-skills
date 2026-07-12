# Bilingual README Template

Keep the final README compact. The validator counts each Han character and each English word as one text unit after ignoring Markdown destinations and image syntax; the combined maximum is 200.

````markdown
# Project Name / 项目名

中文：一句话说明项目解决什么问题。

English: One sentence explaining what the project does.

![Project screenshot](./assets/screenshot.png)

[在线体验 / Live Demo](https://OWNER.github.io/REPO/) · [GitHub Repo](https://github.com/OWNER/REPO)

## 本地运行 / Run locally

```bash
npm install
npm run dev
```
````

Use the actual package-manager commands. Prefer a repository-relative screenshot path so forks and branches render correctly. Do not include badges, long feature lists, generated marketing copy, or duplicate links unless the project needs them.
