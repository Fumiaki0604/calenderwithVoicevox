#!/usr/bin/env python3
"""
Slack Bot Token権限チェックツール
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def check_bot_permissions():
    """Bot Tokenの権限を詳細チェック"""
    token = os.getenv('SLACK_BOT_TOKEN')
    if not token:
        print("❌ SLACK_BOT_TOKEN が設定されていません")
        return
    
    print("🔍 Slack Bot Token 権限チェック")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. 基本認証テスト
    print("1️⃣ 基本認証テスト")
    try:
        response = requests.get("https://slack.com/api/auth.test", headers=headers)
        data = response.json()
        
        if data.get('ok'):
            print(f"   ✅ 認証成功")
            print(f"   👤 ユーザー: {data.get('user')}")
            print(f"   🏢 チーム: {data.get('team')}")
            print(f"   🆔 ユーザーID: {data.get('user_id')}")
        else:
            print(f"   ❌ 認証失敗: {data.get('error')}")
            return
    except Exception as e:
        print(f"   ❌ 認証エラー: {e}")
        return
    
    # 2. チャンネル読み取りテスト
    print(f"\n2️⃣ チャンネル読み取りテスト")
    test_api_permission("conversations.list", {"types": "public_channel", "limit": 1})
    
    # 3. DM読み取りテスト  
    print(f"\n3️⃣ DM読み取りテスト")
    test_api_permission("conversations.list", {"types": "im", "limit": 1})
    
    # 4. ユーザー情報テスト
    print(f"\n4️⃣ ユーザー情報テスト")
    test_api_permission("users.list", {"limit": 1})
    
    # 5. メッセージ履歴テスト
    print(f"\n5️⃣ メッセージ履歴テスト")
    channel_id = os.getenv('SLACK_CHANNEL_ID')
    if channel_id:
        test_api_permission("conversations.history", {"channel": channel_id, "limit": 1})
    else:
        print("   ⚠️  SLACK_CHANNEL_ID が設定されていません")
    
    # 6. メッセージ投稿テスト
    print(f"\n6️⃣ メッセージ投稿テスト")
    if channel_id:
        test_message_post(channel_id)
    else:
        print("   ⚠️  SLACK_CHANNEL_ID が設定されていません")
    
    print(f"\n📊 権限チェック完了")

def test_api_permission(method, params):
    """API権限をテスト"""
    token = os.getenv('SLACK_BOT_TOKEN')
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://slack.com/api/{method}"
    
    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        if data.get('ok'):
            print(f"   ✅ {method}: 成功")
        else:
            error = data.get('error')
            print(f"   ❌ {method}: 失敗 - {error}")
            
            # エラーの詳細説明
            if error == 'missing_scope':
                print(f"      → 権限不足です")
                if method == 'conversations.list':
                    print(f"      → channels:read または im:read が必要")
                elif method == 'users.list':
                    print(f"      → users:read が必要")
                elif method == 'conversations.history':
                    print(f"      → channels:history または im:history が必要")
            elif error == 'not_in_channel':
                print(f"      → Botがチャンネルに招待されていません")
            elif error == 'channel_not_found':
                print(f"      → チャンネルIDが間違っています")
                
    except Exception as e:
        print(f"   ❌ {method}: エラー - {e}")

def test_message_post(channel_id):
    """メッセージ投稿権限をテスト"""
    token = os.getenv('SLACK_BOT_TOKEN')
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "channel": channel_id,
        "text": "🧪 権限テスト投稿（自動削除されます）",
        "username": "Permission Test Bot"
    }
    
    try:
        response = requests.post("https://slack.com/api/chat.postMessage", 
                               headers=headers, json=payload)
        data = response.json()
        
        if data.get('ok'):
            print(f"   ✅ chat.postMessage: 成功")
            message_ts = data.get('ts')
            
            # 投稿したメッセージを削除
            delete_payload = {
                "channel": channel_id,
                "ts": message_ts
            }
            
            delete_response = requests.post("https://slack.com/api/chat.delete",
                                          headers=headers, json=delete_payload)
            delete_data = delete_response.json()
            
            if delete_data.get('ok'):
                print(f"   🗑️  テストメッセージを削除しました")
            else:
                print(f"   ⚠️  テストメッセージの削除に失敗: {delete_data.get('error')}")
                
        else:
            error = data.get('error')
            print(f"   ❌ chat.postMessage: 失敗 - {error}")
            
            if error == 'missing_scope':
                print(f"      → chat:write 権限が必要です")
            elif error == 'not_in_channel':
                print(f"      → Botがチャンネルに招待されていません")
            elif error == 'channel_not_found':
                print(f"      → チャンネルIDが間違っています")
                
    except Exception as e:
        print(f"   ❌ chat.postMessage: エラー - {e}")

def show_required_scopes():
    """必要な権限スコープを表示"""
    print(f"\n📋 Calendar Voice Bot に必要な権限:")
    print("=" * 50)
    
    scopes = [
        ("channels:history", "チャンネル履歴の読み取り", "必須"),
        ("channels:read", "チャンネル情報の読み取り", "必須"),
        ("im:history", "DM履歴の読み取り", "必須"),
        ("im:read", "DM情報の読み取り", "必須"),
        ("users:read", "ユーザー情報の読み取り", "推奨"),
        ("chat:write", "メッセージ投稿", "必須"),
        ("chat:write.public", "パブリックチャンネル投稿", "推奨"),
    ]
    
    for scope, description, priority in scopes:
        priority_icon = "🔴" if priority == "必須" else "🟡"
        print(f"   {priority_icon} {scope:<20} - {description}")
    
    print(f"\n🔧 権限追加手順:")
    print(f"   1. https://api.slack.com/apps")
    print(f"   2. あなたのアプリを選択")
    print(f"   3. OAuth & Permissions")
    print(f"   4. Bot Token Scopes に上記権限を追加")
    print(f"   5. Reinstall to Workspace")

if __name__ == "__main__":
    check_bot_permissions()
    show_required_scopes()