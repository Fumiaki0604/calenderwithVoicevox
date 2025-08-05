#!/usr/bin/env python3
"""
音声合成のみテスト
"""

import os
import requests
import tempfile
from dotenv import load_dotenv

load_dotenv()

def clean_voice_text(text):
    """音声用テキストをクリーンアップ"""
    import re
    
    # Slackの絵文字記号を除去
    text = re.sub(r':[\w]+:', '', text)  # :date: :clock1: など
    
    # Markdown記号を除去
    text = re.sub(r'\*([^*]+)\*', r'\1', text)  # *bold* → bold
    
    # 絵文字を除去
    text = re.sub(r'📅|🕐|📍|📝|✨|📊', '', text)
    
    # 改行を句点に
    text = re.sub(r'\n+', '。', text)
    
    # 特殊文字を変換
    text = re.sub(r'〜', 'から', text)
    text = re.sub(r'・', '、', text)
    
    # 連続する句点を整理
    text = re.sub(r'。+', '。', text)
    
    # 先頭・末尾の空白を除去
    text = text.strip()
    
    # 長すぎる場合は短縮
    if len(text) > 150:
        text = text[:150] + '。'
    
    return text

def test_voice_synthesis(text):
    """音声合成テスト"""
    voicevox_api_key = os.getenv('VOICEVOX_API_KEY')
    voicevox_speaker_id = int(os.getenv('VOICEVOX_SPEAKER_ID', '3'))
    url = 'https://api.tts.quest/v3/voicevox/synthesis'
    
    print(f"🎵 音声合成テスト")
    print(f"📝 入力テキスト: '{text}'")
    print(f"🗣️  スピーカーID: {voicevox_speaker_id} (ずんだもん)")
    
    params = {
        'speaker': voicevox_speaker_id,
        'text': text
    }
    
    if voicevox_api_key:
        params['key'] = voicevox_api_key
    
    try:
        response = requests.post(url, data=params)
        print(f"📡 API response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ VOICEVOX API error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        result = response.json()
        mp3_url = result.get('mp3DownloadUrl')
        
        if not mp3_url:
            print("❌ No MP3 download URL in response")
            print(f"   Response: {result}")
            return False
        
        print(f"✅ 音声URL取得成功: {mp3_url}")
        
        # ダウンロードテスト
        audio_response = requests.get(mp3_url)
        if audio_response.status_code != 200:
            print(f"❌ Failed to download audio: {audio_response.status_code}")
            return False
        
        # 一時ファイルに保存
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
        temp_file.write(audio_response.content)
        temp_file.close()
        
        file_size = os.path.getsize(temp_file.name)
        print(f"✅ 音声ファイル生成成功!")
        print(f"   ファイルサイズ: {file_size:,} bytes")
        print(f"   ファイルパス: {temp_file.name}")
        print(f"🎵 実際のPC環境では、この音声が再生されます")
        
        # クリーンアップ
        os.unlink(temp_file.name)
        print(f"🗑️  一時ファイルを削除しました")
        
        return True
        
    except Exception as e:
        print(f"❌ 音声合成エラー: {e}")
        return False

def main():
    """各種テキストで音声合成テスト"""
    print("🧪 音声合成テストスイート")
    print("=" * 50)
    
    # テストケース1: シンプルなテキスト
    print("\n1️⃣ テストケース1: シンプルなテキスト")
    simple_text = "今日の予定をお知らせします。"
    success1 = test_voice_synthesis(simple_text)
    
    # テストケース2: カレンダー形式のテキスト（クリーンアップ前）
    print("\n2️⃣ テストケース2: 生のSlackメッセージ")
    raw_slack = ":date: *今日の予定 - 2025年08月05日 (Tuesday)*\n\n*1. （確定）RAFT様定例会*\n:clock1: 11:00 〜 12:00"
    print(f"📝 元テキスト: {raw_slack}")
    
    # クリーンアップ
    cleaned = clean_voice_text(raw_slack)
    print(f"🧹 クリーンアップ後: {cleaned}")
    success2 = test_voice_synthesis(cleaned)
    
    # テストケース3: より自然な音声用テキスト
    print("\n3️⃣ テストケース3: 自然な音声用テキスト")
    natural_text = "今日8月5日の予定をお知らせします。11時からRAFT様定例会です。以上1件の予定でした。"
    success3 = test_voice_synthesis(natural_text)
    
    # 結果まとめ
    print("\n" + "=" * 50)
    print("📊 テスト結果:")
    print(f"   シンプルテキスト: {'✅' if success1 else '❌'}")
    print(f"   Slackメッセージ: {'✅' if success2 else '❌'}")
    print(f"   自然音声テキスト: {'✅' if success3 else '❌'}")
    
    if all([success1, success2, success3]):
        print("\n🎉 すべての音声合成テスト成功！")
        print("💡 PC環境では実際に音声が再生されます")
    else:
        print("\n⚠️  一部のテストで問題があります")
        print("   VOICEVOX APIキーや設定を確認してください")

if __name__ == "__main__":
    main()