@echo off
REM Calendar Voice Bot - 監視モード (Windows用)
REM 常時起動して音声読み上げを実行

echo [%date% %time%] Calendar Voice Monitor 起動中...

REM 作業ディレクトリに移動
cd /d "%~dp0"

REM 仮想環境を有効化
call venv\Scripts\activate

REM 監視モード開始
echo [%date% %time%] Slack監視モード開始...
echo 新しいカレンダーメッセージを検出すると音声で読み上げます
echo 停止するには Ctrl+C を押してください
echo.

python slack_voice_monitor.py

echo [%date% %time%] 監視モード終了