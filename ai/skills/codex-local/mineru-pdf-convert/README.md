# MinerU PDF Convert Skill

把 PDF 转成 Markdown 的个人 Codex skill。适合论文阅读、Zotero 附件解析、批量构建 Markdown 语料，以及需要保留公式、表格、图片资产的 PDF 解析任务。

## 位置

- Codex 实际使用位置：`/Users/justin/.codex/skills/mineru-pdf-convert`
- 仓库备份位置：`ai/skills/codex-local/mineru-pdf-convert`
- 私有 token：`/Users/justin/.codex/skills/mineru-pdf-convert/.mineru.env`

仓库备份不包含 `.mineru.env`，不要把 MinerU token 提交进仓库。

## 功能

- 调用 MinerU precise API 转换单个 PDF 或 PDF 目录。
- 输出 `paper.md`、`extraction.json`、`extraction.log`、`mineru-result.zip` 和 `assets/`。
- 支持 `--dry-run` 预检文件大小、页数、跳过状态和计划输出。
- 默认跳过已经转换完成的 PDF；用 `--force` 可重新转换。
- 可配合 Zotero skill 取本地 PDF 附件路径后转换。

## 常用命令

单篇 PDF：

```bash
python3 /Users/justin/.codex/skills/mineru-pdf-convert/scripts/mineru_pdf_convert.py \
  --input-pdf path/to/paper.pdf \
  --output-dir mineru-md
```

目录批量转换：

```bash
python3 /Users/justin/.codex/skills/mineru-pdf-convert/scripts/mineru_pdf_convert.py \
  --input-dir path/to/pdfs \
  --output-dir mineru-md
```

批量转换前先预检：

```bash
python3 /Users/justin/.codex/skills/mineru-pdf-convert/scripts/mineru_pdf_convert.py \
  --input-dir path/to/pdfs \
  --output-dir mineru-md \
  --dry-run
```

## 输出结构

```text
mineru-md/<pdf-stem-slug>/
├── paper.md
├── extraction.json
├── extraction.log
├── mineru-result.zip
└── assets/
```

## 安装或恢复

从仓库备份恢复到 Codex skills 目录：

```bash
rsync -a --delete \
  --exclude='.mineru.env' \
  --exclude='__pycache__/' \
  --exclude='*.pyc' \
  ai/skills/codex-local/mineru-pdf-convert/ \
  /Users/justin/.codex/skills/mineru-pdf-convert/
```

然后在 `/Users/justin/.codex/skills/mineru-pdf-convert/.mineru.env` 中放置：

```text
MINERU_TOKEN=<your-token>
```

并设置权限：

```bash
chmod 600 /Users/justin/.codex/skills/mineru-pdf-convert/.mineru.env
```

## 验证记录

创建时已验证：

- `quick_validate.py`：skill 结构有效。
- `pytest scripts/test_mineru_pdf_convert.py`：4 个脚本测试通过。
- Zotero 三篇 PDF 批量 dry-run：全部 eligible。
- Zotero 单篇 PDF 真实转换：`BAFL: A Blockchain-Based Asynchronous Federated Learning Framework` 转换成功，生成约 65 KB Markdown。
