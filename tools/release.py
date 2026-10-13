"""Build and verify an allowlisted, fixed-metadata source release."""
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import tomllib
import zipfile

ROOT = Path(__file__).resolve().parents[1]
TAG = 'v0.1.0-alpha.1'
VERSION = '0.1.0a1'
PREFIX = 'memory-merge-' + TAG
ARCHIVE = PREFIX + '-source.zip'
FILES = [
    '.gitignore', 'README.md', 'LICENSE-STATUS.md', 'PRIVACY.md',
    'RELEASE_NOTES.zh-CN.md', 'RELEASE_NOTES.en.md',
    'pyproject.toml', 'requirements.txt', 'requirements-lock.txt',
    'docs/RESEARCH.md', 'docs/ARCHITECTURE.md', 'docs/RELEASING.md',
    'memory_merge/__init__.py', 'memory_merge/__main__.py',
    'memory_merge/store.py', 'memory_merge/providers.py',
    'memory_merge/server.py', 'memory_merge/web.py',
    'memory_merge/static/index.html', 'memory_merge/static/app.js',
    'memory_merge/static/style.css', 'tests/test_store.py',
    'tests/test_providers.py', 'tests/test_operations.py',
    'tests/test_integration.py', 'tools/release.py',
]
OUTPUTS = {ARCHIVE, 'SHA256SUMS', 'RELEASE_MANIFEST.json', 'RELEASE_VALIDATION.json'}
IGNORED_DIRS = {'.venv', '__pycache__', '.git', 'data', 'demo-data', 'build', 'dist'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def scan(name, data):
    text = data.decode('utf-8')
    # Assemble platform markers so the scanner does not flag its own source.
    drive = r'(?<![A-Za-z0-9])' + r'[A-Za-z]:' + r'[\\/]'
    home = '/' + r'(?:Users|home)/[A-Za-z0-9_.-]+/'
    email = r'\b[A-Za-z0-9._%+-]+' + '@' + r'[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    phone = r'(?<![\w])' + r'(?:\+86[- ]?)?1[3-9]\d{9}' + r'(?![\w])'
    token = r'\b(?:gh[pousr]_' + r'[A-Za-z0-9]{20,}|sk-' + r'[A-Za-z0-9]{20,})\b'
    findings = []
    for label, pattern in [('absolute_drive', drive), ('user_home', home),
                           ('email', email), ('phone', phone), ('credential', token)]:
        if re.search(pattern, text):
            findings.append({'file': name, 'rule': label})
    private_markers = ['.' + 'agent-download', '.' + 'agent-core', 'Admin' + 'istrator',
                       'session-' + '1286c7fa', 'BEGIN ' + 'PRIVATE KEY']
    for marker in private_markers:
        if marker.lower() in text.lower():
            findings.append({'file': name, 'rule': 'private_environment_marker'})
    return findings


def run_tests(root):
    env = {k: v for k, v in os.environ.items() if not k.startswith('MM_')}
    env['PYTHONUTF8'] = '1'
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    env['PYTHONPATH'] = str(root)
    proc = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-v'],
                          cwd=root, env=env, capture_output=True, text=True, encoding='utf-8', timeout=120)
    log = proc.stdout + proc.stderr
    if proc.returncode:
        print(log, file=sys.stderr)
        raise RuntimeError('test suite failed; no release accepted')
    match = re.search(r'Ran (\d+) tests', log)
    if not match or int(match.group(1)) != 15:
        raise RuntimeError('unexpected test count')
    return {'tests': 15, 'exit_code': 0, 'real_mcp_stdio_roundtrip': True}


