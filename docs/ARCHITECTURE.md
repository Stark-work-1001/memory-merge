# Architecture and operations / 架构与运维

```text
host event / user request
          |
     capture / remember
          |
 SQLite transaction + outbox -----> retryable Markdown mirror
          |
 pending -> human review -> approved
                              |
                lexical + optional embeddings
                              |
                   cited evidence -> client answer
                              |
                    read-only local mind graph
```

## Contracts / 契约

- Automatic captures are pending. Only approved records appear in recall and graphs. Manual confirmation must reflect explicit user intent, not an agent's guess. 自动候选待审；只有已批准记录进入召回与图谱；manual确认必须反映真实用户意图。
- Idempotency key: project + source + event_id. Reusing a key with different content is rejected. 幂等键为project/source/event_id，同键异文拒绝。
- Categories: fact, decision, preference, procedure, lesson, knowledge. Relations: supports, contradicts, supersedes, related. 类别和关系为显式枚举；关系本身不会自动停用旧记录。
- SQLite transactions serialize updates; Markdown failures leave outbox entries for retry. Rebuild derives mirrors from the database. SQLite事务保证更新顺序；镜像失败留待重试，rebuild从库重建。
- Vectors are normalized and stored in SQLite; small-scale linear cosine scans and RRF are used, not a production ANN service. 向量归一化后存SQLite，使用小规模线性余弦与RRF，不是生产ANN服务。
- Provider identity currently includes endpoint/model with dimension/content compatibility checks, not a complete immutable model revision fingerprint. 当前模型指纹不是完整不可变revision，换模型别名时应重新索引。
- Judge failure is fail-closed; no automatic approval. RAG generation is client-owned. Judge异常保持待审，生成由客户端负责。

## Operational boundaries / 运维边界

The HTTP viewer binds only to loopback, checks Host, serves read-only routes, uses CSP and renders text without innerHTML. Do not expose it through a public reverse proxy. Local processes under the same OS account may access files; project scopes are not tenant ACLs.

网页仅回环绑定、校验Host、只读路由、使用CSP与文本渲染。不要通过公网反向代理暴露；同OS账号仍可访问文件，project不是租户ACL。

Backup uses SQLite's backup API and refuses existing targets. For recovery, stop all writers, copy the backup into a new empty data directory as memory.sqlite3, run health and rebuild, inspect the result, then repoint clients. Never overwrite an active database or copy only an active primary file while ignoring WAL.

备份使用SQLite backup API并拒绝覆盖。恢复时停写，在新空目录放置备份并命名memory.sqlite3，执行health与rebuild，确认后切换客户端；不要覆盖运行中的库或忽略WAL。

## Limits / 限制

Indexing: up to 1,000 approved records per call. Graph: up to 1,000 nodes. Vector/literal candidates: up to 5,000. Content: up to 16,000 characters. Query: up to 1,000 characters. Budget is character-based, not token-exact.

索引每次最多1,000条已审记录，图谱最多1,000节点，向量/字面候选最多5,000；正文16,000字符，查询1,000字符；上下文预算按字符而非精确token计算。

Soft deletion retains database content and may leave copies in backups. Full erasure, multi-user authentication, edit/merge history, automatic host hooks, large-scale pagination and real-model evaluation remain future work.

软删除保留数据库正文，备份也可能保留副本。完整擦除、多用户认证、编辑合并历史、自动hooks、大规模分页及真实模型评测仍属后续工作。
