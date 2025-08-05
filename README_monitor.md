# Slack Voice Monitor

既存のカレンダーボットのSlackメッセージを監視して音声読み上げするシンプルなボット

## 概要

- **既存システム活用**: 動作中の `calendar-slack-bot` はそのまま
- **Slack監視**: カレンダーボットのメッセージを自動検出
- **音声読み上げ**: VOICEVOX APIで「ずんだもん」が読み上げ
- **軽量設計**: 最小限のライブラリで動作

## 必要な設定

### 1. Slack Bot Token の取得

1. https://api.slack.com/apps → 既存アプリまたは新規作成
2. **OAuth & Permissions** で以下のスコープを追加:
   - `channels:history` (メッセージ履歴読み取り)
   - `channels:read` (チャンネル情報読み取り)
3. **Install App to Workspace** でトークンを取得
4. `.env` の `SLACK_BOT_TOKEN` に設定

### 2. チャンネル ID の取得

1. Slack でターゲットチャンネルを右クリック
2. **チャンネル詳細を表示**
3. 最下部のチャンネル ID をコピー
4. `.env` の `SLACK_CHANNEL_ID` に設定

## 使用方法

### テスト実行
```bash
cd ~/calendar-voice-bot
TEST_MODE=true python3 slack_voice_monitor.py
```

### 連続監視
```bash
python3 slack_voice_monitor.py
```

## 動作の流れ

1. **メッセージ監視**: 30秒間隔でSlackをチェック
2. **カレンダーボット検出**: `📅`、`Calendar Bot` などで判定
3. **テキスト変換**: Slack形式から音声向けテキストに変換
4. **音声合成**: VOICEVOX APIで音声ファイル生成
5. **音声再生**: ローカルで自動再生

## 特徴

- ✅ **既存システム無変更**
- ✅ **リアルタイム監視**
- ✅ **自動テキスト整形**
- ✅ **依存関係最小**
- ✅ **エラー処理完備**

## トラブルシューティング

### Slack API エラー
- Bot Token が正しく設定されているか確認
- 必要なスコープが付与されているか確認

### 音声再生エラー
- `pygame` がインストールされているか確認
- 音声出力デバイスが接続されているか確認

### VOICEVOX API エラー  
- API キーが有効か確認
- インターネット接続を確認