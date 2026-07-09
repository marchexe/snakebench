# PSB Upstream Mapping for Snakebench

This document maps Snakebench Advisor against PSB as the upstream source of
truth. It is based on:

- `../psb-upstream/docs/spec.md`
- `../psb-upstream/docs/roadmap.md`
- `../psb-upstream/internal/models/models.go`
- `../psb-upstream/internal/handlers/telemetry.go`
- `../psb-upstream/internal/handlers/views.go`
- `../psb-snakemake-plugin/README.md`
- `../psb-snakemake-plugin/src/snakemake_logger_plugin_benchmark_telemetry/*.py`
- the current Snakebench parquet files in `data/`

No code behavior is specified as already implemented unless this document says so
explicitly.

## 1. PSB Core Concepts

### Session

A PSB session is one workflow invocation. It is identified by `session_id`, a
client-generated UUIDv4 created when the workflow starts. Session metadata is
small and workflow-level:

- `session_id`
- `workflow_url`
- `workflow_version`

In the wire format, session fields are repeated on every JSONL observation line.
On the server, they are stored once per `session_id`. In parquet exports, they
are flattened back onto every row.

### Observation

An observation is one rule execution within a session. It is the main unit
Snakebench should analyze. PSB identifies an observation with `record_id`.
According to the spec, `record_id` is a deterministic truncated SHA256 hash of:

```text
session_start_iso + ":" + rule_name + ":" + sorted wildcards
```

The observation carries tool identity, command context, input/output metadata,
observed runtime, observed memory, allocated resources, extended process metrics,
exit status, and distress/system-state metrics.

### Environment

An environment is a fingerprint of the execution platform. It is not necessarily
one-to-one with a session: distributed workflow execution can produce multiple
environments within one session. The server deduplicates environments by a
deterministic hash derived from host hash, CPU model/features/cores/cache/freq,
OS/kernel, Snakemake version, and deployment mode.

Snakebench should treat environment fields as analysis dimensions, not just
decorative metadata. Resource behavior from different environments may not be
directly comparable.

### Tool

`tool` is the primary scientific tool invoked by a rule, for example `samtools`,
`bwa`, `STAR`, or `gzip`. PSB resolution order is:

1. Explicit rule annotation, such as `_psb_tool`.
2. Auto-detection from shell template.
3. Drop the observation if the resolved tool is generic or missing.

Generic interpreters include `python`, `python3`, `bash`, `sh`, `Rscript`,
`perl`, `java`, and `ruby`. For script-based or multi-command rules, PSB expects
annotations because auto-detection is fragile.

### Inputs and Outputs

PSB represents inputs and outputs as arrays of file entries. Each file entry is:

```json
{"type": ".fastq.gz", "size": 123456789}
```

The server stores `inputs` and `outputs` as JSON-encoded strings and exports both
the raw JSON fields and derived scalar fields:

- `input_size`: total input bytes
- `num_inputs`
- `input_type`
- `output_size`: total output bytes
- `num_outputs`

Important for Snakebench: canonical PSB parquet export uses `input_size` in
bytes, not `input_size_mb`.

### Resources

PSB has two related concepts:

- Observed resource usage: `runtime_sec`, `max_rss_mb`, `cpu_percent`, extended
  memory/IO fields.
- Allocated or declared resources: `threads` and `resources`.

`resources` is a JSON-encoded dict from Snakemake resource allocations, such as:

```json
{"_cores": 4, "mem_mb": 8000}
```

The upstream server sanitizes path-like values in `resources`, for example
`tmpdir`, before storing them.

### Annotations

PSB annotations are intended to live in the Snakemake rule `params:` namespace
using `_psb_*` keys:

- `_psb_tool` -> `tool`
- `_psb_tool_version` -> `tool_version`
- `_psb_primary_cmd` -> `command`
- `_psb_params` -> `params`
- `_psb_category` -> `category`

Workflow-level defaults can also come from a `psb:` config section:

- `psb.workflow_url`
- `psb.workflow_version`
- `psb.category`

The spec states this precedence:

```text
rule-level _psb_* param > workflow config psb.* > auto-detection
```

## 2. Exact PSB Fields Snakebench Should Support

