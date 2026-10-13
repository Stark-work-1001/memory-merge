# References & Authors / 参考项目与作者

Public upstream repository owners and contributors are credited below. These are research references, not bundled implementations or endorsements. No private identity of this project's requester is published. 本节仅列公开上游账号与贡献者，属于设计参考，不表示捆绑其实现或获得背书；不披露本项目委托人的私人身份。

| Project / 项目 | GitHub repository / 仓库 | Public author or organization / 公开作者或组织 |
|---|---|---|
| Basic Memory | [basicmachines-co/basic-memory](https://github.com/basicmachines-co/basic-memory) | [basicmachines-co](https://github.com/basicmachines-co) & contributors |
| MCP Memory Service | [doobidoo/mcp-memory-service](https://github.com/doobidoo/mcp-memory-service) | [doobidoo](https://github.com/doobidoo) & contributors |
| 灵枢 / dsh-memory | [FuRongJun-1999/dsh-memory](https://github.com/FuRongJun-1999/dsh-memory) | [FuRongJun-1999](https://github.com/FuRongJun-1999) & contributors |
| SynaBun | [danilokhury/Synabun](https://github.com/danilokhury/Synabun) | [danilokhury](https://github.com/danilokhury) & contributors |
| Engram (Go) | [Gentleman-Programming/engram](https://github.com/Gentleman-Programming/engram) | [Gentleman-Programming](https://github.com/Gentleman-Programming) & contributors |
| Engram (model research / 模型研究) | [deepseek-ai/Engram](https://github.com/deepseek-ai/Engram) | [deepseek-ai](https://github.com/deepseek-ai) & contributors |
| Shodh Memory | [varun29ankuS/shodh-memory](https://github.com/varun29ankuS/shodh-memory) | [varun29ankuS](https://github.com/varun29ankuS) & contributors |
| Engram MCP (Rust) | [edg-l/engram-mcp](https://github.com/edg-l/engram-mcp) | [edg-l](https://github.com/edg-l) & contributors |
| Engram (Python) | [raya-ac/engram](https://github.com/raya-ac/engram) | [raya-ac](https://github.com/raya-ac) & contributors |
| Mem0 | [mem0ai/mem0](https://github.com/mem0ai/mem0) | [mem0ai](https://github.com/mem0ai) & contributors |
| Letta / Letta Code | [letta-ai/letta](https://github.com/letta-ai/letta), [letta-ai/letta-code](https://github.com/letta-ai/letta-code) | [letta-ai](https://github.com/letta-ai) & contributors |
| Graphiti / Zep | [getzep/graphiti](https://github.com/getzep/graphiti), [getzep/zep](https://github.com/getzep/zep) | [getzep](https://github.com/getzep) & contributors |
| Cognee | [topoteretes/cognee](https://github.com/topoteretes/cognee) | [topoteretes](https://github.com/topoteretes) & contributors |
| MemOS | [MemTensor/MemOS](https://github.com/MemTensor/MemOS) | [MemTensor](https://github.com/MemTensor) & contributors |
| Memobase | [memodb-io/memobase](https://github.com/memodb-io/memobase) | [memodb-io](https://github.com/memodb-io) & contributors |
| A-MEM | [agiresearch/A-mem](https://github.com/agiresearch/A-mem) | [agiresearch](https://github.com/agiresearch) & contributors |
| LightRAG | [HKUDS/LightRAG](https://github.com/HKUDS/LightRAG) | [HKUDS](https://github.com/HKUDS) & contributors |
| MCP Memory / Python SDK | [servers/src/memory](https://github.com/modelcontextprotocol/servers/tree/main/src/memory), [python-sdk](https://github.com/modelcontextprotocol/python-sdk) | [modelcontextprotocol](https://github.com/modelcontextprotocol) & contributors |
| Claude-Mem | [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) | [thedotmack](https://github.com/thedotmack) & contributors |
| LangMem | [langchain-ai/langmem](https://github.com/langchain-ai/langmem) | [langchain-ai](https://github.com/langchain-ai) & contributors |
| Hindsight | [vectorize-io/hindsight](https://github.com/vectorize-io/hindsight) | [vectorize-io](https://github.com/vectorize-io) & contributors |
| OpenViking | [volcengine/OpenViking](https://github.com/volcengine/OpenViking) | [volcengine](https://github.com/volcengine) & contributors |
| Qwen3 Embedding (candidate / 候选) | [QwenLM/Qwen3-Embedding](https://github.com/QwenLM/Qwen3-Embedding) | [QwenLM](https://github.com/QwenLM) & contributors |

# Memory Merge — v0.1.0-alpha.1

Local-first, single-user memory prototype. 本地优先的单用户记忆原型。

Release tag / 发布标签：`v0.1.0-alpha.1` · Python version / Python版本：`0.1.0a1` · Status / 状态：**pre-release / 预发布**。

## 中文

### 功能与边界

SQLite作为事务真源，outbox重试导出Markdown镜像；支持自动候选、用户主动记忆、审核、分类、项目范围、幂等事件及显式关系。通过官方MCP SDK提供原生stdio工具，通过只读本地网页查看mind-graph。

- 自动候选保持pending，仅approved进入正式检索和图谱。
- 默认FTS5/字面检索，不调用模型；配置Embedding后可启用余弦相似度与RRF混合检索。
- Judge只给建议，不获得自动批准权限；RAG提供带来源的证据包，最终生成由客户端完成。
- 模型端点必须显式配置；非回环地址要求HTTPS及`MM_ALLOW_REMOTE=1`。不会自动下载模型或导入旧数据。
- 本版本不是多租户生产服务；不提供完整隐私擦除、自动宿主hooks、自动合并或所有客户端认证。图谱界面当前以中文为主。

### 安装与运行

要求Python ≥3.11和SQLite FTS5。在项目根目录执行以下命令。建议先创建并激活自己的虚拟环境；命令中的python应指向该环境。

```shell
python -m venv .venv
# Windows PowerShell: ./.venv/Scripts/Activate.ps1
# POSIX shell: . .venv/bin/activate
python -m pip install -r requirements-lock.txt
python -m memory_merge --data ./demo-data demo
python -m memory_merge --data ./demo-data web --port 8765
```

打开`http://127.0.0.1:8765`，载入`demo`；Ctrl+C停止。演示使用合成数据。锁文件来自Windows测试环境（pywin32带平台条件），其他平台未全面实测；遇到平台依赖问题可尝试最小依赖`python -m pip install -r requirements.txt`，并重新运行测试。

```shell
python -m memory_merge --data ./data capture --project demo --source demo:synthetic --event-id event-1 "SQLite decision"
python -m memory_merge --data ./data list --project demo --status pending
python -m memory_merge --data ./data review --project demo MEMORY_ID approve
python -m memory_merge --data ./data recall --project demo SQLite
python -m memory_merge --data ./data rag --project demo SQLite
python -m memory_merge --data ./data backup ./backup.sqlite3
python -m memory_merge --data ./data rebuild
python -m unittest discover -s tests -v
```

将MEMORY_ID替换为返回的ID。Markdown是派生镜像，不应手工编辑后期待双向同步；forget是软删除，不会保证擦除数据库及备份中的原文。

### MCP与模型配置

在客户端中将command设置为所选环境的Python解释器，args设置为`["-m", "memory_merge.server"]`，cwd设置为项目根目录（若不支持cwd，可设置PYTHONPATH或先`pip install .`）。MM_DATA设置为自行选择的数据目录。不要将个人配置提交到仓库。

默认工具：capture、remember、recall、rag_context、graph、judge、index、health（均以`memory_`为前缀）。审核端另设`MM_ENABLE_REVIEW=1`并重启，才注册review_queue、review、link。

可选环境变量：`MM_EMBED_URL` / `MM_EMBED_MODEL` / `MM_EMBED_KEY`与`MM_JUDGE_URL` / `MM_JUDGE_MODEL` / `MM_JUDGE_KEY`。模型服务由使用者另行部署。远程传输需明确同意；不要在文件中提交密钥。stdio没有TCP端口，8765只是图谱端口。

### 文档、许可与隐私

- [研究整理](<docs/RESEARCH.md>) · [架构与运维](<docs/ARCHITECTURE.md>) · [发布检查](<docs/RELEASING.md>)。
- [中文Release Notes](<RELEASE_NOTES.zh-CN.md>) · [隐私说明](<PRIVACY.md>) · [许可状态](<LICENSE-STATUS.md>)。
- 原创部分尚未选择开源许可证；公开前由权利人决定。不把上游许可证套用到本项目。
- 发布包排除原始会话、私人资料、本机绝对路径、数据库、模型、虚拟环境、原始研究快照、日志与Git历史。公开上游账号仅用于归属。

## English

### Features and limitations

SQLite is the transactional source of truth, with retryable outbox exports to Markdown. The prototype supports automatic candidates, user-requested memories, review, classification, project scopes, idempotent events and explicit relationships. Native stdio tools use the official MCP SDK; a read-only local web page presents the mind graph.

- Automatic candidates remain pending. Only approved records enter retrieval and the graph.
- Default retrieval is lexical (FTS5/literal fallback), with no model calls. A configured embedding provider enables cosine similarity and RRF fusion.
- Judge output is advisory, never automatic approval. RAG returns cited evidence; the client generates the answer.
- Providers are opt-in. Non-loopback endpoints require HTTPS and `MM_ALLOW_REMOTE=1`. No automatic model downloads or existing-data imports.
- This is not a multi-tenant production service. Secure erasure, automatic host hooks, automatic merging and universal client certification are not implemented. The graph UI currently uses mostly Chinese labels.

### Install and run

Use Python ≥3.11 with SQLite FTS5. Run the shared installation and demo commands above from the project root, with your own activated virtual environment. Open `http://127.0.0.1:8765`, select `demo`, and stop with Ctrl+C. Demo data is synthetic.

The lock file was tested on Windows and includes a platform marker for pywin32. Other platforms have not been comprehensively validated. The minimal dependency file is an alternative, not an equally tested lock. Run `python -m unittest discover -s tests -v` after installation.

The shared CLI examples cover capture, pending review, recall, RAG context, backup and Markdown rebuilding. Replace MEMORY_ID with an actual returned ID. Markdown is a derived view, not a bidirectional editor. Forgetting is a soft delete and does not securely erase database or backup content.

### MCP and optional models

Configure the client's command as your chosen Python interpreter, args as `["-m", "memory_merge.server"]`, and cwd as the project root. If cwd is unsupported, set PYTHONPATH or install the package with `pip install .`. Choose your own MM_DATA directory; never commit personal client configuration.

Default tools are capture, remember, recall, rag_context, graph, judge, index and health, all prefixed with `memory_`. Set `MM_ENABLE_REVIEW=1` only for a trusted review instance to expose review_queue, review and link.

Optional environment variables are `MM_EMBED_URL`, `MM_EMBED_MODEL`, `MM_EMBED_KEY`, `MM_JUDGE_URL`, `MM_JUDGE_MODEL`, and `MM_JUDGE_KEY`. Deploy model endpoints separately. Explicitly consent before enabling remote transmission, and keep credentials out of files. Stdio has no TCP port; port 8765 is only for the graph viewer.

### Documentation, licensing and privacy

See [research summary](<docs/RESEARCH.md>), [architecture and operations](<docs/ARCHITECTURE.md>), [release checklist](<docs/RELEASING.md>), [English release notes](<RELEASE_NOTES.en.md>), [privacy statement](<PRIVACY.md>), and [license status](<LICENSE-STATUS.md>).

No open-source license has been selected for the original work; the rights holder must choose one before presenting this as licensed open-source software. Upstream licenses do not automatically license this implementation.

The release excludes original conversations, private data, machine-specific absolute paths, databases, models, virtual environments, raw research snapshots, logs and Git history. Public upstream accounts are retained solely for attribution. This is a local release bundle, not proof of a GitHub upload.
