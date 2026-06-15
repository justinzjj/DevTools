# Mentor Research OS 设计文档

日期：2026-06-12  
状态：设计基线  
目标仓库：建议单独新建仓库 `mentor-research-os`

## 1. 背景与目标

导师在论文指导上可能无法提供稳定、细致、可复用的反馈。这个系统的目标不是替代导师本人，也不是简单收集导师论文，而是把导师已有论文、学生论文、主页、项目、引用网络和写作习惯蒸馏成一个可查询、可更新、可用于指导自己论文工作的研究操作系统。

系统最终要回答四类问题：

1. 这个导师通常认可什么样的研究问题？
2. 导师论文如何构造 gap、方法、贡献和讨论？
3. 我的论文方向和导师研究谱系是什么关系？
4. 如果导师或审稿人质疑我的论文，最可能质疑哪里？

## 2. 设计原则

### 2.1 先知识结构，后自动化

第一版不追求复杂脚本和 UI。先用 Markdown、JSON 和少量模板把知识结构跑通。只有当手工流程稳定后，再自动化论文抓取、元数据抽取、卡片生成和分析报告生成。

### 2.2 区分事实、推断和建议

导师论文中的事实、我们对导师风格的推断、对自己论文的建议必须分层保存。系统不能把“导师曾经这样写”直接等同于“我的论文必须这样写”。

### 2.3 每个结论都要能追溯到论文证据

`research-dna.md`、`method-patterns.md`、`advisor-risk-map.md` 中的判断应尽量链接回具体 paper card。不能只写空泛结论，例如“导师重视创新性”，而要说明是哪些论文体现了这一点。

### 2.4 服务自己的论文，而不是崇拜导师

系统要帮助自己形成独立论文方向。导师论文是训练材料，不是边界。所有“advisor fit”都应同时记录继承点、偏离点和偏离的合理性。

## 3. 总体架构

建议仓库结构如下：

```text
mentor-research-os/
  README.md

  mentors/
    <mentor-id>/
      profile.md
      profile.json
      sources.md

      papers/
        manifest.json
        pdfs/
        notes/
        cards/

      analysis/
        research-dna.md
        topic-evolution.md
        method-patterns.md
        contribution-patterns.md
        writing-patterns.md
        venue-map.md
        citation-network.md
        advisor-risk-map.md

      guidance/
        choose-topic.md
        evaluate-research-question.md
        outline-review.md
        intro-review.md
        contribution-review.md
        defense-questions.md

  my-projects/
    <project-id>/
      project-brief.md
      research-question.md
      argument-map.md
      literature-map.md
      chapter-plan.md
      advisor-fit-report.md
      weekly-log.md

  schemas/
    paper.schema.json
    mentor-profile.schema.json
    research-pattern.schema.json
    project-brief.schema.json

  templates/
    paper-card.md
    mentor-profile.md
    research-dna.md
    project-brief.md
    weekly-review.md

  prompts/
    extract-paper-card.md
    distill-mentor-profile.md
    compare-my-topic.md
    review-outline-as-advisor.md
    find-research-gap.md

  scripts/
    ingest_papers.py
    build_manifest.py
    extract_metadata.py
    generate_profile.py
    audit_completeness.py

  docs/
    workflow.md
    data-model.md
    operating-manual.md
```

## 4. 核心模块

### 4.1 Mentor 模块

每个导师一个目录，例如：

```text
mentors/jiachi-chen/
```

该目录是导师画像的边界。它不存自己的论文项目，只存导师相关材料和从导师材料蒸馏出的模式。

核心文件：

- `profile.md`：面向人阅读的导师画像。
- `profile.json`：结构化导师画像，供脚本或 LLM 使用。
- `sources.md`：导师主页、Google Scholar、DBLP、ORCID、实验室页面、项目页面、学生论文等来源。

### 4.2 Corpus 模块

位置：

```text
mentors/<mentor-id>/papers/
```

职责是管理原始论文材料和阅读状态。

建议文件：

```text
papers/
  manifest.json
  pdfs/
  notes/
  cards/
```

`manifest.json` 是论文清单，不承载深度分析。它只回答“有哪些论文、材料在哪里、处理到什么状态”。

建议字段：

```json
{
  "id": "chen-2024-example",
  "title": "Example Paper Title",
  "year": 2024,
  "authors": ["A. Author", "Jiachi Chen"],
  "venue": "Conference or Journal",
  "doi": "10.xxxx/example",
  "url": "https://example.com",
  "pdf": "pdfs/chen-2024-example.pdf",
  "status": {
    "metadata": "done",
    "pdf": "done",
    "card": "todo",
    "analysis": "todo"
  },
  "tags": ["topic-a", "method-b"],
  "importance": "core"
}
```

### 4.3 Paper Card 模块

位置：

```text
mentors/<mentor-id>/papers/cards/
```

每篇论文一张结构化卡片。Paper card 是系统最重要的中间产物，因为后续所有导师画像都应从它汇总。

模板：

