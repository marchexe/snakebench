# Integration Notes

## Current Boundary

- PSB/plugin collect and export telemetry.
- Snakebench consumes exported telemetry.
- Snakebench does not submit telemetry.
- Snakebench does not run a server.

## PSB Fields Used

- `session_id`
- `record_id`
- `tool`
- `command`
- `category`
- `tool_version`
- `runtime_sec`
- `max_rss_mb`
- `threads`
- `input_size`
- `output_size`
- `resources`
- `exit_code`
- `host_hash`
- `cpu_model`
- `sm_version`
- `deploy_mode`

## Upstream Gaps Relevant to Snakebench

- The plugin emits less than the PSB spec/server supports.
- `rule_name` is needed for better audit matching.
- `resources` should be consistently emitted.
- `inputs`, `outputs`, `input_size`, and `output_size` are important for stratified advice.
- `_psb_*` annotations should be aligned between the spec and plugin.
- The `cpu_features` mapping mismatch should be checked upstream.

## Proposed Upstream Work

- Add `rule_name` to plugin output.
- Emit `resources` from Snakemake job context.
- Emit inputs/outputs or derived sizes where safe.
- Align `_psb_*` annotation handling.
- Clarify `resources` semantics in spec/export docs.
- Expose advisor-friendly parquet fields without replacing raw PSB fields.
