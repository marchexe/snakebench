# Snakebench Dataset Readiness Report

## Dataset overview

- **Observations:** 205
- **Tools:** 5
- **Unique environments:** 1
- **PSB-like records:** 205 (100.0%)

## Available metadata

- **Runtime column:** runtime_sec
- **Memory column:** max_rss_mb
- **Threads column:** threads
- **Input size metadata:** yes
- **Tool version metadata:** yes
- **Environment metadata:** yes
- **Declared Snakemake resources:** yes
- **Failure/OOM information:** yes

## PSB compatibility

- **PSB input size fields recognized:** yes
- **PSB resources field recognized:** yes
- **PSB environment fields recognized:** yes
- **PSB input columns:** input_size, inputs, num_inputs, input_type
- **PSB resource columns:** resources
- **PSB environment columns:** host_hash, cpu_model, cpu_features, cpu_cores, l2_cache_kb, l3_cache_kb, cpu_freq_mhz, os, kernel_version, kernel_string, sm_version, deploy_mode

## Readiness levels

- **tool level advisor:** ready - Runtime and memory metadata are present with at least 20 observations.
- **input size advisor:** ready - Tool-level advice is ready and input size metadata is available.
- **ml prediction:** limited - Enough data exists for exploratory analysis, but not full ML readiness.
- **workflow resource audit:** ready - Declared resource columns and observed runtime/memory metadata are present.

The current data should be treated honestly: small or incomplete telemetry can support summaries and heuristic advice, but it is not enough for reliable ML prediction unless the ML prediction level is marked ready.

## Missing metadata

- No major readiness metadata gaps detected.

## Recommended next telemetry fields

- input_size_mb
- rule name
- declared mem_mb
- declared runtime
- workflow name/version
- failed/OOM jobs
- environment ID
