"""Static Snakefile resource declaration parsing."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass
class RuleResource:
    rule_name: str
    threads: int | None = None
    mem_mb: float | None = None
    runtime: str | None = None
    psb_tool: str | None = None
    psb_primary_cmd: str | None = None
    benchmark: str | None = None


def _strip_comment(line: str) -> str:
    in_single = False
    in_double = False
    for idx, char in enumerate(line):
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif char == "#" and not in_single and not in_double:
            return line[:idx]
    return line


def _clean_value(value: str) -> str:
    cleaned = _strip_comment(value).strip().rstrip(",")
    if (
        len(cleaned) >= 2
        and cleaned[0] == cleaned[-1]
        and cleaned[0] in {"'", '"'}
    ):
        return cleaned[1:-1]
    return cleaned


def _parse_number(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(str(value).strip().strip("'\""))
    except (TypeError, ValueError):
        return None


def _parse_int(value: Any) -> int | None:
    number = _parse_number(value)
    if number is None:
        return None
    return int(number)


def _parse_runtime_seconds(value: Any) -> float | None:
    if value is None or pd.isna(value):
        return None

    text = str(value).strip().strip("'\"")
    if not text:
        return None

    if re.fullmatch(r"\d+(\.\d+)?", text):
        return float(text)

    if re.fullmatch(r"\d{1,3}:\d{2}:\d{2}", text):
        hours, minutes, seconds = [int(part) for part in text.split(":")]
        return float(hours * 3600 + minutes * 60 + seconds)

    if re.fullmatch(r"\d{1,3}:\d{2}", text):
        minutes, seconds = [int(part) for part in text.split(":")]
        return float(minutes * 60 + seconds)

    match = re.fullmatch(r"(\d+(\.\d+)?)(s|m|h)", text.lower())
    if match:
        value_float = float(match.group(1))
        unit = match.group(3)
        if unit == "s":
            return value_float
        if unit == "m":
            return value_float * 60
        if unit == "h":
            return value_float * 3600

    return None


def _split_assignments(text: str) -> list[tuple[str, str]]:
    assignments = []
    pattern = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+?)(?=,\s*[A-Za-z_][A-Za-z0-9_]*\s*=|$)")
    for match in pattern.finditer(text.strip().rstrip(",")):
        assignments.append((match.group(1), _clean_value(match.group(2))))
    return assignments


def _parse_assignment(line: str) -> tuple[str, str] | None:
    stripped = line.strip()
    if "=" not in stripped:
        return None
    key, value = stripped.split("=", 1)
    key = key.strip()
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
        return None
    return key, _clean_value(value)


def _is_section_header(stripped: str) -> bool:
    return bool(re.match(r"^(threads|benchmark|resources|params|input|output|shell|run|script|log)\s*:", stripped))


def _apply_resource(rule: RuleResource, key: str, value: str) -> None:
    if key == "mem_mb":
        rule.mem_mb = _parse_number(value)
    elif key in {"runtime", "time"}:
        rule.runtime = _clean_value(value)


def _apply_param(rule: RuleResource, key: str, value: str) -> None:
    if key == "_psb_tool":
        rule.psb_tool = _clean_value(value)
    elif key == "_psb_primary_cmd":
        rule.psb_primary_cmd = _clean_value(value)


def parse_snakefile(path: str | Path) -> list[dict]:
    """Parse common static Snakefile rule resource declarations."""
    path = Path(path)
    rules: list[RuleResource] = []
    current: RuleResource | None = None
    section: str | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = _strip_comment(raw_line)
        stripped = line.strip()
        if not stripped:
            continue

        rule_match = re.match(r"^rule\s+([A-Za-z_][A-Za-z0-9_]*)\s*:", stripped)
        if rule_match:
            current = RuleResource(rule_name=rule_match.group(1))
            rules.append(current)
            section = None
            continue

        if current is None:
            continue

        section_match = re.match(r"^(threads|benchmark|resources|params)\s*:\s*(.*)$", stripped)
        if section_match:
            section = section_match.group(1)
            rest = section_match.group(2).strip()

            if section == "threads" and rest:
                current.threads = _parse_int(rest)
            elif section == "benchmark" and rest:
                current.benchmark = _clean_value(rest)
            elif section == "resources" and rest:
                for key, value in _split_assignments(rest):
                    _apply_resource(current, key, value)
            elif section == "params" and rest:
                for key, value in _split_assignments(rest):
                    _apply_param(current, key, value)
            continue

        if _is_section_header(stripped):
            section = None
            continue

        if section == "threads":
            current.threads = _parse_int(stripped)
        elif section == "benchmark":
            current.benchmark = _clean_value(stripped)
        elif section == "resources":
            assignment = _parse_assignment(stripped)
            if assignment:
                _apply_resource(current, assignment[0], assignment[1])
        elif section == "params":
            assignment = _parse_assignment(stripped)
            if assignment:
                _apply_param(current, assignment[0], assignment[1])

    return [asdict(rule) for rule in rules]
