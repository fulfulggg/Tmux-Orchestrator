![Orchestrator Hero](/Orchestrator.png)

**Run AI agents 24/7 while you sleep** - The Tmux Orchestrator enables Claude agents to work autonomously, schedule their own check-ins, and coordinate across multiple projects without human intervention.

## 🤖 Key Capabilities & Autonomous Features

- **Self-trigger** - Agents schedule their own check-ins and continue work autonomously
- **Coordinate** - Project managers assign tasks to engineers across multiple codebases  
- **Persist** - Work continues even when you close your laptop
- **Scale** - Run multiple teams working on different projects simultaneously

## 🏗️ Architecture

The Tmux Orchestrator uses a three-tier hierarchy to overcome context window limitations:

```
┌─────────────┐
│ Orchestrator│ ← You interact here
└──────┬──────┘
       │ Monitors & coordinates
       ▼
┌─────────────┐     ┌─────────────┐
│  Project    │     │  Project    │
│  Manager 1  │     │  Manager 2  │ ← Assign tasks, enforce specs
└──────┬──────┘     └──────┬──────┘
       │                   │
       ▼                   ▼
┌─────────────┐     ┌─────────────┐
│ Engineer 1  │     │ Engineer 2  │ ← Write code, fix bugs
└─────────────┘     └─────────────┘
```

### Why Separate Agents?
- **Limited context windows** - Each agent stays focused on its role
- **Specialized expertise** - PMs manage, engineers code
- **Parallel work** - Multiple engineers can work simultaneously
- **Better memory** - Smaller contexts mean better recall

## 📸 Examples in Action

### Project Manager Coordination
![Initiate Project Manager](Examples/Initiate%20Project%20Manager.png)
*The orchestrator creating and briefing a new project manager agent*

### Status Reports & Monitoring
![Status Reports](Examples/Status%20reports.png)
*Real-time status updates from multiple agents working in parallel*

### Tmux Communication
![Reading TMUX Windows and Sending Messages](Examples/Reading%20TMUX%20Windows%20and%20Sending%20Messages.png)
*How agents communicate across tmux windows and sessions*

### Project Completion
![Project Completed](Examples/Project%20Completed.png)
*Successful project completion with all tasks verified and committed*

## 🎯 Quick Start

### 🚀 TmuxOrchestra クイックスタートガイド

#### 1️⃣ 初期セットアップ
```bash
# tmuxがインストールされているか確認
tmux -V

# プロジェクトディレクトリに移動
cd /workspace/Tmux-Orchestrator

# システムテスト実行
python3 test_orchestra.py
```

#### 2️⃣ プロジェクトにチームを展開

```bash
# 例: Webアプリプロジェクトに中規模チームを展開
python3 tmuxorchestra.py deploy --project my-webapp --path ~/Coding/my-webapp --team-size medium
```

**チームサイズオプション:**
- `small`: 開発者1名 + PM1名
- `medium`: 開発者2名 + PM1名 + QA1名
- `large`: 開発者3名 + PM1名 + QA1名 + DevOps1名 + レビュアー1名

#### 3️⃣ リアルタイム監視ダッシュボード

```bash
# インタラクティブダッシュボードを起動
python3 orchestra_dashboard.py
```

**ダッシュボード操作:**
- `↑/↓` - リスト内を移動
- `Enter` - 詳細表示
- `s` - ステータス更新要求
- `m` - メッセージ送信
- `b` - 戻る
- `h` - ヘルプ
- `q` - 終了

#### 4️⃣ エージェントとの対話

```bash
# メッセージ送信（形式: session:window "message"）
./send-claude-message.sh my-webapp:2 "プロジェクトの進捗を教えてください"
./send-claude-message.sh my-webapp:0 "ユーザー認証機能を実装してください"
./send-claude-message.sh my-webapp:3 "ログイン機能のテストを作成してください"
```

#### 5️⃣ 便利なユーティリティ

