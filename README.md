# arXiv Paper Summary Agent

arXivから最新論文を収集し、Gemini APIで日本語要約を生成してSlack/Discordに通知するPythonエージェントです。

## Features

- arXiv APIで論文を自動収集
- Google Gemini APIで日本語要約を生成
- Slack/Discord Webhookで通知
- GitHub Actionsで毎日定時実行

## Requirements

- Python 3.11 or 3.12 (recommended for stable library support)
- Note: Python 3.13+ may have compatibility issues with some dependencies

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables

以下の環境変数を設定してください：

```bash
export GEMINI_API_KEY="your-gemini-api-key"
export SLACK_WEBHOOK_URL="your-slack-webhook-url"  # Optional
export DISCORD_WEBHOOK_URL="your-discord-webhook-url"  # Optional
```

### 3. Configure settings

`config/default.yaml` を編集して、検索条件や通知設定をカスタマイズできます：

```yaml
arxiv:
  categories:
    - cs.AI
    - cs.LG
  keywords:
    - LLM
  max_results: 10

notification:
  slack:
    enabled: true
  discord:
    enabled: false
```

## Usage

### Local execution

```bash
python -m arxiv_agent.main config/default.yaml
```

### GitHub Actions

GitHub Secretsに以下を設定してください：

- `GEMINI_API_KEY`
- `SLACK_WEBHOOK_URL` (optional)
- `DISCORD_WEBHOOK_URL` (optional)

ワークフローは毎日01:00 UTC（JST 10:00）に自動実行されます。手動実行も可能です。

## Project Structure

```
.
├── src/arxiv_agent/
│   ├── config/          # Configuration management
│   ├── collection/      # arXiv API client
│   ├── summarization/   # Gemini API client
│   ├── notification/    # Slack/Discord notifiers
│   └── utils/           # Utilities
├── config/
│   └── default.yaml     # Default configuration
├── tests/               # Unit tests
└── .github/workflows/   # GitHub Actions
```

## Testing

```bash
# Run all tests
pytest tests/

# Run core tests only (no external API dependencies)
PYTHONPATH=src pytest tests/test_config_loader.py tests/test_prompt_builder.py -v
```

**Note**: Some tests may fail on Python 3.13+ due to library compatibility issues. Use Python 3.11-3.12 for full test coverage.

## License

MIT
