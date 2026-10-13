# Release privacy / 发布隐私

This bundle contains selected implementation files, synthetic tests and rewritten public documentation only. It excludes requester identity, phone numbers, personal contact details, machine-specific absolute paths, original prompts, conversation histories, private memories, model weights, local configuration, virtual environments, databases, caches, raw logs and original research snapshots. Public upstream repository accounts are included only for requested attribution.

本包只包含精选实现、合成测试和重写的公开文档；排除委托人身份、手机号、私人联系方式、本机绝对路径、原始提示词、会话、私人记忆、模型权重、本地配置、虚拟环境、数据库、缓存、原始日志和研究快照。公开上游账号仅作为要求保留的来源署名。

Automated pattern scans and allowlist checks are defense in depth, not a mathematical guarantee that all possible identifying information can be recognized. Review any newly added data before publishing. Generic relative paths and loopback service examples are portable usage instructions, not source-machine details.

白名单与正则扫描是辅助防线，无法数学保证识别一切隐私；新增资料发布前仍需审阅。通用相对路径、回环服务示例是可移植使用说明，并非源机器详情。

Runtime is separate from release hygiene: the application stores user-provided content in plaintext locally. Credential-pattern screening is not comprehensive DLP. Remote providers receive the relevant text only when explicitly configured and allowed. Soft deletion is not secure erasure. Protect the data directory and backups with OS permissions and appropriate storage encryption.

运行时隐私不同于发布脱敏：应用在本地明文保存用户输入，凭据正则不是完整DLP。显式配置并同意远程模型后，相关文本会发送到该服务。软删除不等于安全擦除；数据目录与备份需由操作系统权限及合适的存储加密保护。
