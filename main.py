#!/usr/bin/env python3
"""
Calendar Voice Bot
A bot that integrates with calendar services, posts daily schedules to Slack,
and reads them aloud using VOICEVOX API.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import requests
from dotenv import load_dotenv
import pytz
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import json
import jpholiday
import pygame
import tempfile
import asyncio
import aiohttp
from urllib.parse import urlencode

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CalendarVoiceBot:
    def __init__(self):
        self.slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        self.google_credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
        self.calendar_id = os.getenv('CALENDAR_ID')
        self.timezone = os.getenv('TIMEZONE', 'Asia/Tokyo')
        self.tz = pytz.timezone(self.timezone)
        
        # VOICEVOX API settings
        self.voicevox_api_key = os.getenv('VOICEVOX_API_KEY')
        self.voicevox_speaker_id = int(os.getenv('VOICEVOX_SPEAKER_ID', '3'))  # Default: ずんだもん
        self.voicevox_api_url = 'https://api.su-shiki.com/v2/voicevox/audio/'
        
        if not all([self.slack_webhook_url, self.google_credentials_json, self.calendar_id]):
            raise ValueError("Missing required environment variables: SLACK_WEBHOOK_URL, GOOGLE_CREDENTIALS_JSON, CALENDAR_ID")
        
        # Initialize Google Calendar service
        self.service = None
        self._init_calendar_service()
        
        # Initialize pygame for audio playback
        pygame.mixer.init()
    
    def _init_calendar_service(self):
        """Initialize Google Calendar service with Service Account credentials."""
        try:
            # Parse the JSON credentials
            credentials_info = json.loads(self.google_credentials_json)
            
            # Create credentials from the service account info
            credentials = Credentials.from_service_account_info(
                credentials_info,
                scopes=['https://www.googleapis.com/auth/calendar.readonly']
            )
            
            # Build the service
            self.service = build('calendar', 'v3', credentials=credentials)
            logger.info("Google Calendar service initialized successfully with Service Account")
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in GOOGLE_CREDENTIALS_JSON: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Google Calendar service: {e}")
            raise
    
    def _is_business_day(self, date: datetime) -> bool:
        """平日かどうかを判定（土日祝日を除外）"""
        # 日付のみを取得（時刻情報を除去）
        date_only = date.date()
        
        # 土曜日（5）、日曜日（6）をチェック
        if date.weekday() >= 5:
            logger.info(f"{date_only} は土日のため配信をスキップします")
            return False
        
        # 日本の祝日をチェック
        if jpholiday.is_holiday(date_only):
            holiday_name = jpholiday.is_holiday_name(date_only)
            logger.info(f"{date_only} は祝日（{holiday_name}）のため配信をスキップします")
            return False
        
        return True
    
    def _filter_declined_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out events where user has declined attendance."""
        filtered_events = []
        
        for event in events:
            attendees = event.get('attendees', [])
            
            # If no attendees list, include the event (likely a personal event)
            if not attendees:
                filtered_events.append(event)
                continue
            
            # Check if any attendee has declined (assuming the service account represents the user)
            user_declined = False
            for attendee in attendees:
                # Check if this attendee is the calendar owner/user and has declined
                if attendee.get('responseStatus') == 'declined':
                    # If the attendee email matches the calendar ID or is marked as organizer/self
                    attendee_email = attendee.get('email', '')
                    if (attendee_email == self.calendar_id or 
                        attendee.get('self', False) or 
                        attendee.get('organizer', False)):
                        user_declined = True
                        break
            
            # Only include event if user hasn't declined
            if not user_declined:
                filtered_events.append(event)
            else:
                logger.info(f"Filtered out declined event: {event.get('summary', 'Untitled')}")
        
        return filtered_events

    def get_daily_events(self, date: datetime = None) -> List[Dict[str, Any]]:
        """Fetch calendar events for a specific date."""
        if date is None:
            date = datetime.now(self.tz)
        
        # Ensure date is timezone-aware
        if date.tzinfo is None:
            date = self.tz.localize(date)
        
        # Set time range for the day
        start_time = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        logger.info(f"Fetching events for {date.strftime('%Y-%m-%d')} ({self.timezone})")
        
        try:
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=start_time.isoformat(),
                timeMax=end_time.isoformat(),
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            logger.info(f"Found {len(events)} total events")
            
            # Filter out declined events
            filtered_events = self._filter_declined_events(events)
            logger.info(f"After filtering declined events: {len(filtered_events)} events")
            
            return filtered_events
            
        except Exception as e:
            logger.error(f"Failed to fetch calendar events: {e}")
            # Return placeholder events as fallback
            return [
                {
                    'summary': 'API接続エラー - プレースホルダーイベント',
                    'start': {'dateTime': '09:00'},
                    'end': {'dateTime': '10:00'},
                    'description': 'Google Calendar APIへの接続に失敗しました'
                }
            ]
    
    def format_schedule_message(self, events: List[Dict[str, Any]], date: datetime, is_tomorrow: bool = False) -> str:
        """Format events into a beautiful Slack message."""
        day_label = "明日" if is_tomorrow else "今日"
        date_str = date.strftime('%Y年%m月%d日 (%A)')
        
        if not events:
            if is_tomorrow:
                return f"📅 *{day_label}の予定 - {date_str}*\n\n✨ 予定はありません。ゆっくりお過ごしください！"
            else:
                return f"📅 *{day_label}の予定 - {date_str}*\n\n✨ 予定はありません。お疲れ様です！"
        
        message = f"📅 *{day_label}の予定 - {date_str}*\n\n"
        
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
    
    def format_voice_message(self, events: List[Dict[str, Any]], date: datetime, is_tomorrow: bool = False) -> str:
        """Format events into a voice-friendly message."""
        day_label = "明日" if is_tomorrow else "今日"
        date_str = date.strftime('%m月%d日')
        
        if not events:
            return f"{day_label}{date_str}の予定はありません。"
        
        message = f"{day_label}{date_str}の予定をお知らせします。"
        
        for i, event in enumerate(events, 1):
            start_time = self._format_voice_time(event.get('start', {}))
            summary = event.get('summary', '無題のイベント')
            
            message += f"{i}番目、{start_time}から{summary}。"
        
        message += f"以上、合計{len(events)}件の予定です。"
        return message
    
    def _format_voice_time(self, time_data: Dict[str, Any]) -> str:
        """Format time data for voice output."""
        if 'dateTime' in time_data:
            dt = datetime.fromisoformat(time_data['dateTime'].replace('Z', '+00:00'))
            dt_jst = dt.astimezone(self.tz)
            hour = dt_jst.hour
            minute = dt_jst.minute
            
            if minute == 0:
                return f"{hour}時"
            else:
                return f"{hour}時{minute}分"
        elif 'date' in time_data:
            return '終日'
        else:
            return '時刻未定で'
    
    async def synthesize_speech(self, text: str) -> str:
        """Synthesize speech using VOICEVOX API and return audio file path."""
        try:
            params = {
                'speaker': self.voicevox_speaker_id,
                'text': text
            }
            
            if self.voicevox_api_key:
                params['key'] = self.voicevox_api_key
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.voicevox_api_url, data=params, headers=headers) as response:
                    if response.status != 200:
                        logger.error(f"VOICEVOX API error: {response.status}")
                        error_text = await response.text()
                        logger.error(f"Error response: {error_text}")
                        return None
                    
                    # su-shiki.com API returns audio data directly
                    audio_data = await response.read()
                    
                    # Save to temporary file
                    temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
                    temp_file.write(audio_data)
                    temp_file.close()
                    
                    logger.info(f"Audio file saved: {temp_file.name}")
                    return temp_file.name
                        
        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}")
            return None
    
    def play_audio(self, audio_file_path: str) -> bool:
        """Play audio file using pygame."""
        try:
            pygame.mixer.music.load(audio_file_path)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
            
            logger.info("Audio playback completed")
            return True
            
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            return False
        finally:
            # Clean up temporary file
            try:
                os.unlink(audio_file_path)
            except:
                pass
    
    async def speak_schedule(self, events: List[Dict[str, Any]], date: datetime, is_tomorrow: bool = False) -> bool:
        """Convert schedule to speech and play it."""
        voice_message = self.format_voice_message(events, date, is_tomorrow)
        logger.info(f"Voice message: {voice_message}")
        
        audio_file = await self.synthesize_speech(voice_message)
        if audio_file:
            return self.play_audio(audio_file)
        return False
    
    def _format_time(self, time_data: Dict[str, Any]) -> str:
        """Format time data from Google Calendar API."""
        if 'dateTime' in time_data:
            # Parse datetime and convert to JST
            dt = datetime.fromisoformat(time_data['dateTime'].replace('Z', '+00:00'))
            dt_jst = dt.astimezone(self.tz)
            return dt_jst.strftime('%H:%M')
        elif 'date' in time_data:
            return '終日'
        else:
            return '時刻未定'
    
    def send_to_slack(self, message: str) -> bool:
        """Send message to Slack webhook."""
        try:
            payload = {
                'text': message,
                'username': 'Calendar Bot',
                'icon_emoji': ':calendar:'
            }
            
            response = requests.post(self.slack_webhook_url, json=payload)
            response.raise_for_status()
            
            logger.info("Message sent to Slack successfully")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send message to Slack: {e}")
            return False
    
    async def send_daily_schedule(self, date: datetime = None, include_tomorrow: bool = True, with_voice: bool = True) -> bool:
        """Main method to fetch events, send daily schedule to Slack, and optionally speak it."""
        try:
            if date is None:
                date = datetime.now(self.tz)
            
            # Ensure date is timezone-aware
            if date.tzinfo is None:
                date = self.tz.localize(date)
            
            # Get today's events
            today_events = self.get_daily_events(date)
            today_message = self.format_schedule_message(today_events, date, is_tomorrow=False)
            
            # Get tomorrow's events if requested
            message = today_message
            tomorrow_events = []
            if include_tomorrow:
                tomorrow = date + timedelta(days=1)
                # 明日が平日の場合のみ明日の予定を表示
                if self._is_business_day(tomorrow):
                    tomorrow_events = self.get_daily_events(tomorrow)
                    tomorrow_message = self.format_schedule_message(tomorrow_events, tomorrow, is_tomorrow=True)
                    message += "\n\n" + "="*30 + "\n\n" + tomorrow_message
            
            # Send to Slack
            slack_success = self.send_to_slack(message)
            
            # Speak the schedule if voice is enabled
            voice_success = True
            if with_voice:
                # Speak today's schedule
                today_voice_success = await self.speak_schedule(today_events, date, is_tomorrow=False)
                
                # Speak tomorrow's schedule if available
                tomorrow_voice_success = True
                if tomorrow_events and include_tomorrow:
                    tomorrow = date + timedelta(days=1)
                    tomorrow_voice_success = await self.speak_schedule(tomorrow_events, tomorrow, is_tomorrow=True)
                
                voice_success = today_voice_success and tomorrow_voice_success
            
            return slack_success and voice_success
            
        except Exception as e:
            logger.error(f"Error sending daily schedule: {e}")
            return False


async def main():
    """Main entry point."""
    try:
        logger.info("Starting Calendar Voice Bot...")
        bot = CalendarVoiceBot()
        
        # 現在の日付をJSTで取得
        now = datetime.now(bot.tz)
        
        # 平日判定（土日祝日をスキップ）
        if not bot._is_business_day(now):
            logger.info("今日は土日または祝日のため、配信をスキップします")
            return
        
        # Send today's schedule (and tomorrow's if available) with voice
        success = await bot.send_daily_schedule(include_tomorrow=True, with_voice=True)
        
        if success:
            logger.info("Daily schedule sent successfully to Slack and spoken")
        else:
            logger.error("Failed to send daily schedule or speak it")
            exit(1)
            
    except Exception as e:
        logger.error(f"Application error: {e}")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())