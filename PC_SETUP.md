# PC環境セットアップ手順

## 1. リポジトリのクローン
```bash
git clone https://github.com/Fumiaki0604/calenderwithVoicevox.git
cd calenderwithVoicevox
```

## 2. Python仮想環境のセットアップ
```bash
python setup.py
```

## 3. .envファイルの作成

WSL環境で動作確認済みの設定をPC環境に適用するため、以下のPythonコードを実行して.envファイルを生成してください：

```python
import json

# 実際の認証情報（使用する実際の値に置き換えてください）
credentials = {
    "type": "service_account",
    "project_id": "YOUR_GOOGLE_PROJECT_ID",
    "private_key_id": "YOUR_PRIVATE_KEY_ID",
    "private_key": "YOUR_COMPLETE_PRIVATE_KEY_WITH_NEWLINES",
    "client_email": "YOUR_SERVICE_ACCOUNT_EMAIL",
    "client_id": "YOUR_CLIENT_ID",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "YOUR_CLIENT_X509_CERT_URL",
    "universe_domain": "googleapis.com"
}

# JSON形式に変換（適切にエスケープされる）
credentials_json = json.dumps(credentials, separators=(',', ':'))

# .envファイルの内容を作成
env_content = f'''# Slack Configuration
SLACK_WEBHOOK_URL=YOUR_SLACK_WEBHOOK_URL

# Google Calendar Configuration (Service Account)
GOOGLE_CREDENTIALS_JSON={credentials_json}
CALENDAR_ID=YOUR_CALENDAR_ID

# Timezone (optional, defaults to Asia/Tokyo)
TIMEZONE=Asia/Tokyo

# VOICEVOX API Configuration
VOICEVOX_API_KEY=YOUR_VOICEVOX_API_KEY
VOICEVOX_SPEAKER_ID=3

# Slack Bot Token (for monitoring messages)
SLACK_BOT_TOKEN=YOUR_SLACK_BOT_TOKEN
SLACK_CHANNEL_ID=YOUR_SLACK_CHANNEL_ID'''

# .envファイルを保存
with open('.env', 'w', encoding='utf-8') as f:
    f.write(env_content)
print("✅ .env file created!")
```

## 4. アプリケーションの実行

### 手動実行（テスト用）
```bash
run_calendar.bat
```

### スケジュール実行（毎朝8:00）
Windowsタスクスケジューラーで`run_calendar.bat`を設定

## 重要な修正点

- ✅ JSON形式の認証情報が正しくエスケープされるようになりました
- ✅ Google Calendar API接続エラーが解決されています  
- ✅ PC環境では音声出力が正常に動作します

## トラブルシューティング

### JSON parsing error が発生する場合
上記のPythonコードを使用して.envファイルを再生成してください。`json.dumps()`を使用することで、適切なエスケープが保証されます。

### 音声が再生されない場合
- PC環境で実行していることを確認
- 音量設定を確認
- スピーカー/ヘッドフォンの接続を確認

### Google Calendar API エラーの場合
- Service Account の認証情報が正しく設定されていることを確認
- Google Cloud Console でCalendar APIが有効になっていることを確認