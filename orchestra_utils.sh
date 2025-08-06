#!/bin/bash
# Orchestra ユーティリティ関数 - 迅速な操作用

ORCHESTRA_DIR="/workspace/Tmux-Orchestrator"
SEND_MESSAGE_SCRIPT="$ORCHESTRA_DIR/send-claude-message.sh"

# プロジェクトを迅速に展開する関数
deploy_project() {
    local project_name=$1
    local team_size=${2:-medium}
    
    # ~/Codingでプロジェクトを探す
    local project_path=$(find ~/Coding -maxdepth 1 -type d -iname "*$project_name*" | head -1)
    
    if [ -z "$project_path" ]; then
        echo "エラー: ~/Codingに'$project_name'を含むプロジェクトが見つかりません"
        return 1
    fi
    
    echo "プロジェクトを発見: $project_path"
    echo "$team_size チームを展開中..."
    
    python3 "$ORCHESTRA_DIR/tmuxorchestra.py" deploy \
        --project "$(basename "$project_path")" \
        --path "$project_path" \
        --team-size "$team_size"
}

# セッション内のすべてのエージェントのステータスを取得する関数
get_session_status() {
    local session=$1
    python3 "$ORCHESTRA_DIR/tmuxorchestra.py" status --session "$session"
}

# セッション内のすべてのエージェントにメッセージをブロードキャストする関数
broadcast_to_session() {
    local session=$1
    local message=$2
    
    # セッション内のすべてのウィンドウを取得
    tmux list-windows -t "$session" -F "#{window_index}" | while read -r window; do
        echo "$session:$window に送信中"
        "$SEND_MESSAGE_SCRIPT" "$session:$window" "$message"
        sleep 1
    done
}

# デイリースタンドアップを実行する関数
daily_standup() {
    local session=$1
    local standup_message="デイリースタンドアップ: 1) 昨日完了したこと、2) 今日取り組むこと、3) ブロッカーがあれば教えてください"
    
    echo "$session のデイリースタンドアップを開始..."
    broadcast_to_session "$session" "$standup_message"
}

# すべてのプロジェクトウィンドウのgitステータスをチェックする関数
check_git_status() {
    local session=$1
    
    echo "$session のすべてのウィンドウのgitステータスをチェック中..."
    
    tmux list-windows -t "$session" -F "#{window_index}:#{window_name}" | while read -r window_info; do
        local window_idx=$(echo "$window_info" | cut -d: -f1)
        local window_name=$(echo "$window_info" | cut -d: -f2-)
        
        echo -e "\n--- ウィンドウ: $window_name ---"
        
        # gitステータスコマンドを送信
        tmux send-keys -t "$session:$window_idx" "git status --short" Enter
        sleep 1
        
        # 出力をキャプチャ
        tmux capture-pane -t "$session:$window_idx" -p | tail -20
    done
}

# すべての開発者にコミットを促す関数
git_commit_reminder() {
    local message="Gitリマインダー: 30分以上コミットせずに作業している場合は、今すぐ意味のあるメッセージで作業をコミットしてください！"
    
    # すべての開発者ウィンドウを検索
    tmux list-sessions -F "#{session_name}" | while read -r session; do
        tmux list-windows -t "$session" -F "#{window_index}:#{window_name}" | grep -i "dev\|claude" | while read -r window_info; do
            local window_idx=$(echo "$window_info" | cut -d: -f1)
            local target="$session:$window_idx"
            
            echo "$target にコミットリマインダーを送信中..."
            "$SEND_MESSAGE_SCRIPT" "$target" "$message"
        done
    done
}

# セッションのプロジェクトマネージャーを作成する関数
create_pm() {
    local session=$1
    
    # 最初のウィンドウからプロジェクトパスを取得
    local project_path=$(tmux display-message -t "$session:0" -p '#{pane_current_path}')
    
    # 利用可能な次のウィンドウインデックスを検索
    local last_window=$(tmux list-windows -t "$session" -F "#{window_index}" | tail -1)
    local new_window=$((last_window + 1))
    
    # PMウィンドウを作成
    tmux new-window -t "$session" -n "Project-Manager" -c "$project_path"
    
    # Claudeを起動
    tmux send-keys -t "$session:$new_window" "claude" Enter
    sleep 5
    
    # PMブリーフィングを送信
    "$SEND_MESSAGE_SCRIPT" "$session:$new_window" "あなたはこのプロジェクトのプロジェクトマネージャーです。あなたの責任：

1. **品質基準**: 非常に高い基準を維持する。ショートカットなし、妥協なし。
2. **検証**: すべてを徹底的にテストする。信頼するが検証する。
3. **チーム調整**: チームメンバー間のコミュニケーションを効率的に管理する。
4. **進捗追跡**: 速度を監視し、ブロッカーを特定し、オーケストレーターに報告する。
5. **リスク管理**: 問題になる前に潜在的な問題を特定する。

まず、プロジェクトと既存のチームメンバーを分析し、ウィンドウ0の開発者に自己紹介してください。"
    
    echo "プロジェクトマネージャーを $session:$new_window に作成しました"
}

# 引数がない場合は使用方法を表示
if [ $# -eq 0 ]; then
    echo "Orchestra ユーティリティ - 迅速なオーケストレーションコマンド"
    echo ""
    echo "使用方法:"
    echo "  source orchestra_utils.sh                    # シェルに関数をロード"
    echo ""
    echo "利用可能な関数:"
    echo "  deploy_project <名前> [チームサイズ]        # プロジェクトのチームを展開"
    echo "  get_session_status <セッション>             # すべてのエージェントのステータスを取得"
    echo "  broadcast_to_session <セッション> <メッセージ> # すべてのウィンドウにメッセージを送信"
    echo "  daily_standup <セッション>                  # デイリースタンドアップを開始"
    echo "  check_git_status <セッション>               # ウィンドウ全体のgitステータスをチェック"
    echo "  git_commit_reminder                         # すべての開発者にコミットを促す"
    echo "  create_pm <セッション>                      # セッションのPMを作成"
fi
