# Releasing / 发布流程

## Local release / 本地Release

Version: `v0.1.0-alpha.1`; Python metadata: `0.1.0a1`. This is the first public-delivery candidate, not a claim that the earlier research prototype was a stable release. 这是首次公开交付候选，不将研究原型视为稳定版本。

From the repository root with dependencies installed / 在项目根目录和已安装依赖的环境运行：

```shell
python tools/release.py
```

The builder uses an explicit allowlist, rejects unexpected files (except documented runtime caches/environments/output), scans text, validates local documentation links and versions, runs source tests, creates a fixed-metadata ZIP, extracts it to a temporary directory, compares file hashes, and reruns tests. It writes the ZIP, SHA256SUMS, RELEASE_MANIFEST.json and RELEASE_VALIDATION.json to the repository root. Test output with machine paths is not distributed; failures stop packaging and report details only to the invoking console.

构建器使用白名单，拒绝非预期文件（明确的运行缓存、环境及输出除外），扫描文本、检查链接和版本，运行源码测试，生成固定元数据ZIP，临时解包并逐文件比对哈希，再运行测试。输出ZIP、校验和、逐文件清单与脱敏验证报告；含机器路径的测试原始输出不分发，失败停止打包并只在本机控制台报告。

The archive contains one versioned top-level folder. No Git history, personal client configuration, data or virtual environment is included. Determinism assumes the same source bytes and Python/zlib environment. 校验ZIP只包含一个版本目录；无Git历史、私人配置、数据或虚拟环境。同源码与相同Python/zlib环境下可重建一致结果。

## Before online publishing / 在线发布前

1. Select an original-work license and add LICENSE. If source changes, rebuild. 由权利人选择原创许可；变更后重建。
2. Review public attribution and privacy exclusions. Do not commit personal configuration or old research snapshots. 检查公开归属与隐私，不提交私人配置或旧快照。
3. Create a repository under the intended account. Verify remote and Git identity locally; this bundle deliberately has neither. 自行确认目标账号、远程与提交身份，本包不携带这些信息。
4. Commit reviewed source and tag the release `v0.1.0-alpha.1`. Tags are not created by the local archive builder. 审查提交后创建标签，打包器不伪造Git标签。
5. Create a GitHub Release with **Pre-release** enabled; use the provided bilingual notes and attach the ZIP and checksum. 创建预发布，附双语notes、ZIP与校验值。
6. Download the uploaded asset and verify its SHA-256. 上传后下载核对哈希。

No GitHub upload, remote tag or package-registry publication is performed by this preparation. 此准备工作不执行GitHub上传、远程标签或包仓库发布。
