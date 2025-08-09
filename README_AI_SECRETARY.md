# AI秘書システム

Tmux Orchestra用の智能秘書システムです。複数のClaudeエージェントを効率的に管理し、プロジェクトの進行をサポートします。

## 🚀 クイックスタート

```bash
# 秘書システムを起動
./start_secretary.sh

# または個別に起動
python3 ai_secretary.py start
python3 secretary_ui.py  # Web UI
```

## 🎯 主な機能

### 1. タスク管理
- **GitHub連携**: イシューを自動的にタスクとして取り込み
- **優先度管理**: Critical、High、Medium、Lowの4段階
- **自動割り当て**: エージェントのワークロードを考慮した自動割り当て
- **進捗追跡**: タスクのステータス管理（未着手→進行中→完了）

### 2. エージェント管理
- **リアルタイム監視**: エージェントの活動状況を監視
- **ヘルスチェック**: 長時間応答のないエージェントを検出
- **メッセージ送信**: エージェントへの指示やステータス確認

### 3. レポーティング
- **日報生成**: 毎日17時に自動生成
- **チームステータス**: プロジェクト全体の進捗状況
- **活動履歴**: エージェントの作業履歴を記録

### 4. スケジューリング
- **定期スタンドアップ**: 朝9時に自動実施
- **リマインダー**: 期限が近いタスクの通知
- **自動チェック**: 5分間隔でシステム状態を確認

## 📊 Web Dashboard

http://localhost:5555 でアクセス可能なWebダッシュボード：

- **概要**: 統計情報とタスク状況の一覧
- **タスク管理**: タスクの作成、編集、割り当て
- **エージェント監視**: リアルタイムの活動状況
- **レポート**: 生成されたレポートの閲覧

## 💻 コマンドライン使用法

### 基本コマンド

```bash
# 秘書サービスを開始（常駐）
python3 ai_secretary.py start

# GitHub イシューを同期
python3 ai_secretary.py sync --repo owner/repository --github-token YOUR_TOKEN

# タスクをエージェントに割り当て
python3 ai_secretary.py assign --task-id gh-123 --agent project:0

# 日報を生成
python3 ai_secretary.py report --session project-name

# スタンドアップをスケジュール
python3 ai_secretary.py standup --session project-name
```

### API使用例

```bash
# タスク一覧を取得
curl http://localhost:5555/api/tasks

# 新しいタスクを作成
curl -X POST http://localhost:5555/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"新機能の実装","priority":"high","description":"ユーザー認証機能を追加"}'

# エージェントにメッセージを送信
curl -X POST http://localhost:5555/api/agents/project:0/message \
  -H "Content-Type: application/json" \
  -d '{"message":"進捗状況を教えてください"}'
```

## 🔧 設定

### 環境変数

```bash
# GitHub Token (repo スコープが必要)
export GITHUB_TOKEN=your_github_token

# データ保存ディレクトリ (デフォルト: ~/Coding/Tmux orchestrator/secretary)
export SECRETARY_DATA_PATH=/path/to/secretary/data
```

### GitHub Token の取得

1. GitHub Settings → Developer settings → Personal access tokens
2. "Generate new token" をクリック
3. `repo` スコープを選択
4. トークンを生成してコピー

## 📁 ディレクトリ構造

```
~/Coding/Tmux orchestrator/secretary/
├── tasks/           # タスクデータ
│   └── tasks.json
├── meetings/        # ミーティング記録
├── reports/         # 生成されたレポート
│   ├── daily-2024-01-15.md
│   └── daily-2024-01-15-project.md
└── logs/           # システムログ
```

## 🔄 ワークフロー例

### 新プロジェクト開始時

1. **セッション作成**: tmux orchestratorでプロジェクトセッションを作成
2. **GitHub同期**: プロジェクトのイシューを同期
3. **チーム展開**: 必要な役割のエージェントを配置
4. **秘書起動**: AI秘書サービスを開始
5. **自動運用**: タスクの自動割り当てと進捗管理

### 日常運用

```bash
# 朝: スタンドアップミーティング（自動実行）
# → 各エージェントから状況報告を収集

# 日中: 継続的なタスク管理
# → 新しいイシューの同期
# → ワークロード調整
# → ブロッカーの検出と解決

# 夕方: 日報生成（自動実行）
# → 完了タスクの集計
# → 明日の優先事項の特定
```

## 🛠️ カスタマイズ

### 新しいエージェント役割の追加

`ai_secretary.py` の `AgentRole` enum に新しい役割を追加：

```python
class AgentRole(Enum):
    # 既存の役割...
    DESIGNER = "designer"      # デザイナー
    SECURITY = "security"      # セキュリティ専門家
```

### カスタムタスク優先度の設定

GitHubラベルベースの優先度判定をカスタマイズ：

```python
def determine_priority(labels):
    label_names = [label['name'].lower() for label in labels]
    
    if 'p0' in label_names or 'critical' in label_names:
        return Priority.CRITICAL
    elif 'p1' in label_names or 'high' in label_names:
        return Priority.HIGH
    # ... カスタムロジック
```

## 🐛 トラブルシューティング

### よくある問題

**Q: GitHubイシューが同期されない**
A: GitHub Tokenの権限を確認。`repo`スコープが必要です。

**Q: エージェントにメッセージが送信できない**
A: tmuxセッション/ウィンドウが存在するか確認してください。

**Q: Web UIが起動しない**
A: ポート5555が使用中でないか確認。他のポートを使用する場合は `app.run(port=別のポート)` を変更。

### デバッグモード

```bash
# デバッグログを有効化
export PYTHONPATH=/workspace/Tmux-Orchestrator
python3 -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from ai_secretary import AISecretary
secretary = AISecretary()
secretary.run_secretary_cycle()
"
```

## 🤝 貢献

プルリクエストやイシューレポートを歓迎します。新機能の提案や改善案があれば、お気軽にお知らせください。

## 📝 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

---

**作成者**: Claude AI  
**バージョン**: 1.0.0  
**最終更新**: 2024年8月6日