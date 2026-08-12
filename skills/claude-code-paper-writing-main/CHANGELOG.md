# 更新日志

记录《Claude Code 科研手记》仓库的每一次实质性更新。最新的在最上面。

每次内容有变动 —— 新章节、新 Skill、新视频、勘误 —— 都会在这里加一行。订阅成员只需 `git pull` 就能拿到最新内容。

---

## 进行中(下次推送会落地的)

- **经管实证 Claude Code 视频讲解系列(小红书)**:逐期上线,每期上线后在 README 的"持续更新计划"那一节挂外链

## 在路线图上

- **Empirical Wiki**:借鉴 Karpathy 的 LLM Wiki 思想,做一个面向经管实证研究的语义检索资料库 —— 你问"这种面板数据用什么方法",它直接给方法名 + R 包 + 注意事项,而不是让你自己翻一长串目录
- **应用案例书 · 因果推断 R 实践**:作为系列第一本应用书,单独仓库 `causal-flipbook`,会迁入 Chanw-research 组织
- **应用案例书 · Meta 分析 / HLM / 时间序列**:看读者反馈和我自己的研究节奏

具体什么时候上线不在 CHANGELOG 里写死,会在做完的那一刻挪到下面"已发布"区。

---

## v1.1 — paper-to-beamer 集成 + 子目录 README 完善

- **`book-companion-skills/paper-to-beamer/` 上线**:附录 F 介绍的"论文 PDF 一键转组会 Beamer 幻灯片"Skill 完整收入仓库,从 14 个通用 Skill 扩到 15 个
- **三个子目录的 README 改版**:
  - `book-companion-skills/README.md` —— 安装方式改成"按熟悉程度三档"(零基础 ZIP 单文件夹下载 / 命令行 / 软链接跟随更新),最重要的"只下载单个 Skill"路径放在最前
  - `skills/README.md` —— 同样的三档安装结构,修正了之前指向不存在仓库的错误链接
  - `chapters/README.md` —— 新建,有读者直接进 chapters 文件夹也能找到方向
- **主 README 学习 ml-engineering 的目录组织**:Part 1–5 + 附录的紧凑结构、Updates / Lectures / Shortcuts / Repository Map 等栏目
- **新增英文版 README_EN.md**,顶部互相切换

## v1.0 — 2026 年春 · 首次发布

主书内容、配套 Skill 集、写作纪律 Skill 集全部到位。

### 主书内容

- 16 章正文 + 6 份附录的精简 markdown 版,放在 `chapters/`
- 完整版 PDF (`book-main.pdf`),用 ElegantBook 模板编译
- 章节之间交叉引用、图表、终端截图全部完成

### 配套 Skill

- **`book-companion-skills/` · 14 个论文写作通用 Skill**(v1.1 起增加 paper-to-beamer 共 15 个)
  - 文献:`pdf`、`arxiv-database`、`citation-management`、`pyzotero`
  - 排版:`drawio`、`markitdown`、`docx`、`xlsx`、`pptx`
  - 写作:`humanizer-zh`、`paper-polish-workflow`
  - 数据:`statistical-analysis`、`seaborn`、`plotly`

- **`skills/` · 12 条写作纪律 Skill**
  - 防灾:`paper-backup-before-word`、`paper-protect-terminology`
  - 流程:`paper-confirm-before-doing`、`paper-one-session-one-task`、`paper-pilot-before-batch`
  - 验证:`paper-verify-before-handoff`、`paper-logical-consistency`
  - 实证:`paper-empirical-pap`、`paper-claude-md-bootstrap`、`paper-translate-advisor-feedback`、`paper-parallel-audit`、`paper-using-skills`、`paper-writing-discipline`

### 文档

- README 重写,加入"三种打开方式"(适合不同基础的读者各选一条)
- 持续更新计划公示 —— 让订阅成员知道未来会加什么

---

## 怎么知道有更新

### 自动通知

GitHub 网页登录后,在仓库页面点右上角 `Watch → All Activity`,有新 push 会发邮件提醒。

### 手动检查

```bash
cd claude-code-paper-writing
git fetch                # 拉远端但不合并
git log HEAD..origin/main --oneline   # 看远端比本地新出了哪些 commit
```

如果有新内容:

```bash
git pull
```

不熟悉 git 的同学,直接到 GitHub 仓库页面看顶部的 "Latest commit" 时间戳,如果比你上次拉的时间新,就重新 ZIP 下载一次也行。

### 看 CHANGELOG 比看 commit 信息更直观

每次实质性更新都会在这份文件最上面加一段,告诉你这次新增了什么、改了什么。看完这里就知道有没有必要重新 pull。

---

*维护者:chanw · 反馈走 Issues 或小红书私信*
