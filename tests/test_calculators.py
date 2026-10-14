import datetime

import pytest

from fortune_teller.calculators.bazi_converter import calculate_bazi
from fortune_teller.calculators.tarot_picker import TAROT_CARDS, draw_cards
from fortune_teller.plugins.bazi.fortune_system import BaziFortuneSystem
from fortune_teller.tools.mcp_tools import MCPBaZiTool


def test_reference_jiazi_day():
    assert calculate_bazi(2000, 1, 7)["four_pillars"]["day"] == "甲子"


def test_before_lichun_uses_previous_year_and_chou_month():
    assert calculate_bazi(2026, 1, 15)["four_pillars"] == {
        "year": "乙巳", "month": "己丑", "day": "己丑", "hour": "庚午"
    }


@pytest.mark.parametrize("before,after,expected", [
    ((2026, 2, 4, 4, 2, 7), (2026, 2, 4, 4, 2, 8),
     (("乙巳", "己丑"), ("丙午", "庚寅"))),
    ((2026, 3, 5, 21, 58, 59), (2026, 3, 5, 21, 59, 0),
     (("丙午", "庚寅"), ("丙午", "辛卯"))),
])
def test_solar_term_boundaries(before, after, expected):
    for birth, pillars in zip((before, after), expected):
        chart = calculate_bazi(*birth)["four_pillars"]
        assert (chart["year"], chart["month"]) == pillars


def test_late_zi_hour_and_midnight():
    evening = calculate_bazi(2000, 1, 7, 22, 59)["four_pillars"]
    late = calculate_bazi(2000, 1, 7, 23)["four_pillars"]
    next_day = calculate_bazi(2000, 1, 8, 0)["four_pillars"]
    assert evening["day"] == late["day"] == "甲子"
    assert evening["hour"].endswith("亥")
    assert late["hour"].endswith("子")
    assert next_day["day"] == "乙丑"
    assert next_day["hour"].endswith("子")


@pytest.mark.parametrize("args", [(2026, 2, 29), (2026, 1, 1, -1),
                                  (2026, 1, 1, 24), (2026, 1, 1, 12, 60)])
def test_invalid_birth_datetime(args):
    assert calculate_bazi(*args)["success"] is False


def test_leap_day():
    assert calculate_bazi(2024, 2, 29)["success"] is True


def test_plugin_uses_same_calculator_and_keeps_minutes():
    plugin = BaziFortuneSystem()
    for minute in (1, 3):
        result = plugin.process_data({
            "birth_date": datetime.date(2026, 2, 4),
            "birth_time": datetime.time(4, minute), "gender": "男", "location": None,
        })
        assert result["four_pillars"] == calculate_bazi(2026, 2, 4, 4, minute)["four_pillars"]


def test_unknown_time_stays_unknown():
    result = BaziFortuneSystem().process_data({
        "birth_date": datetime.date(2000, 1, 7), "birth_time": None,
        "gender": "女", "location": None,
    })
    assert result["four_pillars"]["hour"] == "未知"
    assert result["hour_pillar"] is None
    assert result["calculation"]["assumed_noon"] is True
    assert sum(result["elements"]["counts"].values()) == 6


async def test_packaged_bazi_dispatch_preserves_minutes():
    result = await MCPBaZiTool().convert_to_bazi(2026, 2, 4, 4, 3)
    assert result["four_pillars"]["year"] == "丙午"


def test_tarot_draws_are_independent():
    first = draw_cards(78, False)
    original = [card.copy() for card in first]
    second = draw_cards(78, False)
    for card in second:
        card["reversed"] = True
    assert first == original
    assert all("reversed" not in card for card in TAROT_CARDS)
    assert len({card["id"] for card in first}) == 78


@pytest.mark.parametrize("count", [0, 79])
def test_tarot_rejects_invalid_count(count):
    with pytest.raises(ValueError):
        draw_cards(count)


def test_legacy_cli_entry_point():
    import json
    import subprocess
    import sys
    from pathlib import Path
    script = Path(__file__).resolve().parents[1] / "mcp/tools/bazi_converter.py"
    result = subprocess.run(
        [sys.executable, str(script), "convert", "2000", "1", "7", "12"],
        capture_output=True, text=True, check=True,
    )
    assert json.loads(result.stdout)["four_pillars"]["day"] == "甲子"
