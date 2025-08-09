#!/usr/bin/env python3
"""
Secretary UI - AI秘書システム用のWebインターフェース

このモジュールは、AI秘書システムの操作を簡単にするWeb UIを提供します。
Flask を使用したシンプルなダッシュボードで、タスク管理、エージェント監視、
レポート表示などの機能を提供します。
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
from datetime import datetime, timedelta
from ai_secretary import AISecretary, Task, Priority, TaskStatus
from tmuxorchestra import TmuxOrchestra
import logging

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('SecretaryUI')

app = Flask(__name__)
app.secret_key = 'ai-secretary-secret-key'

# グローバル変数
secretary = None
orchestra = None

def init_secretary():
    """秘書システムを初期化"""
    global secretary, orchestra
    if secretary is None:
        secretary = AISecretary()
        orchestra = TmuxOrchestra()

@app.route('/')
def dashboard():
    """メインダッシュボード"""
    init_secretary()
    
    # 統計情報を収集
    stats = {
        'total_tasks': len(secretary.tasks),
        'pending_tasks': len([t for t in secretary.tasks.values() if t.status == TaskStatus.PENDING]),
        'in_progress_tasks': len([t for t in secretary.tasks.values() if t.status == TaskStatus.IN_PROGRESS]),
        'completed_tasks': len([t for t in secretary.tasks.values() if t.status == TaskStatus.COMPLETED]),
        'active_agents': len([a for a in orchestra.agents.values() if a.status == "active"])
    }
    
    # 優先度別タスク
    priority_tasks = secretary.prioritize_tasks()
    
    # 最近のタスク (直近5件)
    recent_tasks = sorted(secretary.tasks.values(), 
                         key=lambda t: t.updated_at, reverse=True)[:5]
    
    return render_template('dashboard.html', 
                         stats=stats,
                         priority_tasks=priority_tasks[:10],
                         recent_tasks=recent_tasks)

@app.route('/tasks')
def tasks():
    """タスク一覧ページ"""
    init_secretary()
    
    filter_status = request.args.get('status', 'all')
    filter_priority = request.args.get('priority', 'all')
    
    task_list = list(secretary.tasks.values())
    
    # フィルタリング
    if filter_status != 'all':
        task_list = [t for t in task_list if t.status.value == filter_status]
    
    if filter_priority != 'all':
        task_list = [t for t in task_list if t.priority.value == filter_priority]
    
    # ソート
    task_list.sort(key=lambda t: t.updated_at, reverse=True)
    
    return render_template('tasks.html', 
                         tasks=task_list,
                         current_status=filter_status,
                         current_priority=filter_priority)

@app.route('/agents')
def agents():
    """エージェント監視ページ"""
    init_secretary()
    
    # エージェント情報を収集
    agents_info = []
    for target, agent in orchestra.agents.items():
        # 最新のステータスを取得
        content = orchestra.capture_pane_content(target, lines=20)
        
        agent_info = {
            'target': target,
            'role': agent.role.value,
            'project': agent.project,
            'status': agent.status,
            'last_activity': agent.last_activity,
            'recent_content': content[-500:] if content else "応答なし"  # 最後の500文字
        }
        agents_info.append(agent_info)
    
    return render_template('agents.html', agents=agents_info)

@app.route('/reports')
def reports():
    """レポート一覧ページ"""
    init_secretary()
    
    reports_dir = os.path.join(secretary.data_path, "reports")
    reports_list = []
    
    if os.path.exists(reports_dir):
        for filename in os.listdir(reports_dir):
            if filename.endswith('.md'):
                filepath = os.path.join(reports_dir, filename)
                stat = os.stat(filepath)
                
                reports_list.append({
                    'filename': filename,
                    'filepath': filepath,
                    'created_at': datetime.fromtimestamp(stat.st_ctime),
                    'size': stat.st_size
                })
    
    reports_list.sort(key=lambda r: r['created_at'], reverse=True)
    
    return render_template('reports.html', reports=reports_list)

@app.route('/view_report/<path:filename>')
def view_report(filename):
    """個別レポート表示"""
    init_secretary()
    
    filepath = os.path.join(secretary.data_path, "reports", filename)
    
    if os.path.exists(filepath) and filename.endswith('.md'):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return render_template('view_report.html', 
                             filename=filename, 
                             content=content)
    else:
        return "レポートが見つかりません", 404

@app.route('/api/tasks', methods=['GET'])
def api_get_tasks():
    """タスク一覧API"""
    init_secretary()
    
    tasks_data = []
    for task in secretary.tasks.values():
        task_dict = {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'priority': task.priority.value,
            'status': task.status.value,
            'assignee': task.assignee,
            'project': task.project,
            'created_at': task.created_at.isoformat(),
            'updated_at': task.updated_at.isoformat()
        }
        tasks_data.append(task_dict)
    
    return jsonify(tasks_data)

@app.route('/api/tasks', methods=['POST'])
def api_create_task():
    """タスク作成API"""
    init_secretary()
    
    data = request.get_json()
    
    if not data.get('title'):
        return jsonify({'error': 'タイトルは必須です'}), 400
    
    # 新しいタスクID生成
    task_id = f"task-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # タスク作成
    task = Task(
        id=task_id,
        title=data['title'],
        description=data.get('description', ''),
        priority=Priority(data.get('priority', 'medium')),
        status=TaskStatus.PENDING,
        project=data.get('project')
    )
    
    secretary.tasks[task_id] = task
    secretary.save_state()
    
    return jsonify({'task_id': task_id, 'message': 'タスクを作成しました'}), 201

@app.route('/api/tasks/<task_id>', methods=['PUT'])
def api_update_task(task_id):
    """タスク更新API"""
    init_secretary()
    
    if task_id not in secretary.tasks:
        return jsonify({'error': 'タスクが見つかりません'}), 404
    
    data = request.get_json()
    task = secretary.tasks[task_id]
    
    # 更新可能フィールド
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'priority' in data:
        task.priority = Priority(data['priority'])
    if 'status' in data:
        task.status = TaskStatus(data['status'])
    if 'assignee' in data:
        task.assignee = data['assignee']
    
    task.updated_at = datetime.now()
    secretary.save_state()
    
    return jsonify({'message': 'タスクを更新しました'})

@app.route('/api/assign_task', methods=['POST'])
def api_assign_task():
    """タスク割り当てAPI"""
    init_secretary()
    
    data = request.get_json()
    task_id = data.get('task_id')
    agent_target = data.get('agent_target')
    
    if not task_id or not agent_target:
        return jsonify({'error': 'task_idとagent_targetは必須です'}), 400
    
    task = secretary.tasks.get(task_id)
    if not task:
        return jsonify({'error': 'タスクが見つかりません'}), 404
    
    if secretary.assign_task_to_agent(task, agent_target):
        return jsonify({'message': 'タスクを割り当てました'})
    else:
        return jsonify({'error': 'タスク割り当てに失敗しました'}), 500

@app.route('/api/agents/<agent_target>/message', methods=['POST'])
def api_send_message(agent_target):
    """エージェントへのメッセージ送信API"""
    init_secretary()
    
    data = request.get_json()
    message = data.get('message')
    
    if not message:
        return jsonify({'error': 'メッセージは必須です'}), 400
    
    if orchestra.send_message_to_agent(agent_target, message):
        return jsonify({'message': 'メッセージを送信しました'})
    else:
        return jsonify({'error': 'メッセージ送信に失敗しました'}), 500

@app.route('/api/generate_report', methods=['POST'])
def api_generate_report():
    """レポート生成API"""
    init_secretary()
    
    data = request.get_json()
    session = data.get('session')
    
    report = secretary.generate_daily_report(session)
    return jsonify({'report': report})

@app.route('/api/sync_github', methods=['POST'])
def api_sync_github():
    """GitHub同期API"""
    init_secretary()
    
    data = request.get_json()
    repo = data.get('repo')  # "owner/name" 形式
    
    if not repo:
        return jsonify({'error': 'リポジトリは必須です'}), 400
    
    try:
        owner, name = repo.split('/')
        synced_tasks = secretary.sync_github_issues(owner, name)
        return jsonify({
            'message': f'{len(synced_tasks)}個のイシューを同期しました',
            'synced_count': len(synced_tasks)
        })
    except ValueError:
        return jsonify({'error': 'リポジトリは "owner/name" 形式で指定してください'}), 400

# HTMLテンプレートを作成するためのヘルパー関数
def create_templates():
    """HTMLテンプレートファイルを作成"""
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    # base.html
    base_template = '''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Secretary Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">
                <i class="fas fa-robot"></i> AI秘書
            </a>
            <div class="navbar-nav">
                <a class="nav-link" href="/">ダッシュボード</a>
                <a class="nav-link" href="/tasks">タスク</a>
                <a class="nav-link" href="/agents">エージェント</a>
                <a class="nav-link" href="/reports">レポート</a>
            </div>
        </div>
    </nav>
    
    <div class="container-fluid mt-4">
        {% block content %}{% endblock %}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>'''
    
    # dashboard.html
    dashboard_template = '''{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-md-12">
        <h1>AI秘書ダッシュボード</h1>
    </div>
</div>

<div class="row mb-4">
    <div class="col-md-3">
        <div class="card text-white bg-primary">
            <div class="card-body">
                <h5 class="card-title">総タスク数</h5>
                <h2>{{ stats.total_tasks }}</h2>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-white bg-warning">
            <div class="card-body">
                <h5 class="card-title">進行中</h5>
                <h2>{{ stats.in_progress_tasks }}</h2>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-white bg-success">
            <div class="card-body">
                <h5 class="card-title">完了</h5>
                <h2>{{ stats.completed_tasks }}</h2>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-white bg-info">
            <div class="card-body">
                <h5 class="card-title">アクティブエージェント</h5>
                <h2>{{ stats.active_agents }}</h2>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5>優先度順タスク</h5>
            </div>
            <div class="card-body">
                {% for task in priority_tasks %}
                <div class="d-flex justify-content-between align-items-center border-bottom py-2">
                    <div>
                        <strong>{{ task.title }}</strong>
                        <br>
                        <small class="text-muted">{{ task.description[:100] }}...</small>
                    </div>
                    <div>
                        {% if task.priority.value == 'critical' %}
                            <span class="badge bg-danger">{{ task.priority.value.upper() }}</span>
                        {% elif task.priority.value == 'high' %}
                            <span class="badge bg-warning">{{ task.priority.value.upper() }}</span>
                        {% else %}
                            <span class="badge bg-secondary">{{ task.priority.value.upper() }}</span>
                        {% endif %}
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5>最近のタスク</h5>
            </div>
            <div class="card-body">
                {% for task in recent_tasks %}
                <div class="d-flex justify-content-between align-items-center border-bottom py-2">
                    <div>
                        <strong>{{ task.title }}</strong>
                        <br>
                        <small class="text-muted">更新: {{ task.updated_at.strftime('%Y-%m-%d %H:%M') }}</small>
                    </div>
                    <div>
                        {% if task.status.value == 'completed' %}
                            <span class="badge bg-success">{{ task.status.value.upper() }}</span>
                        {% elif task.status.value == 'in_progress' %}
                            <span class="badge bg-primary">{{ task.status.value.upper() }}</span>
                        {% else %}
                            <span class="badge bg-secondary">{{ task.status.value.upper() }}</span>
                        {% endif %}
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
    
    # tasks.html
    tasks_template = '''{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-md-12">
        <h1>タスク管理</h1>
        
        <div class="row mb-3">
            <div class="col-md-6">
                <form method="GET" class="d-flex">
                    <select name="status" class="form-select me-2">
                        <option value="all" {% if current_status == 'all' %}selected{% endif %}>全ステータス</option>
                        <option value="pending" {% if current_status == 'pending' %}selected{% endif %}>未着手</option>
                        <option value="in_progress" {% if current_status == 'in_progress' %}selected{% endif %}>進行中</option>
                        <option value="completed" {% if current_status == 'completed' %}selected{% endif %}>完了</option>
                    </select>
                    <select name="priority" class="form-select me-2">
                        <option value="all" {% if current_priority == 'all' %}selected{% endif %}>全優先度</option>
                        <option value="critical" {% if current_priority == 'critical' %}selected{% endif %}>緊急</option>
                        <option value="high" {% if current_priority == 'high' %}selected{% endif %}>高</option>
                        <option value="medium" {% if current_priority == 'medium' %}selected{% endif %}>中</option>
                        <option value="low" {% if current_priority == 'low' %}selected{% endif %}>低</option>
                    </select>
                    <button type="submit" class="btn btn-primary">フィルタ</button>
                </form>
            </div>
        </div>
        
        <div class="table-responsive">
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>タイトル</th>
                        <th>優先度</th>
                        <th>ステータス</th>
                        <th>担当者</th>
                        <th>更新日時</th>
                    </tr>
                </thead>
                <tbody>
                    {% for task in tasks %}
                    <tr>
                        <td>
                            <strong>{{ task.title }}</strong>
                            <br>
                            <small class="text-muted">{{ task.description[:100] }}...</small>
                        </td>
                        <td>
                            {% if task.priority.value == 'critical' %}
                                <span class="badge bg-danger">{{ task.priority.value.upper() }}</span>
                            {% elif task.priority.value == 'high' %}
                                <span class="badge bg-warning">{{ task.priority.value.upper() }}</span>
                            {% else %}
                                <span class="badge bg-secondary">{{ task.priority.value.upper() }}</span>
                            {% endif %}
                        </td>
                        <td>
                            {% if task.status.value == 'completed' %}
                                <span class="badge bg-success">{{ task.status.value.upper() }}</span>
                            {% elif task.status.value == 'in_progress' %}
                                <span class="badge bg-primary">{{ task.status.value.upper() }}</span>
                            {% else %}
                                <span class="badge bg-secondary">{{ task.status.value.upper() }}</span>
                            {% endif %}
                        </td>
                        <td>{{ task.assignee or '未割り当て' }}</td>
                        <td>{{ task.updated_at.strftime('%Y-%m-%d %H:%M') }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}'''
    
    # テンプレートファイルを作成
    templates = {
        'base.html': base_template,
        'dashboard.html': dashboard_template,
        'tasks.html': tasks_template
    }
    
    for filename, content in templates.items():
        filepath = os.path.join(templates_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

if __name__ == '__main__':
    # テンプレートを作成
    create_templates()
    
    # Flaskアプリケーションを開始
    app.run(debug=True, host='0.0.0.0', port=5555)