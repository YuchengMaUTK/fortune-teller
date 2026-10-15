"""Shared terminal theme, responsive charts, and scrollback-friendly streaming."""
import logging
import sys
import time
from typing import Any, Dict, Iterable

from rich import box
from rich.console import Console, Group
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

THEME = Theme({
    "accent": "#7dcfff", "title": "bold #c4a7e7", "border": "#3d5968",
    "muted": "#9aa5b1", "success": "#9ece6a", "warning": "#e0af68", "error": "bold #f7768e",
    "markdown.h1": "bold #7dcfff", "markdown.h2": "bold #7dcfff",
})
ELEMENT_STYLES = {"木": "#9ece6a", "火": "#f7768e", "土": "#e0af68", "金": "#cdd6f4",
                  "水": "#7aa2f7", "风": "#7dcfff"}
_console = None


def get_console() -> Console:
    global _console
    if _console is None or _console.file is not sys.stdout:
        _console = Console(theme=THEME, markup=False, highlight=False)
    return _console


def heading(title: str) -> None:
    get_console().rule(Text.from_ansi(title), style="accent", align="left")


def message(text: str, style: str = "muted") -> None:
    get_console().print(Text(text, style=style))


def markdown(text: str) -> None:
    get_console().print(Markdown(text))


def details(items):
    table = Table.grid(padding=(0, 2))
    table.add_column(style="muted", no_wrap=True)
    table.add_column(overflow="fold")
    for label, value in items:
        table.add_row(Text(label), Text(str(value if value not in (None, "") else "未知")))
    return table


def welcome() -> None:
    get_console().print(Panel(
        Group(Text("霄占", style="title"), Text("FORTUNE TELLER", style="muted"),
              Text("八字 · 塔罗 · 星座", style="accent"), Text("古法遇新技，探索生活的可能性。")),
        border_style="border", padding=(1, 2), width=min(get_console().width, 100),
    ))


def bazi_chart(data: Dict[str, Any]):
    console = get_console()
    labels = [("year", "年柱"), ("month", "月柱"), ("day", "日柱"), ("hour", "时柱")]
    table = Table(box=box.ROUNDED, border_style="border", expand=True)
    if console.width >= 56:
        table.add_column("四柱", style="muted")
        for _, label in labels:
            table.add_column(label, justify="center")
        for field, label in [("stem", "天干"), ("branch", "地支")]:
            row = [Text(label)]
            for key, _ in labels:
                pillar = data.get(key + "_pillar") or {}
                element = pillar.get(field + "_element", "")
                value = pillar.get(field, "未知")
                row.append(Text(f"{value}\n{element}" if element else value,
                                style=ELEMENT_STYLES.get(element, "muted")))
            table.add_row(*row)
        table.add_row("命柱", *[Text(data.get("four_pillars", {}).get(key, "未知")) for key, _ in labels])
    else:
        table.add_column("四柱", style="muted")
        table.add_column("命柱", justify="center")
        table.add_column("五行")
        for key, label in labels:
            pillar = data.get(key + "_pillar") or {}
            table.add_row(label, Text(data.get("four_pillars", {}).get(key, "未知")),
                          Text(" / ".join(pillar.get(f + "_element", "未知") for f in ("stem", "branch"))))
    elements = data.get("elements", {})
    counts = elements.get("counts", {})
    bars = Table.grid(padding=(0, 1))
    bars.add_column(no_wrap=True)
    bars.add_column()
    bars.add_column()
    for element in ("木", "火", "土", "金", "水"):
        count = counts.get(element, 0)
        bars.add_row(Text(element, style=ELEMENT_STYLES[element]),
                     Text("━" * count, style=ELEMENT_STYLES[element]), Text(str(count)))
    master = data.get("day_master", {})
    notes = Text("北京时间（UTC+08:00） · 节气换月 · 立春换年 · 午夜换日\n不校正真太阳时", style="muted")
    if data.get("calculation", {}).get("assumed_noon"):
        notes.append("\n出生时间未知：前三柱暂按中午计算，节气当日可能有歧义。", style="warning")
    return Panel(Group(
        details([( "出生日期", data.get("birth_date")), ("出生时间", data.get("birth_time")),
                 ("性别", data.get("gender")), ("出生地点", data.get("location"))]),
        Text(""), table, Text(""), Text("五行分布", style="accent"), bars,
        details([( "日主", f"{master.get('character', '未知')}（{master.get('element', '未知')}）"),
                 ("最强五行", elements.get("strongest")), ("最弱五行", elements.get("weakest"))]),
        Text(""), notes,
    ), title=Text("八字命盘", style="title"), border_style="border", padding=(1, 1),
        width=min(console.width, 100))