```bash
# 関数をロード
source orchestra_utils.sh

# よく使うコマンド
daily_standup my-webapp        # デイリースタンドアップ実行
git_commit_reminder            # 全開発者にコミットリマインダー
check_git_status my-webapp     # Gitステータス確認
create_pm existing-project     # 既存プロジェクトにPMを追加
```

### 📋 実践例：タスク管理アプリ開発

#### ステップ1: プロジェクト仕様作成
```bash
cat > ~/Coding/task-app/spec.md << 'EOF'
プロジェクト: タスク管理アプリ
目標: シンプルなタスク管理システムの構築

機能要件:
- タスクの作成/編集/削除
- カテゴリー分類
- 期限設定
- 進捗ステータス管理

技術要件:
- フロントエンド: React + TypeScript
- バックエンド: FastAPI
- データベース: PostgreSQL
- 認証: JWT
EOF
```

#### ステップ2: チーム展開
```bash
# プロジェクトディレクトリ作成
mkdir -p ~/Coding/task-app

# チーム展開（中規模）
python3 tmuxorchestra.py deploy --project task-app --path ~/Coding/task-app --team-size medium
```

#### ステップ3: PMに仕様を渡す
```bash
# PMに仕様を確認させてタスク割り当て
./send-claude-message.sh task-app:2 "spec.mdを確認して、チームにタスクを割り当ててください"
```

#### ステップ4: 進捗監視
```bash
# ダッシュボードで監視
python3 orchestra_dashboard.py

# または個別ステータス確認
python3 tmuxorchestra.py status --session task-app
```

#### ステップ5: 定期チェックイン設定
```bash
# 30分ごとのPMチェックイン
./schedule_with_note.sh 30 "進捗確認とブロッカー解決" "task-app:2"

# 60分ごとのコード品質チェック
./schedule_with_note.sh 60 "コードレビューとテストカバレッジ確認" "task-app:2"
```

### 🔧 tmux基本操作

```bash
# セッション操作
tmux ls                        # セッション一覧
tmux attach -t task-app        # セッションに接続
tmux detach                    # Ctrl+b d でセッションから離脱

# ウィンドウ操作（セッション内で）
Ctrl+b 0-9                     # ウィンドウ番号で切り替え
Ctrl+b n                       # 次のウィンドウ
Ctrl+b p                       # 前のウィンドウ
Ctrl+b w                       # ウィンドウ一覧

# コンテンツ確認
tmux capture-pane -t task-app:0 -p | tail -50  # 最近の50行を表示
```

### 🎯 よくある使用シナリオ

#### シナリオ1: 既存プロジェクトの継続
```bash
# 現在のセッションを確認
python3 tmuxorchestra.py list

# プロジェクトステータス確認
python3 tmuxorchestra.py status --session my-project

# PMに現状確認
./send-claude-message.sh my-project:2 "現在の優先事項を教えてください"
```

#### シナリオ2: 複数プロジェクトの並行管理
```bash
# フロントエンドチーム
python3 tmuxorchestra.py deploy --project frontend --path ~/Coding/frontend --team-size small

# バックエンドチーム
python3 tmuxorchestra.py deploy --project backend --path ~/Coding/backend --team-size medium

# 全体監視
python3 orchestra_dashboard.py
```

#### シナリオ3: 緊急バグ修正
```bash
# 緊急対応チーム作成
python3 tmuxorchestra.py deploy --project hotfix --path ~/Coding/app --team-size small

# 緊急ブリーフィング
./send-claude-message.sh hotfix:0 "緊急: 本番環境でログインエラーが発生。すぐに調査して修正してください"
./send-claude-message.sh hotfix:1 "開発者をサポートして、修正後すぐにテストを実行してください"
```

### 💡 プロのヒント

1. **エージェントの自律性を活用**
   - 細かい指示より、明確な目標を与える
   - エージェントに判断の余地を残す
   - 定期的なチェックインで方向性を確認

2. **効率的なコミュニケーション**
   ```bash
   # 全体ブロードキャスト
   source orchestra_utils.sh
   broadcast_to_session my-project "重要: 15時からデプロイ開始します"
   ```

