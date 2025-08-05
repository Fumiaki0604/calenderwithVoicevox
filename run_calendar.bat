@echo off
REM Calendar Voice Bot - カレンダー投稿スクリプト (Windows用)
REM 朝8:00に自動実行されるバッチファイル

echo [%date% %time%] Calendar Voice Bot 起動中...

REM 作業ディレクトリに移動
cd /d "%~dp0"

REM 仮想環境を有効化
call venv\Scripts\activate

REM カレンダー予定を投稿
echo [%date% %time%] カレンダー予定を投稿中...
python main.py

REM 結果を表示
if %ERRORLEVEL% EQU 0 (
    echo [%date% %time%] カレンダー投稿成功
) else (
    echo [%date% %time%] カレンダー投稿失敗 - エラーコード: %ERRORLEVEL%
)

REM ログに記録
echo [%date% %time%] Calendar Bot 実行完了 >> calendar_bot.log

pause