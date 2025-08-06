#!/usr/bin/env python3
"""
TmuxOrchestra - Tmuxセッション全体でClaudeエージェントを管理する高度なオーケストレーションシステム

このモジュールは、複数のClaudeエージェントをtmuxセッション全体で管理するための
包括的なオーケストレーションシステムを提供します。
"""

import subprocess
import json
import time
import os
import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('TmuxOrchestra')


class AgentRole(Enum):
    """利用可能なエージェントロールの列挙"""
    ORCHESTRATOR = "orchestrator"
    PROJECT_MANAGER = "project-manager"
    DEVELOPER = "developer"
    QA_ENGINEER = "qa"
    DEVOPS = "devops"
    CODE_REVIEWER = "code-reviewer"
    RESEARCHER = "researcher"
    DOCUMENTATION_WRITER = "doc-writer"


@dataclass
class Agent:
    """システム内のClaudeエージェントを表現"""
    session: str
    window: str
    role: AgentRole
    project: str
    status: str = "active"
    created_at: datetime = None
    last_activity: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_activity is None:
            self.last_activity = datetime.now()
    
    @property
    def target(self) -> str:
        """tmuxターゲット識別子を返す"""
        return f"{self.session}:{self.window}"


class TmuxOrchestra:
    """Claudeエージェントを管理するメインオーケストレーションクラス"""
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.registry_path = os.path.expanduser("~/Coding/Tmux orchestrator/registry")
        self.ensure_registry_structure()
        self.load_agents()
    
    def ensure_registry_structure(self):
        """レジストリディレクトリ構造が存在することを確認"""
        os.makedirs(os.path.join(self.registry_path, "logs"), exist_ok=True)
        os.makedirs(os.path.join(self.registry_path, "notes"), exist_ok=True)
    
    def run_tmux_command(self, command: str) -> Tuple[bool, str]:
        """tmuxコマンドを実行し、成功ステータスと出力を返す"""
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True
            )
            return result.returncode == 0, result.stdout.strip()
        except Exception as e:
            logger.error(f"tmuxコマンド実行エラー: {e}")
            return False, str(e)
    
    def list_sessions(self) -> List[str]:
        """すべてのtmuxセッションをリスト"""
        success, output = self.run_tmux_command("tmux list-sessions -F '#{session_name}'")
        if success and output:
            return output.strip().split('\n')
        return []
    
    def list_windows(self, session: str) -> List[Dict[str, str]]:
        """セッション内のすべてのウィンドウとその詳細をリスト"""
        cmd = f"tmux list-windows -t {session} -F '#{{window_index}}:#{{window_name}}:#{{pane_current_path}}'"
        success, output = self.run_tmux_command(cmd)
        if success and output:
            windows = []
            for line in output.strip().split('\n'):
                parts = line.split(':')
                if len(parts) >= 3:
                    windows.append({
                        'index': parts[0],
                        'name': parts[1],
                        'path': ':'.join(parts[2:])  # コロンを含むパスを処理
                    })
            return windows
        return []
    
    def capture_pane_content(self, target: str, lines: int = 50) -> str:
        """tmuxペインからコンテンツをキャプチャ"""
        cmd = f"tmux capture-pane -t {target} -p | tail -{lines}"
        success, output = self.run_tmux_command(cmd)
        return output if success else ""
    
    def send_message_to_agent(self, target: str, message: str) -> bool:
        """send-claude-message.shスクリプトを使用してClaudeエージェントにメッセージを送信"""
        script_path = "/workspace/Tmux-Orchestrator/send-claude-message.sh"
        if os.path.exists(script_path):
            cmd = f'{script_path} {target} "{message}"'
            success, _ = self.run_tmux_command(cmd)
            return success
        else:
            # 直接メソッドへのフォールバック
            success1, _ = self.run_tmux_command(f'tmux send-keys -t {target} "{message}"')
            time.sleep(0.5)
            success2, _ = self.run_tmux_command(f'tmux send-keys -t {target} Enter')
            return success1 and success2
    
    def create_agent(self, session: str, project_path: str, role: AgentRole, 
                    window_name: Optional[str] = None) -> Optional[Agent]:
        """指定されたセッションに新しいエージェントを作成"""
        if window_name is None:
            window_name = f"Claude-{role.value.title()}"
        
        # 新しいウィンドウを作成
        cmd = f'tmux new-window -t {session} -n "{window_name}" -c "{project_path}"'
        success, _ = self.run_tmux_command(cmd)
        if not success:
            logger.error(f"{role.value}のウィンドウ作成に失敗しました")
            return None
        
        # ウィンドウインデックスを取得
        windows = self.list_windows(session)
        window_idx = None
        for w in windows:
            if w['name'] == window_name:
                window_idx = w['index']
                break
        
        if window_idx is None:
            logger.error(f"新しく作成されたウィンドウ {window_name} が見つかりません")
            return None
        
        # Claudeを起動
        target = f"{session}:{window_idx}"
        self.run_tmux_command(f'tmux send-keys -t {target} "claude" Enter')
        time.sleep(5)  # Claudeの起動を待つ
        
        # エージェントオブジェクトを作成
        agent = Agent(
            session=session,
            window=window_idx,
            role=role,
            project=os.path.basename(project_path)
        )
        
        # 初期ブリーフィングを送信
        briefing = self.generate_agent_briefing(agent)
        self.send_message_to_agent(target, briefing)
        
        # エージェントを登録
        self.agents[target] = agent
        self.save_agents()
        
        logger.info(f"{role.value}エージェントを{target}に作成しました")
        return agent
    
    def generate_agent_briefing(self, agent: Agent) -> str:
        """エージェントのロール固有のブリーフィングを生成"""
        briefings = {
            AgentRole.PROJECT_MANAGER: f"""あなたはこのプロジェクトのプロジェクトマネージャーです。あなたの責任：

1. **品質基準**: 非常に高い基準を維持する。ショートカットなし、妥協なし。
2. **検証**: すべてを徹底的にテストする。信頼するが検証する。
3. **チーム調整**: チームメンバー間のコミュニケーションを効率的に管理する。
4. **進捗追跡**: 速度を監視し、ブロッカーを特定し、オーケストレーターに報告する。
5. **リスク管理**: 問題になる前に潜在的な問題を特定する。

主要原則：
- テストと検証に細心の注意を払う
- すべての機能のテスト計画を作成する
- コードがベストプラクティスに従うことを確認する
- 技術的負債を追跡する
- 明確かつ建設的にコミュニケーションする

まず、プロジェクトと既存のチームメンバーを分析し、作業の調整を開始してください。""",
            
            AgentRole.DEVELOPER: f"""{agent.project}プロジェクトの開発者です。あなたの責任：

1. **実装**: クリーンで効率的、よくドキュメント化されたコードを書く
2. **ベストプラクティス**: プロジェクトの規約と業界標準に従う
3. **テスト**: コードのユニットテストを書く
4. **協力**: PMや他の開発者と協力する
5. **Git規律**: 30分ごとに意味のあるメッセージでコミットする

覚えておくべきこと：
- 常にフィーチャーブランチで作業する
- 1時間以上コミットせずに作業しない
- 要件が不明確な場合は明確化を求める
- 進捗とブロッカーをPMに報告する

まず、現在のプロジェクトステータスとオープンイシューを確認してください。""",
            
            AgentRole.QA_ENGINEER: """あなたはこのプロジェクトのQAエンジニアです。あなたの責任：

1. **テスト計画**: 包括的なテスト計画を作成する
2. **テスト実行**: すべての機能を徹底的にテストする
3. **バグ報告**: 再現手順とともに問題を明確に文書化する
4. **回帰テスト**: 修正が既存の機能を壊さないことを確認する
5. **品質ゲート**: 品質基準を強制する

焦点：
- エッジケースとエラー条件
- パフォーマンステスト
- セキュリティの脆弱性
- ユーザーエクスペリエンスの問題
- クロスブラウザ/プラットフォーム互換性

最近の変更をレビューし、テスト計画を作成することから始めてください。""",
            
            AgentRole.DEVOPS: """あなたはこのプロジェクトのDevOpsエンジニアです。あなたの責任：

1. **インフラ**: デプロイメントとインフラストラクチャを管理する
2. **CI/CD**: パイプラインのセットアップと保守
3. **監視**: ロギングと監視を実装する
4. **パフォーマンス**: アプリケーションのパフォーマンスを最適化する
5. **セキュリティ**: セキュリティのベストプラクティスを実装する

主要タスク：
- 必要に応じてコンテナ化
- 環境管理
- 自動デプロイメント
- バックアップ戦略
- スケーリングの考慮事項

現在のインフラストラクチャのセットアップを分析することから始めてください。""",
        }
        
        return briefings.get(agent.role, f"あなたは{agent.project}プロジェクトの{agent.role.value}です。コードベースを分析し、責任を理解することから始めてください。")
    
    def deploy_team(self, project_name: str, project_path: str, team_size: str = "medium"):
        """プロジェクトの完全なチームを展開"""
        # セッションが存在するか確認、存在しない場合は作成
        if project_name not in self.list_sessions():
            cmd = f'tmux new-session -d -s {project_name} -c "{project_path}"'
            success, _ = self.run_tmux_command(cmd)
            if not success:
                logger.error(f"セッション{project_name}の作成に失敗しました")
                return
            
            # 最初のウィンドウの名前を変更
            self.run_tmux_command(f'tmux rename-window -t {project_name}:0 "Claude-Lead"')
        
        # チーム構成を定義
        teams = {
            "small": [AgentRole.DEVELOPER, AgentRole.PROJECT_MANAGER],
            "medium": [AgentRole.DEVELOPER, AgentRole.DEVELOPER, 
                      AgentRole.PROJECT_MANAGER, AgentRole.QA_ENGINEER],
            "large": [AgentRole.DEVELOPER, AgentRole.DEVELOPER, AgentRole.DEVELOPER,
                     AgentRole.PROJECT_MANAGER, AgentRole.QA_ENGINEER, 
                     AgentRole.DEVOPS, AgentRole.CODE_REVIEWER]
        }
        
        team_composition = teams.get(team_size, teams["medium"])
        
        logger.info(f"{project_name}に{team_size}チームを展開中")
        
        for role in team_composition:
            agent = self.create_agent(project_name, project_path, role)
            if agent:
                logger.info(f"{project_name}に{role.value}を展開しました")
                time.sleep(2)  # システムを圧迫しないよう
    
    def get_agent_status(self, agent: Agent) -> Dict[str, any]:
        """エージェントの現在のステータスを取得"""
        content = self.capture_pane_content(agent.target, lines=100)
        
        # コンテンツ内のステータスパターンを探す
        status = {
            "agent": agent.target,
            "role": agent.role.value,
            "project": agent.project,
            "last_activity": agent.last_activity.isoformat(),
            "current_task": None,
            "blockers": [],
            "completed_tasks": []
        }
        
        # ステータス情報のコンテンツを解析
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "Current:" in line or "Working on:" in line or "現在:" in line:
                status["current_task"] = line.split(":", 1)[1].strip()
            elif "Blocked:" in line or "ブロッカー:" in line:
                status["blockers"].append(line.split(":", 1)[1].strip())
            elif "Completed:" in line or "完了:" in line and i + 1 < len(lines):
                # 次の行で完了したタスクを探す
                j = i + 1
                while j < len(lines) and lines[j].strip().startswith("-"):
                    status["completed_tasks"].append(lines[j].strip()[1:].strip())
                    j += 1
        
        return status
    
    def request_status_update(self, target: str):
        """エージェントにステータス更新を要求"""
        message = "ステータス更新: 1) 完了したタスク、2) 現在の作業、3) ブロッカーを提供してください"
        self.send_message_to_agent(target, message)
    
    def aggregate_team_status(self, session: str) -> Dict[str, any]:
        """セッション内のすべてのエージェントからステータスを集約"""
        team_status = {
            "session": session,
            "timestamp": datetime.now().isoformat(),
            "agents": []
        }
        
        for target, agent in self.agents.items():
            if agent.session == session:
                agent_status = self.get_agent_status(agent)
                team_status["agents"].append(agent_status)
        
        return team_status
    
    def save_agents(self):
        """エージェントレジストリをディスクに保存"""
        registry_file = os.path.join(self.registry_path, "agents.json")
        agents_data = {}
        for target, agent in self.agents.items():
            agents_data[target] = {
                "session": agent.session,
                "window": agent.window,
                "role": agent.role.value,
                "project": agent.project,
                "status": agent.status,
                "created_at": agent.created_at.isoformat(),
                "last_activity": agent.last_activity.isoformat()
            }
        
        with open(registry_file, 'w') as f:
            json.dump(agents_data, f, indent=2, ensure_ascii=False)
    
    def load_agents(self):
        """ディスクからエージェントレジストリをロード"""
        registry_file = os.path.join(self.registry_path, "agents.json")
        if os.path.exists(registry_file):
            with open(registry_file, 'r') as f:
                agents_data = json.load(f)
            
            for target, data in agents_data.items():
                agent = Agent(
                    session=data["session"],
                    window=data["window"],
                    role=AgentRole(data["role"]),
                    project=data["project"],
                    status=data["status"],
                    created_at=datetime.fromisoformat(data["created_at"]),
                    last_activity=datetime.fromisoformat(data["last_activity"])
                )
                self.agents[target] = agent
    
    def orchestrate(self):
        """メインオーケストレーションループ"""
        logger.info("TmuxOrchestraオーケストレーションを開始")
        
        while True:
            try:
                # すべてのエージェントをチェック
                for target, agent in list(self.agents.items()):
                    # エージェントがまだ存在することを確認
                    content = self.capture_pane_content(target, lines=10)
                    if not content:
                        logger.warning(f"エージェント{target}は死んでいるようです")
                        agent.status = "dead"
                        continue
                    
                    # 新しいコンテンツがある場合は最終活動を更新
                    agent.last_activity = datetime.now()
                
                # 定期的なステータスチェック
                current_time = datetime.now()
                for target, agent in self.agents.items():
                    if agent.status == "active":
                        time_since_update = (current_time - agent.last_activity).seconds
                        if time_since_update > 900:  # 15分
                            logger.info(f"{target}からステータスを要求中")
                            self.request_status_update(target)
                
                # 状態を保存
                self.save_agents()
                
                # 次の反復前にスリープ
                time.sleep(60)  # 毎分チェック
                
            except KeyboardInterrupt:
                logger.info("ユーザーによってオーケストレーションが停止されました")
                break
            except Exception as e:
                logger.error(f"オーケストレーションエラー: {e}")
                time.sleep(10)  # 再試行前に短い一時停止