Snakebench should support the upstream parquet/export schema directly, then
normalize to internal analysis columns. The following field groups come from the
PSB spec and server `ParquetRow`.

### Required Observation Fields

These are required by PSB ingestion validation or required for Snakebench's core
analysis.

| Field | Type | Meaning | Snakebench use |
|---|---:|---|---|
| `session_id` | string | Workflow invocation ID | group/filter sessions |
| `record_id` | string | Observation ID | dedupe, trace records |
| `tool` | string | Primary tool | primary grouping key |
| `runtime_sec` | float | Wall-clock runtime | runtime summaries/advice |
| `max_rss_mb` | float | Peak resident set size | memory summaries/advice |
| `cpu_percent` | float | CPU usage/load measure | future CPU/resource audit |

The server also validates `runtime_sec > 0`, non-empty `session_id`,
non-empty `record_id`, and non-empty `tool`.

### Optional Tool and Command Fields

| Field | Type | Meaning | Snakebench use |
|---|---:|---|---|
| `command` | string | Command or subcommand | command-level summaries |
| `params` | string | Sanitized parameters | feature grouping later |
| `shell_block` | string | Unresolved shell template | audit/debug context |
| `tool_version` | string | Tool version | version-specific summaries |
| `category` | string | Workflow step category | cross-tool/category comparison |

### Environment Fields

| Field | Type | Meaning |
|---|---:|---|
| `host_hash` | string | Hashed hostname |
| `cpu_model` | string | CPU model name |
| `cpu_features` | string or uint64 | Curated CPU feature bitmask or decoded export string |
| `cpu_cores` | int | Physical/logical core count as collected |
| `l2_cache_kb` | int | L2 cache size |
| `l3_cache_kb` | int | L3 cache size |
| `cpu_freq_mhz` | int | Max CPU frequency |
| `os` | string | Platform |
| `kernel_version` | string | Numeric kernel/release |
| `kernel_string` | string | Full platform string |
| `sm_version` | string | Snakemake version |
| `deploy_mode` | string | host/conda/apptainer/env_modules combination |

Snakebench should not assume one environment per session.

### Resource Fields

| Field | Type | Meaning | Snakebench use |
|---|---:|---|---|
| `threads` | int | Threads allocated by Snakemake | stratification/audit |
| `resources` | string | JSON-encoded declared resources | v0.3 audit input |
| `exit_code` | int | Process exit code | filter failed jobs; failure analysis |

`resources` is the field that should eventually yield declared `mem_mb`,
runtime/time, disk, tmpdir, and other Snakemake resource values. Snakebench
should not require separate `declared_mem_mb` columns in PSB data if `resources`
is available and parseable.

### Input and Output Fields

| Field | Type | Meaning | Unit |
|---|---:|---|---|
| `inputs` | string | JSON-encoded input file entries | raw JSON |
| `outputs` | string | JSON-encoded output file entries | raw JSON |
| `input_size` | int64 | Total input size | bytes |
| `num_inputs` | int | Number of input files | count |
| `input_type` | string | Input extensions/types | string |
| `output_size` | int64 | Total output size | bytes |
| `num_outputs` | int | Number of output files | count |

Snakebench should normalize `input_size` to `input_size_mb` internally while
retaining the original byte value.

### Extended Memory, IO, and Distress Fields

| Field | Type | Meaning |
|---|---:|---|
| `max_vms_mb` | float | Peak virtual memory |
| `max_uss_mb` | float | Peak unique set size |
| `max_pss_mb` | float | Peak proportional set size |
| `io_in_mb` | float | Cumulative read IO |
| `io_out_mb` | float | Cumulative write IO |
| `cpu_time_sec` | float | CPU time |
| `load_avg` | float | Load average at job start |
| `mem_avail_mb` | int | Available memory at job start |
| `swap_used_mb` | int | Swap used at job start |
| `io_wait_pct` | float | IO wait percentage |
| `timestamp` | string | Server-side observation timestamp/export timestamp |

Snakebench should initially preserve these fields and use them in readiness
checks. Later versions can use them to exclude distressed runs or explain noisy
measurements.

### Session Fields