3. **Git規律の維持**
   ```bash
   # 定期的なリマインダー設定（cron風）
   while true; do
     git_commit_reminder
     sleep 1800  # 30分ごと
   done &
   ```

4. **ログの活用**
   ```bash
   # エージェントの会話を保存
   tmux capture-pane -t my-project:0 -S - > ~/Coding/logs/agent0_$(date +%Y%m%d_%H%M%S).log
   ```

### 🚨 トラブルシューティング

**問題**: エージェントが応答しない
```bash
# エージェントの状態確認
tmux capture-pane -t session:window -p | tail -20

# エージェントを再起動
tmux send-keys -t session:window C-c  # 現在のコマンドを中断
tmux send-keys -t session:window "claude" Enter
```

**問題**: セッションが見つからない
```bash
# セッション一覧を更新
python3 tmuxorchestra.py list

# エージェントレジストリを確認
cat ~/Coding/Tmux\ orchestrator/registry/agents.json
```

## ✨ Key Features

### 🔄 Self-Scheduling Agents
Agents can schedule their own check-ins using:
```bash
./schedule_with_note.sh 30 "Continue dashboard implementation"
```

### 👥 Multi-Agent Coordination
- Project managers communicate with engineers
- Orchestrator monitors all project managers
- Cross-project knowledge sharing

### 💾 Automatic Git Backups
- Commits every 30 minutes of work
- Tags stable versions
- Creates feature branches for experiments

### 📊 Real-Time Monitoring
- See what every agent is doing
- Intervene when needed
- Review progress across all projects

## 📋 Best Practices

### Writing Effective Specifications

```markdown
PROJECT: E-commerce Checkout
GOAL: Implement multi-step checkout process

CONSTRAINTS:
- Use existing cart state management
- Follow current design system
- Maximum 3 API endpoints
- Commit after each step completion

DELIVERABLES:
1. Shipping address form with validation
2. Payment method selection (Stripe integration)
3. Order review and confirmation page
4. Success/failure handling

SUCCESS CRITERIA:
- All forms validate properly
- Payment processes without errors  
- Order data persists to database
- Emails send on completion
```

### Git Safety Rules

1. **Before Starting Any Task**
   ```bash
   git checkout -b feature/[task-name]
   git status  # Ensure clean state
   ```

2. **Every 30 Minutes**
   ```bash
   git add -A
   git commit -m "Progress: [what was accomplished]"
   ```

3. **When Task Completes**
   ```bash
   git tag stable-[feature]-[date]
   git checkout main
   git merge feature/[task-name]
   ```

## 🚨 Common Pitfalls & Solutions

| Pitfall | Consequence | Solution |
|---------|-------------|----------|
| Vague instructions | Agent drift, wasted compute | Write clear, specific specs |
| No git commits | Lost work, frustrated devs | Enforce 30-minute commit rule |
| Too many tasks | Context overload, confusion | One task per agent at a time |
| No specifications | Unpredictable results | Always start with written spec |
| Missing checkpoints | Agents stop working | Schedule regular check-ins |

## 🛠️ How It Works

### The Magic of Tmux
Tmux (terminal multiplexer) is the key enabler because:
- It persists terminal sessions even when disconnected
- Allows multiple windows/panes in one session
- Claude runs in the terminal, so it can control other Claude instances
- Commands can be sent programmatically to any window

### 🎭 TmuxOrchestra - 高度なオーケストレーション

新しいTmuxOrchestraシステムは、複数のClaudeエージェントを管理するための包括的なソリューションを提供します：

#### コアコンポーネント

1. **`tmuxorchestra.py`** - メインオーケストレーションエンジン
   ```bash
   # チームを展開
   python3 tmuxorchestra.py deploy --project myapp --path ~/Coding/myapp --team-size medium
   
   # ステータスを確認
   python3 tmuxorchestra.py status --session myapp
   
   # オーケストレーションループを開始
   python3 tmuxorchestra.py start
   ```

