"""Explicit live CLI E2E: three paid Bedrock requests, never run by pytest.

Usage: python tests/e2e_live_cli.py --profile PROFILE --output-dir PATH
Uses synthetic birth data; no credentials are written to artifacts.
"""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from fortune_teller.core.plugin_manager import PluginManager


def validate_cli_response(mode, transcript, stderr, returncode):
    """Check observable CLI behavior without requiring the LLM to echo pillars."""
    assert returncode == 0, f'exit status {returncode}'
    assert not stderr.strip(), 'unexpected stderr'
    assert '[MOCK]' not in transcript and '模拟' not in transcript, 'mock response'
    for failure in ('Error:', '解读生成出错', '错误:', 'Traceback', '数据处理出错'):
        assert failure not in transcript, failure
    assert '✓ 解读生成完成' in transcript, 'reading did not complete'
    assert '请选择要深入解读的主题' in transcript, 'follow-up menu not reached'
    assert transcript.rstrip().endswith('已取消选择'), 'normal main-menu exit not reached'
    expected = {'bazi': ['日主: 甲 (木)', '北京时间'],
                'tarot': ['过去', '现在', '未来'], 'zodiac': ['摩羯']}
    for term in expected[mode]:
        assert term in transcript, f'missing processed data: {term}'
    if mode == 'bazi':
        assert re.search(r'天干:\s+己 \(土\)\s+丁 \(火\)\s+甲 \(木\)\s+庚 \(金\)', transcript)
        assert re.search(r'地支:\s+卯 \(木\)\s+丑 \(土\)\s+子 \(水\)\s+午 \(火\)', transcript)
    body = transcript.split('✨ 正在生成解读 ✨', 1)[1].split('✓ 解读生成完成', 1)[0]
    reading = body.replace('=' * 60, '').strip()
    assert len(reading) >= 100, f'response too short: {len(reading)}'
    return reading


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', required=True)
    parser.add_argument('--region', default='us-west-2')
    parser.add_argument('--model', default='us.anthropic.claude-sonnet-4-5-20250929-v1:0')
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--timeout', type=int, default=240)
    parser.add_argument('--max-tokens', type=int, default=6000)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manager = PluginManager()
    assert manager.load_all_plugins() == 3
    systems = [item['name'] for item in manager.get_plugin_info_list()]
    cases = {
        'bazi': ['2000-01-07', '12:30', '1', '北京'],
        'tarot': ['如何合理安排业余项目与学习的时间？', '2', '2', 'E2E测试'],
        'zodiac': ['2000-01-07', '', '', '2'],
    }
    results = []
    with tempfile.TemporaryDirectory(prefix='fortune-e2e-') as directory:
        config = Path(directory) / 'config.yaml'
        config.write_text(yaml.safe_dump({
            'llm': {'provider': 'aws_bedrock', 'profile': args.profile,
                    'region': args.region, 'model': args.model,
                    'temperature': 0.7, 'max_tokens': args.max_tokens},
            'plugins': {'enabled': systems},
        }), encoding='utf-8')
        for mode, values in cases.items():
            # Select the actual discovered menu index; then confirm, cancel the
            # follow-up menu, and exit the main menu (two independent q inputs).
            feed = '\n'.join([str(systems.index(mode) + 1), *values, '', 'q', 'q']) + '\n'
            events_file = args.output_dir.resolve() / f'{mode}-bedrock-events.jsonl'
            events_file.write_text('', encoding='utf-8')
            env = {**os.environ, 'PYTHONPATH': str(REPO), 'FORTUNE_TELLER_STREAMING': 'true',
                   'PYTHONUNBUFFERED': '1', 'E2E_BEDROCK_EVENTS': str(events_file), 'AWS_EC2_METADATA_DISABLED': 'true'}
            started = time.monotonic()
            print(f'RUN {mode} (real Bedrock streaming)', flush=True)
            try:
                process = subprocess.run(
                    [sys.executable, str(REPO / 'tests/e2e_live_bootstrap.py'), '--lang', 'zh', '--config', str(config)],
                    input=feed, text=True, capture_output=True, cwd=directory,
                    env=env, timeout=args.timeout,
                )
                transcript = re.sub(r'\x1b\[[0-9;]*[A-Za-z]', '', process.stdout)
                (args.output_dir / f'{mode}-cli.txt').write_text(transcript, encoding='utf-8')
                (args.output_dir / f'{mode}-stderr.txt').write_text(process.stderr, encoding='utf-8')
                events = [json.loads(line) for line in events_file.read_text().splitlines()]
                delta = next(event for event in reversed(events) if event['type'] == 'message_delta')
                stop_reason = delta.get('delta', {}).get('stop_reason')
                assert stop_reason == 'end_turn', f'model stopped with {stop_reason}'
                assert any(event['type'] == 'message_stop' for event in events), 'missing terminal stream event'
                reading = validate_cli_response(mode, transcript, process.stderr, process.returncode)
                (args.output_dir / f'{mode}-reading.md').write_text(reading + '\n', encoding='utf-8')
                chunks_log = Path(directory) / 'streaming_chunks.log'
                chunks = chunks_log.read_text(encoding='utf-8') if chunks_log.exists() else ''
                last = chunks.rsplit('=== START OF STREAMING SESSION ===', 1)[-1]
                chunk_count = len(re.findall(r'Chunk #\d+ received', last))
                assert chunk_count > 1, 'no multi-chunk model stream observed'
                latency = re.search(r'首个块延迟: ([\d.]+)秒', last)
                result = {'mode': mode, 'status': 'PASS', 'response_characters': len(reading),
                          'chunks': chunk_count, 'stop_reason': stop_reason,
                          'output_tokens': delta.get('usage', {}).get('output_tokens'),
                          'first_chunk_seconds': float(latency[1]) if latency else None}
            except Exception as exc:
                result = {'mode': mode, 'status': 'FAIL', 'error': str(exc)}
            result['elapsed_seconds'] = round(time.monotonic() - started, 2)
            results.append(result)
            print(json.dumps(result, ensure_ascii=False), flush=True)
    report = {'provider': 'aws_bedrock', 'model': args.model, 'region': args.region,
              'transport': 'real CLI / streamed invoke_model_with_response_stream',
              'synthetic_inputs': True, 'max_tokens': args.max_tokens, 'results': results}
    (args.output_dir / 'results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if any(result['status'] != 'PASS' for result in results):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
