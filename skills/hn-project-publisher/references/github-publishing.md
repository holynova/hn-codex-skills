# GitHub Source Publishing

GitHub 承载源码和仓库元数据。默认生产部署见 [cloudflare-publishing.md](cloudflare-publishing.md)，Git push 不会自动部署 Cloudflare。

已发布项目先走 [existing-project-checks.md](existing-project-checks.md)，仅对实际缺口或待发布变更使用下方操作。已满足的配置与元数据只检查、复用，不重复初始化、提交或写入。

## 身份与来源

```bash
gh auth status
gh api user --jq .login
git status --short --branch
git remote -v
gh repo view OWNER/REPO --json defaultBranchRef,url
```

复用已核实的远端与唯一主分支；项目沿用已有 `main` 或 `master`，不要将示例值覆盖到既有配置。源码、README、Wrangler 配置均提交到同一主分支，Cloudflare 从该分支同一提交手动发布。不得新建 Cloudflare 专用发布分支、构建产物分支或 GitHub Action/workflow。没有 Git/npm 元数据时才初始化，并补齐 `.gitignore`，排除依赖、凭据与临时缓存，保留必要 `.env.example`。

## 版本

读取唯一主分支的 package.json、release/tag 或线上版本。仅在本次需要发布应用变更时递增版本，默认 patch，用户指定 minor/major 时遵从；在构建前更新 package.json 与 lockfile。纯检查、仓库/作品集元数据补齐或重部署相同产物不自动递增版本：

```bash
npm version patch --no-git-tag-version
```

页面可见版本应来自构建注入或明确静态元素。运行技能的 `validate_release_version.mjs` 检查部署产物，并通过浏览器确认版本实际可见；文本标记存在不等于 UI 显示正确。

## 仓库创建与推送

只暂存本次明确路径。已有远端时直接复用；授权包含创建公开仓库且尚无目标仓库时，在本地提交后：

```bash
gh repo create OWNER/REPO --public --source=. --remote=origin --push
```

既有仓库：

```bash
git add <intentional-paths>
git commit -m "Publish project to Cloudflare"
git push origin <verified-main-branch>
```

不要 force push 或用 `git add -A` 混入用户已有改动。记录发布提交，Cloudflare 产物必须来自该提交及对应 lockfile。

## 公开元数据

项目 Cloudflare HTTPS 与实际内容验证通过后设置 Homepage，描述沿用项目真实简介：

```bash
gh repo edit OWNER/REPO --homepage "https://<project-slug>.xiaosang.cc/"
gh api repos/OWNER/REPO --jq '{url:.html_url,homepage:.homepage,default_branch:.default_branch}'
```

Repo 链接、Umami、截图、README 与二维码要求以 SKILL.md 为准，二维码使用同一 Cloudflare Demo 地址。

## 既有 GitHub Pages

默认保留已有 Pages 作为回退，不开启新 Pages、不删除历史发布。迁移时检查 Pages 的 CNAME、Actions 与框架 base 是否会冲突；只有授权覆盖域名迁移时才调整相关配置。若用户要求继续维护双部署，从同一主分支为根域名与 Pages 子路径分别构建并验证，不新建发布分支或 Cloudflare Action，不复用错误 base 的产物。Cloudflare 发布不等待 Pages 构建。
