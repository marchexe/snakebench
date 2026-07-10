"""Tests for static Snakefile parsing."""

from snakebench.snakefile import parse_snakefile


SNAKEFILE_TEXT = """
rule sort_bam:
    threads: 4
    benchmark:
        "benchmarks/sort_bam.tsv"
    resources:
        mem_mb=2000,
        runtime="00:30:00"
    params:
        _psb_tool="samtools",
        _psb_primary_cmd="sort",

rule gzip_reads:
    threads: 1
    resources:
        mem_mb=128,
        runtime="00:00:05"
    params:
        _psb_tool="gzip",
"""


def test_parse_snakefile_finds_rule_names(tmp_path):
    snakefile = tmp_path / "Snakefile"
    snakefile.write_text(SNAKEFILE_TEXT, encoding="utf-8")

    rules = parse_snakefile(snakefile)

    assert [rule["rule_name"] for rule in rules] == ["sort_bam", "gzip_reads"]


def test_parse_snakefile_extracts_threads(tmp_path):
    snakefile = tmp_path / "Snakefile"
    snakefile.write_text(SNAKEFILE_TEXT, encoding="utf-8")

    rules = parse_snakefile(snakefile)

    assert rules[0]["threads"] == 4


def test_parse_snakefile_extracts_resources_mem_mb(tmp_path):
    snakefile = tmp_path / "Snakefile"
    snakefile.write_text(SNAKEFILE_TEXT, encoding="utf-8")

    rules = parse_snakefile(snakefile)

    assert rules[0]["mem_mb"] == 2000


def test_parse_snakefile_extracts_runtime(tmp_path):
    snakefile = tmp_path / "Snakefile"
    snakefile.write_text(SNAKEFILE_TEXT, encoding="utf-8")

    rules = parse_snakefile(snakefile)

    assert rules[0]["runtime"] == "00:30:00"


def test_parse_snakefile_extracts_psb_tool(tmp_path):
    snakefile = tmp_path / "Snakefile"
    snakefile.write_text(SNAKEFILE_TEXT, encoding="utf-8")

    rules = parse_snakefile(snakefile)

    assert rules[0]["psb_tool"] == "samtools"
