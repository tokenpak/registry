# TokenPak Registry

Platform-neutral plugin registry for [TokenPak](https://tokenpak.ai) — distributing integrations across AI coding tools.

## Supported Platforms

| Platform | Status | Install |
|---|---|---|
| **Claude Code** | Active | `claude plugin marketplace add tokenpak/registry` |
| **VS Code / Cursor** | Planned | -- |
| **JetBrains** | Planned | -- |

## Claude Code Quick Start

```bash
# Add the registry
claude plugin marketplace add tokenpak/registry

# Install the plugin
claude plugin install tokenpak-claude-code@tokenpak

# Verify
claude plugin list
```

See [claude-code/README.md](claude-code/README.md) for full documentation.

## Repository Structure

```
tokenpak/registry/
├── .claude-plugin/
│   └── marketplace.json     # Claude Code marketplace catalog
├── claude-code/
│   ├── manifest.json        # Extended metadata and release notes
│   └── README.md            # Claude Code install and usage docs
├── vscode/                  # Future: VS Code / Cursor extension
├── jetbrains/               # Future: JetBrains plugin
├── registry.json            # Universal index across all platforms
├── LICENSE                  # Apache 2.0
└─��� README.md                # This file
```

## How It Works

This registry acts as a distribution hub. Each platform subdirectory contains platform-specific manifests and documentation. The plugin source code lives in [tokenpak/tokenpak](https://github.com/tokenpak/tokenpak) — this repo only contains metadata and install instructions.

- **`registry.json`** — universal index listing all platforms and their status
- **`.claude-plugin/marketplace.json`** — Claude Code's native marketplace catalog format
- **`claude-code/manifest.json`** — extended metadata (components, versions, release notes)

## License

Apache 2.0 — see [LICENSE](LICENSE).
