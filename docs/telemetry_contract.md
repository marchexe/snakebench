# Telemetry Contract

Snakebench consumes exported PSB-style telemetry. It does not collect telemetry, submit telemetry, run Snakemake, or run a server.

## Required For Audit

Observed usage:

- `runtime_sec`;
- `max_rss_mb`;
- `tool` or `command`.

Rule matching:

- best: `rule_name`;
- fallback: `tool`;
- fallback: `command`.

Snakefile-side hints:

- `_psb_tool`;
- `_psb_primary_cmd`.

## Useful Fields

Identity:

- `session_id`;
- `record_id`;
- `source_file`.

Declared resources from telemetry:

- `resources`;
- `resources.mem_mb`;
- `resources.runtime`;
- `resources._cores`;
- `threads`.

Input/output size:

- `input_size`;
- `output_size`;
- `num_inputs`;
- `num_outputs`;
- `input_type`.

Environment and failure metadata:

- preserved when present;
- not used as the main audit key yet.

## PSB Units And Shapes

- `input_size` and `output_size` are bytes.
- `resources` is a JSON object from Snakemake resource allocations.
- A PSB session is one workflow invocation and uses `session_id`.
- A PSB observation is one rule execution and uses `record_id`.

Known annotation mapping:

| Snakefile param | Telemetry field |
|---|---|
| `_psb_tool` | `tool` |
| `_psb_tool_version` | `tool_version` |
| `_psb_primary_cmd` | `command` |
| `_psb_params` | `params` |
| `_psb_category` | `category` |

## Upstream Work Needed

1. Export `rule_name` consistently.
2. Export Snakemake `resources` consistently.
3. Export `input_size` and `output_size` consistently.
4. Keep `_psb_*` names and precedence aligned between plugin, PSB export, and Snakebench.
5. Define how failed and OOM observations should affect resource advice.