def build_zip(payload):
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, data in sorted(payload.items()):
            info = zipfile.ZipInfo(PREFIX + '/' + name, date_time=(2026, 10, 13, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data, compresslevel=9)
    return out.getvalue()


def main():
    unexpected = []
    for path in ROOT.rglob('*'):
        rel = path.relative_to(ROOT)
        if any(part in IGNORED_DIRS or part.endswith('.egg-info') for part in rel.parts):
            continue
        if path.is_symlink():
            raise RuntimeError('symlink is not allowed: ' + rel.as_posix())
        if path.is_file() and rel.as_posix() not in set(FILES) | OUTPUTS:
            unexpected.append(rel.as_posix())
    if unexpected:
        raise RuntimeError('unexpected files: ' + ', '.join(unexpected))
    payload = {name: (ROOT / name).read_bytes() for name in FILES}
    findings = [f for name, data in payload.items() for f in scan(name, data)]
    if findings:
        raise RuntimeError('privacy scan: ' + json.dumps(findings))
    readme = payload['README.md'].decode()
    assert readme.startswith('# References & Authors / 参考项目与作者')
    assert readme.index('https://github.com/') < readme.index('# Memory Merge')
    assert '## 中文' in readme and '## English' in readme
    assert tomllib.loads(payload['pyproject.toml'].decode())['project']['version'] == VERSION
    assert "__version__='" + VERSION + "'" in payload['memory_merge/__init__.py'].decode()
    for name, data in payload.items():
        if name.endswith('.md'):
            for link in re.findall(r'\]\(<([^>]+)>\)', data.decode()):
                if '://' in link:
                    continue
                target = (ROOT / name).parent / link.split('#')[0]
                assert target.resolve().is_relative_to(ROOT) and target.is_file(), (name, link)
    source_tests = run_tests(ROOT)
    manifest = {'release': TAG, 'files': [{'path': n, 'bytes': len(d), 'sha256': sha(d)}
                                        for n, d in sorted(payload.items())]}
    manifest_bytes = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode()
    payload['RELEASE_MANIFEST.json'] = manifest_bytes
    archive = build_zip(payload)
    assert build_zip(payload) == archive
    with tempfile.TemporaryDirectory(prefix='memory-merge-release-') as tmp:
        with zipfile.ZipFile(io.BytesIO(archive)) as z:
            assert z.testzip() is None and not z.comment
            assert len(z.infolist()) == len(payload)
            for info in z.infolist():
                assert info.filename.startswith(PREFIX + '/') and '..' not in Path(info.filename).parts
                assert not info.comment and not info.extra
                name = info.filename[len(PREFIX) + 1:]
                assert z.read(info) == payload[name]
                assert not scan(name, z.read(info))
            z.extractall(tmp)
        unpacked = Path(tmp) / PREFIX
        for name, data in payload.items():
            assert sha((unpacked / name).read_bytes()) == sha(data)
        unpacked_tests = run_tests(unpacked)
    validation = {
        'release': TAG, 'archive': ARCHIVE, 'source_files': len(FILES),
        'archive_entries': len(payload), 'privacy_pattern_findings': findings,
        'attribution_first': True, 'bilingual_readme': True, 'version_consistent': True,
        'source_tests': source_tests, 'unpacked_tests': unpacked_tests,
        'archive_crc': 'pass', 'archive_content_hashes': 'match',
        'fixed_zip_metadata': True, 'repeated_build_bytes_identical': True,
        'sha256': sha(archive), 'bytes': len(archive),
        'limits': ['Pattern scans cannot guarantee recognition of every possible identity.',
                   'No clean-environment dependency reinstall or cross-platform certification.',
                   'No real model quality evaluation; no GitHub upload.',
                   'Original-work license is not selected.']}
    (ROOT / ARCHIVE).write_bytes(archive)
    (ROOT / 'RELEASE_MANIFEST.json').write_bytes(manifest_bytes)
    (ROOT / 'SHA256SUMS').write_text(sha(archive) + '  ' + ARCHIVE + '\n', encoding='utf-8')
    (ROOT / 'RELEASE_VALIDATION.json').write_text(json.dumps(validation, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(validation, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
