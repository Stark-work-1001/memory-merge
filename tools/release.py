"""Build and verify an allowlisted, reproducible source release into dist/.

    python tools/release.py

Checks, in order: no unexpected files; privacy scan of every included text file; one version string
everywhere (memory_merge/__init__.py, CHANGELOG.md, release notes); local Markdown links resolve;
the test suite passes from the checkout; the ZIP is byte-identical when built twice; every archive
entry matches its source; the suite passes again from the unpacked archive. Nothing is uploaded.
"""
import hashlib, io, json, os, re, subprocess, sys, tempfile, zipfile
from fnmatch import fnmatch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = re.search(r"__version__ = '([^']+)'", (ROOT / 'memory_merge' / '__init__.py').read_text(encoding='utf-8')).group(1)
TAG = 'v' + VERSION
PREFIX = 'memory-merge-' + TAG
ARCHIVE = PREFIX + '-source.zip'
INCLUDE = ['.gitignore', '.gitattributes', '.dockerignore', 'Dockerfile', 'LICENSE', 'LICENSE-STATUS.md', 'PRIVACY.md', 'SECURITY.md',
           'CONTRIBUTING.md', 'CHANGELOG.md', 'README.md', 'README.zh-CN.md', 'RELEASE_NOTES.en.md', 'RELEASE_NOTES.zh-CN.md',
           'pyproject.toml', 'requirements.txt', 'requirements-lock.txt',
           'memory_merge/*.py', 'memory_merge/static/*', 'native/Cargo.toml', 'native/Cargo.lock', 'native/pyproject.toml', 'native/src/*.rs',
           'tests/*.py', 'tests/legacy/*.py', 'datasets/*/*.jsonl', 'datasets/*/*.md', 'docs/*.md', 'docs/eval/*.json', 'bench/*.py', 'tools/*.py',
           'integrations/*.md', 'integrations/examples/*', '.github/workflows/*.yml', '.github/ISSUE_TEMPLATE/*.yml', '.github/*.md']
IGNORED_DIRS = {'.venv', 'venv', '__pycache__', '.git', 'data', 'demo-data', 'build', 'dist', 'target', 'backups', 'markdown', 'results'}
# Test fixtures that contain path-like strings on purpose (path-validation tests). Exempt per file and rule only.
SCAN_EXEMPT = {('tests/test_review_findings.py', 'absolute_drive'),
               # synthetic credentials in URLs (user:pass@host) that the screening tests must detect
               ('tests/test_review_findings.py', 'email'), ('tests/test_text_vectors.py', 'email')}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def scan(name, data):
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError:
        return [{'file': name, 'rule': 'not_utf8'}]
    # Patterns are assembled from pieces so the scanner does not flag its own source.
    rules = [('absolute_drive', r'(?<![A-Za-z0-9])' + r'[A-Za-z]:' + r'[\\/]'),
             ('user_home', '/' + r'(?:Users|home)/[A-Za-z0-9_.-]+/'),
             ('email', r'\b[A-Za-z0-9._%+-]+' + '@' + r'(?!example\.)[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'),
             ('phone', r'(?<![\w])' + r'(?:\+86[- ]?)?1[3-9]\d{9}' + r'(?![\w])'),
             ('credential', r'\b(?:gh[pousr]_' + r'[A-Za-z0-9]{20,}|sk-' + r'[A-Za-z0-9]{20,})\b')]
    found = [{'file': name, 'rule': label} for label, pattern in rules if re.search(pattern, text) and (name, label) not in SCAN_EXEMPT]
    for marker in ['.' + 'agent-download', '.' + 'agent-core', 'Admin' + 'istrator', 'BEGIN ' + 'PRIVATE KEY']:
        if marker.lower() in text.lower(): found.append({'file': name, 'rule': 'private_environment_marker'})
    return found


def collect():
    included, unexpected = [], []
    for path in sorted(ROOT.rglob('*')):
        rel = path.relative_to(ROOT).as_posix()
        if any(part in IGNORED_DIRS or part.endswith('.egg-info') for part in path.relative_to(ROOT).parts): continue
        if path.is_symlink(): raise RuntimeError('symlink is not allowed: ' + rel)
        if not path.is_file() or path.suffix in ('.pyc', '.pyd', '.so'): continue
        (included if any(fnmatch(rel, p) for p in INCLUDE) else unexpected).append(rel)
    if unexpected: raise RuntimeError('unexpected files (add to INCLUDE or remove): ' + ', '.join(unexpected))
    return included


