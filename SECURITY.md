# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.9.x   | yes       |
| 0.8.x   | yes       |
| < 0.8   | no        |

## Reporting a vulnerability

Email `security@animator-host.dev` with a PoC. Do not open a public issue
for memory-safety bugs in `extensions/native_ops_cpp/`. We triage within
72 hours.

## Threat model

The plugin host executes third-party Python and native extensions in-process.
Extensions are **trusted by default** — installing one is equivalent to running
its code. Untrusted extensions should run under `--sandbox` (Job Object +
AppContainer on Windows 10 22H2+).

## Known considerations

- `.safetensors` loaders must `mmap` with `MAP_PRIVATE` to avoid TOCTOU on
  swap files.
- Native ops are built with `/guard:cf` and CFG enabled. Disable only if you
  know why.
- Outbound telemetry is off by default. See `config/default.toml`.