```md
# Paper Card: <title>

## Citation

## One-Sentence Thesis

## Research Problem

## Research Gap

## Research Question

## Method

## Data / Material

## Contribution

## Argument Structure

### Introduction Move

### Literature Review Move

### Method Move

### Results Move

### Discussion Move

## Writing Moves

## Reusable Patterns

## Risks / Limitations

## Relation To Mentor DNA

## Relevance To My Thesis

## Evidence Links
```

重点不是摘要，而是回答：这篇论文体现了导师什么研究判断。

### 4.4 Analysis 模块

位置：

```text
mentors/<mentor-id>/analysis/
```

该模块从多篇 paper cards 中提炼跨论文模式。

建议文件：

- `research-dna.md`：导师研究基因，回答“这个导师长期关心什么、如何判断问题重要”。
- `topic-evolution.md`：主题演化，回答“导师研究方向如何变化”。
- `method-patterns.md`：方法偏好，回答“导师常用什么方法、接受什么证据”。
- `contribution-patterns.md`：贡献类型，回答“导师论文常见贡献是什么”。
- `writing-patterns.md`：写作套路，回答“引言、文献综述、讨论如何组织”。
- `venue-map.md`：投稿场域，回答“导师常投哪里、不同 venue 对论文形态有什么要求”。
- `citation-network.md`：引用网络，回答“导师常引用谁、属于哪个学术共同体”。
- `advisor-risk-map.md`：风险地图，回答“哪些选题或写法可能被导师质疑”。

每个分析文件必须包含“证据来源”小节，列出支撑判断的 paper cards。

### 4.5 Guidance 模块

位置：

```text
mentors/<mentor-id>/guidance/
```

这是把导师画像转为指导能力的地方。每个文件都是一个可执行工作流，而不是普通笔记。

建议工作流：

- `choose-topic.md`：帮助判断一个方向是否值得做。
- `evaluate-research-question.md`：检查研究问题是否清晰、可答、符合导师谱系。
- `outline-review.md`：按导师偏好审查论文大纲。
- `intro-review.md`：审查引言的 urgency、gap、contribution。
- `contribution-review.md`：检查贡献是否足够明确。
- `defense-questions.md`：生成导师/答辩/审稿可能追问的问题。

示例检查问题：

```md
## Evaluate Research Question

1. 这个问题是否落在导师已有研究谱系附近？
2. 它继承了导师论文中的哪个问题意识？
3. 它偏离导师已有工作的地方是什么？
4. 这个偏离是否有合理性？
5. 研究问题是否能被当前方法回答？
6. 贡献类型是否清晰？
7. 最可能被导师质疑的三点是什么？
```

### 4.6 My Projects 模块

位置：

```text
my-projects/<project-id>/
```

自己的论文项目与导师画像分开保存。这样可以一个导师画像服务多个论文项目，也可以一个论文项目对比多个导师或研究者。

建议文件：

- `project-brief.md`：项目基本盘。
- `research-question.md`：研究问题的多版本演化。
- `argument-map.md`：主张、证据、反驳、限制。
- `literature-map.md`：自己的文献地图。
- `chapter-plan.md`：章节计划。
- `advisor-fit-report.md`：与导师研究谱系的关系。
- `weekly-log.md`：每周推进记录。

`advisor-fit-report.md` 是连接导师画像和自己论文的核心文件。

模板：

```md
# Advisor Fit Report

## Project

## Related Mentor Patterns

## Fit

我的选题继承了导师哪些问题意识？

## Divergence

我和导师已有论文相比偏离在哪里？

## Justification

这个偏离为什么合理？

## Risks

导师最可能质疑哪三点？

## Evidence Needed

为了让这个方向更稳，我需要补什么文献、数据或实验？

## Next Move
```

## 5. 数据流

系统数据流如下：

```text
Sources
  -> Manifest
  -> PDFs / raw notes
  -> Paper Cards
  -> Mentor Analysis
  -> Guidance Workflows
  -> My Project Reviews
  -> Weekly Decisions
```

每一层都应能独立检查：

1. Sources 是否可信且完整。
2. Manifest 是否记录了所有核心论文。
3. Paper cards 是否覆盖核心论文。
4. Mentor analysis 是否有证据支撑。
5. Guidance workflows 是否能对自己的论文产出具体建议。
6. My project 是否记录了每次方向变化和决策理由。

## 6. MVP 范围

第一版只做最小可用系统，不做全量自动化。

### 6.1 必需目录

```text
mentors/<mentor-id>/
  sources.md
  profile.md
  papers/
    manifest.json
    cards/
  analysis/
    research-dna.md
    method-patterns.md
    advisor-risk-map.md

my-projects/<project-id>/
  project-brief.md
  advisor-fit-report.md
  weekly-log.md

templates/
  paper-card.md
  project-brief.md
  weekly-review.md

prompts/
  extract-paper-card.md
  review-outline-as-advisor.md
```

### 6.2 MVP 成功标准

MVP 完成时应满足：

1. 至少收集 5 篇导师核心论文。
2. 至少完成 5 张 paper cards。
3. 能写出一份 `research-dna.md`，包含主题偏好、方法偏好、贡献偏好。
4. 能写出一份 `advisor-risk-map.md`，列出导师可能质疑的方向风险。
5. 能对自己的一个论文想法生成 `advisor-fit-report.md`。
6. 每个分析结论都能追溯到至少一张 paper card。

