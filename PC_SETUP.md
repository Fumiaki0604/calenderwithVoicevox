# PC環境セットアップ手順

## 1. リポジトリのクローン
```bash
git clone https://github.com/Fumiaki0604/calenderwithVoicevox.git
cd calenderwithVoicevox
```

## 2. Python仮想環境のセットアップ
```bash
python setup.py
```

## 3. .envファイルの作成

**最も簡単な方法：**

1. `create_pc_env.py` ファイルをテキストエディターで開く
2. 【】で囲まれた部分を実際の認証情報に置き換える
3. ターミナルで以下のコマンドを実行：

```bash
python create_pc_env.py
```

これで.envファイルが自動生成されます！

**手動で作成する場合（上級者向け）：**
必要に応じて、以下のPythonコードをターミナルのPythonインタープリターまたは.pyファイルとして実行することも可能です：

```python
import json
credentials = {"type": "service_account", "project_id": "YOUR_PROJECT_ID", ...}
# 以下省略
```

## 4. アプリケーションの実行

### 手動実行（テスト用）
```bash
run_calendar.bat
```

### スケジュール実行（毎朝8:00）
Windowsタスクスケジューラーで`run_calendar.bat`を設定

## 重要な修正点

- ✅ JSON形式の認証情報が正しくエスケープされるようになりました
- ✅ Google Calendar API接続エラーが解決されています  
- ✅ PC環境では音声出力が正常に動作します

## トラブルシューティング

### JSON parsing error が発生する場合
上記のPythonコードを使用して.envファイルを再生成してください。`json.dumps()`を使用することで、適切なエスケープが保証されます。

### 音声が再生されない場合
- PC環境で実行していることを確認
- 音量設定を確認
- スピーカー/ヘッドフォンの接続を確認

### Google Calendar API エラーの場合
- Service Account の認証情報が正しく設定されていることを確認
- Google Cloud Console でCalendar APIが有効になっていることを確認