def main():
    """TmuxOrchestraのメインエントリーポイント"""
    import argparse
    
    parser = argparse.ArgumentParser(description="TmuxOrchestra - tmuxでClaudeエージェントをオーケストレート")
    parser.add_argument('command', choices=['start', 'deploy', 'status', 'list'],
                       help='実行するコマンド')
    parser.add_argument('--project', help='プロジェクト名')
    parser.add_argument('--path', help='プロジェクトパス')
    parser.add_argument('--team-size', choices=['small', 'medium', 'large'],
                       default='medium', help='展開するチームサイズ')
    parser.add_argument('--session', help='ステータス/リスト用のセッション名')
    
    args = parser.parse_args()
    
    orchestra = TmuxOrchestra()
    
    if args.command == 'start':
        orchestra.orchestrate()
    
    elif args.command == 'deploy':
        if not args.project or not args.path:
            print("エラー: deployには--projectと--pathが必要です")
            return
        orchestra.deploy_team(args.project, args.path, args.team_size)
    
    elif args.command == 'status':
        if args.session:
            status = orchestra.aggregate_team_status(args.session)
            print(json.dumps(status, indent=2, ensure_ascii=False))
        else:
            # すべてのエージェントを表示
            for target, agent in orchestra.agents.items():
                print(f"{target}: {agent.role.value} ({agent.status})")
    
    elif args.command == 'list':
        sessions = orchestra.list_sessions()
        for session in sessions:
            print(f"\nセッション: {session}")
            windows = orchestra.list_windows(session)
            for window in windows:
                print(f"  {window['index']}: {window['name']} ({window['path']})")


if __name__ == "__main__":
    main()