| Field | Type | Meaning |
|---|---:|---|
| `workflow_url` | string | Workflow repository/release URL |
| `workflow_version` | string | Version tag, branch/hash, or release identifier |

## 3. What the Snakemake Plugin Actually Emits

The current plugin implementation emits less than the PSB spec and server
support.

From `client.py`, each submitted JSONL line contains:

- `session_id`
- optional `workflow_url`
- optional `workflow_version`
- environment fields from `collect_environment()`
- fields passed to `add_record()`

From `environment.py`, the plugin currently collects:

- `host_hash`
- `cpu_model`
- `cpu_features`
- `cpu_cores`
- `os`
- `kernel_version`
- `sm_version`

It does not currently emit:

- `l2_cache_kb`
- `l3_cache_kb`
- `cpu_freq_mhz`
- `kernel_string`
- `deploy_mode`

There is also a significant compatibility issue: the plugin's `cpu_features`
bit positions do not match the PSB spec/Go server registry. For example, the
plugin maps `sse4_2` to bit 0, but the PSB registry maps bit 0 to `sse2` and
`sse4_2` to bit 4. Snakebench should treat plugin-emitted numeric CPU feature
bitmasks with caution unless the plugin is fixed upstream.

From `__init__.py`, on each finished job the plugin currently emits:

- `record_id`
- `tool`
- `params`
- `runtime_sec`
- `max_rss_mb`
- `cpu_percent`
- `threads`

It reads benchmark values from Snakemake benchmark TSV or JSONL:

- `s` -> `runtime_sec`
- `max_rss` -> `max_rss_mb`
- `mean_load * 100` -> `cpu_percent`

It does not currently emit:

- `command`
- `shell_block`
- `inputs`
- `outputs`
- `input_size`
- `output_size`
- `resources`
- `exit_code`
- `tool_version`
- `category`
- extended memory fields
- IO fields
- distress/system-state fields

The plugin README says it uses a `benchmark_telemetry` param in extended
benchmark data. The spec, however, describes `_psb_*` params. The implementation
currently checks `bench["params"]["benchmark_telemetry"]` and supports:

- `tool`
- `primary_cmd`

There is another behavior mismatch: when `primary_cmd` is found, the
implementation assigns it to `params`, not to `command`.

The plugin only works for rules with a Snakemake `benchmark:` directive.

## 4. Which PSB Fields Already Exist in Current Snakebench Data

The current `data/*.parquet` files contain 205 rows and 47 columns. The columns
match the PSB server parquet export shape closely:

- `session_id`
- `record_id`
- `tool`
- `tool_version`
- `category`
- `command`
- `params`
- `shell_block`
- `inputs`
- `outputs`
- `input_size`
- `num_inputs`
- `input_type`
- `output_size`
- `num_outputs`
- `runtime_sec`
- `threads`
- `max_rss_mb`
- `max_vms_mb`
- `max_uss_mb`
- `max_pss_mb`
- `cpu_percent`
- `cpu_time_sec`
- `io_in_mb`
- `io_out_mb`
- `resources`
- `exit_code`
- `load_avg`
- `mem_avail_mb`
- `swap_used_mb`
- `io_wait_pct`
- `timestamp`
- `host_hash`
- `cpu_model`
- `cpu_features`
- `cpu_cores`
- `l2_cache_kb`
- `l3_cache_kb`
- `cpu_freq_mhz`
- `os`
- `kernel_version`
- `kernel_string`
- `sm_version`
- `deploy_mode`
- `workflow_url`
- `workflow_version`

The current data therefore has many more PSB fields than Snakebench currently
uses. In the current files, all rows have non-null values for these columns, but
some string fields may be empty strings and some numeric fields may be zero. In
particular, `resources`, `inputs`, and `outputs` can appear present as columns
without carrying useful declared-resource or file-entry content for every row.

The current `input_size` column is populated as bytes. Its observed range in the
current data is 0 to 171,821,136 bytes.

## 5. PSB Fields Snakebench Currently Ignores or Handles Incorrectly

### `input_size` is ignored incorrectly

Snakebench's `features.py` detects:

- `input_size_mb`
- `inputs_size_mb`
- `total_input_size_mb`
- `input_bytes`
- `inputs_bytes`
- `total_input_bytes`

