# 配套 Skill 集 · Claude Code 科研手记

附录 C 表「科研论文写作推荐 Skill」里列出的 14 个通用 Skill,加上附录 F 介绍的 `paper-to-beamer`,合计 15 个。每个文件夹里至少有一份 `SKILL.md` 描述用途与触发方式,多数还附带 `references/`、`scripts/`、`assets/` 等运行时资源。

> 这一集合就是附录 C 推荐表的"实物版" —— 书里看到表格觉得哪个有用,直接到这里把对应文件夹拿走装到本地即可。

---

## 怎么装(按你熟悉程度挑一种)

Claude Code 默认从 `~/.claude/skills/` 加载 Skill,所以"装"这件事说白了就是把对应的文件夹放到那里。

### 方式 A · 完全不写命令(推荐第一次接触命令行的同学)

适合**只想要某一两个 Skill** 的情况,完全不需要 clone 整个仓库:

1. 在 GitHub 上点进你想要的 Skill 文件夹,比如 [pdf](pdf/)
2. 复制浏览器地址栏的 URL,例如 `https://github.com/Chanw-research/claude-code-paper-writing/tree/main/book-companion-skills/pdf`
3. 把这个 URL 粘贴到 [download-directory.github.io](https://download-directory.github.io/),按回车
4. 浏览器会下载一个 ZIP,只包含那一个 Skill 文件夹
5. 解压后把整个文件夹拖到 `~/.claude/skills/` 里

> [!TIP]
> **`~/.claude/skills/` 这个目录在哪里?**
>
> - **macOS**:打开"访达"(Finder),按 `Cmd + Shift + G`,输入 `~/.claude/skills/` 回车就能看到
> - **Windows**:打开文件资源管理器,在地址栏输入 `%USERPROFILE%\.claude\skills\` 回车
>
> 如果这个文件夹不存在,说明你还没装过 Skill —— 安装 Claude Code 之后这个文件夹会在第一次加载 Skill 时自动建好。也可以自己手动建一个空的。

### 方式 B · 命令行(适合一次想装好几个的情况)

把整个仓库 clone 下来,再挑文件夹复制:

```bash
# 整个仓库 clone 到本地任意位置
git clone https://github.com/Chanw-research/claude-code-paper-writing.git
cd claude-code-paper-writing

# 装单个 Skill(把 humanizer-zh 换成你需要的名字)
cp -r book-companion-skills/humanizer-zh ~/.claude/skills/

# 或者一次铺全部 15 个
for d in book-companion-skills/*/; do
  cp -r "$d" ~/.claude/skills/
done
```

### 方式 C · 软链接(进阶,跟随仓库更新自动同步)

如果你想以后 `git pull` 拿到新版 Skill 时不用再复制一遍,用软链接把 `~/.claude/skills/` 里的 Skill 直接指向仓库里的那一份:

```bash
cd claude-code-paper-writing
ln -sf "$(pwd)/book-companion-skills/"*/ ~/.claude/skills/
```

这样仓库里的 Skill 和 `~/.claude/skills/` 里那份是同一份内容。我每次更新 Skill 后你 `git pull` 一次就同步了,不用再装。

### 装完之后

不管用哪种方式,装完后**开一个新的 Claude Code 会话**(不需要重启电脑或终端),Claude Code 会自动发现新装的 Skill。验证方法:

```
/pdf
读一下 ~/Desktop/sample.pdf 的第一页
```

能正常识别说明装好了。第 9 章详细讲了 Skill 的工作原理与诊断方法。

---

## 15 个 Skill 一览

| Skill | 用途 |
|:--|:--|
| [pdf](pdf/) | 读取 PDF 全文。支持合并、拆分、加水印、OCR 识别扫描件。论文写作中使用频率最高的 Skill |
| [drawio](drawio/) | 用 Draw.io 格式画流程图、架构图、研究框架图。输出 .drawio 文件,导师可以直接用 Draw.io 打开编辑 |
| [markitdown](markitdown/) | 微软开发的文件格式转换工具。把 PDF、Word、PPT、Excel 等转成 Markdown。适合把导师发来的 Word 批注转成 Claude Code 能解析的格式 |
| [pyzotero](pyzotero/) | 连接 Zotero 文献库。按标签筛选文献、拉取元数据、核查引用信息。需要 Zotero 账号和 API 密钥 |
| [citation-management](citation-management/) | 引用管理和核查。搜索 Google Scholar 和 PubMed、生成 BibTeX 条目、验证引用格式 |
| [arxiv-database](arxiv-database/) | 搜索 arXiv 预印本。按关键词、作者、时间范围检索。适合追踪最新的方法论文章 |
| [docx](docx/) | 创建和编辑 Word 文档。适合学校要求提交 Word 格式论文的情况。注意 DOCX 操作有风险,操作前务必备份 |
| [xlsx](xlsx/) | 读取和编辑 Excel 文件。适合处理数据说明文件、价格表等表格数据 |
| [pptx](pptx/) | 创建和编辑 PowerPoint。适合做答辩 PPT 和学术报告幻灯片 |
| [paper-polish-workflow](paper-polish-workflow/) | 论文润色工作流。从结构到逻辑到表达逐层打磨。适合论文提交前的最终润色 |
| [humanizer-zh](humanizer-zh/) | 中文学术润色 Skill。内置术语保护、AI 味消除、句式控制等规则。第 9 章详细讲了使用方法 |
| [statistical-analysis](statistical-analysis/) | 统计分析辅助。帮你选择合适的统计检验方法、检查假设条件、生成 APA 格式的结果报告 |
| [seaborn](seaborn/) | 用 Seaborn 库生成统计可视化图表。适合画箱线图、热力图、散点图等探索性分析图 |
| [plotly](plotly/) | 生成交互式图表。适合做报告展示或探索性分析。正式论文插图建议用 matplotlib |
| [paper-to-beamer](paper-to-beamer/) | 论文 PDF 一键转 Beamer 幻灯片。六阶段流水线 + 论文类型骨架 + 模板四层栈,作者自研。附录 F 详解 |

---

## 几点补充

**[pdf](pdf/) 和 [drawio](drawio/) 是用得最多的两个**,分别用了 100+ 次和 104 次。如果只装两个,就装这两个。

**Skill 之间可以配合使用**。比如用 [pyzotero](pyzotero/) 从 Zotero 筛选出一批文献,用 [pdf](pdf/) 读取其中几篇的全文,用 [citation-management](citation-management/) 核查 BibTeX 格式。每个 Skill 解决一个环节的问题。

**不是所有 Skill 都需要装**。根据你的实际需求选择就好。如果你的论文不涉及图表,就不需要装 drawio。如果你不用 Zotero,就不需要装 pyzotero。按需安装,避免环境臃肿。

**装错了 / 不想要某个了 / 想升级**:直接到 `~/.claude/skills/` 把对应文件夹删掉就好,没有别的清理工作。重新装就再走一遍上面的方式 A / B / C。

---

## 关于版权与归属

这里收录的 14 个 Skill 都来自社区公开的 Skill 库(多数挂在 [skills.sh](https://skills.sh) 上),各 Skill 的原作者保留各自的版权与许可。本仓库做的事仅是**按附录 C 的清单整理打包**,方便读者一次性拿到全部书中推荐的 Skill。

每个 Skill 文件夹内通常带有自己的 `LICENSE` 或在 `SKILL.md` 中注明许可信息。再分发或修改前,请阅读对应 Skill 的许可证。

如果你是某个 Skill 的原作者,发现本仓库的整理有不合适的地方,请通过仓库 [Issues](https://github.com/Chanw-research/claude-code-paper-writing/issues) 或小红书 chanw 联系我。
