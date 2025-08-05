# 📦 PC移行ガイド

## 🎯 必要なファイル一覧

以下のファイルをPCにコピーしてください：

### 📁 **メインファイル**
```
calendar-voice-bot/
├── main.py                    # カレンダー投稿メインスクリプト
├── slack_voice_monitor.py     # Slack監視・音声再生スクリプト
├── requirements.txt           # Python依存関係
├── .env                      # 環境変数設定（重要！）
├── setup.py                  # PC環境自動セットアップ
├── README.md                 # プロジェクト説明
└── setup_pc.md              # PC環境詳細セットアップガイド
```

### 🖥️ **実行用スクリプト**
```
├── run_calendar.bat          # Windows用：カレンダー投稿
├── run_monitor.bat           # Windows用：監視モード
├── run_calendar.sh           # macOS/Linux用：カレンダー投稿  
└── run_monitor.sh            # macOS/Linux用：監視モード
```

### 🧪 **テスト用ファイル（オプション）**
```
├── test_slack_setup.py       # Slack接続テスト
├── check_permissions.py      # 権限確認
├── final_test_nosound.py     # 完全フローテスト
└── test_voice_only.py        # 音声合成テスト
```

## 📋 移行方法

### 方法1: 個別ファイルコピー（推奨）

1. **PCに新しいフォルダを作成**
   ```
   C:\calendar-voice-bot\        (Windows)
   /Users/user/calendar-voice-bot/  (macOS)
   /home/user/calendar-voice-bot/   (Linux)
   ```

2. **上記リストのファイルを1つずつコピー**
   - 各ファイルをテキストエディタで開く  
   - 内容をコピー
   - PCの対応するファイルに貼り付け

### 方法2: GitHub経由

1. **GitHubリポジトリ作成**
2. **ファイルをアップロード**
3. **PCでクローン**

## 🔧 PC側でのセットアップ手順

### 1. Python 3.8+ インストール確認
```bash
python --version
# または
python3 --version
```

### 2. 自動セットアップ実行
```bash
cd calendar-voice-bot
python setup.py
```

### 3. 接続テスト
```bash
python test_slack_setup.py
```

### 4. 手動テスト
```bash
# Windows
run_calendar.bat
run_monitor.bat

# macOS/Linux
./run_calendar.sh
./run_monitor.sh
```

## ⚠️ 重要な注意点

### .env ファイルの確認
以下の認証情報が正しく設定されていることを確認：

```bash
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_CHANNEL_ID=D098WFXBEHH
GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}
CALENDAR_ID=f_sato@atoj.co.jp
VOICEVOX_API_KEY=p-s205e-L706841
VOICEVOX_SPEAKER_ID=3
```

### 音声出力の確認
- スピーカー/ヘッドフォンが接続されている
- 音量が適切に設定されている
- 既定の音声出力デバイスが正しい

## 🎯 移行後の動作確認

1. **setup.py** で環境セットアップ
2. **test_slack_setup.py** で接続確認  
3. **run_calendar** でカレンダー投稿テスト
4. **run_monitor** で音声再生テスト

## 🆘 トラブルシューティング

### よくある問題
- **Python バージョンエラー**: Python 3.8以上をインストール
- **pip エラー**: `python -m pip install --upgrade pip`
- **権限エラー**: 管理者として実行
- **音声エラー**: 音声デバイス設定を確認

### サポートファイル
- `setup_pc.md`: 詳細セットアップガイド
- `check_permissions.py`: Slack権限確認
- `test_voice_only.py`: 音声合成テスト

## 🎊 移行完了後

自動実行設定：
- **Windows**: タスクスケジューラーで毎朝8:00に `run_calendar.bat` 実行
- **macOS/Linux**: crontab で毎朝8:00に `run_calendar.sh` 実行
- **監視モード**: `run_monitor` を常時起動

これで朝起きると「今日の予定をお知らせします...」と音声で聞こえるようになります！