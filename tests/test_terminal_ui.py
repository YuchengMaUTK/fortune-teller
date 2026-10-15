import io
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
from rich.console import Console
from rich.cells import cell_len

from fortune_teller.core.plugin_manager import PluginManager
from fortune_teller.ui import rendering
from fortune_teller.ui.animation import LoadingAnimation
from fortune_teller.ui.display import print_reading_result_streaming
from fortune_teller.ui.keyboard_input import pick_from_list


def capture_console(monkeypatch, width=80, terminal=False):
    buffer = io.StringIO()
    console = Console(file=buffer, width=width, height=24, force_terminal=terminal,
                      color_system=None, theme=rendering.THEME)
    monkeypatch.setattr(rendering, 'get_console', lambda: console)
    monkeypatch.setattr('fortune_teller.ui.animation.get_console', lambda: console)
    return console, buffer


def chart_data(mode):
    manager = PluginManager()
    assert manager.load_all_plugins() == 3
    inputs = {
        'bazi': {'birth_date': '2000-01-07', 'birth_time': '12:30', 'gender': '男'},
        'tarot': {'question': '如何安排业余学习？', 'spread': 'three_card', 'focus_area': '事业'},
        'zodiac': {'birth_date': '2000-01-07', 'question_area': '事业'},
    }
    plugin = manager.get_plugin(mode)
    return plugin.process_data(plugin.validate_input(inputs[mode]))


@pytest.mark.parametrize('mode', ['bazi', 'tarot', 'zodiac'])
@pytest.mark.parametrize('width', [40, 80, 120])
def test_charts_fit_terminal_and_preserve_data(monkeypatch, mode, width):
    console, output = capture_console(monkeypatch, width)
    rendering.display_chart(mode, chart_data(mode))
    text = output.getvalue()
    assert '\x1b' not in text
    assert all(cell_len(line) <= width for line in text.splitlines())
    if mode == 'bazi':
        assert all(pillar in text for pillar in ('己卯', '丁丑', '甲子', '庚午'))
    elif mode == 'tarot':
        assert all(position in text for position in ('过去', '现在', '未来'))
    else:
        assert '摩羯座' in text and '估算' in text


def test_pipe_stream_preserves_whitespace_and_markup(monkeypatch):
    _, output = capture_console(monkeypatch)
    text = '  \n## 标题\n\n**中文** 和 [label]，空 格\n'
    assert rendering.stream_markdown(iter(text), '解读') == text
    assert text in output.getvalue()
    assert '\x1b' not in output.getvalue()


def test_tty_stream_renders_markdown_without_losing_text(monkeypatch):
    _, output = capture_console(monkeypatch, terminal=True)
    text = '## 解读\n\n**中文关键词**\n\n```python\nx = 1\n\nx += 2\n```\n\n结尾完整。'
    assert rendering.stream_markdown(iter(text), '解读') == text
    assert '结尾完整。' in output.getvalue()
    assert 'x += 2' in output.getvalue()


def test_paragraph_commit_keeps_fenced_code_intact():
    pending = '```python\nx = 1\n\nx += 2\n'
    assert rendering._completed_block(pending) == (None, pending)
    block, remaining = rendering._completed_block(pending + '```\n\n下一段')
    assert 'x += 2' in block and remaining == '下一段'


def test_spinner_does_not_redraw_in_pipes(monkeypatch):
    _, output = capture_console(monkeypatch)
    spinner = LoadingAnimation('连接模型')
    spinner.start()
    spinner.stop()
    assert '\x1b' not in output.getvalue() and '\r' not in output.getvalue()


def test_stream_failure_stops_spinner_and_does_not_claim_success(monkeypatch):
    _, output = capture_console(monkeypatch)
    class Spinner:
        stopped = False
        def stop(self):
            self.stopped = True
    spinner = Spinner()
    def broken():
        yield '部分内容'
        raise RuntimeError('stream failed')
    with pytest.raises(RuntimeError):
        print_reading_result_streaming(broken(), pending_animation=spinner)
    assert spinner.stopped
    assert '解读生成完成' not in output.getvalue()


def test_provider_error_not_rendered_as_success(monkeypatch):
    _, output = capture_console(monkeypatch)
    print_reading_result_streaming(iter(['Error: missing credentials']))
    assert '解读生成完成' not in output.getvalue()


def test_numbered_menu_validates_and_can_cancel(monkeypatch, capsys):
    monkeypatch.setattr('fortune_teller.ui.keyboard_input._interactive', lambda: False)
    answers = iter(['bad', '3', '2'])
    monkeypatch.setattr('builtins.input', lambda _: next(answers))
    assert pick_from_list(['八字', '塔罗']) == 1
    monkeypatch.setattr('builtins.input', lambda _: 'q')
    assert pick_from_list(['八字', '塔罗']) is None


