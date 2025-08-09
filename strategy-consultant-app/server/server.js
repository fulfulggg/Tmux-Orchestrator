require('dotenv').config();
const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const { verifyArgumentWithAI } = require('./ai-services');

const app = express();
const PORT = process.env.PORT || 5000;

// ミドルウェア
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// SQLiteデータベース初期化
const dbPath = path.join(__dirname, 'database.sqlite');
const db = new sqlite3.Database(dbPath);

// データベーステーブル作成
db.serialize(() => {
  // プロジェクトテーブル
  db.run(`CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    client_name TEXT,
    industry TEXT,
    theme TEXT,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )`);

  // 論点テーブル
  db.run(`CREATE TABLE IF NOT EXISTS arguments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    major_point TEXT,
    medium_point TEXT,
    minor_point TEXT,
    hypothesis TEXT,
    verification_approach TEXT,
    required_data TEXT,
    assignee TEXT,
    priority TEXT,
    status TEXT,
    deadline TEXT,
    ai_consensus INTEGER DEFAULT 0,
    ai_feedback TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects (id)
  )`);

  // 過去事例テーブル
  db.run(`CREATE TABLE IF NOT EXISTS past_cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    industry TEXT,
    theme TEXT,
    tags TEXT,
    project_scale TEXT,
    region TEXT,
    urgency TEXT,
    outcome TEXT,
    arguments_json TEXT,
    lessons_learned TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )`);

  // クライアント情報テーブル
  db.run(`CREATE TABLE IF NOT EXISTS client_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    company_name TEXT,
    industry TEXT,
    business_scale TEXT,
    revenue TEXT,
    employees TEXT,
    regions TEXT,
    business_model TEXT,
    key_challenges TEXT,
    stakeholders TEXT,
    decision_process TEXT,
    kpis TEXT,
    financial_info TEXT,
    competitive_landscape TEXT,
    past_initiatives TEXT,
    FOREIGN KEY (project_id) REFERENCES projects (id)
  )`);
});

// API エンドポイント

// プロジェクト関連
app.get('/api/projects', (req, res) => {
  db.all('SELECT * FROM projects ORDER BY created_at DESC', (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json(rows);
  });
});

app.post('/api/projects', (req, res) => {
  const { name, client_name, industry, theme, description } = req.body;
  db.run(
    'INSERT INTO projects (name, client_name, industry, theme, description) VALUES (?, ?, ?, ?, ?)',
    [name, client_name, industry, theme, description],
    function(err) {
      if (err) {
        res.status(500).json({ error: err.message });
        return;
      }
      res.json({ id: this.lastID, message: 'プロジェクトが作成されました' });
    }
  );
});

// 論点関連
app.get('/api/projects/:id/arguments', (req, res) => {
  const projectId = req.params.id;
  db.all('SELECT * FROM arguments WHERE project_id = ? ORDER BY id', [projectId], (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json(rows);
  });
});

app.post('/api/projects/:id/arguments', (req, res) => {
  const projectId = req.params.id;
  const {
    major_point, medium_point, minor_point, hypothesis,
    verification_approach, required_data, assignee,
    priority, status, deadline
  } = req.body;

  db.run(
    `INSERT INTO arguments 
    (project_id, major_point, medium_point, minor_point, hypothesis, 
     verification_approach, required_data, assignee, priority, status, deadline) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    [projectId, major_point, medium_point, minor_point, hypothesis,
     verification_approach, required_data, assignee, priority, status, deadline],
    function(err) {
      if (err) {
        res.status(500).json({ error: err.message });
        return;
      }
      res.json({ id: this.lastID, message: '論点が追加されました' });
    }
  );
});

app.put('/api/arguments/:id', (req, res) => {
  const argumentId = req.params.id;
  const {
    major_point, medium_point, minor_point, hypothesis,
    verification_approach, required_data, assignee,
    priority, status, deadline
  } = req.body;

  db.run(
    `UPDATE arguments SET 
    major_point = ?, medium_point = ?, minor_point = ?, hypothesis = ?,
    verification_approach = ?, required_data = ?, assignee = ?,
    priority = ?, status = ?, deadline = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?`,
    [major_point, medium_point, minor_point, hypothesis,
     verification_approach, required_data, assignee, priority, status, deadline, argumentId],
    function(err) {
      if (err) {
        res.status(500).json({ error: err.message });
        return;
      }
      res.json({ message: '論点が更新されました' });
    }
  );
});

// AI検証エンドポイント
app.post('/api/ai-verify/:id', async (req, res) => {
  const argumentId = req.params.id;
  
  try {
    // 論点データを取得
    db.get('SELECT * FROM arguments WHERE id = ?', [argumentId], async (err, argument) => {
      if (err) {
        res.status(500).json({ error: err.message });
        return;
      }
      
      if (!argument) {
        res.status(404).json({ error: '論点が見つかりません' });
        return;
      }

      // AI検証を実行
      const feedback = await verifyArgumentWithAI(argument);

      // 結果をデータベースに保存
      db.run(
        'UPDATE arguments SET ai_consensus = ?, ai_feedback = ? WHERE id = ?',
        [feedback.consensus, JSON.stringify(feedback), argumentId],
        function(err) {
          if (err) {
            res.status(500).json({ error: err.message });
            return;
          }
          res.json(feedback);
        }
      );
    });
  } catch (error) {
    console.error('AI verification error:', error);
    res.status(500).json({ error: 'AI検証でエラーが発生しました' });
  }
});

// 過去事例検索
app.get('/api/past-cases', (req, res) => {
  const { industry, theme, tags } = req.query;
  let query = 'SELECT * FROM past_cases WHERE 1=1';
  const params = [];

  if (industry) {
    query += ' AND industry LIKE ?';
    params.push(`%${industry}%`);
  }
  if (theme) {
    query += ' AND theme LIKE ?';
    params.push(`%${theme}%`);
  }
  if (tags) {
    query += ' AND tags LIKE ?';
    params.push(`%${tags}%`);
  }

  query += ' ORDER BY created_at DESC LIMIT 20';

  db.all(query, params, (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json(rows);
  });
});

// サーバー起動
app.listen(PORT, () => {
  console.log(`サーバーがポート${PORT}で起動しました`);
  console.log(`http://localhost:${PORT}`);
});

module.exports = app;