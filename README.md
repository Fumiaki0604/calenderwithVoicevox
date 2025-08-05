# Calendar Voice Bot

音声読み上げ機能付きカレンダー Slack ボット

## 🎯 概要

このボットは Google Calendar の予定を取得し、Slack に投稿すると同時に VOICEVOX API を使用して音声で読み上げます。

## ✨ 機能

- Google Calendar からの予定取得
- Slack への予定投稿
- VOICEVOX API による音声合成・再生（ずんだもん）
- 平日のみの自動実行（土日祝日をスキップ）
- 欠席予定の自動除外
- DM での通知と音声読み上げ

## 🖥️ PC環境での実行

### 1. リポジトリクローン

```bash
git clone https://github.com/Fumiaki0604/calenderwithVoicevox.git
cd calenderwithVoicevox
```

### 2. 環境変数設定

`.env.example` をコピーして `.env` を作成し、以下の認証情報を設定してください：

```bash
cp .env.example .env
# .envファイルを編集して認証情報を設定
```

**必要な認証情報:**
- Google Calendar Service Account JSON
- Slack Webhook URL & Bot Token
- VOICEVOX API Key

### 3. 自動セットアップ

```bash
python setup.py
```

### 4. 動作テスト

```bash
# Windows
run_calendar.bat    # カレンダー投稿テスト
run_monitor.bat     # 音声監視テスト

# macOS/Linux
./run_calendar.sh   # カレンダー投稿テスト
./run_monitor.sh    # 音声監視テスト
```

## 🔄 自動実行設定

### Windows (タスクスケジューラー)
- 毎朝8:00に `run_calendar.bat` を実行
- `run_monitor.bat` を常時起動

### macOS/Linux (crontab)
```bash
# 平日8:00に実行
0 8 * * 1-5 /path/to/calenderwithVoicevox/run_calendar.sh
```

## 🎵 音声機能

- **VOICEVOX API** による日本語音声合成
- **ずんだもん** による読み上げ
- PC スピーカーからの音声出力

## 📋 動作環境

- Python 3.8+
- 音声出力デバイス
- インターネット接続

## 🔧 トラブルシューティング

詳細なセットアップガイドは以下を参照：
- `setup_pc.md` - PC環境詳細設定
- `GITHUB_SETUP.md` - GitHub設定ガイド
- `PC_MIGRATION_GUIDE.md` - 移行ガイド

## 📄 ライセンス

MIT License