@pytest.mark.parametrize('mode,selection,values', [
    ('bazi', '1', ['2000-01-07', '12:30', '1', '北京']),
    ('tarot', '2', ['如何安排学习时间？', '2', '2', '测试']),
    ('zodiac', '3', ['2000-01-07', '', '', '2']),
])
def test_cli_pipe_and_streaming_export(tmp_path, mode, selection, values):
    repo = Path(__file__).resolve().parents[1]
    config = tmp_path / 'config.yaml'
    config.write_text('llm:\n  provider: mock\n  model: mock-model\n')
    output = tmp_path / 'reading.json'
    env = {**os.environ, 'PYTHONPATH': str(repo), 'FORTUNE_TELLER_STREAMING': 'true'}
    result = subprocess.run(
        [sys.executable, '-m', 'fortune_teller', '--lang', 'zh', '--config', str(config), '--output', str(output)],
        input='\n'.join([selection, *values, '', 'q', 'q']) + '\n',
        capture_output=True, text=True, cwd=tmp_path, env=env, timeout=15,
    )
    assert result.returncode == 0 and not result.stderr
    assert '\x1b' not in result.stdout and 'Traceback' not in result.stdout
    assert result.stdout.rstrip().endswith('已取消选择')
    data = json.loads(output.read_text())
    assert data['metadata']['system_name'] == mode
    assert data['full_text'].startswith('[MOCK]')
    assert len(data['full_text']) > 30
    assert data['full_text'] in result.stdout


def test_questionary_arrow_keys_and_q():
    pexpect = pytest.importorskip('pexpect')
    repo = Path(__file__).resolve().parents[1]
    env = {**os.environ, 'PYTHONPATH': str(repo), 'TERM': 'xterm-256color'}
    code = ('from fortune_teller.ui.keyboard_input import pick_from_list; '
            'print("RESULT", pick_from_list(["八字", "塔罗", "星座"], "选择模式"))')
    for keys, expected in [('\x1b[B\r', '1'), ('q', 'None')]:
        child = pexpect.spawn(sys.executable, ['-c', code], env=env, encoding='utf-8', timeout=10)
        child.expect('选择模式')
        child.send(keys)
        child.expect('RESULT ' + expected)
        child.expect(pexpect.EOF)
        child.close()
        assert child.exitstatus == 0


@pytest.mark.parametrize('mode,arrow_count,answers', [
    ('bazi', 0, [('出生日期', '2000-01-07'), ('出生时间', '12:30'),
                 ('性别', ''), ('出生地点', '北京')]),
    ('tarot', 1, [('你想要咨询的问题', '如何安排学习时间？'),
                  ('塔罗牌阵', '\x1b[B'), ('问题领域', '\x1b[B'), ('你的姓名', '测试')]),
    ('zodiac', 2, [('出生日期', '2000-01-07'), ('出生时间', ''),
                   ('出生地点', ''), ('关注领域', '\x1b[B')]),
])
def test_full_tty_cli_flow(tmp_path, mode, arrow_count, answers):
    pexpect = pytest.importorskip('pexpect')
    repo = Path(__file__).resolve().parents[1]
    config = tmp_path / 'config.yaml'
    config.write_text('llm:\n  provider: mock\n  model: mock-model\n')
    output = tmp_path / 'reading.json'
    env = {**os.environ, 'PYTHONPATH': str(repo), 'TERM': 'xterm-256color'}
    child = pexpect.spawn(
        sys.executable, ['-m', 'fortune_teller', '--lang', 'zh', '--config', str(config), '--output', str(output)],
        cwd=str(tmp_path), env=env, encoding='utf-8', timeout=15, dimensions=(30, 80),
    )
    try:
        child.expect('请选择占卜系统')
        child.send('\x1b[B' * arrow_count + '\r')
        for prompt, answer in answers:
            child.expect(prompt)
            child.send(answer + '\r')
        child.expect('按回车键继续')
        child.send('\r')
        child.expect('解读生成完成')
        child.expect('请选择要深入解读的主题')
        child.send('q')
        child.expect('请选择占卜系统')
        child.send('q')
        child.expect(pexpect.EOF)
        child.close()
        assert child.exitstatus == 0
        saved = json.loads(output.read_text())
        assert saved['metadata']['system_name'] == mode
        assert saved['full_text'].startswith('[MOCK]')
    finally:
        if child.isalive():
            child.close(force=True)


def test_menu_ctrl_c_propagates(monkeypatch):
    monkeypatch.setattr('fortune_teller.ui.keyboard_input._interactive', lambda: True)
    class Prompt:
        from prompt_toolkit.key_binding import KeyBindings
        application = type('Application', (), {'key_bindings': KeyBindings()})()
        def unsafe_ask(self):
            raise KeyboardInterrupt
    monkeypatch.setattr('fortune_teller.ui.keyboard_input.questionary.select', lambda *a, **k: Prompt())
    with pytest.raises(KeyboardInterrupt):
        pick_from_list(['男', '女'], '性别')


def test_plugin_menu_order_is_stable(tmp_path, monkeypatch):
    for name in ('zodiac', 'tarot', 'bazi'):
        folder = tmp_path / name
        folder.mkdir()
        (folder / 'manifest.yaml').write_text('')
    monkeypatch.setattr('fortune_teller.core.plugin_manager.os.listdir', lambda _: ['zodiac', 'tarot', 'bazi'])
    assert PluginManager(str(tmp_path)).discover_plugins() == ['bazi', 'tarot', 'zodiac']
