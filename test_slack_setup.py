#!/usr/bin/env python3
"""
Slack設定テストスクリプト
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_bot_token():
    """Bot Tokenの接続テスト"""
    token = os.getenv('SLACK_BOT_TOKEN')
    if not token:
        print("❌ SLACK_BOT_TOKEN が設定されていません")
        return False
    
    url = "https://slack.com/api/auth.test"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if data.get('ok'):
            print(f"✅ Bot Token接続成功!")
            print(f"   ユーザー名: {data.get('user')}")
            print(f"   チーム名: {data.get('team')}")
            return True
        else:
            print(f"❌ Bot Token接続失敗: {data.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Bot Token接続エラー: {e}")
        return False

def test_channel_access():
    """チャンネルアクセステスト"""
    token = os.getenv('SLACK_BOT_TOKEN')
    channel_id = os.getenv('SLACK_CHANNEL_ID', 'general')
    
    if not token:
        print("❌ SLACK_BOT_TOKEN が設定されていません")
        return False
    
    url = "https://slack.com/api/conversations.history"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"channel": channel_id, "limit": 1}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        if data.get('ok'):
            print(f"✅ チャンネルアクセス成功!")
            print(f"   チャンネルID: {channel_id}")
            messages = data.get('messages', [])
            print(f"   取得メッセージ数: {len(messages)}")
            return True
        else:
            error = data.get('error')
            print(f"❌ チャンネルアクセス失敗: {error}")
            if error == 'not_in_channel':
                print("   → Botがチャンネルに招待されていません")
            elif error == 'channel_not_found':
                print("   → チャンネルIDが間違っています")
            elif error == 'missing_scope':
                print("   → channels:history権限が不足しています")
            return False
            
    except Exception as e:
        print(f"❌ チャンネルアクセスエラー: {e}")
        return False

def test_webhook():
    """Webhook URLテスト"""
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    if not webhook_url:
        print("❌ SLACK_WEBHOOK_URL が設定されていません")
        return False
    
    payload = {
        "text": "🧪 Calendar Voice Bot - 設定テスト",
        "username": "Calendar Bot",
        "icon_emoji": ":calendar:"
    }
    
    try:
        response = requests.post(webhook_url, json=payload)
        
        if response.status_code == 200:
            print("✅ Webhook投稿成功!")
            print("   Slackチャンネルにテストメッセージが投稿されました")
            return True
        else:
            print(f"❌ Webhook投稿失敗: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Webhook投稿エラー: {e}")
        return False

def main():
    """メインテスト"""
    print("🔧 Slack設定テスト開始")
    print("=" * 50)
    
    # Bot Tokenテスト
    print("\n1. Bot Token接続テスト")
    bot_ok = test_bot_token()
    
    # チャンネルアクセステスト
    print("\n2. チャンネルアクセステスト")
    channel_ok = test_channel_access()
    
    # Webhookテスト
    print("\n3. Webhook投稿テスト")
    webhook_ok = test_webhook()
    
    # 結果まとめ
    print("\n" + "=" * 50)
    print("📊 テスト結果:")
    print(f"   Bot Token: {'✅' if bot_ok else '❌'}")
    print(f"   チャンネルアクセス: {'✅' if channel_ok else '❌'}")
    print(f"   Webhook投稿: {'✅' if webhook_ok else '❌'}")
    
    if all([bot_ok, channel_ok, webhook_ok]):
        print("\n🎉 すべての設定が正常です!")
        print("   Calendar Voice Botが動作準備完了です")
    else:
        print("\n⚠️  設定に問題があります")
        print("   上記のエラーメッセージを確認してください")

if __name__ == "__main__":
    main()