#!/usr/bin/env python3
"""
Calendar Voice Bot セットアップスクリプト
PC環境での初期設定を自動化
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Python バージョン確認"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8以上が必要です")
        print(f"   現在のバージョン: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} 確認")
    return True

def create_virtual_environment():
    """仮想環境作成"""
    if os.path.exists('venv'):
        print("✅ 仮想環境 'venv' は既に存在します")
        return True
    
    print("📦 仮想環境を作成中...")
    try:
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        print("✅ 仮想環境 'venv' を作成しました")
        return True
    except subprocess.CalledProcessError:
        print("❌ 仮想環境の作成に失敗しました")
        return False

def install_dependencies():
    """依存関係インストール"""
    print("📚 依存関係をインストール中...")
    
    # プラットフォーム別のPythonパス
    if platform.system() == "Windows":
        python_path = os.path.join('venv', 'Scripts', 'python.exe')
        pip_path = os.path.join('venv', 'Scripts', 'pip.exe')
    else:
        python_path = os.path.join('venv', 'bin', 'python')
        pip_path = os.path.join('venv', 'bin', 'pip')
    
    try:
        # pip アップグレード
        subprocess.run([python_path, '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)
        
        # requirements.txt からインストール
        subprocess.run([pip_path, 'install', '-r', 'requirements.txt'], check=True)
        print("✅ 依存関係のインストール完了")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依存関係のインストールに失敗: {e}")
        return False

def check_env_file():
    """環境変数ファイル確認"""
    if not os.path.exists('.env'):
        print("⚠️  .env ファイルが見つかりません")
        print("   .env.example をコピーして .env を作成し、認証情報を設定してください")
        return False
    
    print("✅ .env ファイル確認")
    
    # 必須環境変数をチェック
    required_vars = [
        'SLACK_BOT_TOKEN',
        'SLACK_CHANNEL_ID', 
        'GOOGLE_CREDENTIALS_JSON',
        'CALENDAR_ID',
        'VOICEVOX_API_KEY'
    ]
    
    missing_vars = []
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            content = f.read()
            
        for var in required_vars:
            if f"{var}=" not in content or f"{var}=your_" in content or f"{var}=xoxb-your" in content:
                missing_vars.append(var)
        
        if missing_vars:
            print("⚠️  以下の環境変数を設定してください:")
            for var in missing_vars:
                print(f"   - {var}")
            return False
        
        print("✅ 必須環境変数が設定されています")
        return True
        
    except Exception as e:
        print(f"❌ .env ファイルの読み取りエラー: {e}")
        return False

def run_test():
    """接続テスト実行"""
    print("🧪 接続テストを実行中...")
    
    # プラットフォーム別のPythonパス
    if platform.system() == "Windows":
        python_path = os.path.join('venv', 'Scripts', 'python.exe')
    else:
        python_path = os.path.join('venv', 'bin', 'python')
    
    try:
        result = subprocess.run([python_path, 'test_slack_setup.py'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ 接続テスト成功")
            return True
        else:
            print("❌ 接続テスト失敗")
            print("エラー出力:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️  接続テストがタイムアウトしました")
        return False
    except FileNotFoundError:
        print("⚠️  test_slack_setup.py が見つかりません")
        return False

def show_next_steps():
    """次のステップを表示"""
    print("\n" + "="*60)
    print("🎉 セットアップ完了！")
    print("\n📝 次のステップ:")
    
    if platform.system() == "Windows":
        print("   1. 手動テスト:")
        print("      run_calendar.bat     # カレンダー投稿テスト")
        print("      run_monitor.bat      # 監視モードテスト")
        print("\n   2. 自動実行設定:")
        print("      - タスクスケジューラーで run_calendar.bat を毎朝8:00に実行")
        print("      - run_monitor.bat を常時起動")
    else:
        print("   1. 手動テスト:")
        print("      ./run_calendar.sh    # カレンダー投稿テスト")
        print("      ./run_monitor.sh     # 監視モードテスト")
        print("\n   2. 自動実行設定:")
        print("      crontab -e")
        print("      0 8 * * 1-5 /path/to/calendar-voice-bot/run_calendar.sh")
    
    print(f"\n🔊 音声設定:")
    print(f"   - スピーカー/ヘッドフォンが接続されていることを確認")
    print(f"   - 音量を適切に調整")
    
    print(f"\n📚 詳細な設定方法:")
    print(f"   setup_pc.md を参照してください")

def main():
    """メインセットアップ"""
    print("🚀 Calendar Voice Bot セットアップ")
    print("="*60)
    
    # Step 1: Python バージョン確認
    if not check_python_version():
        return False
    
    # Step 2: 仮想環境作成
    if not create_virtual_environment():
        return False
    
    # Step 3: 依存関係インストール
    if not install_dependencies():
        return False
    
    # Step 4: 環境変数確認
    env_ok = check_env_file()
    
    # Step 5: 接続テスト（環境変数OKの場合のみ）
    test_ok = False
    if env_ok:
        test_ok = run_test()
    
    # Step 6: 次のステップを表示
    show_next_steps()
    
    return env_ok and test_ok

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎊 すべてのセットアップが完了しました！")
    else:
        print("\n⚠️  セットアップで問題が発生しました")
        print("   setup_pc.md を確認してトラブルシューティングしてください")