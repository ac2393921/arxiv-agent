# arxiv-agent

arXiv論文を自動収集・要約・通知するPythonアプリケーション

## 機能

- **論文収集**: arXiv APIを使用して、指定したカテゴリ・キーワードで論文を検索
- **要約生成**: Gemini APIを使用して、論文の要約を日本語で生成
- **通知**: SlackまたはDiscordへ要約を送信

## 前提条件

- Python 3.10以上
- Gemini APIキー

## セットアップ

1. 依存関係をインストール

```bash
pip install -r requirements.txt
```

2. 環境変数を設定

```bash
cp .env.example .env
```

`.env`ファイルを編集してAPIキーを設定

- `GEMINI_API_KEY`: Gemini APIのAPIキー（必須）
- `SLACK_WEBHOOK_URL`: Slack Webhook URL（任意、Slack通知使用時）
- `DISCORD_WEBHOOK_URL`: Discord Webhook URL（任意、Discord通知使用時）

3. 設定ファイル（config.yaml）を編集

```yaml
search:
  categories:
    - "cs.AI"
  keywords:
    - "LLM"
  max_results: 10

summary:
  prompt_template: |
    以下の論文を日本語で簡潔に要約してください。

    タイトル: {title}

    概要:
    {abstract}

    要約は以下の形式で出力してください：
    - 研究の目的（1-2文）
    - 手法の概要（1-2文）
    - 主な結果・貢献（1-2文）

notification:
  slack_enabled: false
  discord_enabled: false
```

## 実行

```bash
python -m src.main
```

## プロジェクト構造

```
.
├── src/
│   ├── main.py        # メインエントリポイント
│   ├── collector.py   # arXiv論文収集
│   ├── summarizer.py  # Gemini API要約生成
│   ├── notifier.py    # Slack/Discord通知
│   ├── config.py      # 設定読み込み
│   └── models.py      # データモデル
├── tests/             # テストコード
├── config.yaml        # 設定ファイル
└── requirements.txt   # 依存関係
```

## テスト

```bash
pytest
```
