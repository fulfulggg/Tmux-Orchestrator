#!/usr/bin/env python3
"""
Orchestra Dashboard - TmuxOrchestraのリアルタイム監視インターフェース
"""

import curses
import json
import time
import subprocess
from datetime import datetime
from typing import List, Dict, Optional
import os
import sys

# 現在のディレクトリをPythonパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tmuxorchestra import TmuxOrchestra, Agent, AgentRole


class OrchestrationDashboard:
    """オーケストレートされたエージェントを監視するターミナルダッシュボード"""
    
    def __init__(self):
        self.orchestra = TmuxOrchestra()
        self.selected_session = None
        self.selected_agent = None
        self.view_mode = "overview"  # overview, session, agent
        self.refresh_interval = 5  # 秒
        self.last_refresh = 0
    
    def draw_header(self, stdscr, title: str):
        """ダッシュボードヘッダーを描画"""
        height, width = stdscr.getmaxyx()
        header = f"🎭 TmuxOrchestra ダッシュボード - {title} 🎭"
        header_pad = " " * ((width - len(header)) // 2)
        
        stdscr.attron(curses.color_pair(1))
        stdscr.addstr(0, 0, " " * width)
        stdscr.addstr(0, len(header_pad), header)
        stdscr.attroff(curses.color_pair(1))
        
        # ステータス行
        status = f"最終更新: {datetime.now().strftime('%H:%M:%S')} | 'q'で終了、'h'でヘルプ"
        stdscr.addstr(1, 0, status)
        stdscr.addstr(2, 0, "─" * width)
    
    def draw_overview(self, stdscr):
        """メイン概要画面を描画"""
        self.draw_header(stdscr, "システム概要")
        height, width = stdscr.getmaxyx()
        
        sessions = self.orchestra.list_sessions()
        y = 4
        
        stdscr.addstr(y, 2, "アクティブセッション:", curses.A_BOLD)
        y += 2
        
        for i, session in enumerate(sessions):
            # セッション内のエージェント数をカウント
            agent_count = sum(1 for a in self.orchestra.agents.values() 
                            if a.session == session and a.status == "active")
            
            if i == self.selected_session:
                stdscr.attron(curses.A_REVERSE)
            
            line = f"  [{i+1}] {session:<20} エージェント数: {agent_count}"
            if y < height - 5:
                stdscr.addstr(y, 2, line)
            
            if i == self.selected_session:
                stdscr.attroff(curses.A_REVERSE)
            
            y += 1
        
        # 指示
        y = height - 3
        stdscr.addstr(y, 2, "↑/↓で選択、Enterでセッション表示、'a'で全エージェント表示")
    
    def draw_session_view(self, stdscr, session: str):
        """セッションの詳細ビューを描画"""
        self.draw_header(stdscr, f"セッション: {session}")
        height, width = stdscr.getmaxyx()
        
        y = 4
        windows = self.orchestra.list_windows(session)
        
        stdscr.addstr(y, 2, f"{session}のウィンドウ:", curses.A_BOLD)
        y += 2
        
        for i, window in enumerate(windows):
            target = f"{session}:{window['index']}"
            agent = self.orchestra.agents.get(target)
            
            if i == self.selected_agent:
                stdscr.attron(curses.A_REVERSE)
            
            window_info = f"  [{window['index']}] {window['name']:<25}"
            if agent:
                window_info += f" ロール: {agent.role.value:<15} ステータス: {agent.status}"
            
            if y < height - 10:
                stdscr.addstr(y, 2, window_info[:width-4])
            
            if i == self.selected_agent:
                stdscr.attroff(curses.A_REVERSE)
            
            y += 1
        
        # 選択されたエージェントの詳細を表示
        if self.selected_agent is not None and self.selected_agent < len(windows):
            y += 2
            window = windows[self.selected_agent]
            target = f"{session}:{window['index']}"
            
            if target in self.orchestra.agents:
                agent = self.orchestra.agents[target]
                status = self.orchestra.get_agent_status(agent)
                
                stdscr.addstr(y, 2, "エージェント詳細:", curses.A_BOLD)
                y += 1
                
                details = [
                    f"現在のタスク: {status.get('current_task', 'なし')}",
                    f"最終活動: {agent.last_activity.strftime('%H:%M:%S')}",
                    f"ブロッカー: {', '.join(status.get('blockers', [])) or 'なし'}",
                ]
                
                for detail in details:
                    if y < height - 5:
                        stdscr.addstr(y, 4, detail[:width-6])
                        y += 1
        
        # 指示
        y = height - 3
        stdscr.addstr(y, 2, "↑/↓: 選択 | Enter: エージェント詳細 | 's': ステータス更新 | 'b': 戻る | 'q': 終了")
    
    def draw_agent_detail(self, stdscr, agent: Agent):
        """単一エージェントの詳細ビューを描画"""
        self.draw_header(stdscr, f"エージェント: {agent.target}")
        height, width = stdscr.getmaxyx()
        
        y = 4
        
        # エージェント情報
        info = [
            ("ロール", agent.role.value),
            ("プロジェクト", agent.project),
            ("ステータス", agent.status),
            ("作成日時", agent.created_at.strftime('%Y-%m-%d %H:%M')),
            ("最終活動", agent.last_activity.strftime('%H:%M:%S')),
        ]
        
        stdscr.addstr(y, 2, "エージェント情報:", curses.A_BOLD)
        y += 2
        
        for label, value in info:
            if y < height - 15:
                stdscr.addstr(y, 4, f"{label}:", curses.A_BOLD)
                stdscr.addstr(y, 20, str(value))
                y += 1
        
        # 最近の活動
        y += 2
        stdscr.addstr(y, 2, "最近の活動:", curses.A_BOLD)
        y += 1
        
        content = self.orchestra.capture_pane_content(agent.target, lines=10)
        lines = content.split('\n')[-8:]  # 最後の8行
        
        for line in lines:
            if y < height - 5:
                stdscr.addstr(y, 4, line[:width-6])
                y += 1
        
        # 指示
        y = height - 3
        stdscr.addstr(y, 2, "'m': メッセージ送信 | 'l': ログ表示 | 'b': 戻る | 'q': 終了")
    
    def send_message_dialog(self, stdscr, agent: Agent):
        """エージェントにメッセージを送信するダイアログを表示"""
        height, width = stdscr.getmaxyx()
        
        # ダイアログウィンドウを作成
        dialog_height = 8
        dialog_width = min(60, width - 10)
        dialog_y = (height - dialog_height) // 2
        dialog_x = (width - dialog_width) // 2
        
        dialog = curses.newwin(dialog_height, dialog_width, dialog_y, dialog_x)
        dialog.box()
        
        dialog.addstr(1, 2, f"{agent.target}にメッセージを送信", curses.A_BOLD)
        dialog.addstr(3, 2, "メッセージ: ")
        
        curses.echo()
        message = dialog.getstr(3, 14, dialog_width - 16).decode('utf-8')
        curses.noecho()
        
        if message:
            success = self.orchestra.send_message_to_agent(agent.target, message)
            dialog.addstr(5, 2, "メッセージ送信成功！" if success else "メッセージ送信失敗")
            dialog.refresh()
            time.sleep(1)
    
    def handle_input(self, stdscr, key):
        """キーボード入力を処理"""
        if key == ord('q'):
            return False
        
        elif key == ord('h'):
            self.show_help(stdscr)
        
        elif self.view_mode == "overview":
            sessions = self.orchestra.list_sessions()
            
            if key == curses.KEY_UP and self.selected_session is not None:
                self.selected_session = max(0, self.selected_session - 1)
            elif key == curses.KEY_DOWN and self.selected_session is not None:
                self.selected_session = min(len(sessions) - 1, self.selected_session + 1)
            elif key in [curses.KEY_UP, curses.KEY_DOWN] and self.selected_session is None:
                self.selected_session = 0
            elif key == ord('\n') and self.selected_session is not None:
                self.view_mode = "session"
                self.selected_agent = 0
            elif key == ord('a'):
                self.view_mode = "all_agents"
        
        elif self.view_mode == "session":
            session = self.orchestra.list_sessions()[self.selected_session]
            windows = self.orchestra.list_windows(session)
            
            if key == curses.KEY_UP and self.selected_agent > 0:
                self.selected_agent -= 1
            elif key == curses.KEY_DOWN and self.selected_agent < len(windows) - 1:
                self.selected_agent += 1
            elif key == ord('b'):
                self.view_mode = "overview"
            elif key == ord('s') and self.selected_agent is not None:
                window = windows[self.selected_agent]
                target = f"{session}:{window['index']}"
                self.orchestra.request_status_update(target)
            elif key == ord('\n') and self.selected_agent is not None:
                window = windows[self.selected_agent]
                target = f"{session}:{window['index']}"
                if target in self.orchestra.agents:
                    self.view_mode = "agent"
        
        elif self.view_mode == "agent":
            session = self.orchestra.list_sessions()[self.selected_session]
            windows = self.orchestra.list_windows(session)
            window = windows[self.selected_agent]
            target = f"{session}:{window['index']}"
            agent = self.orchestra.agents.get(target)
            
            if key == ord('b'):
                self.view_mode = "session"
            elif key == ord('m') and agent:
                self.send_message_dialog(stdscr, agent)
        
        return True
    
    def show_help(self, stdscr):
        """ヘルプ画面を表示"""
        height, width = stdscr.getmaxyx()
        
        help_text = [
            "TmuxOrchestra ダッシュボード ヘルプ",
            "",
            "ナビゲーション:",
            "  ↑/↓     - リストを移動",
            "  Enter   - 選択/詳細表示",
            "  b       - 戻る",
            "  q       - 終了",
            "",
            "アクション:",
            "  s       - ステータス更新要求 (セッションビュー)",
            "  m       - エージェントにメッセージ送信 (エージェントビュー)",
            "  a       - 全エージェント表示 (概要)",
            "",
            "任意のキーを押して続行..."
        ]
        
        stdscr.clear()
        y = (height - len(help_text)) // 2
        
        for line in help_text:
            x = (width - len(line)) // 2
            if 0 <= y < height:
                stdscr.addstr(y, max(0, x), line)
            y += 1
        
        stdscr.refresh()
        stdscr.getch()
    
    def run(self, stdscr):
        """メインダッシュボードループ"""
        # カラーを初期化
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        
        # cursesを設定
        curses.curs_set(0)  # カーソルを隠す
        stdscr.nodelay(1)   # ノンブロッキング入力
        stdscr.timeout(100) # getch()の100msタイムアウト
        
        running = True
        while running:
            # 定期的にデータを更新
            current_time = time.time()
            if current_time - self.last_refresh > self.refresh_interval:
                self.orchestra.load_agents()  # ディスクからエージェントを再読み込み
                self.last_refresh = current_time
            
            # クリアして描画
            stdscr.clear()
            
            try:
                if self.view_mode == "overview":
                    self.draw_overview(stdscr)
                elif self.view_mode == "session":
                    session = self.orchestra.list_sessions()[self.selected_session]
                    self.draw_session_view(stdscr, session)
                elif self.view_mode == "agent":
                    session = self.orchestra.list_sessions()[self.selected_session]
                    windows = self.orchestra.list_windows(session)
                    window = windows[self.selected_agent]
                    target = f"{session}:{window['index']}"
                    if target in self.orchestra.agents:
                        self.draw_agent_detail(stdscr, self.orchestra.agents[target])
            except Exception as e:
                stdscr.addstr(5, 2, f"エラー: {str(e)}")
            
            stdscr.refresh()
            
            # 入力を処理
            key = stdscr.getch()
            if key != -1:
                running = self.handle_input(stdscr, key)


def main():
    """ダッシュボードのメインエントリーポイント"""
    dashboard = OrchestrationDashboard()
    curses.wrapper(dashboard.run)


if __name__ == "__main__":
    main()
