#!/usr/bin/env python3
"""
PC環境用 .envファイル生成スクリプト

使用方法:
1. このファイルの認証情報を実際の値に更新
2. python create_pc_env.py を実行
3. .envファイルが自動生成されます
"""
import json

print("🔧 PC環境用 .envファイルを生成中...")

# ========================================
# 以下の認証情報を実際の値に置き換えてください
# ========================================

GOOGLE_CREDENTIALS = {
    "type": "service_account",
    "project_id": "calendar-slack-bot-465923",
    "private_key_id": "【実際のprivate_key_idに置き換え】",
    "private_key": "【実際のprivate_keyに置き換え（改行含む）】",
    "client_email": "【実際のclient_emailに置き換え】", 
    "client_id": "【実際のclient_idに置き換え】",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "【実際のclient_x509_cert_urlに置き換え】",
    "universe_domain": "googleapis.com"
}

# その他の設定値
SLACK_WEBHOOK_URL = "【実際のSlack Webhook URLに置き換え】"
CALENDAR_ID = "【実際のカレンダーIDに置き換え】"
VOICEVOX_API_KEY = "【実際のVOICEVOX APIキーに置き換え】"
SLACK_BOT_TOKEN = "【実際のSlack Bot Tokenに置き換え】"
SLACK_CHANNEL_ID = "【実際のSlack Channel IDに置き換え】"

def create_env_file():
    """PC環境用の.envファイルを生成"""
    try:
        # プレースホルダーチェック
        if "【実際の" in str(GOOGLE_CREDENTIALS):
            print("❌ エラー: 認証情報がまだプレースホルダーのままです")
            print("   create_pc_env.py ファイル内の【】部分を実際の値に置き換えてください")
            return False
            
        # Google認証情報をJSON文字列に変換
        credentials_json = json.dumps(GOOGLE_CREDENTIALS, separators=(',', ':'))
        
        # .envファイルの内容を作成
        env_content = f"""# Slack Configuration
SLACK_WEBHOOK_URL={SLACK_WEBHOOK_URL}

# Google Calendar Configuration (Service Account)
GOOGLE_CREDENTIALS_JSON={credentials_json}
CALENDAR_ID={CALENDAR_ID}

# Timezone (optional, defaults to Asia/Tokyo)
TIMEZONE=Asia/Tokyo

# VOICEVOX API Configuration
VOICEVOX_API_KEY={VOICEVOX_API_KEY}
VOICEVOX_SPEAKER_ID=3

# Slack Bot Token (for monitoring messages)
SLACK_BOT_TOKEN={SLACK_BOT_TOKEN}
SLACK_CHANNEL_ID={SLACK_CHANNEL_ID}"""
        
        # .envファイルを保存
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("✅ .envファイルが正常に作成されました！")
        print("📅 Calendar Voice Bot の準備が完了しました")
        print("🎵 PC環境で音声再生が正常に動作するはずです")
        print("\n次の手順:")
        print("1. run_calendar.bat を実行してテスト")
        print("2. Windowsタスクスケジューラーで自動実行設定")
        return True
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

if __name__ == "__main__":
    create_env_file()
    input("\nEnterキーを押して終了...")