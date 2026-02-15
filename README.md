# arxiv-agent

arXiv論文を自動収集・要約・通知するPythonアプリケーション

## 機能

- **論文収集**: arXiv APIを使用して、指定したカテゴリ・キーワードで論文を検索
- **要約生成**: Gemini APIを使用して、論文の要約を日本語で生成
- **通知**: SlackまたはDiscordへ要約を送信

## 前提条件

- Python 3.10以上
- Gemini APIキー（必須）
- Slack Webhook URL（任意、Slack通知使用時）
- Discord Webhook URL（任意、Discord通知使用時）

## セットアップ

1. リポジトリをクローン

```bash
git clone <repository-url>
cd arxiv-agent
```

2. 依存関係をインストール

```bash
pip install -r requirements.txt
```

3. 環境変数を設定

```bash
cp .env.example .env
```

`.env`ファイルを編集してAPIキーを設定

| 環境変数 | 説明 | 必須 |
|---------|------|------|
| `GEMINI_API_KEY` | Gemini APIのAPIキー | はい |
| `SLACK_WEBHOOK_URL` | Slack Webhook URL | いいえ |
| `DISCORD_WEBHOOK_URL` | Discord Webhook URL | いいえ |

4. 設定ファイル（config.yaml）を編集

```yaml
search:
  categories:
    - "cs.AI"
    - "cs.LG"
  keywords:
    - "LLM"
    - "transformer"
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

### 設定項目

#### search（論文検索）

| 項目 | 型 | 説明 |
|-----|---|------|
| `categories` | list[str] | arXivカテゴリ（例: `cs.AI`, `cs.LG`, `cs.CL`） |
| `keywords` | list[str] | 検索キーワード |
| `max_results` | int | 取得する論文数（最大100） |

#### summary（要約生成）

| 項目 | 型 | 説明 |
|-----|---|------|
| `prompt_template` | str | Gemini APIへのプロンプトテンプレート（`{title}`と`{abstract}`を含む必須） |

#### notification（通知）

| 項目 | 型 | 説明 |
|-----|---|------|
| `slack_enabled` | bool | Slack通知を有効にするか |
| `discord_enabled` | bool | Discord通知を有効にするか |

## 実行

```bash
python -m src.main
```

デフォルトでは`config.yaml`を使用します。別の設定ファイルを指定する場合：

```bash
python -m src.main custom_config.yaml
```

## プロジェクト構造

```
.
├── src/
│   ├── __init__.py
│   ├── main.py           # メインエントリポイント
│   ├── collector.py      # arXiv論文収集
│   ├── summarizer.py     # Gemini API要約生成
│   ├── notifier.py       # Slack/Discord通知
│   ├── config.py        # 設定読み込み
│   └── models.py         # データモデル
├── tests/                # テストコード
│   ├── test_collector.py
│   ├── test_summarizer.py
│   ├── test_notifier.py
│   ├── test_config.py
│   └── test_models.py
├── config.yaml           # デフォルト設定ファイル
├── requirements.txt      # 依存関係
├── .env.example          # 環境変数サンプル
└── README.md
```

## テスト

全テストを実行：

```bash
pytest
```

特定のテストファイルのみ実行：

```bash
pytest tests/test_collector.py
```

カバレッジを表示：

```bash
pytest --cov=src
```

## arXivカテゴリ一例

| カテゴリ | 説明 |
|---------|------|
| `cs.AI` | Artificial Intelligence |
| `cs.LG` | Machine Learning |
| `cs.CL` | Computation and Language |
| `cs.CV` | Computer Vision |
| `cs.NE` | Neural and Evolutionary Computing |
| `stat.ML` | Machine Learning (Statistics) |

## ライセンス

MIT License
