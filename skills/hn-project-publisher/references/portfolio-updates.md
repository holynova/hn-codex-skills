# Portfolio Updates

当发布范围包含作品集同步时，更新已授权的两大作品集目标。复用主流程的目标、授权和验证结果；某个目标缺少访问权限或失败时记录待完成项，并继续另一个可独立完成的目标。不要因本参考存在就扩展局部任务的发布范围。仅将已验证地址作为可用演示链接，域名尚未就绪时明确标注或暂不加入在线链接。

先核对每个目标仓库的远端、实际发布分支与工作区改动；以下 `<verified-branch>` 是核对后替换的占位符，不固定使用 `master`，也不混入无关改动。

## Canonical Entry

在更新作品集前，整理标准元数据项：

- **项目名称**：双语或中文项目标题
- **简介**：一句话中文描述（与 README 保持一致）
- **GitHub Repo 链接**：`https://github.com/holynova/<repo>`
- **GitHub Pages 演示链接**：`https://holynova.github.io/<repo>/`
- **Cloudflare 专属域名**：`https://<repo>.xiaosang.cc`
- **预览截图**：`portfolio-<repo>.png` 或项目截图

---

## 目标一：GitHub 个人主页作品列表 (`https://github.com/holynova/`)

GitHub 个人主页由仓库 `holynova/holynova` 的根目录 `README.md` 驱动。

### 操作步骤：
1. 切换到本地目录（如 `/Users/sym/Code/holynova`）或通过 Git 检出。
2. 读取 `README.md` 中的作品展示表格。
3. 如果已有该项目的行，则就地更新；如果是新发布的项目，在表格头部或对应分类中追加一行：
   ```markdown
   | 0 | 项目标题 | <img width="320" alt="项目预览" src="./portfolio-<repo>.png"> | 一句话中文功能简介 | [Demo](https://holynova.github.io/<repo>/) · [Repo](https://github.com/holynova/<repo>) |
   ```
4. 将项目的精简封面图复制到 `portfolio-<repo>.png`。
5. 提交并推送到 GitHub：
   ```bash
   git add README.md portfolio-<repo>.png
   git commit -m "feat: add <repo> to portfolio showcase"
   git push origin <verified-branch>
   ```
6. 访问 `https://github.com/holynova` 验证新条目与链接是否正常呈现。

---

## 目标二：个人作品集主站 (`https://holynova.github.io/`)

作品集主站由本地项目目录（`/Users/sym/Code/holynova.github.io`）及仓库驱动。

### 操作步骤：
1. 切换到本地目录 `/Users/sym/Code/holynova.github.io`。
2. 检查 `data/repos.json`（或相关数据源），在列表中新增或更新该项目对象：
   ```json
   {
     "name": "<repo-name>",
     "title": "项目标题",
     "description": "一句话中文功能简介",
     "category": "web",
     "url": "https://holynova.github.io/<repo-name>/",
     "cloudflareUrl": "https://<repo-name>.xiaosang.cc",
     "github": "https://github.com/holynova/<repo-name>",
     "screenshot": "screenshots/<repo-name>.png"
   }
   ```
3. 将项目有效内容截图同步到 `screenshots/<repo-name>.png`。
4. 运行 `node scripts/verify-data-source.mjs`（如有验证脚本）确保数据格式完好。
5. 提交并推送到 GitHub 触发 GitHub Pages 自动部署：
   ```bash
   git add data/repos.json screenshots/<repo-name>.png
   git commit -m "feat: add <repo-name> showcase"
   git push origin <verified-branch>
   ```
6. 打开 `https://holynova.github.io/` 验证作品卡片展示与双端链接。