2. **`orchestra_dashboard.py`** - リアルタイム監視ダッシュボード
   ```bash
   # インタラクティブダッシュボードを起動
   python3 orchestra_dashboard.py
   ```
   - 全エージェントのライブステータス
   - セッションとエージェントのナビゲーション
   - エージェントへの直接メッセージ送信
   - キーボードショートカットでの迅速なアクション

3. **`orchestra_utils.sh`** - 便利なシェルユーティリティ
   ```bash
   source orchestra_utils.sh
   
   # プロジェクトを迅速に展開
   deploy_project "task-templates" medium
   
   # デイリースタンドアップを実行
   daily_standup my-project
   
   # Gitコミットリマインダーをブロードキャスト
   git_commit_reminder
   ```

#### 主な機能

- **自動エージェント展開**: ロール固有のブリーフィング付き
- **チームテンプレート**: 小規模/中規模/大規模の事前設定済みチーム
- **永続的な状態管理**: エージェントレジストリがセッション間で状態を維持
- **スマートな通信**: ハブアンドスポークモデルで通信過負荷を防止
- **品質保証**: プロジェクトマネージャーが高い基準を強制

#### エージェントロール

- **Orchestrator**: 高レベルの監視と調整
- **Project Manager**: 品質基準と進捗追跡
- **Developer**: 実装とコーディング
- **QA Engineer**: テストと検証
- **DevOps**: インフラとデプロイメント
- **Code Reviewer**: セキュリティとベストプラクティス
- **Researcher**: 技術評価
- **Documentation Writer**: 技術文書

### 💬 Simplified Agent Communication

We now use the `send-claude-message.sh` script for all agent communication:

```bash
# Send message to any Claude agent
./send-claude-message.sh session:window "Your message here"

# Examples:
./send-claude-message.sh frontend:0 "What's your progress on the login form?"
./send-claude-message.sh backend:1 "The API endpoint /api/users is returning 404"
./send-claude-message.sh project-manager:0 "Please coordinate with the QA team"
```

The script handles all timing complexities automatically, making agent communication reliable and consistent.

### Scheduling Check-ins
```bash
# Schedule with specific, actionable notes
./schedule_with_note.sh 30 "Review auth implementation, assign next task"
./schedule_with_note.sh 60 "Check test coverage, merge if passing"
./schedule_with_note.sh 120 "Full system check, rotate tasks if needed"
```

**Important**: The orchestrator needs to know which tmux window it's running in to schedule its own check-ins correctly. If scheduling isn't working, verify the orchestrator knows its current window with:
```bash
echo "Current window: $(tmux display-message -p "#{session_name}:#{window_index}")"
```

## 🎓 Advanced Usage

### Multi-Project Orchestration
```bash
# Start orchestrator
tmux new-session -s orchestrator

# Create project managers for each project
tmux new-window -n frontend-pm
tmux new-window -n backend-pm  
tmux new-window -n mobile-pm

# Each PM manages their own engineers
# Orchestrator coordinates between PMs
```

### Cross-Project Intelligence
The orchestrator can share insights between projects:
- "Frontend is using /api/v2/users, update backend accordingly"
- "Authentication is working in Project A, use same pattern in Project B"
- "Performance issue found in shared library, fix across all projects"

## 📚 Core Files

- `send-claude-message.sh` - Simplified agent communication script
- `schedule_with_note.sh` - Self-scheduling functionality
- `tmux_utils.py` - Tmux interaction utilities
- `CLAUDE.md` - Agent behavior instructions
- `LEARNINGS.md` - Accumulated knowledge base

## 🤝 Contributing & Optimization

The orchestrator evolves through community discoveries and optimizations. When contributing:

1. Document new tmux commands and patterns in CLAUDE.md
2. Share novel use cases and agent coordination strategies
3. Submit optimizations for claudes synchronization
4. Keep command reference up-to-date with latest findings
5. Test improvements across multiple sessions and scenarios

Key areas for enhancement:
- Agent communication patterns
- Cross-project coordination
- Novel automation workflows

## 📄 License

MIT License - Use freely but wisely. Remember: with great automation comes great responsibility.

---

*"The tools we build today will program themselves tomorrow"* - Alan Kay, 1971