## 7. 实施阶段

### Phase 0：仓库初始化

建立目录、模板和 README。只创建骨架，不急着写脚本。

产出：

- 仓库结构
- `README.md`
- `templates/`
- 第一个导师目录
- 第一个项目目录

### Phase 1：导师论文清单

建立 `sources.md` 和 `manifest.json`。先手工收集 5-10 篇核心论文。

优先级：

1. 导师一作或通讯作者论文。
2. 与自己方向最接近的论文。
3. 导师学生的毕业论文或合作论文。
4. 高被引或代表性论文。

### Phase 2：Paper Card 蒸馏

逐篇论文制作 paper card。每篇卡片必须回答 gap、research question、method、contribution、writing moves。

这一阶段不追求一次性读完所有论文，而是先把 5 篇核心论文读深。

### Phase 3：导师 DNA 汇总

从 paper cards 中汇总：

- `research-dna.md`
- `method-patterns.md`
- `contribution-patterns.md`
- `advisor-risk-map.md`

此阶段开始形成真正的指导能力。

### Phase 4：连接自己的论文

建立自己的项目目录，写：

- `project-brief.md`
- `research-question.md`
- `advisor-fit-report.md`

然后用导师 DNA 反查自己的方向是否稳。

### Phase 5：半自动化

当手工流程稳定后，再写脚本：

- `build_manifest.py`：检查论文清单。
- `extract_metadata.py`：从 DOI/BibTeX/PDF 补元数据。
- `audit_completeness.py`：检查哪些论文缺 card，哪些分析缺证据。
- `generate_profile.py`：从 cards 生成 profile 草稿。

## 8. 质量门槛

### 8.1 Paper Card 质量门槛

一张合格 paper card 必须包含：

1. 一句话核心主张。
2. 研究 gap。
3. 研究问题。
4. 方法和数据。
5. 贡献类型。
6. 至少 3 个可复用写作或研究模式。
7. 至少 1 个对自己论文的启发。

### 8.2 Mentor DNA 质量门槛

一份合格 `research-dna.md` 必须包含：

1. 主题偏好。
2. 问题构造方式。
3. 方法偏好。
4. 贡献偏好。
5. 写作风格。
6. 证据来源。
7. 对自己论文的启发与限制。

### 8.3 Advisor Fit 质量门槛

一份合格 `advisor-fit-report.md` 必须回答：

1. 我的选题继承了导师什么问题意识？
2. 我的选题偏离了导师什么既有路径？
3. 这个偏离为什么合理？
4. 导师最可能质疑哪三点？
5. 我下一步需要补什么证据？

## 9. 风险与约束

### 9.1 过度模仿导师

风险：系统可能让自己只会沿着导师旧论文走。  
处理：每个 `advisor-fit-report.md` 必须包含 `Divergence` 和 `Justification`。

### 9.2 结论无证据

风险：生成的导师画像可能变成空泛印象。  
处理：分析文件必须列出支撑 paper cards。

### 9.3 自动化过早

风险：先写脚本会掩盖问题定义不清。  
处理：MVP 阶段只做 Markdown 和 JSON。

### 9.4 材料版权

风险：PDF 不适合公开上传。  
处理：如果仓库公开，`pdfs/` 应加入 `.gitignore`，只保留 DOI、URL 和笔记。

### 9.5 多导师混淆

风险：多个导师/研究者的模式混在一起。  
处理：每个导师独立目录；跨导师比较另设 `comparisons/`，不要写进单个导师画像。

## 10. 推荐 README 结构

新仓库的 `README.md` 建议包含：

```md
# Mentor Research OS

This repository distills advisor papers into reusable research guidance.

## Goals

## Repository Structure

## Quick Start

1. Add mentor sources.
2. Build paper manifest.
3. Create five paper cards.
4. Distill research DNA.
5. Evaluate my thesis project.

## Workflows

## Data Policy

## Current Mentor Profiles

## Current Thesis Projects
```

## 11. 初始任务清单

新仓库创建后，按这个顺序执行：

1. 创建目录结构。
2. 创建 `.gitignore`，忽略 `pdfs/`、临时文件和大文件。
3. 创建 `templates/paper-card.md`。
4. 创建第一个导师目录。
5. 填写 `sources.md`。
6. 建立 `papers/manifest.json`。
7. 选择 5 篇核心论文。
8. 完成 5 张 paper cards。
9. 写第一版 `research-dna.md`。
10. 写自己的 `project-brief.md`。
11. 生成第一版 `advisor-fit-report.md`。

## 12. 设计结论

这个系统的本质不是文献管理，而是研究判断管理。

第一阶段最重要的不是收集更多论文，而是把少量核心论文读到足以回答：

- 导师如何定义一个好问题？
- 导师如何把问题变成论文？
- 导师如何证明贡献成立？
- 我的论文如何继承、偏离并超越这条路径？

只要这四个问题能被系统稳定回答，仓库就已经具备指导价值。
