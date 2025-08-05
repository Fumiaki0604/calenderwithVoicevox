#!/usr/bin/env python3
"""
Slack Voice Monitor
Monitor Slack messages from Calendar Bot and read them aloud using VOICEVOX API.
"""

import os
import re
import time
import logging
import requests
import tempfile
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SlackVoiceMonitor:
    def __init__(self):
        # Slack API settings
        self.slack_token = os.getenv('SLACK_BOT_TOKEN')
        self.target_channel = os.getenv('SLACK_CHANNEL_ID', 'general')
        
        # VOICEVOX API settings
        self.voicevox_api_key = os.getenv('VOICEVOX_API_KEY')
        self.voicevox_speaker_id = int(os.getenv('VOICEVOX_SPEAKER_ID', '3'))
        self.voicevox_api_url = 'https://api.tts.quest/v3/voicevox/synthesis'
        
        if not all([self.slack_token, self.voicevox_api_key]):
            logger.warning("Missing SLACK_BOT_TOKEN or VOICEVOX_API_KEY - some features may not work")
        
        self.last_processed_ts = None
        
        # Initialize audio (try to import pygame)
        self.audio_available = False
        try:
            import pygame
            pygame.mixer.init()
            self.audio_available = True
            logger.info("Audio playback initialized successfully")
        except ImportError:
            logger.warning("pygame not available - audio playback disabled")
    
    def get_recent_messages(self, limit=10):
        """Get recent messages from Slack channel."""
        if not self.slack_token:
            logger.error("SLACK_BOT_TOKEN not set")
            return []
        
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
                logger.error(f"Slack API error: {data.get('error', 'Unknown error')}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching messages: {e}")
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
        
        # Extract key information
        lines = slack_text.split('\n')
        voice_parts = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Title line
            if '予定 -' in line:
                date_match = re.search(r'(\d+年\d+月\d+日)', line)
                day_match = re.search(r'(今日|明日)', line)
                if date_match and day_match:
                    voice_parts.append(f"{day_match.group(1)}の予定をお知らせします。")
            
            # Event lines (numbered items)
            elif re.match(r'^\d+\.', line):
                event_name = re.sub(r'^\d+\.\s*', '', line)
                voice_parts.append(f"{event_name}。")
            
            # Time lines
            elif '🕐' in line:
                time_text = re.sub(r'🕐\s*', '', line)
                time_text = re.sub(r'〜', 'から', time_text)
                voice_parts.append(f"時間は{time_text}です。")
            
            # Summary line
            elif '合計' in line and '件の予定' in line:
                count_match = re.search(r'(\d+)\s*件', line)
                if count_match:
                    count = count_match.group(1)
                    voice_parts.append(f"以上、{count}件の予定でした。")
        
        # Fallback: if no structured content found, clean the whole text
        if not voice_parts:
            cleaned = re.sub(r'[📅🕐📍📝✨📊\*]', '', slack_text)
            cleaned = re.sub(r'\n+', '。', cleaned)
            return cleaned.strip()
        
        return ''.join(voice_parts)
    
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
                logger.error(f"VOICEVOX API error: {response.status_code}")
                return None
            
            result = response.json()
            mp3_url = result.get('mp3DownloadUrl')
            
            if not mp3_url:
                logger.error("No MP3 download URL in response")
                return None
            
            # Download audio file
            audio_response = requests.get(mp3_url)
            if audio_response.status_code != 200:
                logger.error(f"Failed to download audio: {audio_response.status_code}")
                return None
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            temp_file.write(audio_response.content)
            temp_file.close()
            
            logger.info(f"Audio file created: {temp_file.name}")
            return temp_file.name
            
        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}")
            return None
    
    def play_audio(self, audio_file_path):
        """Play audio file."""
        if not self.audio_available:
            logger.warning("Audio playback not available")
            return False
        
        try:
            import pygame
            pygame.mixer.music.load(audio_file_path)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
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
    
    def process_message(self, message):
        """Process a single calendar message."""
        text = message.get('text', '')
        timestamp = message.get('ts', '')
        
        logger.info(f"Processing calendar message: {text[:100]}...")
        
        # Extract voice content
        voice_text = self.extract_voice_content(text)
        if not voice_text:
            logger.warning("No voice content extracted")
            return False
        
        logger.info(f"Voice text: {voice_text}")
        
        # Synthesize and play
        audio_file = self.synthesize_speech(voice_text)
        if audio_file:
            success = self.play_audio(audio_file)
            if success:
                self.last_processed_ts = timestamp
                return True
        
        return False
    
    def monitor_once(self):
        """Check for new calendar messages once."""
        messages = self.get_recent_messages(limit=5)
        
        for message in messages:
            ts = message.get('ts', '')
            
            # Skip if already processed
            if self.last_processed_ts and ts <= self.last_processed_ts:
                continue
            
            # Check if it's a calendar message
            if self.is_calendar_message(message):
                logger.info("New calendar message detected!")
                if self.process_message(message):
                    logger.info("Message processed successfully")
                    return True
                else:
                    logger.error("Failed to process message")
        
        return False
    
    def run_continuous(self, interval=30):
        """Run continuous monitoring."""
        logger.info(f"Starting continuous monitoring (interval: {interval}s)")
        
        while True:
            try:
                self.monitor_once()
                time.sleep(interval)
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(interval)


def main():
    """Main entry point."""
    try:
        monitor = SlackVoiceMonitor()
        
        # Test mode: check once
        if os.getenv('TEST_MODE', '').lower() == 'true':
            logger.info("Running in test mode")
            monitor.monitor_once()
        else:
            # Continuous monitoring
            monitor.run_continuous()
            
    except Exception as e:
        logger.error(f"Application error: {e}")


if __name__ == "__main__":
    main()