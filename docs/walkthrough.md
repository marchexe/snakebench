# Walkthrough

# Inputs

Snakebench uses two inputs:

- The Snakefile provides declared resources and PSB-style annotations.
- `data/` provides PSB-style telemetry observations.

# Example Rule

Simplified from `examples/demo_snakemake/Snakefile`:

```python
rule sort_bam:
    resources:
        mem_mb=256,
        runtime="00:00:01"
    params:
        _psb_tool="samtools"
```

# Matching

`sort_bam` has `_psb_tool="samtools"`, so the audit matches it to telemetry rows where `tool == "samtools"`.

# Estimation

For the matched telemetry rows, Snakebench calculates:

- observed p95 memory from `max_rss_mb`
- `required_mem_mb = p95(max_rss_mb) * 1.25`
- `suggested_mem_mb`, rounded up for scheduler-friendly declarations
- observed p90 runtime from `runtime_sec`
- `required_runtime_sec = ceil(p90(runtime_sec) * 1.5)`

Memory status uses `required_mem_mb`. `suggested_mem_mb` is rounded for scheduler-friendly suggestions and is not used for the memory status comparison.

# Result

For the current demo telemetry:

- `declared_mem_mb = 256`
- `required_mem_mb ~= 504`
- declared runtime is 1 second
- required runtime is about 2 seconds

Therefore `sort_bam` is reported as:

```text
underrequested_mem; underrequested_runtime
```

# Non-Goals

- Snakebench does not run Snakemake.
- Snakebench does not collect telemetry.
- Snakebench does not read missing benchmark TSV files in the demo.
- Snakebench does not rewrite Snakefiles.
