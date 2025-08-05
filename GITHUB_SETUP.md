# 📤 GitHub リポジトリ作成とPC移行手順

## Step 1: GitHubでリポジトリ作成

1. **GitHub** にログイン: https://github.com
2. **右上の「+」** → **「New repository」** をクリック
3. リポジトリ設定：
   - **Repository name**: `calendar-voice-bot`
   - **Description**: `音声読み上げ機能付きカレンダー Slack ボット`
   - **Visibility**: `Private` (認証情報が含まれるため)
   - **Initialize this repository**: チェックを外す（既存コード）

4. **「Create repository」** をクリック

## Step 2: リモートリポジトリ追加・プッシュ

GitHubでリポジトリ作成後、以下のコマンドを実行：

```bash
# リモートリポジトリを追加
git remote add origin https://github.com/[YOUR_USERNAME]/calendar-voice-bot.git

# メインブランチに変更
git branch -M main

# GitHubにプッシュ
git push -u origin main
```

⚠️ **[YOUR_USERNAME]** を実際のGitHubユーザー名に置き換えてください

## Step 3: PC側でクローン

### Windows
```cmd
# 任意のフォルダで実行
git clone https://github.com/[YOUR_USERNAME]/calendar-voice-bot.git
cd calendar-voice-bot
```

### macOS/Linux
```bash
# 任意のフォルダで実行
git clone https://github.com/[YOUR_USERNAME]/calendar-voice-bot.git
cd calendar-voice-bot
```

## Step 4: PC環境セットアップ

```bash
# 自動セットアップ実行
python setup.py
```

これで以下が自動実行されます：
- ✅ Python 3.8+ バージョン確認
- ✅ 仮想環境作成
- ✅ 依存関係インストール
- ✅ 認証情報確認
- ✅ 接続テスト

## Step 5: 動作テスト

### Windows
```cmd
run_calendar.bat    # カレンダー投稿テスト
run_monitor.bat     # 音声監視テスト
```

### macOS/Linux
```bash
./run_calendar.sh   # カレンダー投稿テスト
./run_monitor.sh    # 音声監視テスト
```

## 🎯 セットアップ完了後の動作

1. **朝8:00自動実行**: カレンダー予定をSlack DMに投稿
2. **音声監視**: 新しいメッセージを検出して音声合成
3. **音声再生**: PCスピーカーから「今日の予定をお知らせします...」

## 🆘 トラブルシューティング

### Git認証エラーの場合
1. **Personal Access Token** を作成
2. GitHub Settings → Developer settings → Personal access tokens
3. 権限: `repo` (Full control of private repositories)
4. パスワードの代わりにトークンを使用

### クローンできない場合
```bash
# HTTPS URL確認
git remote -v

# SSH URL に変更（SSH鍵設定済みの場合）
git remote set-url origin git@github.com:[YOUR_USERNAME]/calendar-voice-bot.git
```

## 📋 含まれるファイル

- ✅ `main.py` - カレンダー投稿メイン
- ✅ `slack_voice_monitor.py` - 音声監視・再生
- ✅ `requirements.txt` - Python依存関係
- ✅ `.env` - 認証情報（重要！）
- ✅ `setup.py` - 自動セットアップ
- ✅ `run_*.bat/.sh` - 実行スクリプト
- ✅ 詳細ドキュメント各種

これでGitHub経由でのPC移行が完了します！