It does not detect canonical PSB parquet `input_size`. As a result, current
input-size stratification falls into `input_size_bin = unknown` even though the
data contains `input_size`.

Correct behavior: treat `input_size` as bytes and derive `input_size_mb`.

### Readiness says input-size metadata is missing

`readiness.py` uses the same incomplete input-size column list. It reports
missing input-size metadata for the current PSB parquet data even though
`input_size`, `num_inputs`, and `input_type` exist.

Correct behavior: include `input_size` as PSB byte input size.

### `resources` is not used for declared-resource readiness

Readiness currently looks for columns such as:

- `declared_mem_mb`
- `resources_mem_mb`
- `declared_runtime`
- `resources_runtime`

It does not treat PSB's canonical `resources` JSON string as the upstream source
for declared Snakemake resource allocations.

Correct behavior: detect `resources`; then parse `mem_mb`, runtime/time, and
related keys when the field is non-empty and valid JSON.

### Environment metadata is only partially recognized

Readiness checks a few environment-like names, including `environment_id`,
`env_id`, `hostname_hash`, `cpu_model`, `os`, `kernel`, `platform`,
`snakemake_version`, and `deploy_mode`.

PSB uses:

- `host_hash`, not `hostname_hash`
- `kernel_version` and `kernel_string`, not plain `kernel`
- `sm_version`, not `snakemake_version`

The current data still passes environment checks because `cpu_model`, `os`, and
`deploy_mode` are present, but Snakebench should explicitly support PSB names.

### `cpu_features` semantics are not normalized

PSB ingestion expects a numeric bitmask. PSB parquet export decodes it to a
comma-separated string. The current Snakebench code does not distinguish these
representations.

For v0.2.1, preservation is enough. For later environment-aware analysis,
Snakebench should normalize to both:

- `cpu_features_raw`
- `cpu_features_list`

### Failed or distressed observations are not filtered

Snakebench summarizes all rows without considering:

- `exit_code`
- `swap_used_mb`
- `io_wait_pct`
- `load_avg`
- `mem_avail_mb`

Correct behavior for advice should probably default to successful observations
only (`exit_code == 0`) and report distress metadata separately.

### Extended metrics are ignored

Snakebench currently ignores:

- `max_vms_mb`
- `max_uss_mb`
- `max_pss_mb`
- `io_in_mb`
- `io_out_mb`
- `cpu_time_sec`
- `cpu_percent`

This is acceptable for v0.2, but these fields should be preserved and named in
readiness reports because they matter for future audit and prediction.

### Command/category/version fields are underused

Snakebench counts `tool_version` diversity, but does not group or filter by:

- `command`
- `params`
- `category`
- `tool_version`
- `workflow_url`
- `workflow_version`
- `sm_version`
- `deploy_mode`

This is acceptable for tool-level v0.2, but these are the natural next grouping
dimensions.

## 6. How Snakebench Should Normalize PSB Records

Snakebench should use a small internal normalization layer before summary,
readiness, advice, and reporting. It should accept PSB parquet exports directly
and preserve raw fields.

Recommended normalization:

### Identification

- Keep `session_id` as string.
- Keep `record_id` as string.
- Keep `source_file` if loaded from local parquet files.

### Tool context

- Normalize `tool` to string and require it for analysis.
- Keep `command`, `params`, `shell_block`, `tool_version`, `category`.
- Do not attempt aggressive command parsing in Snakebench. PSB/plugin should own
  tool/command extraction.

### Runtime and memory

- Use `runtime_sec` as canonical runtime.
- Use `max_rss_mb` as canonical memory for current advice.
- Preserve `max_vms_mb`, `max_uss_mb`, `max_pss_mb`, `cpu_percent`,
  `cpu_time_sec`, `io_in_mb`, and `io_out_mb`.

### Input/output

- If `input_size` exists, treat it as bytes.
- Add derived `input_size_mb = input_size / (1024 * 1024)`.
- Keep `input_size_bytes` as a normalized alias for `input_size`.
- If only `input_bytes` or `total_input_bytes` exists, normalize the same way.
- If only `input_size_mb` exists, preserve it and derive bytes only if needed.
- Keep `num_inputs`, `input_type`, `output_size`, `num_outputs`, `outputs`.

