# 课堂考勤与点名提问系统 - 团队协作指南

## 👥 小组成员及分工

- **成员 A (组长)**: 负责 [模块名称，如：用户与课程管理]
- **成员 B**: 负责 [模块名称，如：课堂考勤管理]
- **成员 C**: 负责 [模块名称，如：智能点名提问]
- **成员 D**: 负责 [模块名称，如：数据统计和展示]

------

## 🚀 Git 协作流程 (核心步骤)

本项目采用 **功能分支 (Feature Branch) 工作流**。请严格遵守以下步骤：

### 1. 初始克隆项目

每个成员在开始前，先将项目克隆到本地：

git clone git@github.com:Ocean-TT/CourseDesign.git

### 2. 开发前：同步与创建分支

**永远不要在 `main` 分支上直接修改代码！** 每次开发新功能前，请先同步主仓库并创建自己的分支：

1. 切换到主分支*

git checkout main

2. 拉取远程最新代码，确保本地是最新的*

git pull origin main

3. 创建并切换到属于你的功能分支 (分支名建议：feature/模块名)*

git checkout -b feature/模块名

### 3. 开发中：提交代码

在自己的分支上编写代码，并频繁提交以记录进度：

*# 查看修改状态*

git status

*# 切换到已有分支*

git checkout feature/模块名

*# 将修改添加到暂存区*

git add .

*# 提交修改 (注释描述你做了什么)*

git commit -m "注释"

### 4. 提交到远程仓库

将你的本地分支推送到 GitHub，以便备份和发起合并：

*# 每次切换分支的第一次推送时使用 -u 参数*

git push -u origin feature/[模块名]

*# 只要没有切换分支，之后的推送直接使用*

git push

### 5. 发起合并请求 与代码审查

1. 登录 GitHub 网页端。
2. 点击 **"Create Pull Request"** (或 "新建合并请求")。
3. 源分支选择你的 `feature/[功能名]`，目标分支选择 `main`。
4. **@** 其他组员进行 **Code Review (代码审查)**。
5. 审查通过后，由组长或指定负责人点击 **Merge** 合并到主分支。

------

## ⚠️ 核心注意事项 (必读)

1. **禁止直接推送 `main` 分支**：所有代码必须通过 PR 合并，严禁在本地 `main` 分支 commit 并 push。
2. **保持分支纯净**：一个分支只做一个功能，不要在一个分支里修改不相关的代码。
3. **频繁同步**：在开始工作前，养成先 `git pull origin main` 的习惯，减少冲突。
4. **冲突解决**：如果合并时出现冲突 (Conflict)，请在线下与相关同学商量后再手动修改，不要盲目覆盖。
5. 不要上传垃圾文件
   - 严禁上传 `node_modules`、编译生成的 `target`、`.exe`、`.class` 等文件。
   - 严禁上传个人 IDE 配置文件（如 [.vscode](vscode-file://vscode-app/e:/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html), `.idea/`）。
   - **请确保 `.gitignore` 文件已正确配置。**
6. 有意义的 Commit 信息
   - `feat:` 新功能
   - `fix:` 修复 Bug
   - `docs:` 文档修改
   - `style:` 代码格式修改 (不影响逻辑)

------

## 🛠️ 常用 Git 命令速查表

| 命令                     | 作用                         |
| ------------------------ | ---------------------------- |
| `git branch`             | 查看当前所在分支             |
| `git checkout main`      | 切换到主分支                 |
| `git pull origin main`   | 拉取远程主分支最新代码       |
| `git checkout -b [name]` | 创建并切换到新分支           |
| `git add .`              | 添加所有修改到暂存区         |
| `git commit -m "msg"`    | 提交修改并添加说明           |
| `git push origin [name]` | 推送本地分支到远程           |
| `git merge main`         | 将主分支的更新合并到当前分支 |

------

祝大家协作愉快，顺利完成课程设计！🎉