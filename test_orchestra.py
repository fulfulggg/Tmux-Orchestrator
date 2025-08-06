#!/usr/bin/env python3
"""
TmuxOrchestra機能を検証するテストスクリプト
"""

import os
import sys
import subprocess

# 現在のディレクトリをPythonパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tmuxorchestra import TmuxOrchestra, AgentRole


def test_imports():
    """すべてのモジュールをインポートできることをテスト"""
    print("インポートをテスト中...")
    try:
        import tmuxorchestra
        import orchestra_dashboard
        print("✓ すべてのモジュールが正常にインポートされました")
        return True
    except ImportError as e:
        print(f"✗ インポートエラー: {e}")
        return False


def test_tmux_available():
    """tmuxが利用可能であることをテスト"""
    print("\ntmuxの可用性をテスト中...")
    try:
        result = subprocess.run(['tmux', '-V'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ tmuxが利用可能です: {result.stdout.strip()}")
            return True
        else:
            print("✗ tmuxが見つかりません")
            return False
    except Exception as e:
        print(f"✗ tmuxのチェックエラー: {e}")
        return False


def test_orchestra_creation():
    """TmuxOrchestraインスタンスの作成をテスト"""
    print("\nTmuxOrchestraの作成をテスト中...")
    try:
        orchestra = TmuxOrchestra()
        print("✓ TmuxOrchestraインスタンスが作成されました")
        
        # セッションのリストをテスト
        sessions = orchestra.list_sessions()
        print(f"✓ {len(sessions)}個のtmuxセッションが見つかりました")
        
        return True
    except Exception as e:
        print(f"✗ オーケストラ作成エラー: {e}")
        return False


def test_script_permissions():
    """スクリプトが実行可能であることをテスト"""
    print("\nスクリプトの権限をテスト中...")
    scripts = [
        'tmuxorchestra.py',
        'orchestra_dashboard.py',
        'orchestra_utils.sh',
        'schedule_with_note.sh'
    ]
    
    all_good = True
    for script in scripts:
        if os.path.exists(script):
            if os.access(script, os.X_OK):
                print(f"✓ {script} は実行可能です")
            else:
                print(f"✗ {script} は実行可能ではありません")
                all_good = False
        else:
            print(f"✗ {script} が見つかりません")
            all_good = False
    
    return all_good


def test_registry_structure():
    """レジストリディレクトリ構造をテスト"""
    print("\nレジストリ構造をテスト中...")
    registry_path = os.path.expanduser("~/Coding/Tmux orchestrator/registry")
    
    dirs_to_check = [
        registry_path,
        os.path.join(registry_path, "logs"),
        os.path.join(registry_path, "notes")
    ]
    
    all_good = True
    for dir_path in dirs_to_check:
        if os.path.exists(dir_path):
            print(f"✓ {dir_path} が存在します")
        else:
            print(f"✗ {dir_path} がありません")
            all_good = False
    
    return all_good


def main():
    """すべてのテストを実行"""
    print("🎭 TmuxOrchestra テストスイート\n")
    
    tests = [
        test_imports,
        test_tmux_available,
        test_orchestra_creation,
        test_script_permissions,
        test_registry_structure
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "="*50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ すべてのテストが成功しました！ ({passed}/{total})")
        print("\nTmuxOrchestraを使用する準備ができました！")
        print("\n次の手順:")
        print("1. チームを展開: python3 tmuxorchestra.py deploy --project myapp --path ~/Coding/myapp")
        print("2. ダッシュボードを起動: python3 orchestra_dashboard.py")
        print("3. ステータスを確認: python3 tmuxorchestra.py status")
    else:
        print(f"❌ いくつかのテストが失敗しました ({passed}/{total})")
        print("\nTmuxOrchestraを使用する前に上記の問題を修正してください")


if __name__ == "__main__":
    main()