### Size bins

Use bins over normalized MB:

- `unknown`: missing input size
- `zero`: `input_size == 0`, if the distinction is useful
- `small`: 0-100 MB
- `medium`: 100-1000 MB
- `large`: 1000-10000 MB
- `xlarge`: greater than 10000 MB

The current implementation collapses zero-byte and missing input sizes too
closely. Zero can mean "no file inputs" or "not stat-able"; missing means the
field is absent.

### Resources

- Preserve raw `resources`.
- Parse JSON into normalized fields when possible:
  - `declared_mem_mb`
  - `declared_runtime` or `declared_time`
  - `declared_threads` from `threads`
  - other resource keys as `resources.*` later
- Treat empty string or invalid JSON as "resources unavailable", not as a hard
  failure.

### Environment

- Normalize PSB names directly:
  - `host_hash`
  - `cpu_model`
  - `cpu_features`
  - `cpu_cores`
  - `l2_cache_kb`
  - `l3_cache_kb`
  - `cpu_freq_mhz`
  - `os`
  - `kernel_version`
  - `kernel_string`
  - `sm_version`
  - `deploy_mode`
- Optionally create aliases:
  - `snakemake_version = sm_version`
  - `platform = os`

### Success and distress

- Keep `exit_code`.
- Default resource advice should either filter to `exit_code == 0` or clearly
  report whether failed jobs were included.
- Preserve and report distress fields:
  - `load_avg`
  - `mem_avail_mb`
  - `swap_used_mb`
  - `io_wait_pct`

## 7. What Should Be Implemented in v0.2.1

v0.2.1 should be a PSB compatibility and correctness patch, not a new product
direction.

Recommended scope:

1. Recognize canonical PSB `input_size` as bytes.
2. Derive `input_size_mb` from `input_size`.
3. Update input-size readiness to treat `input_size` as present.
4. Update input-size stratification so the included PSB parquet data no longer
   falls entirely into `unknown`.
5. Explicitly recognize PSB environment field names:
   - `host_hash`
   - `kernel_version`
   - `kernel_string`
   - `sm_version`
6. Recognize `resources` as the canonical PSB resource field in readiness.
7. In readiness, distinguish "resources column exists" from "parseable declared
   mem/runtime exists".
8. Document that PSB `input_size` and `output_size` are bytes.
9. Add focused tests for:
   - `input_size` bytes -> MB conversion
   - readiness detects PSB input size
   - readiness detects PSB environment fields
   - readiness detects `resources`

v0.2.1 should not add Snakefile parsing, ML, a database, a dashboard, or a new
dependency.

## 8. What Should Be Postponed to v0.3

v0.3 should be the resource audit version. It should connect PSB telemetry to
actual Snakemake rules and declared resources.

Postpone these to v0.3:

1. `snakebench audit Snakefile --telemetry data/`
2. Snakefile/rule inspection.
3. Extraction of declared `threads`, `resources.mem_mb`, and runtime/time from
   real rules.
4. Parsing `resources` JSON into audit-ready declared resource fields.
5. Comparing declared resources against observed p90/p95 suggestions.
6. Reporting rules with missing `mem_mb` or runtime declarations.
7. Reporting rules whose declared memory/runtime is lower than observed
   suggested values.
8. Rule/tool matching strategy:
   - direct `rule_name` if PSB eventually emits it
   - `_psb_tool`/`tool`
   - `command`
   - explicit user mapping as fallback
9. Failed-job and OOM-aware audit once failure data is consistently emitted.

v0.3 should not include ML, cloud backends, PostgreSQL, web dashboards, or a
large architectural rewrite. The main value should be local, explainable
comparison of observed PSB telemetry against declared Snakemake resources.

## Summary

PSB's upstream schema is already rich enough for Snakebench's intended direction.
The current Snakebench data is close to PSB parquet export format, but
Snakebench v0.2 does not yet understand some canonical PSB fields. The most
important immediate correction is to treat `input_size` as byte-valued PSB input
size and to treat `resources` as the upstream declared-resource carrier.

The right next patch is v0.2.1 PSB compatibility. The right next feature release
is v0.3 resource audit mode.
