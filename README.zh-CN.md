# Memory Merge

面向 AI 智能体的本地优先、单用户长期记忆。智能体通过 MCP 提出记忆候选，由你审核；
审核通过的记忆以带引用的证据形式返回。SQLite 是唯一真源，Markdown 是可阅读、可编辑的镜像；
除非你明确配置，任何数据都不会离开本机。

版本 `0.2.0a1`（alpha）· MIT 许可 · [English](README.md) · [变更记录](CHANGELOG.md)

## 能做什么

- **先审核后生效**：智能体捕获的决策、偏好、步骤、教训、事实一律进入“待审”，只有你能批准；
  智能体无法自行批准自己写入的记忆（0.1 中可以，这是本版修复的最重要的安全问题）。
- **中文、日文与中英混排可检索**：在 SQLite FTS5 之上用二元切分（bigram）分析器取代 0.1 的空格分词；
  可选的本地向量模型（Qwen3-Embedding）补充语义与跨语言检索。
- **返回证据而不是答案**：`memory_rag_context` 返回带 `[memory:id]` 引用、以随机分隔符隔离的证据块，
  由你的智能体生成回答。
- **任务简报与个人画像**：从已存文本组装（不经过模型）偏好、禁忌、决策、教训。
- **文档与会话**：导入 Markdown、文本、PDF、浏览器书签、摘录（带页码/标题路径出处）；
  通过 Claude Code 钩子自动归档会话。
- **生命周期**：修订（supersedes）、归档、遗忘、彻底清除、重复检测与独立来源计数、冲突提示。
- **运维**：经过校验的备份、恢复演练、迁移前自动备份、`doctor` 诊断、本地图谱查看器（可选审核模式）。

## 快速开始

需要 Python 3.11+（带 SQLite FTS5，python.org 官方版本与主流发行版均满足）。

```bash
git clone https://github.com/Stark-work-1001/memory-merge.git
cd memory-merge
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1      POSIX: . .venv/bin/activate
python -m pip install -r requirements-lock.txt
python -m pip install .
memory-merge doctor
```

用合成数据试用：

```bash
memory-merge --data ./demo-data demo
memory-merge --data ./demo-data recall --project demo "事务的真源是什么"
memory-merge --data ./demo-data briefing --project demo
memory-merge --data ./demo-data web --port 8765        # 打开 http://127.0.0.1:8765 ，项目填 demo
```

接入智能体（只打印配置，不写入任何文件）：

```bash
memory-merge setup claude-code        # 也可 claude-desktop、codex、cursor、generic
```

再把 [integrations/AGENT_INSTRUCTIONS.md](integrations/AGENT_INSTRUCTIONS.md) 交给智能体。审核：

```bash
memory-merge queue --project myproject
memory-merge review --project myproject 记忆ID approve
memory-merge web --review             # 或在浏览器里审核
```

未指定 `--data`/`MM_DATA` 时，数据存放在系统的应用数据目录（`memory-merge doctor` 会显示路径）。

## 检索质量（实测）

数据集 `datasets/memory-eval-v1`：240 条中文、英文、中英混排与日文记忆，160 条分级标注的查询；
所有参数只在 64 条开发集查询上调整，下表为 96 条测试集查询的结果：

| | nDCG@10 | Recall@10 | 零结果查询 | p50 延迟 |
|---|---|---|---|---|
| 0.1（已发布代码） | 0.340 | 0.392 | 45.8% | 6-11 ms |
| 0.2 词法检索（默认，无模型） | 0.649 | 0.754 | 0% | 4-7 ms |
| 0.2 + Qwen3-Embedding-0.6B（Q8_0，经 Ollama） | 0.827 | 0.887 | 0% | 200-470 ms* |

\* 主要是访问嵌入服务的 HTTP 往返，且在共享 GPU 上测得。复现命令、按查询类型的结果，以及数据集的局限
（合成数据，为本项目编写）见 [docs/EVALUATION.md](docs/EVALUATION.md)。词法检索不是语义检索：
没有共同词语的改写需要向量阶段。

## 安全模型

检索到的记忆只是证据，绝不是指令。自动捕获一律待审，只有你能批准。Judge 只给建议，输出异常即失败关闭。
未经明确配置不访问网络。含凭据的单条记忆会被拒绝，批量导入会被脱敏。`forget` 只是隐藏；`purge`
删除并压缩数据库，但无法触及已有备份、文件系统快照或远程模型服务。完整威胁模型（包括明确**不防御**的部分）
见 [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md)。

## 尚未验证的内容

CI 已为 Linux、macOS、Windows 与 Python 3.11-3.13 配置，但尚未实际运行；测试套件只在 Windows 11
（Python 3.11.15、3.12.13、3.13.5、3.14.5）上运行过。检索指标只来自一个合成数据集。未做负载测试，
设计目标是单用户。llama.cpp 进程内后端按 llama-cpp-python 文档 API 实现但未实际执行（测试机上编译失败）；
哪些模型路径真正执行过见 docs/MODELS.md。PDF 导入只用生成的 PDF 测试过。完整清单见 [docs/EVALUATION.md](docs/EVALUATION.md#not-verified)。

## 文档

[架构](docs/ARCHITECTURE.md) · [决策](docs/DECISIONS.md) · [威胁模型](docs/THREAT_MODEL.md) · [模型](docs/MODELS.md) ·
[评测](docs/EVALUATION.md) · [运维](docs/OPERATIONS.md) · [集成](docs/INTEGRATIONS.md) · [数据格式](docs/DATA_FORMATS.md) ·
[原生内核](docs/NATIVE.md) · [独立审查](docs/REVIEW.md) · [参考项目](docs/REFERENCES.md)（文档以英文为准）

## 许可

MIT，见 [LICENSE](LICENSE) 与 [LICENSE-STATUS.md](LICENSE-STATUS.md)。
