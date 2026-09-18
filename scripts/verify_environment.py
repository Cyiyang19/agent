"""Run real workflows and checks; write timestamped, reproducible evidence."""
import asyncio
import importlib.metadata
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lab.graph_lab import run_case
from lab.team_lab import run_team


def main():
    out = ROOT / 'outputs'
    out.mkdir(exist_ok=True)
    checks = []
    for name, args in [('pip_check', ['-m', 'pip', 'check']), ('pytest', ['-m', 'pytest', '-q'])]:
        r = subprocess.run([sys.executable, '-X', 'utf8', *args], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
        (out / f'{name}.txt').write_text(r.stdout + r.stderr, encoding='utf-8')
        checks.append({'name': name, 'pass': r.returncode == 0})
        print(r.stdout.strip())
    graph_specs = [
        ('baseline', {'baseline': True}, 'unreviewed', 1),
        ('reflection', {}, 'pass', 2),
        ('transient', {'scenario': 'transient'}, 'pass', 2),
        ('failure', {'scenario': 'failure'}, 'needs_help', 2),
        ('unknown', {'question': 'tomorrow weather'}, 'needs_help', 2),
        ('no_retry', {'max_retries': 0}, 'needs_help', 1),
        ('strict', {'min_sources': 3}, 'needs_help', 2),
    ]
    for name, kwargs, expected, attempts in graph_specs:
        options = {'min_sources': 2, 'max_retries': 1, **kwargs}
        r = run_case(**options)
        (out / f'{name}.json').write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding='utf-8')
        passed = r['status'] == expected and r['attempts'] == attempts
        checks.append({'name': name, 'pass': passed, 'status': r['status'], 'attempts': r['attempts']})
        print(f"{name}: {r['status']}, attempts={r['attempts']}, acceptance={'PASS' if passed else 'FAIL'}")
    for name, repair, expected in [('team', True, 'pass'), ('team_no_repair', False, 'needs_help')]:
        r = asyncio.run(run_team(repair))
        (out / f'{name}.json').write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding='utf-8')
        checks.append({'name': name, 'pass': r['status'] == expected, 'status': r['status']})
        print(f'{name}: {r["status"]}')
    report = {'verified_at_utc': datetime.now(timezone.utc).isoformat(), 'python': platform.python_version(),
              'platform': platform.system(), 'mode': 'offline; real framework execution; no LLM inference',
              'packages': {name: importlib.metadata.version(name) for name in ['langgraph', 'autogen-agentchat', 'autogen-ext', 'pytest']},
              'checks': checks, 'pass': all(c['pass'] for c in checks)}
    (out / 'environment_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print('PASS: CH6 offline framework lab verified end-to-end.' if report['pass'] else 'FAIL: inspect outputs.')
    return 0 if report['pass'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
