# TokenPak for Claude Code

Install the TokenPak plugin for Claude Code to get corpus-aware context packing, safety hooks, and productivity skills.

## Install

```bash
claude plugin marketplace add tokenpak/registry
claude plugin install tokenpak-claude-code@tokenpak
```

## What you get

| Component | Description |
|---|---|
| **Skills** | `/tokenpak-claude-code:tokenpak-status`, `/tokenpak-claude-code:review-pack`, `/tokenpak-claude-code:migration-pack` |
| **Hooks** | Write-path protection, post-edit validation, telemetry stamping, review-prep enforcement |
| **MCP tools** | `search_corpus`, `build_context_pack`, `extract_structured_fields`, `prepare_review_packet`, `summarize_related_issues` |
| **Agents** | `research-analyst` (OSS), `security-reviewer` (Pro), `migration-planner` (Pro) |

## Requirements

- Claude Code v2.1.85 or later
- Python 3.10+ (for MCP server)
- Optional: tokenpak proxy on `localhost:8766` (plugin works without it)

## Configuration

After install, the plugin works out of the box. For proxy users, set in your shell profile:

```bash
export ENABLE_TOOL_SEARCH=true
export ANTHROPIC_BASE_URL=http://localhost:8766
```

Verify with: `python3 -m tokenpak doctor --claude-code`

## Update

```bash
claude plugin marketplace update tokenpak
claude plugin update tokenpak-claude-code
```

## Uninstall

```bash
claude plugin uninstall tokenpak-claude-code
```

## Documentation

- [TokenPak docs](https://docs.tokenpak.ai)
- [Plugin README](https://github.com/tokenpak/tokenpak/tree/main/tokenpak/integrations/claude_code/plugin)
- [Claude Code plugin docs](https://code.claude.com/docs/en/plugins)
