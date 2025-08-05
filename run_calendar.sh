#!/bin/bash
# Calendar Voice Bot - カレンダー投稿スクリプト (macOS/Linux用)
# 朝8:00に自動実行されるシェルスクリプト

echo "[$(date)] Calendar Voice Bot 起動中..."

# スクリプトのディレクトリに移動
cd "$(dirname "$0")"

# 仮想環境を有効化
source venv/bin/activate

# カレンダー予定を投稿
echo "[$(date)] カレンダー予定を投稿中..."
python main.py

# 結果を確認
if [ $? -eq 0 ]; then
    echo "[$(date)] カレンダー投稿成功"
else
    echo "[$(date)] カレンダー投稿失敗 - エラーコード: $?"
fi

# ログに記録
echo "[$(date)] Calendar Bot 実行完了" >> calendar_bot.log