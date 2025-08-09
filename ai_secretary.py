#!/usr/bin/env python3
"""
AI Secretary - Tmux Orchestra用の智能秘書システム

このモジュールは、Tmux Orchestraの運用を支援するAI秘書機能を提供します。
以下の機能を含みます：
- プロジェクトの自動管理
- エージェント間のコミュニケーション調整
- スケジュール管理とリマインダー
- GitHubイシューの優先順位付け
- 日報・週報の自動生成
"""

import json
import time
import os
import subprocess
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from tmuxorchestra import TmuxOrchestra, Agent, AgentRole

logger = logging.getLogger('AISecretary')

class Priority(Enum):
    """タスクの優先度"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class TaskStatus(Enum):
    """タスクのステータス"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"

@dataclass
class Task:
    """秘書が管理するタスク"""
    id: str
    title: str
    description: str
    priority: Priority
    status: TaskStatus
    assignee: Optional[str] = None
    project: Optional[str] = None
    due_date: Optional[datetime] = None
    created_at: datetime = None
    updated_at: datetime = None
    github_issue: Optional[int] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

@dataclass
class Meeting:
    """会議・チェックイン情報"""
    id: str
    title: str
    participants: List[str]
    scheduled_time: datetime
    duration_minutes: int = 30
    notes: str = ""
    completed: bool = False

