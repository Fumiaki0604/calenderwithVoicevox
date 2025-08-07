# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Japanese calendar voice bot that integrates Google Calendar, Slack, and VOICEVOX API to provide automated daily schedule notifications with text-to-speech functionality.

**Key Features:**
- Fetches daily Google Calendar events using Service Account authentication
- Posts formatted schedule messages to Slack via webhooks
- Converts schedule text to speech using VOICEVOX API (ずんだもん voice)
- Automatically skips weekends and Japanese holidays
- Filters out declined calendar events
- Supports both one-time execution and continuous monitoring modes

## Architecture

### Core Components

**main.py** - Primary calendar bot (`CalendarVoiceBot` class)
- Google Calendar API integration with service account authentication
- Slack webhook posting with formatted messages
- VOICEVOX API integration for speech synthesis
- Business day detection (excludes weekends/holidays using `jpholiday`)
- Event filtering logic for declined invitations

**slack_voice_monitor.py** - Slack monitoring service (`SlackVoiceMonitor` class)
- Monitors Slack channels for calendar bot messages
- Extracts voice-friendly content from formatted Slack messages
- Continuous monitoring mode with configurable intervals
- Audio playback using pygame

### Key Dependencies
- `google-api-python-client` - Google Calendar API access
- `google-auth*` - Service account authentication
- `requests` - HTTP requests for Slack/VOICEVOX APIs
- `pygame` - Audio playback functionality
- `jpholiday` - Japanese holiday detection
- `aiohttp` - Async HTTP requests for VOICEVOX
- `pytz` - Timezone handling (Asia/Tokyo)

## Common Development Commands

### Environment Setup
```bash
# Automated setup (recommended)
python setup.py

# Manual setup
python -m venv venv
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### Configuration
```bash
# Copy and edit environment variables
cp .env.example .env
# Edit .env with actual API credentials
```

**Required Environment Variables:**
- `SLACK_WEBHOOK_URL` - Slack webhook for posting messages
- `SLACK_BOT_TOKEN` - Bot token for reading channel messages
- `SLACK_CHANNEL_ID` - Target channel for monitoring
- `GOOGLE_CREDENTIALS_JSON` - Service account JSON (as string)
- `CALENDAR_ID` - Google Calendar ID
- `VOICEVOX_API_KEY` - VOICEVOX API authentication
- `VOICEVOX_SPEAKER_ID` - Voice character ID (default: 3 for ずんだもん)
- `TIMEZONE` - Timezone setting (default: Asia/Tokyo)

### Execution Commands

**Direct Python execution:**
```bash
# One-time calendar posting with voice
python main.py

# Start continuous Slack monitoring
python slack_voice_monitor.py

# Test mode monitoring
TEST_MODE=true python slack_voice_monitor.py
```

**Platform-specific wrapper scripts:**
```bash
# Linux/macOS
./run_calendar.sh    # Daily schedule posting
./run_monitor.sh     # Continuous monitoring

# Windows
run_calendar.bat     # Daily schedule posting
run_monitor.bat      # Continuous monitoring
```

### Testing
```bash
# Available test files (run individually)
python test_calendar.py           # Calendar integration test
python test_calendar_nosound.py   # Calendar test without audio
python test_slack_setup.py        # Slack API connection test
python test_main_nosound.py       # Main functionality without audio
python test_monitor_nosound.py    # Monitor functionality without audio
python test_voice_only.py         # VOICEVOX API test only
python test_unified_dm.py         # DM functionality test
```

## Development Notes

### Authentication Architecture
- **Google Calendar**: Uses Service Account authentication (JSON credentials)
- **Slack**: Dual authentication - webhooks for posting, bot tokens for reading
- **VOICEVOX**: API key-based authentication with rate limiting handling

### Scheduling and Automation
- Designed for cron/task scheduler execution (weekdays 8:00 AM JST)
- Business day logic filters Saturday/Sunday/Japanese holidays
- Supports both manual execution and automated scheduling

### Audio System
- Uses pygame mixer for cross-platform audio playback
- VOICEVOX API provides Japanese TTS with character voices
- Handles temporary file creation/cleanup for audio streams
- Graceful fallback when audio hardware unavailable

### Error Handling
- Comprehensive logging throughout all components  
- Graceful degradation for API failures
- Placeholder content for calendar API errors
- Rate limiting awareness for VOICEVOX API

### Code Conventions
- Async/await patterns for VOICEVOX integration
- Japanese comments and messages throughout
- Timezone-aware datetime handling
- Service-oriented class design with dependency injection

## Platform Support
- Cross-platform Python 3.8+ compatibility
- Platform-specific execution scripts (`.sh`/`.bat`)
- Virtual environment isolation
- Audio hardware detection and graceful fallbacks