# Snakebench Audit Report

## Summary

- **Rules audited:** 5
- **OK:** 2
- **Missing resources:** 0
- **Underrequested resources:** 3
- **Overrequested resources:** 0
- **Unmatched rules:** 0

## Rule audit table

| rule_name | match_key | match_type | observations | declared_threads | declared_mem_mb | declared_runtime | observed_p95_memory_mb | required_mem_mb | observed_p90_runtime_sec | suggested_mem_mb | suggested_runtime | status | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| align_reads | bwa-mem2 | psb_tool | 29 | 4 | 512.00 | 00:00:20 | 442.34 | 552.92 | 19.09 | 768 | 00:00:29 | underrequested_runtime | Suggested runtime is more than 10% above declared runtime. |
| sort_bam | samtools | psb_tool | 86 | 4 | 256.00 | 00:00:01 | 403.51 | 504.38 | 1.21 | 512 | 00:00:02 | underrequested_mem; underrequested_runtime | Declared mem_mb is more than 10% below required memory. Suggested runtime is more than 10% above declared runtime. |
| compress_fastq | gzip | psb_tool | 61 | 1 | 256.00 | 00:00:30 | 5.80 | 7.25 | 12.69 | 256 | 00:00:20 | ok | Declared resources are broadly aligned with telemetry suggestions. |
| simulate_reads | wgsim | psb_tool | 19 | 1 | 128.00 | 00:00:03 | 21.56 | 26.95 | 2.19 | 256 | 00:00:04 | underrequested_runtime | Suggested runtime is more than 10% above declared runtime. |
| summarize_table | awk | psb_tool | 10 | 1 | 64.00 | 00:00:01 | 7.95 | 9.94 | 0.16 | 256 | 00:00:01 | ok | Declared resources are broadly aligned with telemetry suggestions. |


## Missing resources

- None.


## Underrequested resources

| rule_name | match_key | match_type | observations | declared_threads | declared_mem_mb | declared_runtime | observed_p95_memory_mb | required_mem_mb | observed_p90_runtime_sec | suggested_mem_mb | suggested_runtime | status | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| align_reads | bwa-mem2 | psb_tool | 29 | 4 | 512.00 | 00:00:20 | 442.34 | 552.92 | 19.09 | 768 | 00:00:29 | underrequested_runtime | Suggested runtime is more than 10% above declared runtime. |
| sort_bam | samtools | psb_tool | 86 | 4 | 256.00 | 00:00:01 | 403.51 | 504.38 | 1.21 | 512 | 00:00:02 | underrequested_mem; underrequested_runtime | Declared mem_mb is more than 10% below required memory. Suggested runtime is more than 10% above declared runtime. |
| simulate_reads | wgsim | psb_tool | 19 | 1 | 128.00 | 00:00:03 | 21.56 | 26.95 | 2.19 | 256 | 00:00:04 | underrequested_runtime | Suggested runtime is more than 10% above declared runtime. |


## Overrequested resources

- None.


## Unmatched rules

- None.


## Limitations

- Audit mode uses simple static Snakefile parsing.
- Dynamic Python/Snakemake expressions may not be parsed.
- Matching is best-effort and works best with PSB annotations such as `_psb_tool`.
- Recommendations are heuristic, not ML.