class AISecretary:
    """AI秘書システムのメインクラス"""
    
    def __init__(self, github_token: Optional[str] = None):
        self.orchestra = TmuxOrchestra()
        self.github_token = github_token
        self.data_path = os.path.expanduser("~/Coding/Tmux orchestrator/secretary")
        self.ensure_data_structure()
        
        # 状態管理
        self.tasks: Dict[str, Task] = {}
        self.meetings: Dict[str, Meeting] = {}
        self.load_state()
    
    def ensure_data_structure(self):
        """秘書データディレクトリの構造を確保"""
        os.makedirs(os.path.join(self.data_path, "tasks"), exist_ok=True)
        os.makedirs(os.path.join(self.data_path, "meetings"), exist_ok=True)
        os.makedirs(os.path.join(self.data_path, "reports"), exist_ok=True)
    
    def save_state(self):
        """現在の状態をディスクに保存"""
        # タスクを保存
        tasks_file = os.path.join(self.data_path, "tasks", "tasks.json")
        tasks_data = {}
        for task_id, task in self.tasks.items():
            task_dict = asdict(task)
            # datetimeをISO文字列に変換
            for key in ['created_at', 'updated_at', 'due_date']:
                if task_dict[key]:
                    task_dict[key] = task_dict[key].isoformat() if isinstance(task_dict[key], datetime) else task_dict[key]
            task_dict['priority'] = task_dict['priority'].value if isinstance(task_dict['priority'], Priority) else task_dict['priority']
            task_dict['status'] = task_dict['status'].value if isinstance(task_dict['status'], TaskStatus) else task_dict['status']
            tasks_data[task_id] = task_dict
        
        with open(tasks_file, 'w', encoding='utf-8') as f:
            json.dump(tasks_data, f, indent=2, ensure_ascii=False)
    
    def load_state(self):
        """ディスクから状態をロード"""
        tasks_file = os.path.join(self.data_path, "tasks", "tasks.json")
        if os.path.exists(tasks_file):
            with open(tasks_file, 'r', encoding='utf-8') as f:
                tasks_data = json.load(f)
            
            for task_id, data in tasks_data.items():
                # ISO文字列をdatetimeに変換
                for key in ['created_at', 'updated_at', 'due_date']:
                    if data[key]:
                        data[key] = datetime.fromisoformat(data[key])
                
                data['priority'] = Priority(data['priority'])
                data['status'] = TaskStatus(data['status'])
                
                self.tasks[task_id] = Task(**data)
    
    def sync_github_issues(self, repo_owner: str, repo_name: str) -> List[Task]:
        """GitHubイシューを同期してタスクとして取り込み"""
        if not self.github_token:
            logger.warning("GitHubトークンが設定されていません")
            return []
        
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/issues'
        try:
            response = requests.get(url, headers=headers, params={'state': 'open'})
            response.raise_for_status()
            issues = response.json()
            
            synced_tasks = []
            for issue in issues[:10]:  # 最新10件のみ
                task_id = f"gh-{issue['number']}"
                
                # 優先度をラベルから推定
                labels = [label['name'].lower() for label in issue['labels']]
                priority = Priority.MEDIUM
                if 'urgent' in labels or 'critical' in labels:
                    priority = Priority.CRITICAL
                elif 'high' in labels or 'priority-high' in labels:
                    priority = Priority.HIGH
                elif 'low' in labels or 'priority-low' in labels:
                    priority = Priority.LOW
                
                task = Task(
                    id=task_id,
                    title=issue['title'],
                    description=issue['body'] or "",
                    priority=priority,
                    status=TaskStatus.PENDING,
                    github_issue=issue['number']
                )
                
                self.tasks[task_id] = task
                synced_tasks.append(task)
            
            logger.info(f"{len(synced_tasks)}個のGitHubイシューを同期しました")
            self.save_state()
            return synced_tasks
            
        except Exception as e:
            logger.error(f"GitHubイシューの同期エラー: {e}")
            return []
    
    def prioritize_tasks(self) -> List[Task]:
        """タスクを優先度順にソート"""
        priority_order = {
            Priority.CRITICAL: 0,
            Priority.HIGH: 1,
            Priority.MEDIUM: 2,
            Priority.LOW: 3
        }
        
        active_tasks = [task for task in self.tasks.values() 
                       if task.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]]
        
        return sorted(active_tasks, 
                     key=lambda t: (priority_order[t.priority], t.created_at))
    
    def assign_task_to_agent(self, task: Task, agent_target: str) -> bool:
        """タスクをエージェントに割り当て"""
        if agent_target not in self.orchestra.agents:
            logger.error(f"エージェント {agent_target} が見つかりません")
            return False
        
        task.assignee = agent_target
        task.status = TaskStatus.IN_PROGRESS
        task.updated_at = datetime.now()
        
        # エージェントにタスク通知を送信
        message = f"""新しいタスクが割り当てられました：

タスク: {task.title}
優先度: {task.priority.value}
説明: {task.description[:200]}...

このタスクに取り組み、完了時にステータスを報告してください。"""
        
        success = self.orchestra.send_message_to_agent(agent_target, message)
        if success:
            logger.info(f"タスク {task.id} をエージェント {agent_target} に割り当てました")
            self.save_state()
            return True
        return False
    
    def check_agent_workload(self) -> Dict[str, int]:
        """各エージェントの現在のワークロードを確認"""
        workload = {}
        for task in self.tasks.values():
            if task.status == TaskStatus.IN_PROGRESS and task.assignee:
                workload[task.assignee] = workload.get(task.assignee, 0) + 1
        return workload
    
    def auto_assign_tasks(self):
        """タスクを自動的にエージェントに割り当て"""
        prioritized_tasks = self.prioritize_tasks()
        unassigned_tasks = [t for t in prioritized_tasks if not t.assignee]
        
        if not unassigned_tasks:
            return
        
        # 開発者エージェントを取得
        developer_agents = [target for target, agent in self.orchestra.agents.items() 
                           if agent.role == AgentRole.DEVELOPER and agent.status == "active"]
        
        if not developer_agents:
            logger.warning("利用可能な開発者エージェントがありません")
            return
        
        # ワークロードを確認
        workload = self.check_agent_workload()
        
        # 最も負荷の少ないエージェントから順に割り当て
        for task in unassigned_tasks[:3]:  # 一度に3つまで
            least_loaded_agent = min(developer_agents, 
                                   key=lambda agent: workload.get(agent, 0))
            
            if self.assign_task_to_agent(task, least_loaded_agent):
                workload[least_loaded_agent] = workload.get(least_loaded_agent, 0) + 1
    
    def schedule_standup(self, session: str, time_str: str = "09:00"):
        """定期スタンドアップをスケジュール"""
        try:
            hour, minute = map(int, time_str.split(':'))
            now = datetime.now()
            scheduled_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # 今日の時間が過ぎていれば明日にスケジュール
            if scheduled_time <= now:
                scheduled_time += timedelta(days=1)
            
            # 参加者を取得（セッション内のすべてのアクティブエージェント）
            participants = [target for target, agent in self.orchestra.agents.items() 
                          if agent.session == session and agent.status == "active"]
            
            meeting = Meeting(
                id=f"standup-{session}-{scheduled_time.strftime('%Y%m%d')}",
                title=f"{session}プロジェクト スタンドアップ",
                participants=participants,
                scheduled_time=scheduled_time,
                duration_minutes=15
            )
            
            self.meetings[meeting.id] = meeting
            logger.info(f"スタンドアップを{scheduled_time}にスケジュールしました")
            
        except Exception as e:
            logger.error(f"スタンドアップのスケジュールエラー: {e}")
    
    def conduct_standup(self, meeting: Meeting):
        """スタンドアップを実施"""
        logger.info(f"スタンドアップ開始: {meeting.title}")
        
        # 各参加者にステータス更新を要求
        status_updates = {}
        for participant in meeting.participants:
            self.orchestra.request_status_update(participant)
            time.sleep(2)  # エージェントの応答時間を確保
            
            # 応答を収集
            content = self.orchestra.capture_pane_content(participant, lines=20)
            status_updates[participant] = content
        
        # ミーティングノートを生成
        meeting.notes = f"スタンドアップ実施時間: {datetime.now().isoformat()}\n\n"
        for participant, update in status_updates.items():
            meeting.notes += f"=== {participant} ===\n{update}\n\n"
        
        meeting.completed = True
        
        # ミーティングノートを保存
        meeting_file = os.path.join(self.data_path, "meetings", 
                                  f"{meeting.id}.json")
        with open(meeting_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(meeting), f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"スタンドアップ完了: {meeting.title}")
    
    def generate_daily_report(self, session: str = None) -> str:
        """日報を生成"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        report = f"# 日報 - {today}\n\n"
        
        # タスクの進捗
        report += "## タスク進捗\n\n"
        completed_today = []
        in_progress = []
        
        for task in self.tasks.values():
            if session and task.project != session:
                continue
                
            if (task.status == TaskStatus.COMPLETED and 
                task.updated_at.date() == datetime.now().date()):
                completed_today.append(task)
            elif task.status == TaskStatus.IN_PROGRESS:
                in_progress.append(task)
        
        report += f"### 完了 ({len(completed_today)}件)\n"
        for task in completed_today:
            report += f"- [{task.priority.value.upper()}] {task.title}\n"
        
        report += f"\n### 進行中 ({len(in_progress)}件)\n"
        for task in in_progress:
            report += f"- [{task.priority.value.upper()}] {task.title} (担当: {task.assignee or '未割り当て'})\n"
        
        # エージェントステータス
        if session:
            team_status = self.orchestra.aggregate_team_status(session)
            report += f"\n## {session} チームステータス\n\n"
            
            for agent_status in team_status.get("agents", []):
                report += f"### {agent_status['role'].title()}\n"
                if agent_status.get("current_task"):
                    report += f"- 現在の作業: {agent_status['current_task']}\n"
                if agent_status.get("blockers"):
                    report += f"- ブロッカー: {', '.join(agent_status['blockers'])}\n"
                report += "\n"
        
        # 保存
        report_file = os.path.join(self.data_path, "reports", 
                                 f"daily-{today}{'-' + session if session else ''}.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return report
    
    def run_secretary_cycle(self):
        """秘書の定期実行サイクル"""
        logger.info("AI秘書サイクル開始")
        
        try:
            # 1. タスクの自動割り当て
            self.auto_assign_tasks()
            
            # 2. スケジュールされたミーティングをチェック
            now = datetime.now()
            for meeting_id, meeting in self.meetings.items():
                if (not meeting.completed and 
                    meeting.scheduled_time <= now <= meeting.scheduled_time + timedelta(minutes=5)):
                    self.conduct_standup(meeting)
            
            # 3. 長時間応答のないエージェントをチェック
            for target, agent in self.orchestra.agents.items():
                if agent.status == "active":
                    time_since_activity = (now - agent.last_activity).seconds
                    if time_since_activity > 3600:  # 1時間
                        logger.warning(f"エージェント {target} が1時間以上非アクティブです")
                        self.orchestra.send_message_to_agent(target, 
                                                           "ステータス確認: 応答をお願いします")
            
            # 4. 日次レポート生成（毎日17時）
            if now.hour == 17 and now.minute < 5:
                active_sessions = set(agent.session for agent in self.orchestra.agents.values())
                for session in active_sessions:
                    self.generate_daily_report(session)
            
            self.save_state()
            
        except Exception as e:
            logger.error(f"秘書サイクルエラー: {e}")
    
    def start_secretary_service(self):
        """秘書サービスを開始"""
        logger.info("AI秘書サービス開始")
        
        while True:
            try:
                self.run_secretary_cycle()
                time.sleep(300)  # 5分ごとに実行
                
            except KeyboardInterrupt:
                logger.info("AI秘書サービス停止")
                break
            except Exception as e:
                logger.error(f"秘書サービスエラー: {e}")
                time.sleep(60)  # エラー時は1分待機

def main():
    """AI秘書のメインエントリーポイント"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Secretary for Tmux Orchestra")
    parser.add_argument('command', choices=['start', 'sync', 'assign', 'report', 'standup'],
                       help='実行するコマンド')
    parser.add_argument('--github-token', help='GitHubアクセストークン')
    parser.add_argument('--repo', help='GitHubリポジトリ (owner/name形式)')
    parser.add_argument('--session', help='対象セッション')
    parser.add_argument('--task-id', help='タスクID')
    parser.add_argument('--agent', help='エージェント識別子')
    
    args = parser.parse_args()
    
    secretary = AISecretary(github_token=args.github_token)
    
    if args.command == 'start':
        secretary.start_secretary_service()
    
    elif args.command == 'sync':
        if args.repo:
            owner, name = args.repo.split('/')
            secretary.sync_github_issues(owner, name)
            print(f"GitHubイシューを同期しました: {args.repo}")
        else:
            print("--repo が必要です (例: --repo owner/repository)")
    
    elif args.command == 'assign':
        if args.task_id and args.agent:
            task = secretary.tasks.get(args.task_id)
            if task:
                if secretary.assign_task_to_agent(task, args.agent):
                    print(f"タスク {args.task_id} をエージェント {args.agent} に割り当てました")
                else:
                    print("タスク割り当てに失敗しました")
            else:
                print(f"タスク {args.task_id} が見つかりません")
        else:
            print("--task-id と --agent が必要です")
    
    elif args.command == 'report':
        report = secretary.generate_daily_report(args.session)
        print(report)
    
    elif args.command == 'standup':
        if args.session:
            secretary.schedule_standup(args.session)
            print(f"セッション {args.session} のスタンドアップをスケジュールしました")
        else:
            print("--session が必要です")

if __name__ == "__main__":
    main()