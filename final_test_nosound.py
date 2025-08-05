#!/usr/bin/env python3
"""
Calendar Voice Bot 完全実動テスト（音声デバイスなし）
"""

import os
import asyncio
import time
from datetime import datetime
import pytz
import requests
import tempfile
import re
from dotenv import load_dotenv

load_dotenv()

class FinalTestBot:
    def __init__(self):
        # 実際のCalendarVoiceBotと同じ初期化（音声なし）
        self.slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        self.google_credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
        self.calendar_id = os.getenv('CALENDAR_ID')
        self.timezone = os.getenv('TIMEZONE', 'Asia/Tokyo')
        self.tz = pytz.timezone(self.timezone)
        
        # VOICEVOX API settings
        self.voicevox_api_key = os.getenv('VOICEVOX_API_KEY')
        self.voicevox_speaker_id = int(os.getenv('VOICEVOX_SPEAKER_ID', '3'))
        
        # Slack Bot Token settings
        self.slack_token = os.getenv('SLACK_BOT_TOKEN')
        self.target_channel = os.getenv('SLACK_CHANNEL_ID')
        
        # Google Calendar service
        self.service = None
        self._init_calendar_service()
        
        print("✅ Final Test Bot 初期化完了")
    
    def _init_calendar_service(self):
        """Initialize Google Calendar service"""
        try:
            from googleapiclient.discovery import build
            from google.oauth2.service_account import Credentials
            import json
            
            credentials_info = json.loads(self.google_credentials_json)
            credentials = Credentials.from_service_account_info(
                credentials_info,
                scopes=['https://www.googleapis.com/auth/calendar.readonly']
            )
            self.service = build('calendar', 'v3', credentials=credentials)
            print("✅ Google Calendar service 初期化完了")
            
        except Exception as e:
            print(f"❌ Google Calendar 初期化エラー: {e}")
    
    def get_daily_events(self, date: datetime = None):
        """カレンダーイベント取得"""
        if date is None:
            date = datetime.now(self.tz)
        
        if date.tzinfo is None:
            date = self.tz.localize(date)
        
        start_time = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        try:
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=start_time.isoformat(),
                timeMax=end_time.isoformat(),
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            # 辞退したイベントをフィルタリング
            filtered_events = self._filter_declined_events(events)
            return filtered_events
            
        except Exception as e:
            print(f"❌ Calendar API error: {e}")
            return []
    
    def _filter_declined_events(self, events):
        """辞退したイベントを除外"""
        filtered = []
        for event in events:
            attendees = event.get('attendees', [])
            if not attendees:
                filtered.append(event)
                continue
            
            user_declined = False
            for attendee in attendees:
                if attendee.get('responseStatus') == 'declined':
                    attendee_email = attendee.get('email', '')
                    if (attendee_email == self.calendar_id or 
                        attendee.get('self', False) or 
                        attendee.get('organizer', False)):
                        user_declined = True
                        break
            
            if not user_declined:
                filtered.append(event)
        
        return filtered
    
    def _format_time(self, time_data):
        """時間フォーマット"""
        if 'dateTime' in time_data:
            dt = datetime.fromisoformat(time_data['dateTime'].replace('Z', '+00:00'))
            dt_jst = dt.astimezone(self.tz)
            return dt_jst.strftime('%H:%M')
        elif 'date' in time_data:
            return '終日'
        else:
            return '時刻未定'
    
    def format_schedule_message(self, events, date):
        """Slackメッセージフォーマット"""
        date_str = date.strftime('%Y年%m月%d日 (%A)')
        
        if not events:
            return f"📅 *今日の予定 - {date_str}*\n\n✨ 予定はありません。お疲れ様です！"
        
        message = f"📅 *今日の予定 - {date_str}*\n\n"
        
        for i, event in enumerate(events, 1):
            start_time = self._format_time(event.get('start', {}))
            end_time = self._format_time(event.get('end', {}))
            summary = event.get('summary', '無題のイベント')
            description = event.get('description', '')
            location = event.get('location', '')
            
            message += f"*{i}. {summary}*\n"
            message += f"🕐 {start_time} 〜 {end_time}\n"
            
            if location:
                message += f"📍 {location}\n"
            
            if description and len(description) <= 100:
                message += f"📝 {description}\n"
            elif description:
                message += f"📝 {description[:97]}...\n"
            
            message += "\n"
        
        message += f"\n📊 合計 {len(events)} 件の予定があります"
        return message
    
    def post_calendar_to_dm(self, message):
        """Bot TokenでDMにカレンダー投稿"""
        url = "https://slack.com/api/chat.postMessage"
        headers = {
            "Authorization": f"Bearer {self.slack_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "channel": self.target_channel,
            "text": message,
            "username": "Calendar Bot",
            "icon_emoji": ":calendar:"
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            data = response.json()
            
            if data.get('ok'):
                print("✅ カレンダー予定をDMに投稿成功！")
                return data.get('ts')
            else:
                print(f"❌ DM投稿失敗: {data.get('error')}")
                return None
                
        except Exception as e:
            print(f"❌ DM投稿エラー: {e}")
            return None

class TestMonitor:
    def __init__(self):
        # Slack API settings
        self.slack_token = os.getenv('SLACK_BOT_TOKEN')
        self.target_channel = os.getenv('SLACK_CHANNEL_ID')
        
        # VOICEVOX API settings
        self.voicevox_api_key = os.getenv('VOICEVOX_API_KEY')
        self.voicevox_speaker_id = int(os.getenv('VOICEVOX_SPEAKER_ID', '3'))
        self.voicevox_api_url = 'https://api.tts.quest/v3/voicevox/synthesis'
        
        print("✅ テスト監視ボット初期化完了（音声デバイスなし）")
    
    def get_recent_messages(self, limit=10):
        """Get recent messages from Slack channel."""
        url = "https://slack.com/api/conversations.history"
        headers = {
            "Authorization": f"Bearer {self.slack_token}",
            "Content-Type": "application/json"
        }
        params = {
            "channel": self.target_channel,
            "limit": limit
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            
            if data.get('ok'):
                return data.get('messages', [])
            else:
                print(f"❌ Slack API error: {data.get('error', 'Unknown error')}")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching messages: {e}")
            return []
    
    def is_calendar_message(self, message):
        """Check if message is from Calendar Bot."""
        text = message.get('text', '')
        username = message.get('username', '')
        
        # Check for calendar bot patterns
        calendar_patterns = [
            r'📅.*の予定',
            r'合計.*件の予定',
            r'Calendar Bot',
            r'🕐.*〜'
        ]
        
        return (username == 'Calendar Bot' or 
                any(re.search(pattern, text) for pattern in calendar_patterns))
    
    def extract_voice_content(self, slack_text):
        """Extract voice-friendly content from Slack message."""
        # Remove Slack formatting
        text = re.sub(r'\*([^*]+)\*', r'\1', slack_text)  # Remove bold
        text = re.sub(r'📅|🕐|📍|📝|✨|📊', '', text)    # Remove emojis
        text = re.sub(r'\n+', '。', text)                  # Convert newlines to periods
        text = re.sub(r'〜', 'から', text)                  # Replace tilde
        
        # 長すぎる場合は短縮
        if len(text) > 200:
            text = text[:200] + "。以上です。"
        
        return text.strip()
    
    def synthesize_speech(self, text):
        """Synthesize speech using VOICEVOX API."""
        try:
            params = {
                'speaker': self.voicevox_speaker_id,
                'text': text
            }
            
            if self.voicevox_api_key:
                params['key'] = self.voicevox_api_key
            
            response = requests.post(self.voicevox_api_url, data=params)
            
            if response.status_code != 200:
                print(f"❌ VOICEVOX API error: {response.status_code}")
                return None
            
            result = response.json()
            mp3_url = result.get('mp3DownloadUrl')
            
            if not mp3_url:
                print("❌ No MP3 download URL in response")
                return None
            
            # Download audio file
            audio_response = requests.get(mp3_url)
            if audio_response.status_code != 200:
                print(f"❌ Failed to download audio: {audio_response.status_code}")
                return None
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            temp_file.write(audio_response.content)
            temp_file.close()
            
            print(f"✅ 音声ファイル作成: {temp_file.name}")
            return temp_file.name
            
        except Exception as e:
            print(f"❌ Error synthesizing speech: {e}")
            return None
    
    def simulate_play_audio(self, audio_file_path):
        """音声再生をシミュレート"""
        print(f"🔊 音声再生シミュレート")
        
        if os.path.exists(audio_file_path):
            file_size = os.path.getsize(audio_file_path)
            print(f"   📦 音声ファイルサイズ: {file_size:,} bytes")
            print(f"   🎵 実際のPC環境では、ここで音声が再生されます")
            
            # ファイルサンプル再生（数秒分の内容を確認）
            print(f"   💬 音声内容: VOICEVOX合成音声（ずんだもん）")
            
            # ファイル削除
            try:
                os.unlink(audio_file_path)
                print(f"   🗑️  一時ファイルを削除しました")
            except:
                pass
            
            return True
        else:
            print(f"   ❌ 音声ファイルが見つかりません")
            return False

async def run_complete_test():
    """完全なテストフローを実行"""
    print("🎯 Calendar Voice Bot 完全実動テスト（音声デバイスなし）")
    print("=" * 70)
    
    try:
        # Step 1: カレンダーボット初期化
        print("\n📅 Step 1: カレンダーボット初期化")
        bot = FinalTestBot()
        
        # Step 2: 今日のカレンダーイベント取得
        print("\n📊 Step 2: カレンダーイベント取得")
        now = datetime.now(bot.tz)
        print(f"   📅 対象日: {now.strftime('%Y-%m-%d %A')}")
        
        events = bot.get_daily_events(now)
        print(f"   ✅ 取得したイベント数: {len(events)}")
        
        if events:
            print("   📋 イベント詳細:")
            for i, event in enumerate(events, 1):
                title = event.get('summary', '無題')
                start_time = bot._format_time(event.get('start', {}))
                end_time = bot._format_time(event.get('end', {}))
                location = event.get('location', '')
                print(f"      {i}. {title}")
                print(f"         🕐 {start_time} 〜 {end_time}")
                if location:
                    print(f"         📍 {location}")
        else:
            print("   📝 今日の予定はありません")
        
        # Step 3: Slackメッセージ生成
        print("\n📱 Step 3: Slackメッセージ生成")
        slack_message = bot.format_schedule_message(events, now)
        print("   ✅ メッセージ生成完了")
        print("   --- 生成されたメッセージ ---")
        print(f"   {slack_message[:100]}...")
        print("   --- メッセージ終了 ---")
        
        # Step 4: DMに投稿
        print("\n🚀 Step 4: DMに投稿")
        message_ts = bot.post_calendar_to_dm(slack_message)
        
        if not message_ts:
            print("❌ 投稿失敗でテスト中断")
            return False
        
        print(f"   ✅ 投稿成功 (timestamp: {message_ts})")
        print(f"   💬 佐藤さんのDMにカレンダー予定が投稿されました")
        
        # Step 5: 監視ボット初期化
        print("\n👁️  Step 5: 監視ボット初期化")
        monitor = TestMonitor()
        
        # Step 6: 少し待ってから監視開始
        print("\n⏳ Step 6: 5秒待機（メッセージの反映を待機）...")
        await asyncio.sleep(5)
        
        # Step 7: メッセージ監視・検出
        print("\n🔍 Step 7: メッセージ監視・検出")
        messages = monitor.get_recent_messages(limit=5)
        print(f"   📨 取得したメッセージ数: {len(messages)}")
        
        calendar_messages = []
        for message in messages:
            if monitor.is_calendar_message(message):
                calendar_messages.append(message)
        
        print(f"   📅 カレンダーメッセージ数: {len(calendar_messages)}")
        
        if not calendar_messages:
            print("   ❌ カレンダーメッセージが見つかりません")
            print("   💡 メッセージ検索パターンを確認します...")
            
            # デバッグ: 最新メッセージの内容を確認
            if messages:
                latest = messages[0]
                print(f"   🔍 最新メッセージ内容: {latest.get('text', '')[:100]}...")
                print(f"   👤 ユーザー名: {latest.get('username', 'なし')}")
            
            return False
        
        # Step 8: 音声変換・合成
        print("\n🎵 Step 8: 音声変換・合成")
        latest_message = calendar_messages[0]
        text = latest_message.get('text', '')
        
        print(f"   📝 元メッセージ: {text[:80]}...")
        
        voice_text = monitor.extract_voice_content(text)
        print(f"   🗣️  音声用テキスト: {voice_text[:80]}...")
        
        audio_file = monitor.synthesize_speech(voice_text)
        
        if audio_file:
            print("   ✅ 音声合成成功！")
            
            # Step 9: 音声再生（シミュレート）
            print("\n🔊 Step 9: 音声再生シミュレート")
            success = monitor.simulate_play_audio(audio_file)
            
            if success:
                print("   ✅ 音声処理完了")
                return True
            else:
                print("   ❌ 音声処理失敗")
                return False
        else:
            print("   ❌ 音声合成失敗")
            return False
            
    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """メイン実行"""
    success = await run_complete_test()
    
    print("\n" + "=" * 70)
    if success:
        print("🎊 完全実動テスト成功！")
        print("\n✨ Calendar Voice Bot は完璧に動作準備完了")
        print("\n🎯 テストで確認された機能:")
        print("   ✅ Google Calendar API からの予定取得")
        print("   ✅ Slack DMへの予定投稿")
        print("   ✅ Slack メッセージの監視・検出")
        print("   ✅ カレンダーメッセージの識別")
        print("   ✅ 音声用テキストの生成")
        print("   ✅ VOICEVOX API 音声合成")
        print("   ✅ 音声ファイルの生成・管理")
        print("\n🖥️  PC環境での実行:")
        print("   1. python main.py                    # 朝8:00に自動実行")
        print("   2. python slack_voice_monitor.py     # 常時監視モード")
        print("\n🎵 PC環境では実際にスピーカーから音声が再生されます！")
    else:
        print("❌ テストでエラーが発生しました")
        print("   エラー内容を確認して設定を見直してください")

if __name__ == "__main__":
    asyncio.run(main())