# Snakebench Audit Report

## Summary

- **Rules audited:** 5
- **OK:** 1
- **Missing resources:** 0
- **Underrequested resources:** 4
- **Overrequested resources:** 0
- **Unmatched rules:** 0

## Rule audit table

| rule_name | match_type | match_key | observations | declared_mem_mb | declared_runtime | suggested_mem_mb | suggested_runtime | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| align_reads | psb_tool | bwa-mem2 | 29 | 512.00 | 00:00:20 | 768 | 00:00:29 | underrequested_mem; underrequested_runtime |
| sort_bam | psb_tool | samtools | 86 | 256.00 | 00:00:01 | 512 | 00:00:02 | underrequested_mem; underrequested_runtime |
| compress_fastq | psb_tool | gzip | 61 | 256.00 | 00:00:30 | 256 | 00:00:20 | ok |
| simulate_reads | psb_tool | wgsim | 19 | 128.00 | 00:00:03 | 256 | 00:00:04 | underrequested_mem; underrequested_runtime |
| summarize_table | psb_tool | awk | 10 | 64.00 | 00:00:01 | 256 | 00:00:01 | underrequested_mem |


## Missing resources

- None.


## Underrequested resources

| rule_name | match_type | match_key | observations | declared_mem_mb | declared_runtime | suggested_mem_mb | suggested_runtime | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| align_reads | psb_tool | bwa-mem2 | 29 | 512.00 | 00:00:20 | 768 | 00:00:29 | underrequested_mem; underrequested_runtime |
| sort_bam | psb_tool | samtools | 86 | 256.00 | 00:00:01 | 512 | 00:00:02 | underrequested_mem; underrequested_runtime |
| simulate_reads | psb_tool | wgsim | 19 | 128.00 | 00:00:03 | 256 | 00:00:04 | underrequested_mem; underrequested_runtime |
| summarize_table | psb_tool | awk | 10 | 64.00 | 00:00:01 | 256 | 00:00:01 | underrequested_mem |


## Overrequested resources

- None.


## Unmatched rules

- None.


## Limitations

- Audit mode uses simple static Snakefile parsing.
- Dynamic Python/Snakemake expressions may not be parsed.
- Matching is best-effort and works best with PSB annotations such as `_psb_tool`.
- Recommendations are heuristic, not ML.
