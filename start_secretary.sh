#!/bin/bash

# AI秘書システム起動スクリプト
# Tmux Orchestra用の智能秘書システムを起動します

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SECRETARY_VENV="$HOME/.secretary_venv"

echo "🤖 AI秘書システムを起動しています..."

# 仮想環境の確認・作成
if [ ! -d "$SECRETARY_VENV" ]; then
    echo "📦 Python仮想環境を作成中..."
    python3 -m venv "$SECRETARY_VENV"
fi

# 仮想環境の有効化
source "$SECRETARY_VENV/bin/activate"

# 必要なパッケージのインストール
echo "📚 必要なパッケージをインストール中..."
pip install -q --upgrade pip
pip install -q flask requests

# 秘書システムのディレクトリ準備
SECRETARY_DATA="$HOME/Coding/Tmux orchestrator/secretary"
mkdir -p "$SECRETARY_DATA"/{tasks,meetings,reports}

echo "✅ 環境準備完了"

# 使用方法を表示
cat << EOF

🤖 AI秘書システム使用方法:

1. 秘書サービスを開始:
   python3 $SCRIPT_DIR/ai_secretary.py start

2. GitHub イシューを同期:
   python3 $SCRIPT_DIR/ai_secretary.py sync --repo owner/repository --github-token YOUR_TOKEN

3. タスクをエージェントに割り当て:
   python3 $SCRIPT_DIR/ai_secretary.py assign --task-id task-123 --agent session:0

4. 日報を生成:
   python3 $SCRIPT_DIR/ai_secretary.py report --session your-project

5. Web UIを起動:
   python3 $SCRIPT_DIR/secretary_ui.py

Web UIは http://localhost:5555 でアクセス可能です。

📋 主な機能:
- GitHub イシューの自動同期とタスク化
- エージェントへの自動タスク割り当て
- 定期的なスタンドアップミーティング
- 日報・週報の自動生成
- リアルタイムのエージェント監視
- Web ダッシュボードでの可視化

🔧 設定:
- GitHub Token: 環境変数 GITHUB_TOKEN または --github-token オプション
- データ保存場所: ~/Coding/Tmux orchestrator/secretary/

💡 Tips:
- tmux セッションが起動している状態で秘書を開始してください
- GitHub Token は repo スコープの権限が必要です
- 秘書サービスは5分間隔で自動実行されます

EOF

# オプション: GitHub Token の設定確認
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  GitHub Token が設定されていません"
    echo "   以下のコマンドで設定できます："
    echo "   export GITHUB_TOKEN=your_github_token"
    echo ""
fi

# オプション: Web UIを自動起動
read -p "Web UI を起動しますか? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Web UI を起動中..."
    python3 "$SCRIPT_DIR/secretary_ui.py" &
    WEB_PID=$!
    
    sleep 3
    echo "✅ Web UI が起動しました: http://localhost:5555"
    echo "   停止するには: kill $WEB_PID"
    
    # ブラウザで開く (macOS)
    if command -v open >/dev/null 2>&1; then
        open "http://localhost:5555"
    fi
fi

echo ""
echo "🎉 AI秘書システムの準備が完了しました！"