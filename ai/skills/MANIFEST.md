# Skills Manifest

来源：`/Users/justin/.codex/skills`

同步位置：`ai/skills/codex-local`

未同步：

- `.system/`：Codex 系统技能。
- `codex-primary-runtime/`：当前为空目录。

## 偏个人/项目沉淀

- `agent-browser`
- `ccf-paper-collection`
- `crossdatagen-daily-research-workflow`
- `neat-freak`
- `openclaw-config`
- `paper-pdf-zotero-pipeline`

## 本机安装/通用技能备份

- `doc`
- `find-skills`
- `frontend-design`
- `imagegen`
- `notion-knowledge-capture`
- `notion-meeting-intelligence`
- `notion-research-documentation`
- `notion-spec-to-implementation`
- `pdf`
- `pi-dev`
- `playwright`
- `skill-creator`

## 更新方式

从本机 Codex skills 重新同步：

```bash
rsync -a --delete \
  --exclude='.system/' \
  --exclude='codex-primary-runtime/' \
  /Users/justin/.codex/skills/ \
  ai/skills/codex-local/
```
