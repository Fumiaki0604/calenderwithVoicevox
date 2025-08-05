# PC環境セットアップガイド

## 📁 Step 1: プロジェクトファイルをPCに移行

### オプション A: GitHubを使用（推奨）
```bash
# 1. このディレクトリでGitリポジトリを初期化
git init
git add .
git config user.name "Your Name"
git config user.email "your.email@example.com"
git commit -m "Calendar Voice Bot initial commit"

# 2. GitHubでリポジトリ作成後
git remote add origin https://github.com/yourusername/calendar-voice-bot.git
git push -u origin main

# 3. PCでクローン
git clone https://github.com/yourusername/calendar-voice-bot.git
cd calendar-voice-bot
```

### オプション B: ファイル直接コピー
以下のファイルをPCにコピー：
```
calendar-voice-bot/
├── main.py                    # メインのカレンダー投稿スクリプト
├── slack_voice_monitor.py     # Slack監視・音声再生スクリプト
├── requirements.txt           # Python依存関係
├── .env                      # 環境変数（認証情報）
├── README.md                 # プロジェクト説明
└── test_files/               # テストファイル（オプション）
    ├── test_slack_setup.py
    ├── check_permissions.py
    └── final_test_nosound.py
```

## 🐍 Step 2: Python環境セットアップ

### Windows
```cmd
# Python 3.8+ インストール確認
python --version

# 仮想環境作成
python -m venv venv

# 仮想環境有効化
venv\Scripts\activate

# 依存関係インストール
pip install -r requirements.txt
```

### macOS
```bash
# Python 3.8+ インストール確認
python3 --version

# 仮想環境作成
python3 -m venv venv

# 仮想環境有効化
source venv/bin/activate

# 依存関係インストール
pip install -r requirements.txt
```

### Linux
```bash
# Python 3.8+ インストール確認
python3 --version

# 必要なパッケージをインストール
sudo apt update
sudo apt install python3-pip python3-venv

# 仮想環境作成
python3 -m venv venv

# 仮想環境有効化
source venv/bin/activate

# 依存関係インストール
pip install -r requirements.txt
```

## ⚙️ Step 3: 環境変数設定

`.env` ファイルが正しく設定されていることを確認：

```bash
# Slack Configuration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_CHANNEL_ID=D098WFXBEHH  # 佐藤さんのDM

# Google Calendar Configuration
GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}
CALENDAR_ID=f_sato@atoj.co.jp

# VOICEVOX API Configuration
VOICEVOX_API_KEY=your-api-key
VOICEVOX_SPEAKER_ID=3

# Timezone
TIMEZONE=Asia/Tokyo
```

## 🧪 Step 4: 動作テスト

### 接続テスト
```bash
# 仮想環境を有効化してから実行
python test_slack_setup.py
```

### 手動テスト
```bash
# カレンダー予定を投稿
python main.py

# 別のターミナルで監視開始
python slack_voice_monitor.py
```

## 🔄 Step 5: 自動実行設定

### Windows (タスクスケジューラー)

1. **タスクスケジューラー** を開く
2. **基本タスクの作成** をクリック
3. タスク設定：
   - 名前: `Calendar Voice Bot`
   - トリガー: 毎日 8:00 AM
   - 操作: プログラムの開始
   - プログラム: `C:\path\to\python.exe`
   - 引数: `C:\path\to\calendar-voice-bot\main.py`
   - 開始場所: `C:\path\to\calendar-voice-bot`

### macOS (crontab)

```bash
# crontab編集
crontab -e

# 以下を追加（平日8:00に実行）
0 8 * * 1-5 cd /path/to/calendar-voice-bot && /path/to/venv/bin/python main.py
```

### 監視モード常時起動

**Windows (サービス化)**
```cmd
# 監視モードを常時起動
python slack_voice_monitor.py
```

**macOS/Linux (systemd)**
```bash
# サービスファイル作成
sudo nano /etc/systemd/system/calendar-voice-monitor.service

# サービス内容
[Unit]
Description=Calendar Voice Monitor
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/calendar-voice-bot
Environment=PATH=/path/to/venv/bin
ExecStart=/path/to/venv/bin/python slack_voice_monitor.py
Restart=always

[Install]
WantedBy=multi-user.target

# サービス有効化
sudo systemctl enable calendar-voice-monitor
sudo systemctl start calendar-voice-monitor
```

## 🔊 Step 6: 音声設定確認

### Windows
- スピーカー/ヘッドフォンが接続されていることを確認
- 音量設定を確認
- Windowsサウンド設定で既定のデバイスを確認

### macOS
- システム環境設定 → サウンド → 出力
- 適切な出力デバイスを選択

### Linux
- PulseAudio または ALSA が正常に動作していることを確認
```bash
# 音声テスト
speaker-test -t wav -c 2
```

## 🚨 トラブルシューティング

### よくある問題と解決方法

1. **音声が再生されない**
   ```bash
   # pygame音声テスト
   python -c "import pygame; pygame.mixer.init(); print('音声初期化成功')"
   ```

2. **権限エラー**
   ```bash
   # 権限確認テスト
   python check_permissions.py
   ```

3. **カレンダーAPI接続エラー**
   - Google Service Account JSON の確認
   - Calendar API の有効化確認

4. **Slack接続エラー**
   - Bot Token の確認
   - チャンネル権限の確認

## 📝 実行ログ確認

### ログファイル出力設定
```python
# main.py や slack_voice_monitor.py に追加
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('calendar_bot.log'),
        logging.StreamHandler()
    ]
)
```

### 実行状況確認
```bash
# ログファイル確認
tail -f calendar_bot.log
```

## 🎯 完全自動化

最終的な自動実行構成：

1. **朝8:00**: `main.py` 自動実行（カレンダー投稿）
2. **常時監視**: `slack_voice_monitor.py` バックグラウンド実行
3. **音声再生**: 新しいカレンダーメッセージを検出して自動読み上げ

これで朝起きたときに、PCから「今日の予定をお知らせします...」と音声で聞こえるようになります！