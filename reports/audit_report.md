# Snakebench Audit Report

## Audit summary

- Rules audited: 5
- Matched rules: 5
- Unmatched rules: 0
- Missing memory declarations: 0
- Missing runtime declarations: 0
- Underrequested memory: 1
- Underrequested runtime: 3
- Overrequested memory: 0
- Overrequested runtime: 0
- OK: 2

Memory status uses `required_mem_mb = p95(max_rss_mb) Ã— 1.25`.
`suggested_mem_mb` is rounded up to the nearest 256 MB for scheduler-friendly declarations.

## Rule audit table

| rule_name | match_key | match_type | observations | declared_threads | declared_mem_mb | declared_runtime | declared_runtime_sec | observed_p95_memory_mb | required_mem_mb | suggested_mem_mb | memory_gap_mb | memory_ratio | observed_p90_runtime_sec | required_runtime_sec | suggested_runtime | runtime_gap_sec | runtime_ratio | status | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| align_reads | bwa-mem2 | psb_tool | 29 | 4 | 512.00 | 00:00:20 | 20.00 | 442.34 | 552.92 | 768 | -40.92 | 0.93 | 19.09 | 29 | 00:00:29 | -9.00 | 0.69 | underrequested_runtime | Suggested runtime is more than 10% above declared runtime. |
| sort_bam | samtools | psb_tool | 86 | 4 | 256.00 | 00:00:01 | 1.00 | 403.51 | 504.38 | 512 | -248.38 | 0.51 | 1.21 | 2 | 00:00:02 | -1.00 | 0.50 | underrequested_mem; underrequested_runtime | Declared mem_mb is more than 10% below required memory. Suggested runtime is more than 10% above declared runtime. |
| compress_fastq | gzip | psb_tool | 61 | 1 | 256.00 | 00:00:30 | 30.00 | 5.80 | 7.25 | 256 | 248.75 | 35.31 | 12.69 | 20 | 00:00:20 | 10.00 | 1.50 | ok | Declared resources are broadly aligned with telemetry suggestions. |
| simulate_reads | wgsim | psb_tool | 19 | 1 | 128.00 | 00:00:03 | 3.00 | 21.56 | 26.95 | 256 | 101.05 | 4.75 | 2.19 | 4 | 00:00:04 | -1.00 | 0.75 | underrequested_runtime | Suggested runtime is more than 10% above declared runtime. |
| summarize_table | awk | psb_tool | 10 | 1 | 64.00 | 00:00:01 | 1.00 | 7.95 | 9.94 | 256 | 54.06 | 6.44 | 0.16 | 1 | 00:00:01 | 0.00 | 1.00 | ok | Declared resources are broadly aligned with telemetry suggestions. |


## Missing resources

- None.


## Underrequested resources

| rule_name | match_key | match_type | observations | declared_threads | declared_mem_mb | declared_runtime | declared_runtime_sec | observed_p95_memory_mb | required_mem_mb | suggested_mem_mb | memory_gap_mb | memory_ratio | observed_p90_runtime_sec | required_runtime_sec | suggested_runtime | runtime_gap_sec | runtime_ratio | status | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| align_reads | bwa-mem2 | psb_tool | 29 | 4 | 512.00 | 00:00:20 | 20.00 | 442.34 | 552.92 | 768 | -40.92 | 0.93 | 19.09 | 29 | 00:00:29 | -9.00 | 0.69 | underrequested_runtime | Suggested runtime is more than 10% above declared runtime. |
| sort_bam | samtools | psb_tool | 86 | 4 | 256.00 | 00:00:01 | 1.00 | 403.51 | 504.38 | 512 | -248.38 | 0.51 | 1.21 | 2 | 00:00:02 | -1.00 | 0.50 | underrequested_mem; underrequested_runtime | Declared mem_mb is more than 10% below required memory. Suggested runtime is more than 10% above declared runtime. |
| simulate_reads | wgsim | psb_tool | 19 | 1 | 128.00 | 00:00:03 | 3.00 | 21.56 | 26.95 | 256 | 101.05 | 4.75 | 2.19 | 4 | 00:00:04 | -1.00 | 0.75 | underrequested_runtime | Suggested runtime is more than 10% above declared runtime. |


## Overrequested resources

- None.


## Unmatched rules

- None.


## Limitations

- Audit mode uses simple static Snakefile parsing.
- Dynamic Python/Snakemake expressions may not be parsed.
- Matching is best-effort and works best with PSB annotations such as `_psb_tool`.
- Recommendations are heuristic, not ML.