def tarot_chart(data: Dict[str, Any]):
    cards = []
    for index, card in enumerate(data.get("reading", []), 1):
        orientation = card.get("orientation", "正位")
        body = Group(Text(card.get("card", "未知"), style="bold"),
                     Text(orientation, style="success" if orientation == "正位" else "warning"),
                     Text(" · ".join(card.get("keywords", [])), style="muted"))
        cards.append(Panel(body, title=Text(f"{index} · {card.get('position', '未知')}", style="accent"),
                           border_style="border", padding=(0, 1)))
    # Stack card panels so large spreads and narrow terminals remain readable.
    spread = data.get("spread", {})
    return Panel(Group(
        details([( "问题", data.get("question")), ("领域", data.get("focus_area")),
                 ("咨询者", data.get("name") or "匿名"), ("牌阵", spread.get("name"))]),
        Text(""), *cards,
    ), title=Text("塔罗牌阵", style="title"), border_style="border", padding=(1, 1),
        width=min(get_console().width, 100))


def zodiac_chart(data: Dict[str, Any]):
    sign = data.get("zodiac_sign", {})
    return Panel(Group(
        Text(f"{sign.get('name', '未知')} · {sign.get('english', 'Unknown')}", style="title"),
        Text(""), details([
            ("出生日期", data.get("birth_date")), ("出生时间", data.get("birth_time")),
            ("出生地点", data.get("birth_place")), ("关注领域", data.get("question_area")),
            ("日期范围", sign.get("date_range")), ("元素", sign.get("element")),
            ("品质", sign.get("quality")), ("主宰星", sign.get("ruler")),
            ("月亮星座（估算）", data.get("moon_sign")), ("上升星座（估算）", data.get("rising_sign")),
        ]), Text(""), Text("元素关键词", style="accent"),
        Text(" · ".join(data.get("element_info", {}).get("keywords", []))),
        Text(""), Text("月亮、上升和行运采用简化估算。", style="muted"),
    ), title=Text("星座概览", style="title"), border_style="border", padding=(1, 1),
        width=min(get_console().width, 100))


def display_chart(mode: str, data: Dict[str, Any]) -> None:
    builders = {"bazi": bazi_chart, "tarot": tarot_chart, "zodiac": zodiac_chart}
    get_console().print(builders[mode](data))


def _completed_block(buffer: str):
    """Commit whole paragraphs, retaining blank lines inside fenced code."""
    fence = None
    offset = 0
    for line in buffer.splitlines(keepends=True):
        stripped = line.lstrip()
        if stripped.startswith(("```", "~~~")):
            marker = stripped[:3]
            fence = None if fence == marker else marker if fence is None else fence
        offset += len(line)
        if line.strip() == "" and line.endswith("\n") and fence is None:
            return buffer[:offset], buffer[offset:]
    return None, buffer


def stream_markdown(chunks: Iterable[str], title: str, pending_animation=None,
                    start_time=None) -> str:
    """TTY: live paragraph preview, committed Markdown in scrollback.

    Pipes: exact incremental text, with no ANSI cursor controls or redraws.
    Rendering is throttled without delaying incoming model tokens.
    """
    console = get_console()
    logger = logging.getLogger("StreamingChunks")
    logger.info("=== START OF STREAMING SESSION ===")
    complete, pending = "", ""
    live = None
    count = 0
    refreshed = 0.0
    try:
        for chunk in chunks:
            if not chunk:
                continue
            complete += chunk
            pending += chunk
            if not chunk.strip() and count == 0:
                continue
            if count == 0:
                if pending_animation:
                    pending_animation.stop()
                if start_time:
                    logger.info("首个块延迟: %.3f秒", time.time() - start_time)
                heading(title)
                if console.is_terminal:
                    live = Live(Text(""), console=console, auto_refresh=False,
                                transient=True, vertical_overflow="crop")
                    live.start(refresh=True)
                else:
                    console.file.write(complete)
                    console.file.flush()
            elif not console.is_terminal:
                console.file.write(chunk)
                console.file.flush()
            count += 1
            # Metadata only: model text and personal data stay out of logs.
            logger.info("Chunk #%d received | Length: %d", count, len(chunk))
            if live:
                block, rest = _completed_block(pending)
                while block is not None:
                    live.update(Text(""), refresh=True)
                    console.print(Markdown(block))
                    pending = rest
                    block, rest = _completed_block(pending)
                now = time.monotonic()
                if now - refreshed >= 0.1:
                    # Bound unfinished paragraphs to the visible viewport.
                    limit = max(80, console.width * max(2, min(8, console.height - 4)))
                    live.update(Text(pending[-limit:]), refresh=True)
                    refreshed = now
    finally:
        if live:
            live.stop()
            if pending:
                console.print(Markdown(pending))
        elif count:
            console.file.write("\n")
            console.file.flush()
        if pending_animation:
            pending_animation.stop()
    return complete
