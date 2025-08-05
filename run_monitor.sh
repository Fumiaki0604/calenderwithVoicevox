#!/bin/bash
# Calendar Voice Bot - 監視モード (macOS/Linux用)
# 常時起動して音声読み上げを実行

echo "[$(date)] Calendar Voice Monitor 起動中..."

# スクリプトのディレクトリに移動
cd "$(dirname "$0")"

# 仮想環境を有効化
source venv/bin/activate

# 監視モード開始
echo "[$(date)] Slack監視モード開始..."
echo "新しいカレンダーメッセージを検出すると音声で読み上げます"
echo "停止するには Ctrl+C を押してください"
echo

python slack_voice_monitor.py

echo "[$(date)] 監視モード終了"