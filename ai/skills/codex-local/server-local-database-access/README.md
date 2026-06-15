# server-local-database-access

用于访问 Justin 的 `server_local` PostgreSQL 论文库和采集控制库。

## 如何触发

在和 Codex 对话时，提到下面任意一类需求即可触发：

- `server_local 数据库`
- `本地论文库`
- `paper_collection_literature`
- `paper_collection_control`
- `paperMiner`
- `采集队列`
- `worker 状态`
- `venue/year 覆盖`
- `本地 PDF`
- `查一下论文库里...`

示例：

```text
帮我查一下 server_local 论文库里 VLDB 每年有多少论文。
```

```text
paperMiner 里数据库领域事务与并发控制主题有哪些本地 PDF？
```

```text
server_local 采集队列是不是卡住了？看一下 failed 和 retry_wait。
```

## 使用方式

Codex 触发后会先选择正确数据库：

- 查论文、作者、关键词、venue、PDF、paperMiner：使用 `paper_collection_literature`
- 查采集请求、任务队列、失败任务、worker 心跳：使用 `paper_collection_control`

详细操作规则、连接方式和 SQL 模板见 [SKILL.md](SKILL.md)。
