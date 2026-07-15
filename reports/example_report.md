# Snakebench Advisor Report

**Generated:** 2026-07-12 17:48:37 UTC

## Summary

- **Total observations:** 205
- **Tools analyzed:** 5
- **Data collection period:** PSB Week 11, 2026
- **Method:** medians, percentiles, and fixed safety margins
- **ML model:** no

## PSB Compatibility

- **PSB-like records:** 205 (100.0%)
- **Input size recognized:** yes
- **Resources recognized:** yes
- **Environment metadata recognized:** yes

## Tool Summary

| tool | observations | median_runtime_sec | p90_runtime_sec | median_memory_mb | p95_memory_mb | min_threads | max_threads | num_tool_versions |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| samtools | 86 | 0.53 | 1.21 | 33.11 | 403.51 | 0 | 4 | 2 |
| gzip | 61 | 12.25 | 12.69 | 5.71 | 5.80 | 0 | 1 | 1 |
| bwa-mem2 | 29 | 18.64 | 19.09 | 439.77 | 442.34 | 0 | 4 | 2 |
| wgsim | 19 | 2.14 | 2.19 | 8.26 | 21.56 | 0 | 1 | 2 |
| awk | 10 | 0.15 | 0.16 | 7.90 | 7.95 | 0 | 1 | 1 |


## Resource Suggestions

Runtime suggestion uses `ceil(p90_runtime * 1.5)`. Memory requirement uses p95(max_rss_mb) × 1.25. The displayed suggested_mem_mb is rounded up to the nearest 256 MB for scheduler-friendly resource declarations.

Audit memory status is based on required_mem_mb, not the rounded suggested_mem_mb.

| tool | observations | p90_runtime_sec | suggested_runtime | p95_memory_mb | required_mem_mb | suggested_mem_mb | confidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| samtools | 86 | 1.21 | 00:00:02 | 403.51 | 504.38 | 512 | high |
| gzip | 61 | 12.69 | 00:00:20 | 5.80 | 7.25 | 256 | high |
| bwa-mem2 | 29 | 19.09 | 00:00:29 | 442.34 | 552.92 | 768 | medium |
| wgsim | 19 | 2.19 | 00:00:04 | 21.56 | 26.95 | 256 | medium |
| awk | 10 | 0.16 | 00:00:01 | 7.95 | 9.94 | 256 | medium |


## Input-Size Stratified Suggestions

| tool | input_size_bin | observations | p90_runtime_sec | suggested_runtime | p95_memory_mb | required_mem_mb | suggested_mem_mb | confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| awk | zero | 10 | 0.16 | 00:00:01 | 7.95 | 9.94 | 256 | medium |
| bwa-mem2 | small | 12 | 19.57 | 00:00:30 | 442.71 | 553.38 | 768 | medium |
| bwa-mem2 | zero | 17 | 18.94 | 00:00:29 | 441.72 | 552.16 | 768 | medium |
| gzip | medium | 16 | 12.86 | 00:00:20 | 5.80 | 7.25 | 256 | medium |
| gzip | zero | 45 | 12.44 | 00:00:19 | 5.78 | 7.23 | 256 | medium |
| samtools | small | 36 | 1.22 | 00:00:02 | 403.54 | 504.42 | 512 | medium |
| samtools | zero | 50 | 1.20 | 00:00:02 | 403.50 | 504.38 | 512 | high |
| wgsim | small | 8 | 2.18 | 00:00:04 | 21.68 | 27.10 | 256 | low |
| wgsim | zero | 11 | 2.19 | 00:00:04 | 21.26 | 26.58 | 256 | medium |


## Limitations

- Suggestions are percentile heuristics.
- Results depend on the observed workflow, input distribution, and environment.
- Current dataset size: 205 observations.
- No telemetry collection is performed by Snakebench.

## Next Steps

- Keep field names and units aligned with PSB.
- Improve plugin metadata for `rule_name`, `resources`, inputs/outputs, tool versions, and categories.
- Validate suggestions on held-out workflow runs before evaluating prediction.

---

**Version:** Snakebench Advisor v0.6.0
**Status:** Prototype