def run_tests(root):
    env = {k: v for k, v in os.environ.items() if not k.startswith('MM_')}
    env.update(PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1', PYTHONPATH=str(root))
    proc = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests'], cwd=root, env=env,
                          capture_output=True, text=True, encoding='utf-8', timeout=900)
    log = proc.stdout + proc.stderr
    ran = re.search(r'Ran (\d+) tests', log)
    if proc.returncode or not ran:
        print(log[-4000:], file=sys.stderr); raise RuntimeError('test suite failed; no release built')
    skipped = re.search(r'skipped=(\d+)', log)
    return {'tests': int(ran.group(1)), 'skipped': int(skipped.group(1)) if skipped else 0, 'exit_code': 0}


def build_zip(payload):
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, data in sorted(payload.items()):
            info = zipfile.ZipInfo(PREFIX + '/' + name, date_time=(2026, 10, 13, 0, 0, 0))
            info.create_system = 3; info.external_attr = 0o100644 << 16; info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data, compresslevel=9)
    return out.getvalue()


def main():
    files = collect()
    payload = {name: (ROOT / name).read_bytes() for name in files}
    crlf = [n for n, d in payload.items() if b'\r\n' in d and not n.endswith('.zip')]
    if crlf: raise RuntimeError('CRLF line endings (hashes would depend on the checkout platform): ' + ', '.join(crlf))
    findings = [f for name, data in payload.items() for f in scan(name, data)]
    if findings: raise RuntimeError('privacy scan: ' + json.dumps(findings))
    changelog = payload['CHANGELOG.md'].decode()
    assert f'## {VERSION}' in changelog, 'CHANGELOG.md has no entry for ' + VERSION
    for notes in ('RELEASE_NOTES.en.md', 'RELEASE_NOTES.zh-CN.md'):
        assert payload[notes].decode().startswith(f'# Memory Merge {VERSION}'), notes + ' is not for ' + VERSION
    for name, data in payload.items():
        if name.endswith('.md'):
            for link in re.findall(r'\]\(<?([^)>#\s]+)', data.decode()):
                if '://' in link or link.startswith('mailto:'): continue
                target = (ROOT / name).parent / link
                assert target.resolve().is_relative_to(ROOT) and target.exists(), (name, link)
    source_tests = run_tests(ROOT)
    manifest = {'release': TAG, 'version': VERSION, 'files': [{'path': n, 'bytes': len(d), 'sha256': sha(d)} for n, d in sorted(payload.items())]}
    payload['RELEASE_MANIFEST.json'] = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode()
    archive = build_zip(payload)
    assert build_zip(payload) == archive, 'archive is not reproducible'
    with tempfile.TemporaryDirectory(prefix='memory-merge-release-') as tmp:
        with zipfile.ZipFile(io.BytesIO(archive)) as z:
            assert z.testzip() is None and len(z.infolist()) == len(payload)
            for info in z.infolist():
                assert info.filename.startswith(PREFIX + '/') and '..' not in Path(info.filename).parts
                assert z.read(info) == payload[info.filename[len(PREFIX) + 1:]]
            z.extractall(tmp)
        unpacked_tests = run_tests(Path(tmp) / PREFIX)
    dist = ROOT / 'dist'; dist.mkdir(exist_ok=True)
    (dist / ARCHIVE).write_bytes(archive)
    (dist / 'SHA256SUMS').write_text(sha(archive) + '  ' + ARCHIVE + '\n', encoding='utf-8', newline='\n')
    validation = {'release': TAG, 'archive': ARCHIVE, 'sha256': sha(archive), 'bytes': len(archive), 'files': len(files),
                  'privacy_findings': findings, 'version_consistent': True, 'source_tests': source_tests, 'unpacked_tests': unpacked_tests,
                  'reproducible': True, 'limits': ['Pattern scans cannot recognise every identifier.',
                                                   'Tests ran on the build machine only; CI covers other platforms.', 'Nothing was uploaded.']}
    (dist / 'RELEASE_VALIDATION.json').write_text(json.dumps(validation, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(validation, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
